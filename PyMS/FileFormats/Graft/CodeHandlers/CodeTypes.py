from __future__ import annotations

from .DataContext import DataContext
from ..Definitions import ParamKind, StatFunction, NO_CONNECTED_UNIT

from ....Utilities.CodeHandlers import CodeType
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities import Struct
from ....Utilities.PyMSError import PyMSError

from typing import Sequence

def _data_context(context: SerializeContext | ParseContext) -> DataContext | None:
	return getattr(context, 'data_context', None)

def _lex_int(token: Tokens.Token) -> int | None:
	try:
		if isinstance(token, Tokens.HexToken):
			return int(token.raw_value, 16)
		if isinstance(token, Tokens.IntegerToken):
			return int(token.raw_value)
	except ValueError:
		pass
	return None

class IDCodeType(CodeType.IntCodeType):
	# A DAT entry ID, written as its name (when that name is unique) or as an integer
	def __init__(self, name: str, help_text: str, kind: ParamKind, bytecode_type: Struct.IntField = Struct.l_u16, *, limits: tuple[int, int] | None = None) -> None:
		super().__init__(name, help_text, bytecode_type, limits=limits, allow_hex=True)
		self.kind = kind

	def serialize(self, value: int, context: SerializeContext) -> str:
		if (data_context := _data_context(context)) and (name := data_context.unique_name(self.kind, value)):
			return CodeType.StrCodeType.serialize_string(name)
		return super().serialize(value, context)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		# Only comment when the value couldn't be written as a name
		if (data_context := _data_context(context)) and data_context.unique_name(self.kind, value) is None:
			return data_context.name(self.kind, value)
		return None

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.StringToken):
			_ = parse_context.lexer.next_token()
			name = CodeType.StrCodeType.parse_string(token.raw_value)
			data_context = _data_context(parse_context)
			entry_id = data_context.id(self.kind, name) if data_context else None
			if entry_id is None:
				raise parse_context.error('Parse', f'`{name}` is not a known (or unique) {self.kind.value} name for `{self.name}`')
			return entry_id
		return super().lex(parse_context)

def unit_id_type(name: str = 'unit', help_text: str = 'A unit ID, or its quoted name') -> IDCodeType:
	return IDCodeType(name, help_text, ParamKind.unit, limits=(0, 0xFEFF))

def id_type(kind: ParamKind, name: str | None = None) -> CodeType.IntCodeType:
	if kind == ParamKind.none:
		return CodeType.IntCodeType(name or 'value', 'A raw value', Struct.l_u16, allow_hex=True)
	return IDCodeType(name or kind.value, f'A {kind.value} ID, or its quoted name', kind)

class IconCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('icon', 'A cmdicons.grp frame', Struct.l_u16, allow_hex=True)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.icon_name(value)
		return None

class StringIDCodeType(CodeType.IntCodeType):
	def __init__(self, name: str) -> None:
		super().__init__(name, 'A stat_txt.tbl string ID (0 for no string)', Struct.l_u16, allow_hex=True)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.stat_txt_string(value)
		return None

class ButtonPositionCodeType(CodeType.IntCodeType):
	NAMES = ('Top Left', 'Top Middle', 'Top Right', 'Middle Left', 'Center', 'Middle Right', 'Bottom Left', 'Bottom Middle', 'Bottom Right')

	def __init__(self) -> None:
		super().__init__('position', 'The button position (1 to 9, left to right then top to bottom)', Struct.l_u16)

	def comment(self, value: int, _context: SerializeContext) -> str | None:
		if 1 <= value <= len(ButtonPositionCodeType.NAMES):
			return ButtonPositionCodeType.NAMES[value - 1]
		return None

class UnitHeaderCodeType(CodeType.IntCodeType):
	# A unit ID written as an integer (with its name as a comment)
	def __init__(self) -> None:
		super().__init__('unit', 'A unit ID', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if (data_context := _data_context(context)) and value < data_context.entry_count(ParamKind.unit):
			return data_context.name(ParamKind.unit, value)
		return None

class FunctionCodeType(CodeType.CodeType[int, int], CodeType.HasKeywords):
	# A function referenced by its index, written as its name (or an integer if unknown)
	def __init__(self, name: str, help_text: str, functions: Sequence[StatFunction]) -> None:
		CodeType.CodeType.__init__(self, name, help_text, Struct.l_u32, False)
		self.functions = functions
		self._lookup = {function.name: index for index, function in enumerate(functions)}

	def serialize(self, value: int, context: SerializeContext) -> str:
		if 0 <= value < len(self.functions):
			return self.functions[value].name
		return str(value)

	def comment(self, value: int, _context: SerializeContext) -> str | None:
		if 0 <= value < len(self.functions):
			return None
		return f'Unknown {self.name}'

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken):
			if token.raw_value in self._lookup:
				return self._lookup[token.raw_value]
			raise parse_context.error('Parse', f'`{token.raw_value}` is not a valid `{self.name}`')
		value = _lex_int(token)
		if value is None:
			raise parse_context.error('Parse', f'Expected a `{self.name}` name or integer but got `{token.raw_value}`')
		return value

	def validate(self, value: int, parse_context: ParseContext, token: str | None = None) -> None:
		if value < 0 or value > Struct.l_u32.max:
			raise PyMSError('Parse', f'Value `{value}` is out of range for `{self.name}`')

	def keywords(self) -> Sequence[str]:
		return tuple(self._lookup.keys())

class OptionalCodeType(CodeType.CodeType[int | None, int | None], CodeType.HasKeywords):
	# Wraps an int type to also accept `None`
	NONE = 'None'

	def __init__(self, base: CodeType.IntCodeType) -> None:
		CodeType.CodeType.__init__(self, base.name, f'{base.help_text}, or `None`', Struct.l_u16, False)
		self.base = base

	def serialize(self, value: int | None, context: SerializeContext) -> str:
		if value is None:
			return OptionalCodeType.NONE
		return self.base.serialize(value, context)

	def comment(self, value: int | None, context: SerializeContext) -> str | None:
		if value is None:
			return None
		return self.base.comment(value, context)

	def parse(self, parse_context: ParseContext) -> int | None:
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == OptionalCodeType.NONE:
			_ = parse_context.lexer.next_token()
			return None
		return self.base.parse(parse_context)

	def lex(self, parse_context: ParseContext) -> int | None:
		return self.base.lex(parse_context)

	def keywords(self) -> Sequence[str]:
		return (OptionalCodeType.NONE,)

class ButtonSetCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('button_set', 'A button set ID', Struct.l_u32)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.button_set_name(value)
		return None

class ConnectedUnitCodeType(OptionalCodeType):
	# `None` is stored as 0xFFFF
	def __init__(self) -> None:
		super().__init__(IDCodeType('connected_unit', 'A unit ID, or its quoted name', ParamKind.unit, limits=(0, NO_CONNECTED_UNIT - 1)))

	@staticmethod
	def to_value(value: int | None) -> int:
		return NO_CONNECTED_UNIT if value is None else value

	@staticmethod
	def from_value(value: int) -> int | None:
		return None if value == NO_CONNECTED_UNIT else value
