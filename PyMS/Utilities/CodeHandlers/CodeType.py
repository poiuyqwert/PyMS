
from __future__ import annotations

from PyMS.Utilities.CodeHandlers.ParseContext import ParseContext

from . import Tokens
from .CodeBlock import CodeBlock
from .BuilderContext import BuilderContext
from . import Lexer

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner
from .. import Struct

from typing import TYPE_CHECKING, Generic, TypeVar, cast
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .ParseContext import ParseContext

I = TypeVar('I')
O = TypeVar('O')
class CodeType(Generic[I, O]):
	def __init__(self, name: str, bytecode_type: Struct.Field, block_reference: bool) -> None:
		self.name = name
		self._bytecode_type = bytecode_type
		self._block_reference = block_reference

	def accepts(self, other_type: CodeType) -> bool:
		return type(other_type) == type(self)

	def compatible(self, other_type: CodeType) -> int:
		return type(other_type) == type(self)

	def decompile(self, scanner: BytesScanner) -> I:
		return scanner.scan(self._bytecode_type)

	def compile(self, value: I, context: BuilderContext) -> None:
		context.add_data(self._bytecode_type.pack(value))

	def serialize(self, value: I, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		return str(value)

	def comment(self, value: I, context: SerializeContext) -> str | None:
		return None

	def lex(self, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex()')

	def parse(self, token: str, parse_context: ParseContext | None) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.parse()')

	def validate(self, value: O, parse_context: ParseContext | None, token: str | None = None) -> None:
		pass

	def __eq__(self, other) -> bool:
		return type(other) == type(self)

	def __hash__(self) -> int:
		return hash(type(self))

class IntCodeType(CodeType[int, int]):
	def __init__(self, name: str, bytecode_type: Struct.IntField, limits: tuple[int, int ] | None = None) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		self._limits = limits or (bytecode_type.min, bytecode_type.max)

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', "Expected integer value but got '%s'" % token.raw_value)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> int:
		try:
			num = int(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self.name))
		self.validate(num, parse_context)
		return num

	def validate(self, num: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		min,max = self._limits
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%d', minimum is '%d')" % (self.name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%d', maximum is '%d')" % (self.name, num, max))

class FloatCodeType(CodeType[float, float]):
	def __init__(self, name: str, bytecode_type: Struct.FloatField, limits: tuple[float, float] | None = None) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		self._limits = limits or (bytecode_type.min, bytecode_type.max)

	def lex(self, parse_context: ParseContext) -> float:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.FloatToken):
			raise parse_context.error('Parse', "Expected float value but got '%s'" % token.raw_value)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> float:
		try:
			num = float(token)
		except:
			raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self.name))
		self.validate(num, parse_context)
		return num

	def validate(self, num: float, parse_context: ParseContext | None, token: str | None = None) -> None:
		min,max = self._limits
		if num < min:
			raise PyMSError('Parse', "Value is too small for '%s' (got '%f', minimum is '%f')" % (self.name, num, min))
		if num > max:
			raise PyMSError('Parse', "Value is too large for '%s' (got '%f', maximum is '%f')" % (self.name, num, max))

class AddressCodeType(CodeType[CodeBlock, str]):
	def __init__(self, name: str, bytecode_type: Struct.IntField) -> None:
		CodeType.__init__(self, name, bytecode_type, True)

	def compile(self, block: CodeBlock, context: BuilderContext) -> None:
		context.add_block_ref(block, cast(Struct.IntField, self._bytecode_type))

	def serialize(self, block: CodeBlock, context: SerializeContext) -> str:
		return context.block_label(block)
	
	def lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', "Expected block label identifier but got '%s'" % token.raw_value)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> str:
		return token # TODO: Should this do logic of converting to CodeBlock if the block has already been parsed?

class StrCodeType(CodeType[str, str]):
	def __init__(self, name: str) -> None:
		CodeType.__init__(self, name, Struct.l_str(0), False) # TODO: We don't actually use the Struct field

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
			if not isinstance(result, str):
				raise Exception()
		except:
			raise PyMSError('Parse', "Value '%s' is not a valid string" % string)
		return result

	def decompile(self, scanner: BytesScanner) -> str:
		return scanner.scan_cstr()

	def compile(self, value: str, context: BuilderContext) -> None:
		context.add_data(value.encode('utf-8') + b'\x00')

	def serialize(self, value: str, context: SerializeContext) -> str:
		return StrCodeType.serialize_string(value)

	def lex(self, parse_context: ParseContext) -> str:
		token: Tokens.Token
		if parse_context.command_in_parens:
			token = parse_context.lexer.read_open_string(lambda token: Lexer.Stop.exclude if token.raw_value == ',' or token.raw_value == ')' else Lexer.Stop.proceed)
		else:
			token = parse_context.lexer.next_token()
			if not isinstance(token, Tokens.StringToken):
				raise parse_context.error('Parse', "Expected string value but got '%s'" % token.raw_value)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> str:
		try:
			return StrCodeType.parse_string(token)
		except:
			if parse_context and parse_context.command_in_parens:
				return token
			raise

class EnumCodeType(CodeType[int, int]):
	def __init__(self, name: str, bytecode_type: Struct.IntField, cases: dict[str, int]) -> None:
		CodeType.__init__(self, name, bytecode_type, False)
		self._cases = cases

	def decompile(self, scanner: BytesScanner) -> int:
		value = scanner.scan(self._bytecode_type)
		# TODO: Check if value is valid
		return value

	def serialize(self, value: int, context: SerializeContext) -> str:
		for case_name,case_value in self._cases.items():
			if value == case_value:
				return case_name
		raise PyMSError('Serialize', "Value '%s' has no case for '%s'" % (value, self.name))

	def _possible_values(self) -> str:
		values = ''
		for name in self._cases.keys():
			if values:
				values += ', '
			values += name
		return values

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.IdentifierToken):
			raise parse_context.error('Parse', "Expected a '%s' enum identifier but got '%s' (possible values: %s)" % (self.name, token.raw_value, self._possible_values()))
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> int:
		if not token in self._cases:
			raise PyMSError('Parse', "Value '%s' is not a valid case for '%s' (possible values: %s)" % (token, self.name, self._possible_values()))
		return self._cases[token]

class BooleanCodeType(IntCodeType):
	def __init__(self, name: str, bytecode_type: Struct.IntField) -> None:
		IntCodeType.__init__(self, name, bytecode_type, limits=(0, 1))

	def lex(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.BooleanToken) and not isinstance(token, Tokens.IntegerToken):
			raise parse_context.error('Parse', "Expected a boolean but got '%s'" % token.raw_value)
		return self.parse(token.raw_value, parse_context)

	def parse(self, token: str, parse_context: ParseContext | None) -> bool:
		if token == 'true' or token == '1':
			return True
		elif token == 'false' or token == '0':
			return False
		raise PyMSError('Parse', "Invalid value '%s' for '%s'" % (token, self.name))
