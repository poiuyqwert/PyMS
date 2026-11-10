from __future__ import annotations

from ....Utilities.DataContext import DataContext

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

class _DATCodeType(CodeType.IntCodeType):
	# A DAT entry ID, written as its name (when that name is unique) or as an integer
	KIND: str # What the IDs are for, used in errors

	def __init__(self, name: str, help_text: str, *, limits: tuple[int, int] | None = None) -> None:
		super().__init__(name, help_text, Struct.l_u16, limits=limits, allow_hex=True)

	def _entry_name(self, data_context: DataContext, entry_id: int) -> str | None:
		raise NotImplementedError()

	def _entry_ids(self, data_context: DataContext, name: str) -> tuple[int, ...]:
		raise NotImplementedError()

	def _entry_display_name(self, data_context: DataContext, entry_id: int) -> str | None:
		raise NotImplementedError()

	def serialize(self, value: int, context: SerializeContext) -> str:
		if (data_context := _data_context(context)) and (name := self._entry_name(data_context, value)):
			return CodeType.StrCodeType.serialize_string(name)
		return super().serialize(value, context)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		# Only comment when the value couldn't be written as a name
		if (data_context := _data_context(context)) and self._entry_name(data_context, value) is None:
			return self._entry_display_name(data_context, value)
		return None

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.StringToken):
			_ = parse_context.lexer.next_token()
			name = CodeType.StrCodeType.parse_string(token.raw_value)
			data_context = _data_context(parse_context)
			entry_ids = self._entry_ids(data_context, name) if data_context else ()
			if not entry_ids:
				raise parse_context.error('Parse', f'`{name}` is not a known {self.KIND} name for `{self.name}`')
			if len(entry_ids) > 1:
				raise parse_context.error('Parse', f'`{name}` is the name of multiple {self.KIND} IDs ({", ".join(str(entry_id) for entry_id in entry_ids)}) for `{self.name}`, use the ID instead')
			return entry_ids[0]
		return super().lex(parse_context)

class UnitCodeType(_DATCodeType):
	KIND = 'unit'

	def __init__(self, name: str = 'unit', help_text: str = 'A unit ID, or its quoted name', *, limits: tuple[int, int] | None = None) -> None:
		super().__init__(name, help_text, limits=limits)

	def _entry_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.unit_name(entry_id)

	def _entry_ids(self, data_context: DataContext, name: str) -> tuple[int, ...]:
		return data_context.unit_ids(name)

	def _entry_display_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.unit_display_name(entry_id)

class UpgradeCodeType(_DATCodeType):
	KIND = 'upgrade'

	def __init__(self) -> None:
		super().__init__('upgrade', 'An upgrade ID, or its quoted name')

	def _entry_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.upgrade_name(entry_id)

	def _entry_ids(self, data_context: DataContext, name: str) -> tuple[int, ...]:
		return data_context.upgrade_ids(name)

	def _entry_display_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.upgrade_display_name(entry_id)

class TechCodeType(_DATCodeType):
	KIND = 'tech'

	def __init__(self) -> None:
		super().__init__('tech', 'A tech ID, or its quoted name')

	def _entry_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.tech_name(entry_id)

	def _entry_ids(self, data_context: DataContext, name: str) -> tuple[int, ...]:
		return data_context.tech_ids(name)

	def _entry_display_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return data_context.tech_display_name(entry_id)

class QueueSlotCodeType(CodeType.CodeType[int, int], CodeType.HasKeywords):
	# A training queue slot, written 1-based (stored 0-based), or `last` for the last queued unit
	LAST = 'last'
	LAST_VALUE = 0xFE
	SLOTS = 5

	def __init__(self) -> None:
		CodeType.CodeType.__init__(self, 'queue_slot', f'A training queue slot (1 to {QueueSlotCodeType.SLOTS}), or `{QueueSlotCodeType.LAST}`', Struct.l_u16, False)

	def serialize(self, value: int, _context: SerializeContext) -> str:
		if value == QueueSlotCodeType.LAST_VALUE:
			return QueueSlotCodeType.LAST
		return str(value + 1)

	def lex(self, parse_context: ParseContext) -> int:
		token = parse_context.lexer.next_token()
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == QueueSlotCodeType.LAST:
			return QueueSlotCodeType.LAST_VALUE
		value = _lex_int(token)
		if value is None:
			raise parse_context.error('Parse', f'Invalid value `{token.raw_value}` for `{self.name}` (expected 1 to {QueueSlotCodeType.SLOTS}, or `{QueueSlotCodeType.LAST}`)')
		return value - 1

	def validate(self, value: int, parse_context: ParseContext, token: str | None = None) -> None:
		if value != QueueSlotCodeType.LAST_VALUE and not 0 <= value < QueueSlotCodeType.SLOTS:
			raise PyMSError('Parse', f'Invalid value `{token or value + 1}` for `{self.name}` (expected 1 to {QueueSlotCodeType.SLOTS}, or `{QueueSlotCodeType.LAST}`)')

	def keywords(self) -> Sequence[str]:
		return (QueueSlotCodeType.LAST,)

class ButtonCardCodeType(UnitCodeType):
	# The ID of a button card whose buttons are shown: a unit ID, or a special button card after the units
	def __init__(self) -> None:
		super().__init__('button_card', 'A unit ID (or its quoted name) whose buttons are shown, or a special button card ID after the units')

	def comment(self, value: int, context: SerializeContext) -> str | None:
		# Only comment when the value couldn't be written as a unit name
		if (data_context := _data_context(context)) and self._entry_name(data_context, value) is None:
			return data_context.button_card_name(value)
		return None

class IconCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('icon', 'A cmdicons.grp frame', Struct.l_u16, allow_hex=True)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.icon_name(value)
		return None

class StringIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('string_id', 'A stat_txt.tbl string ID (0 for no string)', Struct.l_u16, allow_hex=True)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		# String IDs are 1-based (0 is no string)
		if (data_context := _data_context(context)) and value >= 1:
			return data_context.stat_txt_string(value - 1)
		return None

class ButtonPositionCodeType(CodeType.EnumCodeType):
	# Written as the row (T, M, B) followed by the column (L, M, R), or as its number
	CODES = {
		'TL': 1,
		'TM': 2,
		'TR': 3,
		'ML': 4,
		'MM': 5,
		'MR': 6,
		'BL': 7,
		'BM': 8,
		'BR': 9
	}
	NAMES = (
		'Top Left',
		'Top Middle',
		'Top Right',
		'Middle Left',
		'Center',
		'Middle Right',
		'Bottom Left',
		'Bottom Middle',
		'Bottom Right'
	)

	def __init__(self) -> None:
		super().__init__('position', 'The button position, as the row (T, M, or B) followed by the column (L, M, or R), or 1 to 9 (left to right then top to bottom, 1 being TL and 9 being BR)', Struct.l_u16, ButtonPositionCodeType.CODES, allow_integer=True)

	def comment(self, value: int, _context: SerializeContext) -> str | None:
		if 1 <= value <= len(ButtonPositionCodeType.NAMES):
			return ButtonPositionCodeType.NAMES[value - 1]
		return None

class UnitIDCodeType(CodeType.IntCodeType):
	# A unit ID written as an integer (with its name as a comment)
	def __init__(self) -> None:
		super().__init__('unit', 'A unit ID', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.unit_display_name(value)
		return None

class ButtonCardIDCodeType(CodeType.IntCodeType):
	# A button card ID written as an integer (with its unit or special button card name as a comment)
	def __init__(self) -> None:
		super().__init__('button_card', 'A button card ID (a unit ID, or a special button card ID after the units)', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.button_card_name(value)
		return None

class ButtonSetCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('button_set', 'A button set ID', Struct.l_u32)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if data_context := _data_context(context):
			return data_context.button_set_name(value)
		return None

class UnitButtonSetCodeType(CodeType.CodeType[int | None, int | None], CodeType.HasKeywords):
	# The button set a button card uses, or `None` for no buttons
	NONE = 'None'

	def __init__(self) -> None:
		CodeType.CodeType.__init__(self, 'button_set', 'A button set ID, or `None`', Struct.l_u32, False)
		self._button_set = ButtonSetCodeType()

	def serialize(self, value: int | None, context: SerializeContext) -> str:
		if value is None:
			return UnitButtonSetCodeType.NONE
		return self._button_set.serialize(value, context)

	def comment(self, value: int | None, context: SerializeContext) -> str | None:
		if value is None:
			return None
		return self._button_set.comment(value, context)

	def parse(self, parse_context: ParseContext) -> int | None:
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == UnitButtonSetCodeType.NONE:
			_ = parse_context.lexer.next_token()
			return None
		return self._button_set.parse(parse_context)

	def lex(self, parse_context: ParseContext) -> int | None:
		return self._button_set.lex(parse_context)

	def keywords(self) -> Sequence[str]:
		return (UnitButtonSetCodeType.NONE,)

class ConnectedUnitCodeType(CodeType.CodeType[int | None, int | None], CodeType.HasKeywords):
	# The unit whose button card a mixed selection falls back to, or `None` (stored as 0xFFFF)
	NONE = 'None'
	NONE_VALUE = 0xFFFF

	def __init__(self) -> None:
		CodeType.CodeType.__init__(self, 'connected_unit', 'A unit ID (or its quoted name), or `None`', Struct.l_u16, False)
		self._unit = UnitCodeType('connected_unit', limits=(0, ConnectedUnitCodeType.NONE_VALUE - 1))

	@staticmethod
	def to_value(value: int | None) -> int:
		return ConnectedUnitCodeType.NONE_VALUE if value is None else value

	@staticmethod
	def from_value(value: int) -> int | None:
		return None if value == ConnectedUnitCodeType.NONE_VALUE else value

	def serialize(self, value: int | None, context: SerializeContext) -> str:
		if value is None:
			return ConnectedUnitCodeType.NONE
		return self._unit.serialize(value, context)

	def comment(self, value: int | None, context: SerializeContext) -> str | None:
		if value is None:
			return None
		return self._unit.comment(value, context)

	def parse(self, parse_context: ParseContext) -> int | None:
		token = parse_context.lexer.next_token(peek=True)
		if isinstance(token, Tokens.IdentifierToken) and token.raw_value == ConnectedUnitCodeType.NONE:
			_ = parse_context.lexer.next_token()
			return None
		return self._unit.parse(parse_context)

	def lex(self, parse_context: ParseContext) -> int | None:
		return self._unit.lex(parse_context)

	def keywords(self) -> Sequence[str]:
		return (ConnectedUnitCodeType.NONE,)
