from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# Static tables for the GPTP "Graft Hook" (the FireGraft replacement).
# Function lists are indexed by their position (that index is what is stored in Buttons.graft),
# in the same order as FireGraft and the hook's lookup tables in `grafting.cpp`. The button conditions and actions
# are the `condition_commands` and `action_commands` of `CodeHandlers.CodeCommands`.

class ParamKind(Enum):
	none = 'none'
	unit = 'unit'
	tech = 'tech'
	upgrade = 'upgrade'
	order = 'order'

# Opcode values are >= 0xFF00, any other value in a script is a "has unit" check
OPCODE_MIN = 0xFF00
END_OF_LIST = 0xFFFF

@dataclass(frozen=True)
class StatFunction:
	address: int # Vanilla StarCraft 1.16.1 function address
	name: str
	display_name: str # Name used by FireGraft

@dataclass(frozen=True)
class StatPreset:
	status_function: int
	display_function: int
	name: str

STATUS_FUNCTIONS: tuple[StatFunction, ...] = (
	StatFunction(0x00424500, 'StatusFunction1', 'Status Function 1'),
	StatFunction(0x00424980, 'StatusFunction2', 'Status Function 2'),
	StatFunction(0x00425180, 'StatusFunction3', 'Status Function 3'),
	StatFunction(0x00424F10, 'StatusFunction4', 'Status Function 4'),
	StatFunction(0x00424B50, 'StatusFunction5', 'Status Function 5'),
	StatFunction(0x00424AF0, 'StatusFunction6', 'Status Function 6'),
	StatFunction(0x00424AC0, 'StatusFunction7', 'Status Function 7'),
	StatFunction(0x00425900, 'StatusFunction8', 'Status Function 8'),
	StatFunction(0x00424520, 'StatusFunction9', 'Status Function 9'),
)

DISPLAY_FUNCTIONS: tuple[StatFunction, ...] = (
	StatFunction(0x00426F50, 'DisplayFunction1', 'Display Function 1'),
	StatFunction(0x00427890, 'DisplayFunction2', 'Display Function 2'),
	StatFunction(0x00427C90, 'DisplayFunction3', 'Display Function 3'),
	StatFunction(0x004274A0, 'DisplayFunction4', 'Display Function 4'),
	StatFunction(0x004273E0, 'DisplayFunction5', 'Display Function 5'),
	StatFunction(0x00427260, 'DisplayFunction6', 'Display Function 6'),
	StatFunction(0x00427D30, 'DisplayFunction7', 'Display Function 7'),
	StatFunction(0x00426EE0, 'DisplayFunction8', 'Display Function 8'),
	StatFunction(0x00425EE0, 'DisplayFunction9', 'Display Function 9'),
)

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
DEFAULT_BUTTON_UNIT_COUNT = 250 # Includes command cards for groups, builder pages, replays, etc.
DEFAULT_STAT_COUNT = 228
NO_CONNECTED_UNIT = 0xFFFF
