
from .IScript import IScript
from . import IType

from .CodeHandlers import ICEByteCodeHandler, ICESerializeContext, ICEParseContext, ICESourceCodeHandler

from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import Struct
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.DecompileStrategy import DecompileStrategyBuilder
from ...Utilities.CodeHandlers.SourceCodeSerializer import SourceCodeSerializer
from ...Utilities.CodeHandlers.ByteCodeBuilder import ByteCodeBuilder

from collections import OrderedDict
import io

from typing import Iterable

class IScriptBIN:
	def __init__(self) -> None:
		self._scripts: OrderedDict[int, IScript] = OrderedDict()
		self._cached_size: int | None = None

	def load(self, input: IO.AnyInputBytes) -> None:
		try:
			with IO.InputBytes(input) as f:
				data = f.read()
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', "Couldn't load iscript.bin from disk", capture_exception=True)
		bytecode_handler = ICEByteCodeHandler(data)
		scanner = BytesScanner(data)
		try:
			header_list_offset = scanner.scan(Struct.l_u32)
			scripts: OrderedDict[int, IScript] = OrderedDict()
			scanner.jump_to(header_list_offset)
			while True:
				if not scanner.can_scan(Struct.l_u32):
					raise PyMSError('Load', 'Unexpected end of header list, file could possibly be invalid or corrupt')
				id = scanner.scan(Struct.l_u16)
				if id == 65535:
					break
				header_offset = scanner.scan(Struct.l_u16)
				if not header_offset or not scanner.is_offset_valid(header_offset):
					raise PyMSError('Load', f'Script with id {id} has invalid header offset {header_offset}, file could possibly be invalid or corrupt')
				header_scanner = scanner.clone(header_offset)
				if not header_scanner.can_scan_bytes(4):
					raise PyMSError('Load', f'Script with id {id} has invalid header offset {header_offset} (insufficient space), file could possibly be invalid or corrupt')
				if header_scanner.scan_bytes(4) != b'SCPE':
					raise PyMSError('Load', f'Script with id {id} header is missing, could possibly be a corrupt iscript.bin')
				if header_scanner.at_end():
					raise PyMSError('Load', f'Script with id {id} has invalid header offset {header_offset} (insufficient space for type), file could possibly be invalid or corrupt')
				script_type = header_scanner.scan(Struct.l_u16)
				entry_points_count = IType.TYPE_TO_ENTRY_POINT_COUNT_MAP.get(script_type)
				if entry_points_count is None:
					raise PyMSError('Load', f'Script with id {id} has invalid type {script_type}, file could possibly be invalid or corrupt')
				header_scanner.skip(2)
				init_entry_point: CodeBlock
				entry_points: list[CodeBlock | None] = []
				for n in range(entry_points_count):
					if not header_scanner.can_scan(Struct.l_u16):
						raise PyMSError('Load', f'Script with id {id} has invalid header offset {header_offset} (insufficient space for entry points), file could possibly be invalid or corrupt')
					block_offset = header_scanner.scan(Struct.l_u16)
					if block_offset == 0:
						if n == 0:
							raise PyMSError('Load', f"Script with id {id} missing block for 'Init', file could possibly be invalid or corrupt")
						entry_points.append(None)
					else:
						entry_point = bytecode_handler.decompile_block(block_offset)
						if n == 0:
							init_entry_point = entry_point
						else:
							entry_points.append(entry_point)
				scripts[id] = IScript(id, script_type, init_entry_point, *entry_points)
			self._scripts = scripts
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', 'Unsupported iscript.bin, could possibly be invalid or corrupt', capture_exception=True)

	@staticmethod
	def _save(scripts: Iterable[IScript], output: IO.AnyOutputBytes) -> None:
		table = bytearray()
		builder = ByteCodeBuilder()
		builder.add_data(Struct.l_u32.pack(0)) # Pack 0 for offset to table, to be updated later
		for script in scripts:
			table += Struct.l_u16.pack(script.id)
			header_offset = builder.add_data(b'SCPE')
			table += Struct.l_u16.pack(header_offset)
			builder.add_data(Struct.l_u16.pack(script.type))
			builder.add_data(b'\x00\x00')
			header_updater = builder.get_updater()
			for _ in range(IType.TYPE_TO_ENTRY_POINT_COUNT_MAP[script.type]):
				builder.add_data(Struct.l_u16.pack(0))
			for entry_point in script.get_entry_points_for_type():
				if entry_point is not None:
					header_updater.update_data(Struct.l_u16.pack(builder.compile_block(entry_point)))
				else:
					header_updater.skip(Struct.l_u16.size)
		table_offset = builder.add_data(table)
		builder.set_data(0, Struct.l_u32.pack(table_offset)) # Update offset to table
		builder.add_data(b'\xFF\xFF\x00\x00')
		with IO.OutputBytes(output) as f:
			f.write(builder.data)

	def save(self, output: IO.AnyOutputBytes) -> None:
		IScriptBIN._save(self._scripts.values(), output)

	def list_scripts(self) -> list[IScript]:
		return list(self._scripts.values())

	def get_script(self, script_id: int) -> IScript | None:
		return self._scripts.get(script_id)

	def remove_script(self, script_id: int) -> None:
		script = self._scripts[script_id]
		for entry_point, _ in script.get_entry_points():
			entry_point.owners.remove(script)
		del self._scripts[script_id]
		self._cached_size = None

	def can_add_scripts(self, add_scripts: Iterable[IScript], allow_replace: bool = True) -> int | None:
		scripts = self._scripts.copy()
		for script in add_scripts:
			if not allow_replace and script.id in scripts:
				raise PyMSError('Internal', f"Script with ID '{script.id}' already exists")
			scripts[script.id] = script
		size = self._calculate_size(scripts.values())
		return (size if size > Struct.l_u16.max else None)

	def add_script(self, script: IScript, allow_replace: bool = True) -> None:
		self.add_scripts([script], allow_replace)

	def add_scripts(self, add_scripts: Iterable[IScript], allow_replace: bool = True) -> None:
		scripts = self._scripts.copy()
		for script in add_scripts:
			if not allow_replace and script.id in scripts:
				raise PyMSError('Internal', f"Script with ID '{script.id}' already exists")
			scripts[script.id] = script
		new_size = self._calculate_size(scripts.values())
		if new_size > Struct.l_u16.max:
			size = self.calculate_size()
			raise PyMSError('Internal', f"There is not enough room in your iscript.bin to compile these changes. The current file is {size}B out of the max 65535B, these changes would make the file {new_size}B.")
		self._scripts = scripts
		self._cached_size = new_size

	@staticmethod
	def _calculate_size(scripts: Iterable[IScript]) -> int:
		# TODO: Should this be calculated without saving?
		output = io.BytesIO()
		IScriptBIN._save(scripts, output)
		return len(output.getvalue())

	def calculate_size(self) -> int:
		if self._cached_size is None:
			self._cached_size = IScriptBIN._calculate_size(self._scripts.values())
		return self._cached_size

	def decompile(self, serialize_context: ICESerializeContext, script_ids: list[int] | None = None) -> None:
		if script_ids is None:
			script_ids = list(self._scripts.keys())
		strategy_builder = DecompileStrategyBuilder()
		for script_id in script_ids:
			script = self._scripts.get(script_id)
			if not script:
				raise PyMSError('Decompile', "There is no Script with ID '%s'" % script_id)
			strategy_builder.add_header(script)
		source_serializer = SourceCodeSerializer()
		source_serializer.decompile(serialize_context, strategy_builder.build())

	@staticmethod
	def compile(parse_context: ICEParseContext) -> list[IScript]:
		source_handler = ICESourceCodeHandler()
		source_handler.parse(parse_context)
		parse_context.finalize()
		return list(script for script,_ in parse_context.scripts.values())
