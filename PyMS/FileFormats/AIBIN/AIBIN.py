
from AICodeHandlers import AIByteCodeHandler, AISerializeContext, AIParseContext, AILexer, AISourceCodeHandler

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.CodeHandlers.Scanner import Scanner
from ...Utilities.CodeHandlers.CodeType import CodeBlock, StrCodeType
from ...Utilities.CodeHandlers.Lexer import *
from ...Utilities import Struct

from collections import OrderedDict

class BWScriptHeader(Struct.Struct):
	_fields = (
		('id', Struct.Type.str(4)),
		('address', Struct.Type.u32())
	)

	def __init__(self):
		self.id = None # type: str
		self.address = None # type: int

class AIScriptHeader(Struct.Struct):
	_fields = (
		('id', Struct.Type.str(4)),
		('address', Struct.Type.u32()),
		('string_id', Struct.Type.u32()),
		('flags', Struct.Type.u32()),
	)

	def __init__(self):
		self.id = None # type: str
		self.address = None # type: int
		self.string_id = None # type: int
		self.flags = None # type: int

class AIFlag:
	broodwar_only = (1 << 2)
	staredit_hidden = (1 << 1)
	requires_location = (1 << 0)

class _AIBIN(object):
	ScriptHeader = None
	FILE_NAME = None

	def __init__(self):
		self.script_headers = OrderedDict() # type: OrderedDict[int, _AIBIN.ScriptHeader]
		self.entry_points = {} # type: dict[str, CodeBlock]

	def load_file(self, file, addstrings=False):
		data = load_file(file, 'aiscript.bin')
		return self.load_data(data, addstrings)

	def load_data(self, data, addstrings=False):
		bytecode_handler = AIByteCodeHandler(data)
		scanner = Scanner(data)
		try:
			headers_offset = scanner.scan(Struct.Type.u32())
			scanner.jump_to(headers_offset)
			script_headers = OrderedDict() # type: OrderedDict[int, _AIBIN.ScriptHeader]
			while scanner.peek(Struct.Type.u32()):
				header = scanner.scan(self.ScriptHeader) # type: _AIBIN.ScriptHeader
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
			raise PyMSError('Load',"Unsupported aiscript.bin, could possibly be invalid or corrupt", capture_exception=True)

	def list_scripts(self): # type: () -> list[_AIBIN.ScriptHeader]
		return list(self.script_headers.values())

	def get_script_header(self, script_id): # type: (str) -> (_AIBIN.ScriptHeader | None)
		return self.script_headers.get(script_id)

	def get_entry_point(self, script_id): # type: (str) -> (CodeBlock | None)
		return self.entry_points.get(script_id)

	def decompile_blocks(self, script_id, serialize_context): # type: (str, AISerializeContext) -> str
		if not script_id in self.script_headers:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		if not script_id in self.entry_points:
			raise PyMSError('Decompile', "The script with ID '%s' is not in %s" % self.FILE_NAME)
		return self.entry_points[script_id].serialize(serialize_context)

class BWBIN(_AIBIN):
	ScriptHeader = BWScriptHeader
	FILE_NAME = 'bwscript.bin'

class AIBIN(_AIBIN):
	ScriptHeader = AIScriptHeader
	FILE_NAME = 'aiscript.bin'

	def __init__(self, bw_bin=None): # type: (BWBIN) -> AIBIN
		_AIBIN.__init__(self)
		self.bw_bin = bw_bin

	def decompile_script_header(self, script_id, serialize_context): # type: (str, AISerializeContext) -> str
		if not script_id in self.script_headers:
			raise PyMSError('Decompile',"There is no AI Script with ID '%s'" % script_id)
		script_header = self.script_headers[script_id] # type: AIScriptHeader
		serialize_context.set_label_prefix(script_id)
		string_info = script_header.string_id
		if serialize_context.data_context:
			string = serialize_context.data_context.stattxt_string(script_header.string_id)
			if string:
				string_info = StrCodeType.serialize(string, serialize_context)
		if script_header.address:
			block = self.get_entry_point(script_id)
		else:
			if not self.bw_bin:
				raise PyMSError('Decompile', "Script with ID '%s' is in bwscript.bin but only aiscript.bin is loaded" % script_id)
			block = self.bw_bin.get_entry_point(script_id)
		return """script %s {
    name_string %s
    bin_file %s
    broodwar_only %d
    staredit_hidden %d
    requires_location %d
    entry_point %s
}""" % (
			script_header.id,
			string_info,
			'aiscript' if script_header.address else 'bwscript',
			not not script_header.flags & AIFlag.broodwar_only,
			not not script_header.flags & AIFlag.staredit_hidden,
			not not script_header.flags & AIFlag.requires_location,
			serialize_context.block_label(block)
		)

	def decompile(self, serialize_context, script_ids=None): # type: (AISerializeContext, list[str] | None) -> str
		if script_ids == None:
			script_ids = list(script.id for script in self.list_scripts())
		result = ''
		for script_id in script_ids:
			script_header = self.get_script_header(script_id)
			if not script_header:
				raise PyMSError('Decompile', "There is no AI Script with ID '%s'" % script_id)
			if len(result):
				result += '\n\n'
			result += self.decompile_script_header(script_id, serialize_context)
			result += '\n'
			if script_header.address == 0:
				result += self.bw_bin.decompile_blocks(script_id, serialize_context)
			else:
				result += self.decompile_blocks(script_id, serialize_context)
		return result

	def compile(self, code, parse_context): # type: (str, AIParseContext) -> list[PyMSWarning]
		lexer = AILexer(code)
		source_handler = AISourceCodeHandler(lexer)
		source_handler.parse(parse_context)
