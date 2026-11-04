from __future__ import annotations

from dataclasses import dataclass

# Static tables for the GPTP "Graft Hook" (the FireGraft replacement).
# Function lists are indexed by their position (that index is what is stored in Buttons.graft),
# in the same order as FireGraft and the hook's lookup tables in `grafting.cpp`. The button conditions and actions
# are the `condition_commands` and `action_commands` of `CodeHandlers.ButtonCodeCommands`, and the unit status and
# display functions are the `status_function_commands` and `display_function_commands` of `CodeHandlers.StatInfoCodeCommands`.

# Opcode values are >= 0xFF00, any other value in a script is a "has unit" check
OPCODE_MIN = 0xFF00
END_OF_LIST = 0xFFFF

@dataclass(frozen=True)
class StatPreset:
	status_function: int
	display_function: int
	name: str

# Most units use one of these status/display function pairs, though not all of them do
STAT_PRESETS: tuple[StatPreset, ...] = (
	StatPreset(2, 1, 'Building'),
	StatPreset(1, 0, 'Normal Unit'),
	StatPreset(4, 3, 'Unit w/ Subunits'),
	StatPreset(3, 2, 'Transport'),
	StatPreset(7, 6, 'Transport w/ Supply'),
	StatPreset(8, 7, 'Powerup'),
	StatPreset(6, 5, 'Morph Unit'),
	StatPreset(5, 4, 'Merge Unit'),
	StatPreset(0, 8, 'Unselectable'),
)

def stat_preset(status_function: int, display_function: int) -> StatPreset | None:
	for preset in STAT_PRESETS:
		if preset.status_function == status_function and preset.display_function == display_function:
			return preset
	return None

# Default table sizes of the vanilla game
DEFAULT_BUTTON_CARD_COUNT = 250 # The units, plus the special button cards for groups, builder pages, replays, etc.
DEFAULT_STAT_COUNT = 228
NO_CONNECTED_UNIT = 0xFFFF

# The first button card after the units (their names are in `Assets.DataReference.ButtonCards`), which aren't units but have `unit` buttons entries
SPECIAL_BUTTON_CARDS_START = 228
