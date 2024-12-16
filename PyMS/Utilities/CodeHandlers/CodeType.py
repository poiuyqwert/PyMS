
from __future__ import annotations

from . import Tokens
from .CodeBlock import CodeBlock
from . import Lexer

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner
from .. import Struct

from typing import TYPE_CHECKING, Generic, TypeVar, cast, runtime_checkable, Protocol, Sequence
if TYPE_CHECKING:
	from .DecompileContext import DecompileContext
	from .ByteCodeCompiler import ByteCodeBuilderType
	from .SerializeContext import SerializeContext
	from .ParseContext import ParseContext

@runtime_checkable
class HasKeywords(Protocol):
	def keywords(self) -> Sequence[str]:
		...

I = TypeVar('I')
O = TypeVar('O')
class CodeType(Generic[I, O]):
	# TODO: Remove `bytecode_type` from `CodeType` and move it to a subclass?
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.Field, block_reference: bool) -> None:
		self.name = name
		self.help_text = help_text
		self._bytecode_type = bytecode_type
		self._block_reference = block_reference

	def accepts(self, other_type: CodeType) -> bool:
		return type(other_type) == type(self)

	def compatible(self, other_type: CodeType) -> int:
		return type(other_type) == type(self)

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> I:
		return scanner.scan(self._bytecode_type)

	def compile(self, value: I, context: ByteCodeBuilderType) -> None:
		context.add_data(self._bytecode_type.pack(value))

	def serialize(self, value: I, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		return str(value)

	def comment(self, value: I, context: SerializeContext) -> str | None:
		return None

	def parse(self, parse_context: ParseContext) -> O:
		start = parse_context.lexer.get_rollback()
		value = self._lex(parse_context)
		raw_value = parse_context.lexer.get_raw(from_state=start)
		self.validate(value, parse_context, raw_value)
		return value

	def _lex(self, parse_context: ParseContext) -> O:
		raise NotImplementedError(self.__class__.__name__ + '.lex_token()')

	def validate(self, value: O, parse_context: ParseContext, token: str | None = None) -> None:
		pass

	def __eq__(self, other) -> bool:
		return type(other) == type(self)

	def __hash__(self) -> int:
		return hash(type(self))

class IntCodeType(CodeType[int, int]):
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.IntField, limits: tuple[int, int ] | None = None, allow_hex: bool = False, param_repeater: bool = False) -> None:
		CodeType.__init__(self, name, help_text, bytecode_type, False)
		self._limits = limits
		self._allow_hex = allow_hex
		self.param_repeater = param_repeater

	def _lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		allowed = 'integer'
		if self._allow_hex:
			allowed += ' or hex'
		try:
			if isinstance(token, Tokens.IntegerToken):
				return int(token.raw_value)
			elif isinstance(token, Tokens.HexToken) and self._allow_hex:
				return int(token.raw_value, 16)
		except:
			raise parse_context.error('Parse', f'Expected {allowed} value but got `{token.raw_value}`')
		raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{self.name}` (expected {allowed})')

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if self._limits:
			return self._limits
		bytecode_type = cast(Struct.IntField, self._bytecode_type)
		return (bytecode_type.min, bytecode_type.max)

	def validate(self, num: int, parse_context: ParseContext, token: str | None = None) -> None:
		min,max = self.get_limits(parse_context)
		if num < min:
			raise PyMSError('Parse', f'Value is too small for `{self.name}` (got `{num}`, minimum is `{min}`)')
		if num > max:
			raise PyMSError('Parse', f'Value is too large for `{self.name}` (got `{num}`, maximum is `{max}`)')

class FloatCodeType(CodeType[float, float]):
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.FloatField, limits: tuple[float, float] | None = None) -> None:
		CodeType.__init__(self, name, help_text, bytecode_type, False)
		self._limits = limits

	def _lex(self, parse_context: ParseContext) -> float:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.FloatToken):
			try:
				return float(token.raw_value)
			except:
				raise PyMSError('Parse', f'Invalid value `{token.raw_value}` for `{self.name}` (expected float value)')
		raise parse_context.error('Parse', f'Expected float value but got `{token.raw_value}`')

	def get_limits(self, parse_context: ParseContext) -> tuple[float, float]:
		if self._limits:
			return self._limits
		bytecode_type = cast(Struct.FloatField, self._bytecode_type)
		return (bytecode_type.min, bytecode_type.max)

	def validate(self, num: float, parse_context: ParseContext, token: str | None = None) -> None:
		min,max = self.get_limits(parse_context)
		if num < min:
			raise PyMSError('Parse', f'Value is too small for `{self.name}` (got `{num}`, minimum is `{min}`)')
		if num > max:
			raise PyMSError('Parse', f'Value is too large for `{self.name}` (got `{num}`, maximum is `{max}`)')

class AddressCodeType(CodeType[CodeBlock, CodeBlock]):
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.IntField) -> None:
		CodeType.__init__(self, name, help_text, bytecode_type, True)

	def compile(self, block: CodeBlock, context: ByteCodeBuilderType) -> None:
		context.add_block_ref(block, cast(Struct.IntField, self._bytecode_type))

	def serialize(self, block: CodeBlock, context: SerializeContext) -> str:
		return context.strategy.block_label(block)
	
	def _lex(self, parse_context: ParseContext) -> CodeBlock:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken):
			return parse_context.get_block(token.raw_value)
		raise parse_context.error('Parse', f'Expected block label identifier but got `{token.raw_value}`')

class StrCodeType(CodeType[str, str]):
	def __init__(self, name: str, help_text: str) -> None:
		CodeType.__init__(self, name, help_text, Struct.l_str(0), False) # TODO: We don't actually use the Struct field

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
			raise PyMSError('Parse', f'Value `{string}` is not a valid string')
		return result

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> str:
		return scanner.scan_cstr()

	def compile(self, value: str, context: ByteCodeBuilderType) -> None:
		context.add_data(value.encode('utf-8') + b'\x00')

	def serialize(self, value: str, context: SerializeContext) -> str:
		return StrCodeType.serialize_string(value)

	def _lex(self, parse_context: ParseContext) -> str:
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.StringToken) and parse_context.command_in_parens:
			token = parse_context.lexer.read_open_string(lambda token: Lexer.Stop.exclude if token.raw_value == ',' or token.raw_value == ')' else Lexer.Stop.proceed)
		if isinstance(token, Tokens.StringToken):
			try:
				return StrCodeType.parse_string(token.raw_value)
			except:
				if parse_context and parse_context.command_in_parens:
					return token.raw_value
				raise
		raise parse_context.error('Parse', f'Expected string value but got `{token.raw_value}`')

class EnumCodeType(CodeType[int, int], HasKeywords):
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.IntField, cases: dict[str, int] | list[str], allow_integer: bool = False) -> None:
		CodeType.__init__(self, name, help_text, bytecode_type, False)
		if isinstance(cases, list):
			cases = dict((name, n) for n,name in enumerate(cases))
		self._cases = cases
		self._values = set(cases.values())
		self._allow_integer = allow_integer

	def decompile(self, scanner: BytesScanner, context: DecompileContext) -> int:
		value = scanner.scan(self._bytecode_type)
		# TODO: Check if value is valid
		return value

	def serialize_basic(self, value: int) -> str:
		for case_name,case_value in self._cases.items():
			if value == case_value:
				return case_name
		raise PyMSError('Serialize', f'Value `{value}` has no case for `{self.name}`')

	def serialize(self, value: int, context: SerializeContext) -> str:
		return self.serialize_basic(value)

	def _possible_values(self) -> str:
		values = ''
		for name in self._cases.keys():
			if values:
				values += ', '
			values += name
		return values

	def _lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken):
			if token.raw_value in self._cases:
				return self._cases[token.raw_value]
			raise PyMSError('Parse', f'Value `{token.raw_value}` is not a valid case for `{self.name}` (possible values: `{self._possible_values()}`)')
		if isinstance(token, Tokens.IntegerToken) and self._allow_integer:
			try:
				value = int(token.raw_value)
				if value in self._values:
					return value
			except:
				pass
		raise parse_context.error('Parse', f'Expected a `{self.name}` enum identifier but got `{token.raw_value}` (possible values: `{self._possible_values()}`)')

	def keywords(self) -> Sequence[str]:
		return tuple(self._cases.keys())

class BooleanCodeType(IntCodeType):
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.IntField) -> None:
		IntCodeType.__init__(self, name, help_text, bytecode_type, limits=(0, 1))

	def _lex(self, parse_context: ParseContext) -> bool:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.BooleanToken) or isinstance(token, Tokens.IntegerToken):
			if token.raw_value == 'true' or token.raw_value == '1':
				return True
			elif token.raw_value == 'false' or token.raw_value == '0':
				return False
		raise parse_context.error('Parse', f'Expected a `{self.name}` boolean but got `{token.raw_value}`')

	def keywords(self) -> Sequence[str]:
		return ('true', 'false')

class FlagsCodeType(CodeType[int, int], HasKeywords):
	# TODO: Should this just always be case insensitive?
	def __init__(self, name: str, help_text: str, bytecode_type: Struct.IntField, flags: dict[str, int], case_sensitive: bool = True, allow_raw_flags: bool = False) -> None:
		CodeType.__init__(self, name, help_text, bytecode_type, False)
		self._names_to_flags = flags
		self._flags_to_names: dict[int, str] = {}
		for name, flag in flags.items():
			self._flags_to_names[flag] = name
		self._case_sensitive = case_sensitive
		self._allow_raw_flags = allow_raw_flags

	@staticmethod
	def serialize_flags(flags: int, flags_to_names: dict[int, str], bytecode_type: Struct.IntField, empty_value: str = '0') -> str:
		if not flags:
			return empty_value
		names = []
		for bit_index in range(bytecode_type.size * 8):
			flag = 1 << bit_index
			if flags & flag:
				names.append(flags_to_names.get(flag, f'0x{flag:X}'))
		return ' | '.join(names)

	def serialize(self, value: int, context: SerializeContext) -> str:
		return FlagsCodeType.serialize_flags(value, self._flags_to_names, cast(Struct.IntField, self._bytecode_type))

	@staticmethod
	def lex_flags(parse_context: ParseContext, names_to_flags: dict[str, int], type_name: str, bytecode_type: Struct.IntField, case_sensitive: bool = True, allow_raw_flags: bool = False) -> int:
		# TODO: The old AISE supported empty parameter for no flags, should this be changed?
		token = parse_context.lexer.next_token(peek=True)
		if token.raw_value == ',' or token.raw_value == ')':
			return 0

		allowed = 'flag name'
		if allow_raw_flags:
			allowed += ' or integer/hex'
		flags = 0
		while True:
			token = parse_context.lexer.next_token()
			if isinstance(token, Tokens.IdentifierToken):
				name = token.raw_value
				if not case_sensitive:
					name = name.lower()
				if not name in names_to_flags:
					raise PyMSError('Parse', f'Value `{token.raw_value}` is not a valid flag for `{type_name}` (must be a {allowed})')
				flags |= names_to_flags[name]
			elif isinstance(token, (Tokens.IntegerToken, Tokens.HexToken)) and allow_raw_flags:
				try:
					if token.raw_value.startswith('0x'):
						flag = int(token.raw_value, 16)
					else:
						flag = int(token.raw_value)
				except:
					raise PyMSError('Parse', f'Value `{token.raw_value}` is not a valid flag for `{type_name}`')
				if flag > bytecode_type.max:
					raise PyMSError('Parse', f'Flag `{token.raw_value}` is too large for `{type_name}`')
				flags |= flag
			else:
				raise parse_context.error('Parse', f'Expected a {type_name} {allowed}, but got `{token.raw_value}`')
			token = parse_context.lexer.next_token(peek=True)
			if token.raw_value == '|':
				_ = parse_context.lexer.next_token()
			else:
				break
		return flags

	def _lex(self, parse_context: ParseContext) -> int:
		return FlagsCodeType.lex_flags(parse_context, self._names_to_flags, self.name, cast(Struct.IntField, self._bytecode_type), self._case_sensitive, self._allow_raw_flags)

	def keywords(self) -> Sequence[str]:
		return tuple(self._names_to_flags.keys())
