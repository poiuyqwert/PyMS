
from .AIFlag import AIFlag

from .AICodeHandlers import AIByteCodeHandler, AISerializeContext, AIParseContext, AISourceCodeHandler, CodeCommands
# from .AICodeHandlers. import Stop, HeaderNameString, HeaderBinFile, BroodwarOnly, StarEditHidden, RequiresLocation, EntryPoint

from ...Utilities.PyMSError import PyMSError
# from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.BytesScanner import  BytesScanner
from ...Utilities.CodeHandlers.ByteCodeBuilder import ByteCodeBuilder
from ...Utilities.CodeHandlers.CodeType import CodeBlock
from ...Utilities.CodeHandlers.Lexer import *
from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities import Struct
from ...Utilities import IO

import io
from collections import OrderedDict
from dataclasses import dataclass

from typing import Type, TypeVar, Iterable

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

@dataclass
class AIScript:
	id: str
	flags: int
	string_id: int
	entry_point: CodeBlock
	in_bwscript: bool

	@staticmethod
	def blank_entry_point() -> CodeBlock:
		entry_point = CodeBlock()
		entry_point.commands = [
			CodeCommand(CodeCommands.Stop, [])
		]
		return entry_point

class AIBIN:
	def __init__(self) -> None:
		self._scripts: OrderedDict[str, AIScript] = OrderedDict()

	@staticmethod
	def _load(header_type: Type[H], file_name: str, input: IO.AnyInputBytes) -> OrderedDict[str, tuple[H, CodeBlock | None]]:
		try:
			with IO.InputBytes(input) as f:
				data = f.read()
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', f"Couldn't load {file_name} from disk", capture_exception=True)
		bytecode_handler = AIByteCodeHandler(data)
		scanner = BytesScanner(data)
		try:
			headers_offset = scanner.scan(Struct.l_u32)
			scanner.jump_to(headers_offset)
			scripts: OrderedDict[str, tuple[H, CodeBlock | None]] = OrderedDict()
			while not scanner.at_end() and scanner.peek(Struct.l_u32):
				header: H = scanner.scan(header_type)
				if header.id in scripts:
					raise PyMSError('Load', "Duplicate AI ID '%s'" % id)
				entry_point: CodeBlock | None = None
				if header.address:
					entry_point = bytecode_handler.decompile_block(header.address)
				scripts[header.id] = (header, entry_point)
			return scripts
		except PyMSError:
			raise
		except:
			raise PyMSError('Load', f"Unsupported {file_name}, could possibly be invalid or corrupt", capture_exception=True)

	def load(self, ai_input: IO.AnyInputBytes, bw_input: IO.AnyInputBytes | None) -> None:
		ai_headers = AIBIN._load(_AIScriptHeader, 'aiscript.bin', ai_input)
		bw_headers: OrderedDict[str, tuple[_BWScriptHeader, CodeBlock | None]] = OrderedDict()
		requires_bw = set(id for id,(header,_) in ai_headers.items() if header.is_in_bw) #any(header[0].address == 0 for header in ai_headers.values())
		if requires_bw:
			if not bw_input:
				raise PyMSError('Load', f'aiscript.bin has {len(requires_bw)} scripts stored in bwscript.bin but no bwscript.bin is loaded: {", ".join(requires_bw)}')
			bw_headers = AIBIN._load(_BWScriptHeader, 'bwscript.bin', bw_input)
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
			scripts[id] = AIScript(id, header.flags, header.string_id - 1, entry_point, header.is_in_bw)
		self._scripts = scripts

	@staticmethod
	def _save(header_type: Type[H], scripts: Iterable[AIScript], output: IO.AnyOutputBytes) -> None:
		headers = bytearray()
		builder = ByteCodeBuilder()
		builder.add_data(Struct.l_u32.pack(0)) # Pack 0 for offset to headers array, to be updated later
		for script in scripts:
			header = header_type()
			header.id = script.id
			header.address = builder.compile_block(script.entry_point)
			if isinstance(header, _AIScriptHeader):
				header.flags = script.flags
				header.string_id = script.string_id + 1 # WARNING: string id's are 1 indexed in the file
			headers += header.pack()
		builder.data[:Struct.l_u32.size] = Struct.l_u32.pack(builder.current_offset) # Update offset to headers array
		headers += b'\x00\x00\x00\x00' # Terminator for headers array
		with IO.OutputBytes(output) as f:
			f.write(builder.data)
			f.write(headers)

	@staticmethod
	def _save_scripts(scripts: Iterable[AIScript], ai_output: IO.AnyOutputBytes, bw_output: IO.AnyOutputBytes | None) -> None:
		ai_scripts: list[AIScript] = []
		bw_scripts: list[AIScript] = []
		for script in scripts:
			if script.in_bwscript:
				bw_scripts.append(script)
			else:
				ai_scripts.append(script)
		if bw_scripts:
			if not bw_output:
				raise PyMSError('Save', f'{len(bw_scripts)} scripts require to be saved inot bwscript.bin but no bwscript.bin is being saved')
			AIBIN._save(_BWScriptHeader, bw_scripts, bw_output)
		AIBIN._save(_AIScriptHeader, ai_scripts, ai_output)

	def save(self, ai_output: IO.AnyOutputBytes, bw_output: IO.AnyOutputBytes | None) -> None:
		AIBIN._save_scripts(self._scripts.values(), ai_output, bw_output)

	def list_scripts(self) -> list[AIScript]:
		return list(self._scripts.values())

	def get_script(self, script_id: str) -> AIScript | None:
		return self._scripts.get(script_id)

	def remove_script(self, script_id: str) -> None:
		del self._scripts[script_id]

	def add_script(self, script: AIScript, allow_replace: bool = True) -> None:
		if not allow_replace and script.id in self._scripts:
			raise PyMSError('Internal', f"Script with ID '{script.id}' already exists")
		# TODO: Check size
		# TODO: How does overwritten scripts affect size check?
		# TODO: Cleanup overwritten scripts
		self._scripts[script.id] = script

	def has_bwscripts(self) -> bool:
		for script in self._scripts.values():
			if script.in_bwscript:
				return True
		return False

	# 59,610 bytes
	# 26,458 bytes
	@staticmethod
	def _calculate_sizes(scripts: Iterable[AIScript]) -> tuple[int, int]:
		ai_output = io.BytesIO()
		bw_output = io.BytesIO()
		AIBIN._save_scripts(scripts, ai_output, bw_output)
		return (len(ai_output.getvalue()), len(bw_output.getvalue()))

	def calculate_sizes(self) -> tuple[int, int]:
		# TODO: Should this be calculated without saving?
		# TODO: Cache file size?
		return AIBIN._calculate_sizes(self._scripts.values())

	def count_scripts(self) -> tuple[int, int]:
		ai_scripts = 0
		bw_scripts = 0
		for script in self._scripts.values():
			if script.in_bwscript:
				bw_scripts += 1
			else:
				ai_scripts += 1
		return (ai_scripts, bw_scripts)

	def _decompile_blocks(self, output: IO.AnyOutputText, script_id: str, serialize_context: AISerializeContext) -> None:
		script = self._scripts.get(script_id)
		if not script:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		if serialize_context.is_block_serialized(script.entry_point):
			return
		with IO.OutputText(output) as f:
			f.write(script.entry_point.decompile(serialize_context))

	def _decompile_script_header(self, output: IO.AnyOutputText, script_id: str, serialize_context: AISerializeContext) -> None:
		script = self._scripts.get(script_id)
		if not script:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		serialize_context.set_label_prefix(script_id)
		with IO.OutputText(output) as f:
			f.write(f"""script {script.id} {{
    {CodeCommand(CodeCommands.HeaderNameString, [script.string_id]).serialize(serialize_context)}
    {CodeCommand(CodeCommands.HeaderBinFile, [script.in_bwscript]).serialize(serialize_context)}
    {CodeCommand(CodeCommands.BroodwarOnly, [1 if script.flags & AIFlag.broodwar_only else 0]).serialize(serialize_context)}
    {CodeCommand(CodeCommands.StarEditHidden, [1 if script.flags & AIFlag.staredit_hidden else 0]).serialize(serialize_context)}
    {CodeCommand(CodeCommands.RequiresLocation, [1 if script.flags & AIFlag.requires_location else 0]).serialize(serialize_context)}
    {CodeCommand(CodeCommands.EntryPoint, [script.entry_point]).serialize(serialize_context)}
}}""")

	def decompile(self, output: IO.AnyOutputText, serialize_context: AISerializeContext, script_ids: list[str] | None = None) -> None:
		if script_ids is None:
			script_ids = list(self._scripts.keys())
		with IO.OutputText(output) as f:
			add_newlines = False
			for script_id in script_ids:
				script = self._scripts.get(script_id)
				if not script:
					raise PyMSError('Decompile', "There is no AI Script with ID '%s'" % script_id)
				if add_newlines:
					f.write('\n\n')
				add_newlines = True
				self._decompile_script_header(f, script_id, serialize_context)
				f.write('\n')
				self._decompile_blocks(f, script_id, serialize_context)

	def compile(self, parse_context: AIParseContext) -> None:
		source_handler = AISourceCodeHandler()
		source_handler.parse(parse_context)
		parse_context.finalize()
		# TODO: Complete
		for id,(parse_header, _) in parse_context.script_headers.items():
			assert parse_header.entry_point is not None
			script = AIScript(id, parse_header.flags, parse_header.string_id, parse_header.entry_point, parse_header.bwscript)
			self.add_script(script)
