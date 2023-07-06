
from __future__ import annotations

from . import Tokens
from .CodeBlock import CodeBlock

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

from typing import TYPE_CHECKING, Generic, TypeVar, cast
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .Lexer import Lexer
	from .ParseContext import ParseContext

I = TypeVar('I')
O = TypeVar('O')
class CodeType(Generic[I, O]):
	def __init__(self, name: str, bytecode_type: str, block_reference: bool) -> None:
		self._name = name
		self._bytecode_type = bytecode_type
		self._block_reference = block_reference

	def decompile(self, scanner: BytesScanner) -> I:
		return scanner.scan(self._bytecode_type)[0]

	def compile(self, value: I) -> bytes:
		return Struct.Value.pack(value, self._bytecode_type)

	def serialize(self, value: I, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		return str(value)

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def parse(self, token: str, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.parse()')

class IntCodeType(CodeType[int, int]):
	def __init__(self, name: str, bytecode_type: str, limits: tuple[int, int ] | None = None) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		if limits is None:
			limits = cast(tuple[int,int], Struct.FieldType.numeric_limits(self._bytecode_type))
		self._limits = limits

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> int:
		token = lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise PyMSError('Parse', "Expected integer value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> int:
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

class FloatCodeType(CodeType[float, float]):
	def __init__(self, name: str, bytecode_type: str, limits: tuple[float, float] | None = None) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		if limits is None:
			limits = cast(tuple[float, float], Struct.FieldType.numeric_limits(self._bytecode_type))
		self._limits = limits

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> float:
		token = lexer.next_token()
		if not isinstance(token, Tokens.FloatToken):
			raise PyMSError('Parse', "Expected float value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> float:
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

class AddressCodeType(CodeType[CodeBlock, str]):
	def __init__(self, name: str, bytecode_type: str) -> None:
		CodeType.__init__(self, name, bytecode_type, True)

	def serialize(self, block: CodeBlock, context: SerializeContext) -> str:
		return context.block_label(block)
	
	def lex(self, lexer: Lexer, parse_context: ParseContext) -> str:
		token = lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise PyMSError('Parse', "Expected block label identifier but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> str:
		return token # TODO: Should this do logic of converting to CodeBlock if the block has already been parsed?

class StrCodeType(CodeType[str, str]):
	def __init__(self, name: str) -> None:
		CodeType.__init__(self, name, 's', False)

	@staticmethod
	def serialize_string(string: str) -> str:
		# TODO: Better serialize?
		result = repr(string)
		while not result[0] in '"\'':
			result = result[1:]
		return result

	@staticmethod
	def parse_string(string: str) -> str:
		import ast
		try:
			result = ast.literal_eval(string)
			if not isinstance(string, str):
				raise Exception()
		except:
			PyMSError('Parse', "Value '%s' is not a valid string" % string)
		return result

	def decompile(self, scanner: BytesScanner) -> str:
		return scanner.scan_cstr()

	def compile(self, value: str) -> bytes:
		return value.encode('utf-8') + b'\x00'

	def serialize(self, value: str, context: SerializeContext) -> str:
		return StrCodeType.serialize_string(value)

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> str:
		token = lexer.next_token()
		if not isinstance(token, Tokens.StringToken):
			raise PyMSError('Parse', "Expected string value but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> str:
		return StrCodeType.parse_string(token)

class EnumCodeType(CodeType[int, int]):
	def __init__(self, name: str, bytecode_type: str, cases: dict[str, int]) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		self._cases = cases

	def decompile(self, scanner: BytesScanner) -> int:
		value = scanner.scan_int(self._bytecode_type)
		# TODO: Check if value is valid
		return value

	def serialize(self, value: int, context: SerializeContext) -> str:
		for case_name,case_value in self._cases.items():
			if value == case_value:
				return case_name
		raise PyMSError('Serialize', "Value '%s' has no case for '%s'" % (value, self._name))

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> int:
		token = lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise PyMSError('Parse', "Expected an enum identifier but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> int:
		if not token in self._cases:
			raise PyMSError('Parse', "Value '%s' is not a valid case for '%s'" % (token, self._name))
		return self._cases[token]

class BooleanCodeType(IntCodeType):
	def __init__(self, name: str, bytecode_type: str) -> None:
		IntCodeType.__init__(self, name, bytecode_type, limits=(0, 1))

	def lex(self, lexer: Lexer, parse_context: ParseContext) -> bool:
		token = lexer.next_token()
		if not isinstance(token, Tokens.BooleanToken) and not isinstance(token, Tokens.IntegerToken):
			raise PyMSError('Parse', "Expected a boolean but got '%s'" % token.raw_value, line=lexer.line)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext) -> bool:
		if token == 'true' or token == '1':
			return True
		elif token == 'false' or token == '0':
			return False
		raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self._name))
