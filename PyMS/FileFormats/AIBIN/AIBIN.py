
from .AICodeHandlers import AIByteCodeHandler, AISerializeContext, AIParseContext, AILexer, AISourceCodeHandler
from .AICodeHandlers import HeaderNameString, HeaderBinFile, BroodwarOnly, StarEditHidden, RequiresLocation, EntryPoint

from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.BytesScanner import  BytesScanner
from ...Utilities.CodeHandlers.CodeType import CodeBlock, StrCodeType
from ...Utilities.CodeHandlers.Lexer import *
from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities import Struct
from ...Utilities import IO

from collections import OrderedDict

from typing import Type, TypeVar, Generic

class BaseScriptHeader(Struct.Struct):
	id: str
	address: int

class BWScriptHeader(BaseScriptHeader):
	_fields = (
		('id', Struct.t_str(4)),
		('address', Struct.t_u32)
	)

class AIScriptHeader(BaseScriptHeader):
	string_id: int
	flags: int 

	_fields = (
		('id', Struct.t_str(4)),
		('address', Struct.t_u32),
		('string_id', Struct.t_u32),
		('flags', Struct.t_u32),
	)

class AIFlag:
	broodwar_only = (1 << 2)
	staredit_hidden = (1 << 1)
	requires_location = (1 << 0)

H = TypeVar('H', bound=BaseScriptHeader)
class _AIBIN(Generic[H]):
	def __init__(self, header_type: Type[H], file_name: str) -> None:
		self.header_type = header_type
		self.file_name = file_name
		self.script_headers: OrderedDict[str, H] = OrderedDict()
		self.entry_points: dict[str, CodeBlock] = {}

	def load(self, input: IO.AnyInputBytes, addstrings: bool = False) -> None:
		with IO.InputBytes(input) as f:
			data = f.read()
		bytecode_handler = AIByteCodeHandler(data)
		scanner = BytesScanner(data)
		try:
			headers_offset = scanner.scan(Struct.l_u32)
			scanner.jump_to(headers_offset)
			script_headers: OrderedDict[str, H] = OrderedDict()
			while not scanner.at_end() and scanner.peek(Struct.l_u32):
				header: H = scanner.scan(self.header_type)
				if header.id in script_headers:
					raise PyMSError('Load',"Duplicate AI ID '%s'" % id)
				script_headers[header.id] = header
				# print(header.id)
				if header.address:
					self.entry_points[header.id] = bytecode_handler.decompile_block(header.address, owner=header)
			self.script_headers = script_headers
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',f"Unsupported {self.file_name}, could possibly be invalid or corrupt", capture_exception=True)

	def list_scripts(self) -> list[H]:
		return list(self.script_headers.values())

	def get_script_header(self, script_id: str) -> H | None:
		return self.script_headers.get(script_id)

	def get_entry_point(self, script_id: str) -> CodeBlock | None:
		return self.entry_points.get(script_id)

	def decompile_blocks(self, output: IO.AnyOutputText, script_id: str, serialize_context: AISerializeContext) -> None:
		if not script_id in self.script_headers:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		if not script_id in self.entry_points:
			raise PyMSError('Decompile', "The script with ID '%s' is not in %s" % self.file_name)
		block = self.entry_points[script_id]
		if serialize_context.is_block_serialized(block):
			return
		with IO.OutputText(output) as f:
			f.write(block.decompile(serialize_context))

class BWBIN(_AIBIN[BWScriptHeader]):
	def __init__(self) -> None:
		_AIBIN.__init__(self, BWScriptHeader, 'bwscript.bin')

class AIBIN(_AIBIN[AIScriptHeader]):
	def __init__(self, bw_bin: BWBIN | None = None) -> None:
		_AIBIN.__init__(self, AIScriptHeader, 'aiscript.bin')
		self.bw_bin = bw_bin

	def decompile_script_header(self, output: IO.AnyOutputText, script_id: str, serialize_context: AISerializeContext) -> None:
		if not script_id in self.script_headers:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		script_header = self.script_headers[script_id]
		serialize_context.set_label_prefix(script_id)
		string_info = str(script_header.string_id)
		if serialize_context.data_context:
			string = serialize_context.data_context.stattxt_string(script_header.string_id)
			if string:
				string_info = StrCodeType.serialize_string(string)
		if script_header.address:
			block = self.get_entry_point(script_id)
		else:
			if not self.bw_bin:
				raise PyMSError('Decompile', "Script with ID '%s' is in bwscript.bin but only aiscript.bin is loaded" % script_id)
			block = self.bw_bin.get_entry_point(script_id)
		if not block:
			raise PyMSError('Decompile', f"Script with ID '{script_id}' was not found")
		with IO.OutputText(output) as f:
			f.write(f"""script {script_header.id} {{
    {CodeCommand(HeaderNameString, [script_header.string_id]).serialize(serialize_context)}
    {CodeCommand(HeaderBinFile, [1 if script_header.address else 0]).serialize(serialize_context)}
    {CodeCommand(BroodwarOnly, [1 if script_header.flags & AIFlag.broodwar_only else 0]).serialize(serialize_context)}
    {CodeCommand(StarEditHidden, [1 if script_header.flags & AIFlag.staredit_hidden else 0]).serialize(serialize_context)}
    {CodeCommand(RequiresLocation, [1 if script_header.flags & AIFlag.requires_location else 0]).serialize(serialize_context)}
    {CodeCommand(EntryPoint, [block]).serialize(serialize_context)}
}}""")

	def decompile(self, output: IO.AnyOutputText, serialize_context: AISerializeContext, script_ids: list[str] | None = None) -> None:
		if script_ids is None:
			script_ids = list(script.id for script in self.list_scripts())
		with IO.OutputText(output) as f:
			add_newlines = False
			for script_id in script_ids:
				script_header = self.get_script_header(script_id)
				if not script_header:
					raise PyMSError('Decompile', "There is no AI Script with ID '%s'" % script_id)
				if add_newlines:
					f.write('\n\n')
				add_newlines = True
				self.decompile_script_header(f, script_id, serialize_context)
				f.write('\n')
				if script_header.address == 0:
					if self.bw_bin is None:
						raise PyMSError('Decompile', f"Script with ID '{script_id}' is in bwscript.bin but only aiscript.bin is loaded")
					self.bw_bin.decompile_blocks(f, script_id, serialize_context)
				else:
					self.decompile_blocks(f, script_id, serialize_context)

	def compile(self, input: IO.AnyInputText, parse_context: AIParseContext) -> list[PyMSWarning]:
		with IO.InputText(input) as f:
			code = f.read()
		lexer = AILexer(code)
		source_handler = AISourceCodeHandler(lexer)
		source_handler.parse(parse_context)
		# TODO: Complete
		return []
