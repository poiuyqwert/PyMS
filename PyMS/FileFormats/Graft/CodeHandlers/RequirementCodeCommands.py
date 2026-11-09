from __future__ import annotations

from . import CodeTypes
from ..Definitions import OPCODE_MIN

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition

# Requirement opcodes (help text is the FireGraft name). units.dat requirements are parsed by a
# different function than the other requirements, so each has its own list of available opcodes.

Or = CodeCommandDefinition('or', 'Or', 0xFF01)
CurrentUnitIs = CodeCommandDefinition('current_unit_is', 'Current unit is {1}', 0xFF02, (CodeTypes.UnitCodeType(),))
MustHave = CodeCommandDefinition('must_have', 'Must have {1}, counting units that are still being built or morphed', 0xFF03, (CodeTypes.UnitCodeType(),))
MustHaveAddon = CodeCommandDefinition('must_have_addon', 'Must have add-on', 0xFF04)
IsNotLiftedOff = CodeCommandDefinition('is_not_lifted_off', 'Is not lifted off', 0xFF05)
IsLiftedOff = CodeCommandDefinition('is_lifted_off', 'Is lifted off', 0xFF06)
IsNotTrainingOrMorphing = CodeCommandDefinition('is_not_training_or_morphing', 'Is not training or morphing', 0xFF07)
IsNotConstructingAddon = CodeCommandDefinition('is_not_constructing_addon', 'Is not constructing add-on', 0xFF08)
IsNotResearching = CodeCommandDefinition('is_not_researching', 'Is not researching', 0xFF09)
IsNotUpgrading = CodeCommandDefinition('is_not_upgrading', 'Is not upgrading', 0xFF0A)
IsNotConstructing = CodeCommandDefinition('is_not_constructing', 'Is not constructing', 0xFF0B)
DoesNotHaveAddon = CodeCommandDefinition('does_not_have_addon', 'Does not have add-on attached', 0xFF0C)
DoesNotHaveExit = CodeCommandDefinition('does_not_have_exit', 'Does not have exit', 0xFF0D)
HasHangarSpace = CodeCommandDefinition('has_hangar_space', 'Has hangar space', 0xFF0E)
MustBeResearched = CodeCommandDefinition('must_be_researched', 'Must be researched', 0xFF0F)
DoesNotHaveNuke = CodeCommandDefinition('does_not_have_nuke', 'Does not have loaded nuke', 0xFF10)
IsNotBurrowed = CodeCommandDefinition('is_not_burrowed', 'Is not burrowed', 0xFF11)
CanAttack = CodeCommandDefinition('can_attack', 'Can attack', 0xFF12)
CanSetRallyPoint = CodeCommandDefinition('can_set_rally_point', 'Can set rally point', 0xFF13)
CanMove = CodeCommandDefinition('can_move', 'Can move', 0xFF14)
HasWeapon = CodeCommandDefinition('has_weapon', 'Has weapon', 0xFF15)
IsWorker = CodeCommandDefinition('is_worker', 'Is worker', 0xFF16)
IsFlyingBuilding = CodeCommandDefinition('is_flying_building', 'Is flying building', 0xFF17)
IsTransport = CodeCommandDefinition('is_transport', 'Is transport', 0xFF18)
IsPowerup = CodeCommandDefinition('is_powerup', 'Is powerup', 0xFF19)
IsSubunit = CodeCommandDefinition('is_subunit', 'Is Subunit', 0xFF1A)
HasSpidermines = CodeCommandDefinition('has_spidermines', 'Has spidermines', 0xFF1B)
IsHeroAndEnabled = CodeCommandDefinition('is_hero_and_enabled', 'Is hero and enabled', 0xFF1C)
CanHoldPosition = CodeCommandDefinition('can_hold_position', 'Can hold position', 0xFF1D)
AllowOnHallucinations = CodeCommandDefinition('allow_on_hallucinations', 'Allow on hallucinations', 0xFF1E)
UpgradeLevel1 = CodeCommandDefinition('upgrade_level_1', 'Upgrade Lv-1 Require...', 0xFF1F)
UpgradeLevel2 = CodeCommandDefinition('upgrade_level_2', 'Upgrade Lv-2 Require...', 0xFF20)
UpgradeLevel3 = CodeCommandDefinition('upgrade_level_3', 'Upgrade Lv-3 Require...', 0xFF21)
Grey = CodeCommandDefinition('grey', 'Grey', 0xFF22)
Blank = CodeCommandDefinition('blank', 'Blank', 0xFF23)
IsBroodWar = CodeCommandDefinition('is_brood_war', 'Must be Brood War', 0xFF24)
IsResearched = CodeCommandDefinition('is_researched', 'Is researched {1}', 0xFF25, (CodeTypes.TechCodeType(),))
IsBurrowed = CodeCommandDefinition('is_burrowed', 'Is burrowed', 0xFF26)

# The next 0xFFFF after these opcodes ends their sub-list rather than the script
sublist_commands = (UpgradeLevel1, UpgradeLevel2)

# A requirement word below 0xFF00 checks that the player has the given unit
Has = CodeCommandDefinition('has', 'Must have {1}, counting only completed units', None, (CodeTypes.UnitCodeType(limits=(0, OPCODE_MIN - 1)),))
# 0xFFFF after an `upgrade_level_1`/`upgrade_level_2` sub-list
EndSublist = CodeCommandDefinition('end_sublist', 'Ends an `upgrade_level_1` or `upgrade_level_2` sub-list', None)

shared_opcode_commands: list[CodeCommandDefinition] = [
	Or,
	CurrentUnitIs,
	MustHave,
	IsNotLiftedOff,
	IsNotTrainingOrMorphing,
	IsNotConstructingAddon,
	IsNotResearching,
	IsNotUpgrading,
	IsNotBurrowed,
	Grey,
	Blank,
	IsBroodWar,
	IsBurrowed,
]

unit_opcode_commands: list[CodeCommandDefinition] = shared_opcode_commands + [
	MustHaveAddon,
	IsNotConstructing,
	DoesNotHaveAddon,
	HasHangarSpace,
	DoesNotHaveNuke,
	IsResearched,
]

other_opcode_commands: list[CodeCommandDefinition] = shared_opcode_commands + [
	DoesNotHaveExit,
	IsLiftedOff,
	MustBeResearched,
	CanAttack,
	CanSetRallyPoint,
	CanMove,
	HasWeapon,
	IsWorker,
	IsFlyingBuilding,
	IsTransport,
	IsPowerup,
	IsSubunit,
	HasSpidermines,
	IsHeroAndEnabled,
	CanHoldPosition,
	AllowOnHallucinations,
	UpgradeLevel1,
	UpgradeLevel2,
	UpgradeLevel3,
]

all_opcode_commands: list[CodeCommandDefinition] = sorted(set(unit_opcode_commands + other_opcode_commands), key=lambda cmd_def: cmd_def.byte_code_id or 0)

unit_req_commands: list[CodeCommandDefinition] = unit_opcode_commands + [Has]
other_req_commands: list[CodeCommandDefinition] = other_opcode_commands + [Has, EndSublist]

# Every requirement command, including the ones a file's language doesn't have available
all_req_commands: list[CodeCommandDefinition] = all_opcode_commands + [Has, EndSublist]
