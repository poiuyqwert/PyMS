from __future__ import annotations

from . import CodeTypes
from .GraftCommandDefinitions import GraftCommandDefinition, ButtonConditionCommandDefinition, ButtonActionCommandDefinition, StatInfoCommandDefinition, number_functions
from ..Definitions import ParamKind, STATUS_FUNCTIONS, DISPLAY_FUNCTIONS

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeType import IntCodeType
from ....Utilities.CodeHandlers.CodeStruct import StructBlockDefinition, StructField
from ....Utilities import Struct

# Requirement opcodes (help text is the FireGraft name). units.dat requirements are parsed by a
# different function than the other requirements, so each has its own list of available opcodes.

Or = CodeCommandDefinition('or', 'Or', 0xFF01)
CurrentUnitIs = CodeCommandDefinition('current_unit_is', 'Current unit is {1}', 0xFF02, (CodeTypes.id_type(ParamKind.unit),))
MustHave = CodeCommandDefinition('must_have', 'Must have {1}', 0xFF03, (CodeTypes.id_type(ParamKind.unit),))
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
IsResearched = CodeCommandDefinition('is_researched', 'Is researched {1}', 0xFF25, (CodeTypes.id_type(ParamKind.tech),))
IsBurrowed = CodeCommandDefinition('is_burrowed', 'Is burrowed', 0xFF26)

# The next 0xFFFF after these opcodes ends their sub-list rather than the script
sublist_commands = (UpgradeLevel1, UpgradeLevel2)

# A requirement word below 0xFF00 checks that the player has the given unit
Has = CodeCommandDefinition('has', 'Must have {1}', None, (CodeTypes.unit_id_type(),))
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

# Buttons.graft commands

ButtonIcon = GraftCommandDefinition('icon', 'The button uses icon {1}', (CodeTypes.IconCodeType(),))
ButtonEnabledString = GraftCommandDefinition('enabled_str', 'The button uses string {1} when enabled', (CodeTypes.StringIDCodeType('enabled_string'),))
ButtonDisabledString = GraftCommandDefinition('disabled_str', 'The button uses string {1} when disabled', (CodeTypes.StringIDCodeType('disabled_string'),))

# Button conditions and actions, in the order of FireGraft and the hook's lookup tables in `grafting.cpp`
# (a button stores the index of its condition and action in these lists)
condition_commands: list[ButtonConditionCommandDefinition] = number_functions([
	ButtonConditionCommandDefinition(0x004DEB40, 'can_slow_down_replay', 'Slow Down Replay', ParamKind.none),
	ButtonConditionCommandDefinition(0x004DEAF0, 'can_speed_up_replay', 'Speed Up Replay', ParamKind.none),
	ButtonConditionCommandDefinition(0x004DEAC0, 'is_watching_replay', 'Play/Pause Replay', ParamKind.none),
	ButtonConditionCommandDefinition(0x004282D0, 'always', 'Always', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428E60, 'can_create', 'Can Create Unit/Building', ParamKind.unit),
	ButtonConditionCommandDefinition(0x00428E00, 'can_build_subunit', 'Can Build Subunit', ParamKind.unit),
	ButtonConditionCommandDefinition(0x00428DA0, 'can_move', 'Mixed Group - Move/Patrol/Hold Position', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428D40, 'can_stop', 'Mixed Group - Stop', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428F30, 'can_attack', 'Unit Has A Weapon', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428ED0, 'can_tower_attack', 'Attacking Building', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428530, 'is_training', 'Cancel Last', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428920, 'is_building_addon', 'Cancel AddOn', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428500, 'is_zerg_town_hall', 'Larva Exists(Upgrading Only)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00429520, 'can_rally', 'Rally Point', ParamKind.none),
	ButtonConditionCommandDefinition(0x00429740, 'can_zerg_town_hall_rally', 'Rally Point - While Upgrading Only', ParamKind.none),
	ButtonConditionCommandDefinition(0x004284E0, 'is_constructing_or_mutating', 'Construction/Mutation Underway', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428900, 'is_upgrading', 'Upgrade Underway', ParamKind.none),
	ButtonConditionCommandDefinition(0x004288E0, 'is_researching', 'Research Underway', ParamKind.none),
	ButtonConditionCommandDefinition(0x004284B0, 'can_harvest', 'Unit Is Carrying Nothing (Gather - Probe)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428480, 'can_return_harvest', 'Unit Is Carrying Something(Return Cargo - Probe)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428FF0, 'can_load', "Unit's Capacity Has Not Been Met", ParamKind.none),
	ButtonConditionCommandDefinition(0x00428EA0, 'can_unload', 'Carrying Some Units', ParamKind.none),
	ButtonConditionCommandDefinition(0x00429500, 'can_research', 'Tech Spell Not Researched', ParamKind.tech),
	ButtonConditionCommandDefinition(0x004294E0, 'can_player_use_tech', 'Spell Researched', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429470, 'can_units_use_tech', 'Has Spidermine and Is Researched', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429450, 'can_upgrade', 'Upgrade Not At Max Level', ParamKind.upgrade),
	ButtonConditionCommandDefinition(0x004293E0, 'can_cloak', 'Can Cloak', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429370, 'is_cloaked', 'Can Decloak', ParamKind.tech),
	ButtonConditionCommandDefinition(0x004292C0, 'can_cloak_mixed', 'Can Cloak - Mixed', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429210, 'is_cloaked_mixed', 'Can Decloak - Mixed', ParamKind.tech),
	ButtonConditionCommandDefinition(0x004291C0, 'can_siege', 'Tank Is In Tank Mode', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429170, 'can_unsiege', 'Tank Is In Siege Mode', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00428860, 'is_not_sieged', 'Tank Is In Tank Mode(Move)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428810, 'is_player_nuke_ready', 'Nuke Available', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428440, 'is_not_disabled', 'Recharge Shields', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428420, 'is_lifted_off', 'Building Can Move And Has Lifted Off', ParamKind.none),
	ButtonConditionCommandDefinition(0x004283F0, 'can_land', 'Building Has Lifted Off', ParamKind.none),
	ButtonConditionCommandDefinition(0x004287D0, 'can_lift_off', 'Building Has Landed', ParamKind.none),
	ButtonConditionCommandDefinition(0x004290F0, 'can_burrow', 'Ability Is Researched', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429070, 'can_unburrow', 'Is Using Ability', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429720, 'can_morph_lurker', 'Morph To Lurker', ParamKind.unit),
	ButtonConditionCommandDefinition(0x004283C0, 'is_not_burrowed', 'Not Burrowed(Move/Stop/Patrol/Hold Position)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428FA0, 'can_attack_and_unburrowed', 'Not Burrowed (Attack)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428780, 'can_harvest_and_unburrowed', 'Has No Cargo (Gather - Drone)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428730, 'can_return_harvest_and_unburrowed', 'Has Cargo (Return Cargo - Drone)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428360, 'has_same_burrow_state', 'Burrowed (Stop - Lurker)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428340, 'has_no_exit', 'Has No Exit', ParamKind.unit),
	ButtonConditionCommandDefinition(0x00428CB0, 'can_build_zerg_basic', 'Zerg Basic Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428C30, 'can_build_zerg_advanced', 'Zerg Advanced Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x004286E0, 'has_interceptors', 'Has Interceptors', ParamKind.none),
	ButtonConditionCommandDefinition(0x004286A0, 'has_scarabs', 'Has Scarabs', ParamKind.none),
	ButtonConditionCommandDefinition(0x004296F0, 'is_archon_unresearched', '2 Units Selected & Not Researched(Archon Merge)', ParamKind.tech),
	ButtonConditionCommandDefinition(0x004296B0, 'can_archon_warp', '2 Units Selected (Archon Warp)', ParamKind.unit),
	ButtonConditionCommandDefinition(0x00429680, 'is_dark_archon_unresearched', '2 Units Selected & Not Researched(Dark Archon Meld)', ParamKind.tech),
	ButtonConditionCommandDefinition(0x00429640, 'can_dark_archon_meld', '2 Units Selected (Dark Archon Meld)', ParamKind.unit),
	ButtonConditionCommandDefinition(0x00428B80, 'can_build_protoss_basic', 'Protoss Basic Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428AD0, 'can_build_protoss_advanced', 'Protoss Advanced Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428310, 'is_constructing', 'Is Constructing (Halt - SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428670, 'is_not_constructing_move', 'Move (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428640, 'is_not_constructing_stop', 'Stop (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428610, 'is_not_constructing_attack', 'Attack (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x004285E0, 'is_not_constructing_repair', 'Repair (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x004285A0, 'can_harvest_and_not_constructing', 'Gather (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428560, 'can_return_harvest_and_not_constructing', 'Return Cargo (SCV)', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428A10, 'can_build_terran_basic', 'Terran Basic Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428990, 'can_build_terran_advanced', 'Terran Advanced Buildings', ParamKind.none),
	ButtonConditionCommandDefinition(0x00428960, 'can_create_single', 'Nuke Train', ParamKind.unit),
])

action_commands: list[ButtonActionCommandDefinition] = number_functions([
	ButtonActionCommandDefinition(0x00423180, 'cancel_infestation', 'Cancel Infestation', ParamKind.none),
	ButtonActionCommandDefinition(0x004244A0, 'rally', 'Rally Point', ParamKind.none),
	ButtonActionCommandDefinition(0x00423930, 'select_larva', 'Select Larva', ParamKind.none),
	ButtonActionCommandDefinition(0x004234B0, 'train', 'Create Unit', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423490, 'cancel_train', 'Cancel Last', ParamKind.none),
	ButtonActionCommandDefinition(0x00423470, 'unsiege', 'Tank Mode', ParamKind.none),
	ButtonActionCommandDefinition(0x00423450, 'siege', 'Siege Mode', ParamKind.tech),
	ButtonActionCommandDefinition(0x00423430, 'cancel_construction', 'Cancel Construction', ParamKind.none),
	ButtonActionCommandDefinition(0x00423410, 'cancel_morph', 'Cancel Morph', ParamKind.none),
	ButtonActionCommandDefinition(0x00424440, 'move', 'Move', ParamKind.none),
	ButtonActionCommandDefinition(0x004233F0, 'stop', 'Stop', ParamKind.none),
	ButtonActionCommandDefinition(0x00424380, 'attack', 'Attack', ParamKind.none),
	ButtonActionCommandDefinition(0x00424320, 'attack_unit', 'Attack(Suicide)', ParamKind.none),
	ButtonActionCommandDefinition(0x004242C0, 'attack_tower', 'Attack(Building)', ParamKind.none),
	ButtonActionCommandDefinition(0x00424260, 'move_carrier_reaver', 'Move (Carrier/Reaver)', ParamKind.none),
	ButtonActionCommandDefinition(0x004233D0, 'stop_carrier', 'Stop Carrier', ParamKind.none),
	ButtonActionCommandDefinition(0x004233B0, 'stop_reaver', 'Stop Reaver', ParamKind.none),
	ButtonActionCommandDefinition(0x00424200, 'attack_carrier', 'Attack Carrier', ParamKind.none),
	ButtonActionCommandDefinition(0x004241A0, 'attack_reaver', 'Attack Reaver', ParamKind.none),
	ButtonActionCommandDefinition(0x00423390, 'build_subunit', 'Build Subunit', ParamKind.unit),
	ButtonActionCommandDefinition(0x00424140, 'patrol', 'Patrol', ParamKind.none),
	ButtonActionCommandDefinition(0x00423370, 'hold_position', 'Hold Position', ParamKind.none),
	ButtonActionCommandDefinition(0x00423350, 'research', 'Research Technology', ParamKind.tech),
	ButtonActionCommandDefinition(0x00423330, 'cancel_research', 'Cancel Technology Research', ParamKind.none),
	ButtonActionCommandDefinition(0x00423F70, 'use_tech', 'Use Technology', ParamKind.tech),
	ButtonActionCommandDefinition(0x004234D0, 'stim', 'StimPack', ParamKind.tech),
	ButtonActionCommandDefinition(0x00423310, 'upgrade', 'Research Upgrade', ParamKind.upgrade),
	ButtonActionCommandDefinition(0x004232F0, 'cancel_upgrade', 'Cancel Upgrade Research', ParamKind.none),
	ButtonActionCommandDefinition(0x004232D0, 'cancel_addon', 'Cancel AddOn', ParamKind.none),
	ButtonActionCommandDefinition(0x00423EB0, 'build_terran', 'Create Building - Terran', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423E90, 'place_cop', 'Place COP', ParamKind.none),
	ButtonActionCommandDefinition(0x00423DD0, 'build_protoss', 'Create Building - Protoss', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423D10, 'build_addon', 'Create AddOn', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423C50, 'build_zerg', 'Create Building - Zerg', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423C40, 'place_nydus_exit', 'Place Nydus Canal Exit', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423860, 'morph_building', 'Building Morph', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423C30, 'land', 'Land', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423BD0, 'repair', 'Repair', ParamKind.none),
	ButtonActionCommandDefinition(0x00423790, 'morph', 'Unit Morph', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423B70, 'harvest', 'Gather', ParamKind.none),
	ButtonActionCommandDefinition(0x00423760, 'return_harvest', 'Return Cargo', ParamKind.none),
	ButtonActionCommandDefinition(0x004232B0, 'burrow', 'Burrow', ParamKind.tech),
	ButtonActionCommandDefinition(0x00423290, 'unburrow', 'Unburrow', ParamKind.none),
	ButtonActionCommandDefinition(0x00423730, 'cloak', 'Cloak', ParamKind.tech),
	ButtonActionCommandDefinition(0x00423270, 'decloak', 'Decloak', ParamKind.none),
	ButtonActionCommandDefinition(0x00423230, 'lift_off', 'Lift Off', ParamKind.none),
	ButtonActionCommandDefinition(0x00423B40, 'load', 'Load', ParamKind.none),
	ButtonActionCommandDefinition(0x00423B00, 'unload', 'Unload', ParamKind.none),
	ButtonActionCommandDefinition(0x00423210, 'archon_warp', 'Archon Warp', ParamKind.unit),
	ButtonActionCommandDefinition(0x004231F0, 'dark_archon_meld', 'Dark Archon Meld', ParamKind.unit),
	ButtonActionCommandDefinition(0x00423AA0, 'recharge_shields', 'Recharge Shields', ParamKind.none),
	ButtonActionCommandDefinition(0x00423A40, 'nuke', 'Nuclear Strike', ParamKind.none),
	ButtonActionCommandDefinition(0x004231D0, 'cancel_nuke', 'Cancel Nuclear Strike', ParamKind.none),
	ButtonActionCommandDefinition(0x004239E0, 'heal', 'Heal', ParamKind.tech),
	ButtonActionCommandDefinition(0x004DF300, 'slow_down_replay', 'Slow Down Replay', ParamKind.none),
	ButtonActionCommandDefinition(0x004DF2C0, 'play_pause_replay', 'Play/Pause Replay', ParamKind.none),
	ButtonActionCommandDefinition(0x004DF260, 'speed_up_replay', 'Speed Up Replay', ParamKind.none),
	ButtonActionCommandDefinition(0x00429770, 'cancel_targeting', 'Cancel', ParamKind.none),
	ButtonActionCommandDefinition(0x00429780, 'cancel_placement', 'Cancel Place Building', ParamKind.none),
	ButtonActionCommandDefinition(0x00459AF0, 'show_button_set', 'Change Displayed Buttons', ParamKind.unit),
])

# Conditions and actions that aren't in `condition_commands`/`action_commands`, by their index
RawCondition = GraftCommandDefinition('condition', 'The button is enabled by the condition at index {1} (with parameter {2})', (
	IntCodeType('condition', 'A button condition index', Struct.l_u32),
	IntCodeType('condition_param', "The condition's parameter", Struct.l_u16, allow_hex=True),
))
RawAction = GraftCommandDefinition('action', 'The button runs the action at index {1} (with parameter {2})', (
	IntCodeType('action', 'A button action index', Struct.l_u32),
	IntCodeType('action_param', "The action's parameter", Struct.l_u16, allow_hex=True),
))

button_commands: list[CodeCommandDefinition] = [ButtonIcon, *condition_commands, RawCondition, *action_commands, RawAction, ButtonEnabledString, ButtonDisabledString]

UnitButtonSet = GraftCommandDefinition('button_set', 'The unit uses button set {1}', (CodeTypes.OptionalCodeType(CodeTypes.ButtonSetCodeType()),))
UnitConnectedUnit = GraftCommandDefinition('connected_unit', 'The unit is connected to {1}', (CodeTypes.ConnectedUnitCodeType(),))
UnitStatInfo = StatInfoCommandDefinition('stat_info', 'The unit uses status function {1} and display function {2} (with the unused unit ID {3}, which defaults to the unit ID)', (
	CodeTypes.FunctionCodeType('status_function', 'A unit status function', STATUS_FUNCTIONS),
	CodeTypes.FunctionCodeType('display_function', 'A unit display function', DISPLAY_FUNCTIONS),
	IntCodeType('debug_unit_id', 'An unused unit ID', Struct.l_u32),
), required_params=2, parens=True)
UnitPadding = GraftCommandDefinition('padding', 'The unused value {1} after the unit\'s connected unit', (IntCodeType('padding', 'Unused value', Struct.l_u16, allow_hex=True),))

unit_commands: list[CodeCommandDefinition] = [UnitButtonSet, UnitConnectedUnit, UnitStatInfo, UnitPadding]
buttons_commands: list[CodeCommandDefinition] = button_commands + unit_commands

# Buttons.graft struct blocks

ButtonConditionField = StructField('condition', (*condition_commands, RawCondition))
ButtonActionField = StructField('action', (*action_commands, RawAction))

ButtonBlock = StructBlockDefinition('button', 'button', 'Button {0}', (CodeTypes.ButtonPositionCodeType(),), fields=(
	StructField(ButtonIcon.name, (ButtonIcon,)),
	ButtonConditionField,
	ButtonActionField,
	StructField(ButtonEnabledString.name, (ButtonEnabledString,)),
	StructField(ButtonDisabledString.name, (ButtonDisabledString,)),
))
ButtonSetBlock = StructBlockDefinition('button_set', 'button set', 'Button set {0}', (CodeTypes.ButtonSetCodeType(),), children=(ButtonBlock,))
UnitBlock = StructBlockDefinition('unit', 'unit', 'Unit {0}', (CodeTypes.UnitHeaderCodeType(),), fields=tuple(StructField(cmd_def.name, (cmd_def,), required=False) for cmd_def in unit_commands))
