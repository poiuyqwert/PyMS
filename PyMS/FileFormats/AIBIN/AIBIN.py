
from .AIScript import AIScript
from .CodeHandlers import AISE

from .CodeHandlers import AIDecompileContext, AISerializeContext, AIParseContext, AISourceCodeHandler, AILanguage, AIByteCodeCompiler

from ...Utilities.PyMSError import PyMSError
from ...Utilities.BytesScanner import  BytesScanner
from ...Utilities.CodeHandlers.ByteCodeDecompiler import ByteCodeDecompiler
from ...Utilities.CodeHandlers.CodeType import CodeBlock
from ...Utilities.CodeHandlers.Lexer import *
from ...Utilities.CodeHandlers.DecompileStrategy import DecompileStrategyBuilder
from ...Utilities.CodeHandlers.SourceCodeSerializer import SourceCodeSerializer
from ...Utilities import Struct
from ...Utilities import IO

import io
from collections import OrderedDict

from typing import Type, TypeVar, Iterable, Mapping

class _BaseScriptHeader(Struct.Struct):
	def __init__(self, id: str = '', address: int = 0) -> None:
		super().__init__()
		self.id = id
		self.address = address

class _BWScriptHeader(_BaseScriptHeader):
	_fields = (
		('id', Struct.t_str(4)),
		('address', Struct.t_u32)
	)

class _AIScriptHeader(_BaseScriptHeader):
	_fields = (
		('id', Struct.t_str(4)),
		('address', Struct.t_u32),
		('string_id', Struct.t_u32),
		('flags', Struct.t_u32),
	)

	@property
	def is_in_bw(self) -> bool:
		return (self.address == 0)

	def __init__(self, id: str = '', address: int = 0, string_id: int = 0, flags: int = 0) -> None:
		super().__init__(id, address)
		self.string_id = string_id
		self.flags = flags

H = TypeVar('H', bound=_BaseScriptHeader)

class AIBIN:
	def __init__(self) -> None:
		self._scripts: OrderedDict[str, AIScript] = OrderedDict()
		self._cached_sizes: tuple[int, int] | None = None
		# Plugin data
		self.expanded = False
		self.active_plugins: set[str] = set()

	@staticmethod
	def _load(header_type: Type[H], file_name: str, input: IO.AnyInputBytes) -> tuple[OrderedDict[str, tuple[H, CodeBlock | None]], AIDecompileContext]:
		try:
			with IO.InputBytes(input) as f:
				data = f.read()
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', f"Couldn't load {file_name} from disk", capture_exception=True)
		bytecode_context = AIDecompileContext(data)
		bytecode_handler = ByteCodeDecompiler()
		scanner = BytesScanner(data)
		try:
			headers_offset = scanner.scan(Struct.l_u32)
			if headers_offset >= AISE.expanded_headers_offset:
				bytecode_context.aise_context.expand(bytecode_context.language_context)
				bytecode_context.aise_context.load_long_jumps(scanner, bytecode_context)
			scanner.jump_to(headers_offset)
			scripts: OrderedDict[str, tuple[H, CodeBlock | None]] = OrderedDict()
			while not scanner.at_end() and scanner.peek(Struct.l_u32):
				header: H = scanner.scan(header_type)
				if header.id in scripts:
					raise PyMSError('Load', "Duplicate AI ID '%s'" % id)
				entry_point: CodeBlock | None = None
				if header.address:
					entry_point = bytecode_handler.decompile_block(header.address, bytecode_context)
				scripts[header.id] = (header, entry_point)
			return (scripts, bytecode_context)
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', f"Unsupported {file_name}, could possibly be invalid or corrupt", capture_exception=True)

	def load(self, ai_input: IO.AnyInputBytes, bw_input: IO.AnyInputBytes | None) -> None:
		ai_headers, ai_context = AIBIN._load(_AIScriptHeader, 'aiscript.bin', ai_input)
		bw_headers: OrderedDict[str, tuple[_BWScriptHeader, CodeBlock | None]] = OrderedDict()
		bw_context: AIDecompileContext | None = None
		requires_bw = set(id for id,(header,_) in ai_headers.items() if header.is_in_bw) #any(header[0].address == 0 for header in ai_headers.values())
		if requires_bw:
			if not bw_input:
				raise PyMSError('Load', f'aiscript.bin has {len(requires_bw)} scripts stored in bwscript.bin but no bwscript.bin is loaded: {", ".join(requires_bw)}')
			bw_headers, bw_context = AIBIN._load(_BWScriptHeader, 'bwscript.bin', bw_input)
		# extra_bw: set[str] = set()
		# not_bw: str[str] = set()
		for id in bw_headers.keys():
			requires_bw.remove(id)
		# 	if not id in ai_headers:
		# 		extra_bw.add(id)
		# 	if not ai_headers[id][0].is_in_bw:
		# 		not_bw.add(id)
		if requires_bw:
			raise PyMSError('Load', f'aiscript.bin has {len(requires_bw)} scripts stored in bwscript.bin that are not found in the loaded bwscript.bin: {", ".join(requires_bw)}')
		scripts: OrderedDict[str, AIScript] = OrderedDict()
		for id,(header,entry_point) in ai_headers.items():
			if header.is_in_bw:
				entry_point = bw_headers[id][1]
			if not entry_point:
				raise PyMSError('Internal', f'Entry point for script {id} missing')
			# WARNING: string id's are 1 indexed in the file
			script = AIScript(id, header.flags, header.string_id - 1, entry_point, header.is_in_bw)
			entry_point.owners.append(script)
			scripts[id] = script
		self._scripts = scripts
		self._cached_sizes = None

		self.expanded = ai_context.aise_context.expanded
		self.active_plugins = ai_context.language_context.active_plugins()
		if bw_context is not None:
			self.expanded |= bw_context.aise_context.expanded
			self.active_plugins.update(bw_context.language_context.active_plugins())

	@staticmethod
	def _save(header_type: Type[H], scripts: Iterable[AIScript], output: IO.AnyOutputBytes, expanded: bool) -> None:
		headers = bytearray()
		builder = AIByteCodeCompiler()
		builder.add_data(Struct.l_u32.pack(0)) # Pack 0 for offset to headers array, to be updated later
		if expanded:
			builder.aise_context.determine_long_jumps(scripts, builder)
		for script in scripts:
			header = header_type()
			header.id = script.id
			header.address = builder.compile_block(script.entry_point)
			if isinstance(header, _AIScriptHeader):
				header.flags = script.flags
				header.string_id = script.string_id + 1 # WARNING: string id's are 1 indexed in the file
			headers += header.pack()
		builder.set_data(0, Struct.l_u32.pack(builder.current_offset)) # Update offset to headers array
		headers += b'\x00\x00\x00\x00' # Terminator for headers array
		with IO.OutputBytes(output) as f:
			f.write(builder.data)
			f.write(headers)

	@staticmethod
	def _save_scripts(scripts: Mapping[str, AIScript], ai_output: IO.AnyOutputBytes, bw_output: IO.AnyOutputBytes | None, expanded: bool) -> None:
		ai_scripts: list[AIScript] = []
		bw_scripts: list[AIScript] = []
		for script in scripts.values():
			if script.in_bwscript:
				bw_scripts.append(script)
			else:
				ai_scripts.append(script)
		if bw_scripts:
			if not bw_output:
				raise PyMSError('Save', f'{len(bw_scripts)} scripts require to be saved inot bwscript.bin but no bwscript.bin is being saved')
			AIBIN._save(_BWScriptHeader, bw_scripts, bw_output, expanded)
		AIBIN._save(_AIScriptHeader, ai_scripts, ai_output, expanded)

	def save(self, ai_output: IO.AnyOutputBytes, bw_output: IO.AnyOutputBytes | None) -> None:
		AIBIN._save_scripts(self._scripts, ai_output, bw_output, self.expanded)

	def list_scripts(self) -> list[AIScript]:
		return list(self._scripts.values())

	def get_script(self, script_id: str) -> AIScript | None:
		return self._scripts.get(script_id)

	def remove_script(self, script_id: str) -> None:
		script = self._scripts[script_id]
		script.entry_point.owners.remove(script)
		del self._scripts[script_id]
		self._cached_sizes = None

	def max_size(self) -> int:
		max_size = Struct.l_u16.max
		if self.expanded:
			max_size = Struct.l_u32.max
		return max_size

	def expand(self) -> None:
		self.expanded = True
		self.active_plugins.add(AILanguage.AISEPlugin.ID)

	def can_add_scripts(self, add_scripts: Iterable[AIScript], allow_replace: bool = True) -> tuple[int | None, int | None]:
		scripts = self._scripts.copy()
		for script in add_scripts:
			if not allow_replace and script.id in scripts:
				raise PyMSError('Internal', f"Script with ID '{script.id}' already exists")
			scripts[script.id] = script
		ai_size, bw_size = self._calculate_sizes(scripts, self.expanded)
		max_size = self.max_size()
		return (ai_size if ai_size > max_size else None, bw_size if bw_size > max_size else None)

	def add_script(self, script: AIScript, allow_replace: bool = True) -> None:
		self.add_scripts([script], allow_replace)

	def add_scripts(self, add_scripts: Iterable[AIScript], allow_replace: bool = True) -> None:
		scripts = self._scripts.copy()
		for script in add_scripts:
			if not allow_replace and script.id in scripts:
				raise PyMSError('Internal', f"Script with ID '{script.id}' already exists")
			scripts[script.id] = script
		new_ai_size, new_bw_size = self._calculate_sizes(scripts, self.expanded)
		# TODO: Should this have logic/messaging around expanded file sizes, or leave that to external handling?
		max_size = self.max_size()
		if new_ai_size > max_size:
			ai_size, _ = self.calculate_sizes()
			raise PyMSError('Internal', f"There is not enough room in your aiscript.bin to compile these changes. The current file is {ai_size}B out of the max {max_size}B, these changes would make the file {new_ai_size}B.")
		if new_bw_size > max_size:
			_, bw_size = self.calculate_sizes()
			raise PyMSError('Internal', f"There is not enough room in your bwscript.bin to compile these changes. The current file is {bw_size}B out of the max {max_size}B, these changes would make the file {new_bw_size}B.")
		self._scripts = scripts
		self._cached_sizes = (new_ai_size, new_bw_size)

	def has_bwscripts(self) -> bool:
		for script in self._scripts.values():
			if script.in_bwscript:
				return True
		return False

	@staticmethod
	def _calculate_sizes(scripts: Mapping[str, AIScript], expanded: bool) -> tuple[int, int]:
		# TODO: Should this be calculated without saving?
		ai_output = io.BytesIO()
		bw_output = io.BytesIO()
		AIBIN._save_scripts(scripts, ai_output, bw_output, expanded)
		return (len(ai_output.getvalue()), len(bw_output.getvalue()))

	def calculate_sizes(self) -> tuple[int, int]:
		if self._cached_sizes is None:
			self._cached_sizes = AIBIN._calculate_sizes(self._scripts, self.expanded)
		return self._cached_sizes

	def count_scripts(self) -> tuple[int, int]:
		ai_scripts = 0
		bw_scripts = 0
		for script in self._scripts.values():
			if script.in_bwscript:
				bw_scripts += 1
			else:
				ai_scripts += 1
		return (ai_scripts, bw_scripts)

	def decompile(self, serialize_context: AISerializeContext, script_ids: list[str] | None = None) -> None:
		if script_ids is None:
			script_ids = list(self._scripts.keys())
		strategy_builder = DecompileStrategyBuilder()
		for script_id in script_ids:
			script = self._scripts.get(script_id)
			if not script:
				raise PyMSError('Decompile', "There is no AI Script with ID '%s'" % script_id)
			strategy_builder.add_header(script)
		source_serializer = SourceCodeSerializer()
		source_serializer.decompile(serialize_context, strategy_builder.build())

	@staticmethod
	def compile(parse_context: AIParseContext) -> list[AIScript]:
		source_handler = AISourceCodeHandler()
		source_handler.parse(parse_context)
		parse_context.finalize()
		return list(script for script,_ in parse_context.scripts.values())
