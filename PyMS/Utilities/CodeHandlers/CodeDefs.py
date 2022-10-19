
from . import SerializeContext
from .Scanner import Scanner
from . import Lexer as _Lexer
from .ParseContext import ParseContext, CommandParamBlockReferenceResolver

from .. import Struct
from ..PyMSError import PyMSError

class CodeBlock(object):
	def __init__(self):
		self.commands = [] # type: list[CodeCommand]
		self.prev_block = None # type: CodeBlock
		self.next_block = None # type: CodeBlock
		self.owners = set()

	def serialize(self, context, add_label=True): # type: (SerializeContext.SerializeContext, bool) -> str
		result = ''
		if add_label:
			result = ':' + context.block_label(self)
		next_blocks = [] # type: list[CodeBlock]
		if self.next_block:
			next_blocks.append(self.next_block)
		for cmd in self.commands:
			if len(result):
				result += '\n'
			result += cmd.serialize(context)
			if cmd._separate or cmd._ends_flow:
				result += '\n'
			for param in cmd.params:
				if isinstance(param, CodeBlock) and not context.is_block_serialized(param):
					next_blocks.append(param)
					# context.mark_block_serialized(param)
					# result = param.serialize(context) + '\n\n' + result
		for next_block in next_blocks:
			if context.is_block_serialized(next_block):
				continue
			context.mark_block_serialized(next_block)
			if not result.endswith('\n'):
				result += '\n'
			result += '\n' + next_block.serialize(context)
		return result


class CodeCommand(object):
	_id = None # type: int
	_name = None # type: str
	_param_types = [] # type: list[Type[CodeType]]
	_ends_flow = False
	_separate = False
	_ephemeral = False # Command is ephemeral, so will not take part in things like block reference resolving

	def __init__(self, params): # type: (list[CodeType], int | None) -> None
		self.params = params
		self.original_address = None

	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Self
		params = []
		for param_type in list(cls._param_types): # TODO: Why do we need to wrap in `list(...)`?
			params.append(param_type.decompile(scanner))
		return cls(params)

	def compile(self): # type: () -> bytes
		data = Struct.Value.pack(self._id, Struct.Type.u8())
		for param,param_type in zip(self.params, self._param_types):
			data += param_type.compile(param)
		return data

	def serialize(self, context): # type: (SerializeContext.SerializeContext) -> str
		result = self._name
		for param,param_type in zip(self.params, self._param_types):
			result += ' '
			result += param_type.serialize(param, context)
		return result

	@classmethod
	def parse(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Self
		# TODO: Support braces?
		params = []
		missing_blocks = [] # type: tuple[str, int, int | None]
		for param_index,param_type in enumerate(cls._param_types):
			value = param_type.lex(lexer, parse_context)
			if issubclass(param_type, AddressCodeType):
				block = parse_context.lookup_block(value)
				if not block:
					missing_blocks.append((value, param_index, lexer.line))
				else:
					value = block
			params.append(value)
		token = lexer.next_token()
		if not isinstance(token, (_Lexer.NewlineToken, _Lexer.EOFToken)):
			raise PyMSError('Parse', "Unexpected token '%s' (expected end of line or file)" % token.raw_value, line=lexer.line)
		cmd = cls(params)
		if not cls._ephemeral:
			for block_name,param_index,source_line in missing_blocks:
				parse_context.missing_block(block_name, CommandParamBlockReferenceResolver(cmd, param_index, source_line))
		return cmd


class CodeType(object):
	_name = None # type: str
	_bytecode_type = None # type: str
	_block_reference = False

	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Any
		return scanner.scan(cls._bytecode_type)

	@classmethod
	def compile(cls, value): # type: (Any) -> bytes
		return Struct.Value.pack(value, cls._bytecode_type)

	@classmethod
	def serialize(cls, value, context): # type: (Any, SerializeContext.SerializeContext) -> str
		if context.definitions:
			variable = context.definitions.lookup_variable(value, cls)
			if variable:
				return variable.name
		return str(value)

	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		raise NotImplementedError(cls.__name__ + '.lex()')

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> Any
		raise NotImplementedError(cls.__name__ + '.parse()')

class IntCodeType(CodeType):
	_limits = None # type: tuple[int, int]

	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IntegerToken):
			raise PyMSError('Parse', "Expected integer value but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> Any
		try:
			num = int(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, cls._name))
		if cls._limits:
			min,max = cls._limits
		else:
			min,max = Struct.Type.numeric_limits(cls._bytecode_type)
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%d', minimum is '%d')" % (cls._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%d', maximum is '%d')" % (cls._name, num, max))
		return num

class FloatCodeType(CodeType):
	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.FloatToken):
			raise PyMSError('Parse', "Expected float value but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> Any
		try:
			num = float(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, cls._name))
		min,max = Struct.Type.numeric_limits(cls._bytecode_type)
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%f', minimum is '%f')" % (cls._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%f', maximum is '%f')" % (cls._name, num, max))
		return num

class AddressCodeType(CodeType):
	_block_reference = True

	@classmethod
	def serialize(cls, block, context): # type: (CodeBlock, SerializeContext.SerializeContext) -> str
		return context.block_label(block)
	
	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IdentifierToken):
			raise PyMSError('Parse', "Expected block label identifier but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> str
		return token # TODO: Should this do logic of converting to CodeBlock if the block has already been parsed?

class StrCodeType(CodeType):
	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Any
		return scanner.scan_str()

	@classmethod
	def compile(cls, value): # type: (str) -> bytes
		return value + '\x00'

	@classmethod
	def serialize(cls, value, context): # type: (str, SerializeContext.SerializeContext) -> str
		result = repr(value)
		while not result[0] in '"\'':
			result = result[1:]
		return result

	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.StringToken):
			raise PyMSError('Parse', "Expected string value but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> str
		import ast
		try:
			string = ast.literal_eval(token)
			if not isinstance(string, str):
				raise Exception()
		except:
			PyMSError('Parse', "Value '%s' is not a valid string" % token)
		return string

class EnumCodeType(IntCodeType):
	_cases = {} # type: dict[str, int]

	@classmethod
	def decompile(cls, scanner): # type: (Scanner) -> Any
		value = scanner.scan(cls._bytecode_type)
		# TODO: Check if value is valid
		return value

	@classmethod
	def serialize(cls, value, context): # type: (int, SerializeContext.SerializeContext) -> str
		for case_name,case_value in cls._cases.items():
			if value == case_value:
				return case_name
		raise PyMSError('Serialize', "Value '%s' has no case for '%s'" % (value, cls._name))

	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IdentifierToken):
			raise PyMSError('Parse', "Expected an enum identifier but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> int
		if not token in cls._cases:
			raise PyMSError('Parse', "Value '%s' is not a valid case for '%s'" % (token, cls._name))
		return cls._cases[token]

class BooleanCodeType(IntCodeType):
	_limits = (0, 1)

	@classmethod
	def lex(cls, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.BooleanToken) and not isinstance(token, _Lexer.IntegerToken):
			raise PyMSError('Parse', "Expected a boolean but got '%s'" % token.raw_value, line=lexer.line)
		return cls.parse(token.raw_value, parse_context)

	@classmethod
	def parse(cls, token, parse_context): # type: (str, ParseContext) -> int
		return token == 'true' or token == '1'
