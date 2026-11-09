from __future__ import annotations

from dataclasses import dataclass

# Static tables and constants for the GPTP "Graft Hook" (the FireGraft replacement) files.

# Requirement .graft files:

# Opcode values are >= 0xFF00, any other value in a script is a "has unit" check
OPCODE_MIN = 0xFF00
# Ends a script, a sub-list, and the list of scripts
END_OF_LIST = 0xFFFF
# Script IDs can be anything but the end of list marker
MAX_SCRIPT_ID = END_OF_LIST - 1

# Buttons.graft:

# Function lists are indexed by their position (that index is what is stored in Buttons.graft),
# in the same order as FireGraft and the hook's lookup tables in `grafting.cpp`. The button conditions and actions
# are the `condition_commands` and `action_commands` of `CodeHandlers.ButtonCodeCommands`, and the unit status and
# display functions are the `status_function_commands` and `display_function_commands` of `CodeHandlers.StatInfoCodeCommands`.

@dataclass(frozen=True)
class StatPreset:
	name: str
	status_function: int
	display_function: int

# Most units use one of these status/display function pairs, though not all of them do
STAT_PRESETS: tuple[StatPreset, ...] = (
	StatPreset('Building', 2, 1),
	StatPreset('Normal Unit', 1, 0),
	StatPreset('Unit w/ Subunits', 4, 3),
	StatPreset('Transport', 3, 2),
	StatPreset('Transport w/ Supply', 7, 6),
	StatPreset('Powerup', 8, 7),
	StatPreset('Morph Unit', 6, 5),
	StatPreset('Merge Unit', 5, 4),
	StatPreset('Unselectable', 0, 8),
)

# Default table sizes of the vanilla game
DEFAULT_BUTTON_CARD_COUNT = 250 # The units, plus the special button cards for groups, builder pages, replays, etc.
DEFAULT_STAT_COUNT = 228
NO_CONNECTED_UNIT = 0xFFFF

# The first button card after the units (their names are in `Assets.DataReference.ButtonCards`), which aren't units but have `unit` buttons entries
SPECIAL_BUTTON_CARDS_START = 228
