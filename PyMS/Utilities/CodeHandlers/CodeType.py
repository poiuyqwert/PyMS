
from . import SerializeContext
from .Scanner import Scanner
from . import Lexer as _Lexer
from .ParseContext import ParseContext
from .CodeBlock import CodeBlock

from .. import Struct
from ..PyMSError import PyMSError

class CodeType(object):
	def __init__(self, name, bytecode_type, block_reference): # type: (str, str, bool) -> CodeType
		self._name = name
		self._bytecode_type = bytecode_type
		self._block_reference = block_reference

	def decompile(self, scanner): # type: (Scanner) -> Any
		return scanner.scan(self._bytecode_type)

	def compile(self, value): # type: (Any) -> bytes
		return Struct.Value.pack(value, self._bytecode_type)

	def serialize(self, value, context): # type: (Any, SerializeContext.SerializeContext) -> str
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		return str(value)

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def parse(self, token, parse_context): # type: (str, ParseContext) -> Any
		raise NotImplementedError(self.__class__.__name__ + '.parse()')

class IntCodeType(CodeType):
	def __init__(self, name, bytecode_type, limits=None): # type: (str, str, tuple[int, int] | None) -> IntCodeType
		CodeType.__init__(self, name, bytecode_type, False)
		if limits == None:
			limits = Struct.Type.numeric_limits(self._bytecode_type)
		self._limits = limits

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IntegerToken):
			raise PyMSError('Parse', "Expected integer value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> Any
		try:
			num = int(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self._name))
		min,max = self._limits
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%d', minimum is '%d')" % (self._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%d', maximum is '%d')" % (self._name, num, max))
		return num

class FloatCodeType(CodeType):
	def __init__(self, name, bytecode_type, limits=None): # type: (str, str, tuple[float, float] | None) -> FloatCodeType
		CodeType.__init__(self, name, bytecode_type, False)
		if limits == None:
			limits = Struct.Type.numeric_limits(self._bytecode_type)
		self._limits = limits

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.FloatToken):
			raise PyMSError('Parse', "Expected float value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> Any
		try:
			num = float(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self._name))
		min,max = self._limits
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%f', minimum is '%f')" % (self._name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%f', maximum is '%f')" % (self._name, num, max))
		return num

class AddressCodeType(CodeType):
	def __init__(self, name, bytecode_type): # type: (str, str) -> AddressCodeType
		CodeType.__init__(self, name, bytecode_type, True)

	def serialize(self, block, context): # type: (CodeBlock, SerializeContext.SerializeContext) -> str
		return context.block_label(block)
	
	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IdentifierToken):
			raise PyMSError('Parse', "Expected block label identifier but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> str
		return token # TODO: Should this do logic of converting to CodeBlock if the block has already been parsed?

class StrCodeType(CodeType):
	def __init__(self, name): # type: (str, str) -> StrCodeType
		CodeType.__init__(self, name, None, False)

	def decompile(self, scanner): # type: (Scanner) -> Any
		return scanner.scan_str()

	def compile(self, value): # type: (str) -> bytes
		return value + '\x00'

	def serialize(self, value, context): # type: (str, SerializeContext.SerializeContext) -> str
		result = repr(value)
		while not result[0] in '"\'':
			result = result[1:]
		return result

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.StringToken):
			raise PyMSError('Parse', "Expected string value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> str
		import ast
		try:
			string = ast.literal_eval(token)
			if not isinstance(string, str):
				raise Exception()
		except:
			PyMSError('Parse', "Value '%s' is not a valid string" % token)
		return string

class EnumCodeType(CodeType):
	def __init__(self, name, bytecode_type, cases): # type: (str, str, dict[str, int]) -> EnumCodeType
		CodeType.__init__(self, name, bytecode_type, False)
		self._cases = cases

	def decompile(self, scanner): # type: (Scanner) -> Any
		value = scanner.scan(self._bytecode_type)
		# TODO: Check if value is valid
		return value

	def serialize(self, value, context): # type: (int, SerializeContext.SerializeContext) -> str
		for case_name,case_value in self._cases.items():
			if value == case_value:
				return case_name
		raise PyMSError('Serialize', "Value '%s' has no case for '%s'" % (value, self._name))

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.IdentifierToken):
			raise PyMSError('Parse', "Expected an enum identifier but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> int
		if not token in self._cases:
			raise PyMSError('Parse', "Value '%s' is not a valid case for '%s'" % (token, self._name))
		return self._cases[token]

class BooleanCodeType(IntCodeType):
	def __init__(self, name, bytecode_type): # type: (str, str) -> CodeType
		IntCodeType.__init__(self, name, bytecode_type, limits=(0, 1))

	def lex(self, lexer, parse_context): # type: (_Lexer.Lexer, ParseContext) -> Any
		token = lexer.next_token()
		if not isinstance(token, _Lexer.BooleanToken) and not isinstance(token, _Lexer.IntegerToken):
			raise PyMSError('Parse', "Expected a boolean but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token, parse_context): # type: (str, ParseContext) -> int
		if token == 'true' or token == '1':
			return True
		elif token == 'false' or token == '0':
			return False
		raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self._name))
