from __future__ import annotations

from . import CodeTypes

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeType import CodeType

from typing import Sequence

class ReqCommandDefinition(CodeCommandDefinition):
	# A requirement command, with a readable name for the Builder
	def __init__(self, name: str, display_name: str, help_text: str, byte_code_id: int | None, *, param_types: Sequence[CodeType] = ()) -> None:
		super().__init__(name, help_text, byte_code_id, param_types)
		self.display_name = display_name # Readable name

# Opcode values are >= 0xFF00, any other value in a script is a `has_completed` unit check
OPCODE_MIN = 0xFF00
# Ends a script, a sub-list, and the list of scripts
END_OF_LIST = 0xFFFF

# Requirement opcodes. units.dat requirements are checked by a different function than the other requirements,
# and some opcodes only make sense for one kind of requirements, so each file has its own list of available opcodes.

Or = ReqCommandDefinition('or', 'Or', 'Or', 0xFF01)
CurrentUnitIs = ReqCommandDefinition('current_unit_is', 'Current Unit Is', 'Current unit is {1}', 0xFF02, param_types=(CodeTypes.UnitCodeType(),))
MustHave = ReqCommandDefinition('must_have', 'Must Have', 'Must have {1}, counting units that are still being built or morphed', 0xFF03, param_types=(CodeTypes.UnitCodeType(),))
MustHaveAddon = ReqCommandDefinition('must_have_addon', 'Must Have Add-on', 'Must have add-on {1} attached', 0xFF04, param_types=(CodeTypes.UnitCodeType(),))
IsNotLiftedOff = ReqCommandDefinition('is_not_lifted_off', 'Is Not Lifted Off', 'Is not lifted off', 0xFF05)
IsLiftedOff = ReqCommandDefinition('is_lifted_off', 'Is Lifted Off', 'Is lifted off', 0xFF06)
IsNotTrainingOrMorphing = ReqCommandDefinition('is_not_training_or_morphing', 'Is Not Training/Morphing', 'Is not training or morphing', 0xFF07)
IsNotConstructingAddon = ReqCommandDefinition('is_not_constructing_addon', 'Is Not Constructing Add-on', 'Is not constructing add-on', 0xFF08)
IsNotResearching = ReqCommandDefinition('is_not_researching', 'Is Not Researching', 'Is not researching', 0xFF09)
IsNotUpgrading = ReqCommandDefinition('is_not_upgrading', 'Is Not Upgrading', 'Is not upgrading', 0xFF0A)
IsNotConstructing = ReqCommandDefinition('is_not_constructing', 'Is Not Constructing', 'Is not constructing', 0xFF0B)
DoesNotHaveAddon = ReqCommandDefinition('does_not_have_addon', 'Does Not Have Add-on', 'Does not have add-on attached', 0xFF0C)
DoesNotHaveExit = ReqCommandDefinition('does_not_have_exit', 'Does Not Have Exit', 'Does not have exit', 0xFF0D)
HasHangarSpace = ReqCommandDefinition('has_hangar_space', 'Has Hangar Space', 'Has hangar space', 0xFF0E)
MustBeResearched = ReqCommandDefinition('must_be_researched', 'Must Be Researched', 'Must be researched', 0xFF0F)
DoesNotHaveNuke = ReqCommandDefinition('does_not_have_nuke', 'Does Not Have Nuke', 'Does not have loaded nuke', 0xFF10)
IsNotBurrowed = ReqCommandDefinition('is_not_burrowed', 'Is Not Burrowed', 'Is not burrowed', 0xFF11)
CanAttack = ReqCommandDefinition('can_attack', 'Can Attack', 'Can attack', 0xFF12)
CanSetRallyPoint = ReqCommandDefinition('can_set_rally_point', 'Can Set Rally Point', 'Can set rally point', 0xFF13)
CanMove = ReqCommandDefinition('can_move', 'Can Move', 'Can move', 0xFF14)
HasWeapon = ReqCommandDefinition('has_weapon', 'Has Weapon', 'Has weapon', 0xFF15)
IsWorker = ReqCommandDefinition('is_worker', 'Is Worker', 'Is worker', 0xFF16)
IsFlyingBuilding = ReqCommandDefinition('is_flying_building', 'Is Flying Building', 'Is flying building', 0xFF17)
IsTransport = ReqCommandDefinition('is_transport', 'Is Transport', 'Is transport', 0xFF18)
IsPowerup = ReqCommandDefinition('is_powerup', 'Is Powerup', 'Is powerup', 0xFF19)
IsSubunit = ReqCommandDefinition('is_subunit', 'Is Subunit', 'Is subunit', 0xFF1A)
HasSpiderMines = ReqCommandDefinition('has_spider_mines', 'Has Spider Mines', 'Has spider mines', 0xFF1B)
IsHero = ReqCommandDefinition('is_hero', 'Is Hero', 'Is hero', 0xFF1C)
CanHoldPosition = ReqCommandDefinition('can_hold_position', 'Can Hold Position', 'Can hold position', 0xFF1D)
AllowOnHallucinations = ReqCommandDefinition('allow_on_hallucinations', 'Allow On Hallucinations', 'Allow on hallucinations', 0xFF1E)
Level1Requires = ReqCommandDefinition('level_1_requires', 'Level 1 Requires...', 'Upgrade level 1 requires the following, until `end_level_requirements` (which ends the requirements for the level). Must be followed by `level_2_requires` and `level_3_requires`, and levels above 3 use the level 1 requirements', 0xFF1F)
Level2Requires = ReqCommandDefinition('level_2_requires', 'Level 2 Requires...', 'Upgrade level 2 requires the following, until `end_level_requirements`. Must directly follow the `end_level_requirements` of `level_1_requires`', 0xFF20)
Level3Requires = ReqCommandDefinition('level_3_requires', 'Level 3 Requires...', 'Upgrade level 3 requires the rest of the script. Must directly follow the `end_level_requirements` of `level_2_requires`', 0xFF21)
DisableButton = ReqCommandDefinition('disable_button', 'Disable Button', 'Disable the button, without checking the rest of the requirements', 0xFF22)
HideButton = ReqCommandDefinition('hide_button', 'Hide Button', 'Hide the button, without checking the rest of the requirements', 0xFF23)
IsBroodWar = ReqCommandDefinition('is_brood_war', 'Is Brood War', 'Is Brood War', 0xFF24)
IsResearched = ReqCommandDefinition('is_researched', 'Is Researched', 'Is researched {1}', 0xFF25, param_types=(CodeTypes.TechCodeType(),))
IsBurrowed = ReqCommandDefinition('is_burrowed', 'Is Burrowed', 'Is burrowed', 0xFF26)

# The next 0xFFFF after these opcodes ends their sub-list rather than the script
sublist_commands = (Level1Requires, Level2Requires)
# The upgrade levels, in the order a script must have them. Only `level_1_requires` is checked by the game, which jumps from it to the word of the
# upgrade's current level, then checks up to the next 0xFFFF. So `level_2_requires` and `level_3_requires` are only ever jumped to.
level_commands = (Level1Requires, Level2Requires, Level3Requires)

# A requirement word below 0xFF00 checks that the player has a completed unit of the given type
HasCompleted = ReqCommandDefinition('has_completed', 'Has Completed', 'Must have {1}, counting only completed units', None, param_types=(CodeTypes.UnitCodeType(limits=(0, OPCODE_MIN - 1)),))
# 0xFFFF after a `level_1_requires`/`level_2_requires` sub-list
EndLevelRequirements = ReqCommandDefinition('end_level_requirements', 'End Level Requirements', 'Ends a `level_1_requires` or `level_2_requires` sub-list', None)

# Commands for units.dat requirements, which the game checks with its own function (`TTAllowed`)
unit_req_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	DisableButton,
	HideButton,
	IsBroodWar,
	IsBurrowed,
	MustHaveAddon,
	IsNotConstructing,
	DoesNotHaveAddon,
	HasHangarSpace,
	DoesNotHaveNuke,
	IsResearched,
	HasCompleted,
]

# The upgrade, research, tech use, and order requirements are all checked by the same function (`CheckAllowed`),
# but a few of its opcodes read the ID the requirements are for as a specific kind of ID,
# so each of them only has the commands that make sense for what its requirements are for.

# The upgrade levels check the level of the upgrade the requirements are for
upgrade_req_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	DisableButton,
	HideButton,
	IsBroodWar,
	IsBurrowed,
	DoesNotHaveExit,
	IsLiftedOff,
	CanAttack,
	CanSetRallyPoint,
	CanMove,
	HasWeapon,
	IsWorker,
	IsFlyingBuilding,
	IsTransport,
	IsPowerup,
	IsSubunit,
	HasSpiderMines,
	IsHero,
	CanHoldPosition,
	AllowOnHallucinations,
	Level1Requires,
	Level2Requires,
	Level3Requires,
	HasCompleted,
	EndLevelRequirements,
]

# No `must_be_researched`, the button is already hidden once the tech is researched
research_req_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	DisableButton,
	HideButton,
	IsBroodWar,
	IsBurrowed,
	DoesNotHaveExit,
	IsLiftedOff,
	CanAttack,
	CanSetRallyPoint,
	CanMove,
	HasWeapon,
	IsWorker,
	IsFlyingBuilding,
	IsTransport,
	IsPowerup,
	IsSubunit,
	HasSpiderMines,
	IsHero,
	CanHoldPosition,
	AllowOnHallucinations,
	HasCompleted,
]

# `must_be_researched` checks the tech the requirements are for. No `allow_on_hallucinations`, hallucinations can never use tech.
tech_use_req_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	DisableButton,
	HideButton,
	IsBroodWar,
	IsBurrowed,
	DoesNotHaveExit,
	IsLiftedOff,
	CanAttack,
	CanSetRallyPoint,
	CanMove,
	HasWeapon,
	IsWorker,
	IsFlyingBuilding,
	IsTransport,
	IsPowerup,
	IsSubunit,
	HasSpiderMines,
	IsHero,
	CanHoldPosition,
	MustBeResearched,
	HasCompleted,
]

order_req_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	DisableButton,
	HideButton,
	IsBroodWar,
	IsBurrowed,
	DoesNotHaveExit,
	IsLiftedOff,
	CanAttack,
	CanSetRallyPoint,
	CanMove,
	HasWeapon,
	IsWorker,
	IsFlyingBuilding,
	IsTransport,
	IsPowerup,
	IsSubunit,
	HasSpiderMines,
	IsHero,
	CanHoldPosition,
	AllowOnHallucinations,
	HasCompleted,
]

# Every requirement command, including the ones a file's language doesn't have available
all_req_commands: list[CodeCommandDefinition] = sorted(dict.fromkeys(unit_req_commands + upgrade_req_commands + research_req_commands + tech_use_req_commands + order_req_commands), key=lambda cmd_def: (cmd_def.byte_code_id is None, cmd_def.byte_code_id or 0))

# The opcodes a file can be loaded with, by their value. The game checks units.dat requirements and the other requirements with different functions,
# each only handling its own opcodes, so a units.dat requirements file only loads with its own opcodes. The other files load with the opcodes of any of them,
# since the game handles them all the same way (a file using an opcode its language doesn't have still loads, and fails validation when it's saved).
unit_loadable_opcodes: dict[int, CodeCommandDefinition] = {cmd_def.byte_code_id: cmd_def for cmd_def in unit_req_commands if cmd_def.byte_code_id is not None}
check_allowed_loadable_opcodes: dict[int, CodeCommandDefinition] = {cmd_def.byte_code_id: cmd_def for cmd_def in upgrade_req_commands + research_req_commands + tech_use_req_commands + order_req_commands if cmd_def.byte_code_id is not None}
