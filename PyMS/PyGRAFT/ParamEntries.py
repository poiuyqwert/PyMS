from __future__ import annotations

from ..FileFormats.Graft.ButtonsGraft import ButtonsGraft
from ..FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftLanguage
from ..FileFormats.Graft.CodeHandlers.CodeTypes import UnitCodeType, UpgradeCodeType, TechCodeType, ButtonCardCodeType, QueueSlotCodeType

from ..Utilities.CodeHandlers.CodeType import CodeType, IntCodeType
from ..Utilities.DataContext import DataContext
from ..Utilities import Assets

# The values the Builders offer for a command's parameter

# The limits of a parameter that isn't an `IntCodeType` (they're all stored as a u16)
U16_LIMITS = (0, 0xFFFF)

def param_limits(data_context: DataContext, language: GraftLanguage, param_type: CodeType) -> tuple[int, int]:
	if isinstance(param_type, IntCodeType):
		return param_type.get_limits(GraftParseContext(GraftLexer(''), data_context, language))
	return U16_LIMITS

def param_entries(data_context: DataContext, language: GraftLanguage, param_type: CodeType) -> list[tuple[str, int | None]]:
	# The named values of a parameter, followed by a catch-all entry for any value without a name (any value can be entered)
	entries: list[tuple[str, int | None]] = []
	if isinstance(param_type, ButtonCardCodeType):
		# The units, followed by the special button cards
		entries.extend((name, card_id) for card_id, name in enumerate(data_context.unit_display_names()[:ButtonsGraft.SPECIAL_BUTTON_CARDS_START]))
		entries.extend((name, ButtonsGraft.SPECIAL_BUTTON_CARDS_START + index) for index, name in enumerate(Assets.data_cache(Assets.DataReference.ButtonCards)))
	elif isinstance(param_type, UnitCodeType):
		entries.extend((name, unit_id) for unit_id, name in enumerate(data_context.unit_display_names()))
	elif isinstance(param_type, UpgradeCodeType):
		entries.extend((name, upgrade_id) for upgrade_id, name in enumerate(data_context.upgrade_display_names()))
	elif isinstance(param_type, TechCodeType):
		entries.extend((name, tech_id) for tech_id, name in enumerate(data_context.tech_display_names()))
	elif isinstance(param_type, QueueSlotCodeType):
		# Slots are stored 0-based
		entries.extend((f'Slot {slot + 1}', slot) for slot in range(QueueSlotCodeType.SLOTS))
		entries.append(('Last', QueueSlotCodeType.LAST_VALUE))
	min_value, max_value = param_limits(data_context, language, param_type)
	return [*((name, value) for name, value in entries if value is not None and min_value <= value <= max_value), ('Unknown', None)]
