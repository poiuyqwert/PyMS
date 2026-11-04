from __future__ import annotations

from . import CodeTypes
from .GraftCommandDefinitions import GraftCommandDefinition, ButtonConditionCommandDefinition, ButtonActionCommandDefinition, number_functions

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeStruct import StructBlockDefinition, StructField

# Buttons.graft commands

Icon = GraftCommandDefinition('icon', 'The button uses icon {1}', (CodeTypes.IconCodeType(),))
EnabledStr = GraftCommandDefinition('enabled_str', 'The button uses string {1} when enabled', (CodeTypes.StringIDCodeType(),))
DisabledStr = GraftCommandDefinition('disabled_str', 'The button uses string {1} when disabled', (CodeTypes.StringIDCodeType(),))

# Button conditions and actions

CanSlowDownReplay = ButtonConditionCommandDefinition('can_slow_down_replay', 'Slow Down Replay')
CanSpeedUpReplay = ButtonConditionCommandDefinition('can_speed_up_replay', 'Speed Up Replay')
IsWatchingReplay = ButtonConditionCommandDefinition('is_watching_replay', 'Play/Pause Replay')
Always = ButtonConditionCommandDefinition('always', 'Always')
CanCreate = ButtonConditionCommandDefinition('can_create', 'Can Create Unit/Building', CodeTypes.UnitCodeType())
CanBuildSubunit = ButtonConditionCommandDefinition('can_build_subunit', 'Can Build Subunit', CodeTypes.UnitCodeType())
CanMove = ButtonConditionCommandDefinition('can_move', 'Mixed Group - Move/Patrol/Hold Position')
CanStop = ButtonConditionCommandDefinition('can_stop', 'Mixed Group - Stop')
CanAttack = ButtonConditionCommandDefinition('can_attack', 'Unit Has A Weapon')
CanTowerAttack = ButtonConditionCommandDefinition('can_tower_attack', 'Attacking Building')
IsTraining = ButtonConditionCommandDefinition('is_training', 'Cancel Last')
IsBuildingAddon = ButtonConditionCommandDefinition('is_building_addon', 'Cancel AddOn')
IsZergTownHall = ButtonConditionCommandDefinition('is_zerg_town_hall', 'Larva Exists(Upgrading Only)')
CanRally = ButtonConditionCommandDefinition('can_rally', 'Rally Point')
CanZergTownHallRally = ButtonConditionCommandDefinition('can_zerg_town_hall_rally', 'Rally Point - While Upgrading Only')
IsConstructingOrMutating = ButtonConditionCommandDefinition('is_constructing_or_mutating', 'Construction/Mutation Underway')
IsUpgrading = ButtonConditionCommandDefinition('is_upgrading', 'Upgrade Underway')
IsResearching = ButtonConditionCommandDefinition('is_researching', 'Research Underway')
CanHarvest = ButtonConditionCommandDefinition('can_harvest', 'Unit Is Carrying Nothing (Gather - Probe)')
CanReturnHarvest = ButtonConditionCommandDefinition('can_return_harvest', 'Unit Is Carrying Something(Return Cargo - Probe)')
CanLoad = ButtonConditionCommandDefinition('can_load', "Unit's Capacity Has Not Been Met")
CanUnload = ButtonConditionCommandDefinition('can_unload', 'Carrying Some Units')
CanResearch = ButtonConditionCommandDefinition('can_research', 'Tech Spell Not Researched', CodeTypes.TechCodeType())
CanPlayerUseTech = ButtonConditionCommandDefinition('can_player_use_tech', 'Spell Researched', CodeTypes.TechCodeType())
CanUnitsUseTech = ButtonConditionCommandDefinition('can_units_use_tech', 'Has Spidermine and Is Researched', CodeTypes.TechCodeType())
CanUpgrade = ButtonConditionCommandDefinition('can_upgrade', 'Upgrade Not At Max Level', CodeTypes.UpgradeCodeType())
CanCloak = ButtonConditionCommandDefinition('can_cloak', 'Can Cloak', CodeTypes.TechCodeType())
IsCloaked = ButtonConditionCommandDefinition('is_cloaked', 'Can Decloak', CodeTypes.TechCodeType())
CanCloakMixed = ButtonConditionCommandDefinition('can_cloak_mixed', 'Can Cloak - Mixed')
IsCloakedMixed = ButtonConditionCommandDefinition('is_cloaked_mixed', 'Can Decloak - Mixed')
CanSiege = ButtonConditionCommandDefinition('can_siege', 'Tank Is In Tank Mode', CodeTypes.TechCodeType())
CanUnsiege = ButtonConditionCommandDefinition('can_unsiege', 'Tank Is In Siege Mode', CodeTypes.TechCodeType())
IsNotSieged = ButtonConditionCommandDefinition('is_not_sieged', 'Tank Is In Tank Mode(Move)')
IsPlayerNukeReady = ButtonConditionCommandDefinition('is_player_nuke_ready', 'Nuke Available')
IsNotDisabled = ButtonConditionCommandDefinition('is_not_disabled', 'Recharge Shields')
IsLiftedOff = ButtonConditionCommandDefinition('is_lifted_off', 'Building Can Move And Has Lifted Off')
CanLand = ButtonConditionCommandDefinition('can_land', 'Building Has Lifted Off')
CanLiftOff = ButtonConditionCommandDefinition('can_lift_off', 'Building Has Landed')
CanBurrow = ButtonConditionCommandDefinition('can_burrow', 'Ability Is Researched', CodeTypes.TechCodeType())
CanUnburrow = ButtonConditionCommandDefinition('can_unburrow', 'Is Using Ability', CodeTypes.TechCodeType())
CanMorphLurker = ButtonConditionCommandDefinition('can_morph_lurker', 'Morph To Lurker')
IsNotBurrowed = ButtonConditionCommandDefinition('is_not_burrowed', 'Not Burrowed(Move/Stop/Patrol/Hold Position)')
CanAttackAndUnburrowed = ButtonConditionCommandDefinition('can_attack_and_unburrowed', 'Not Burrowed (Attack)')
CanHarvestAndUnburrowed = ButtonConditionCommandDefinition('can_harvest_and_unburrowed', 'Has No Cargo (Gather - Drone)')
CanReturnHarvestAndUnburrowed = ButtonConditionCommandDefinition('can_return_harvest_and_unburrowed', 'Has Cargo (Return Cargo - Drone)')
HasSameBurrowState = ButtonConditionCommandDefinition('has_same_burrow_state', 'Burrowed (Stop - Lurker)')
HasNoExit = ButtonConditionCommandDefinition('has_no_exit', 'Has No Exit')
CanBuildZergBasic = ButtonConditionCommandDefinition('can_build_zerg_basic', 'Zerg Basic Buildings')
CanBuildZergAdvanced = ButtonConditionCommandDefinition('can_build_zerg_advanced', 'Zerg Advanced Buildings')
HasInterceptors = ButtonConditionCommandDefinition('has_interceptors', 'Has Interceptors')
HasScarabs = ButtonConditionCommandDefinition('has_scarabs', 'Has Scarabs')
IsArchonUnresearched = ButtonConditionCommandDefinition('is_archon_unresearched', '2 Units Selected & Not Researched(Archon Merge)', CodeTypes.TechCodeType())
CanArchonWarp = ButtonConditionCommandDefinition('can_archon_warp', '2 Units Selected (Archon Warp)')
IsDarkArchonUnresearched = ButtonConditionCommandDefinition('is_dark_archon_unresearched', '2 Units Selected & Not Researched(Dark Archon Meld)', CodeTypes.TechCodeType())
CanDarkArchonMeld = ButtonConditionCommandDefinition('can_dark_archon_meld', '2 Units Selected (Dark Archon Meld)')
CanBuildProtossBasic = ButtonConditionCommandDefinition('can_build_protoss_basic', 'Protoss Basic Buildings')
CanBuildProtossAdvanced = ButtonConditionCommandDefinition('can_build_protoss_advanced', 'Protoss Advanced Buildings')
IsConstructing = ButtonConditionCommandDefinition('is_constructing', 'Is Constructing (Halt - SCV)')
IsNotConstructingMove = ButtonConditionCommandDefinition('is_not_constructing_move', 'Move (SCV)')
IsNotConstructingStop = ButtonConditionCommandDefinition('is_not_constructing_stop', 'Stop (SCV)')
IsNotConstructingAttack = ButtonConditionCommandDefinition('is_not_constructing_attack', 'Attack (SCV)')
IsNotConstructingRepair = ButtonConditionCommandDefinition('is_not_constructing_repair', 'Repair (SCV)')
CanHarvestAndNotConstructing = ButtonConditionCommandDefinition('can_harvest_and_not_constructing', 'Gather (SCV)')
CanReturnHarvestAndNotConstructing = ButtonConditionCommandDefinition('can_return_harvest_and_not_constructing', 'Return Cargo (SCV)')
CanBuildTerranBasic = ButtonConditionCommandDefinition('can_build_terran_basic', 'Terran Basic Buildings')
CanBuildTerranAdvanced = ButtonConditionCommandDefinition('can_build_terran_advanced', 'Terran Advanced Buildings')
CanCreateSingle = ButtonConditionCommandDefinition('can_create_single', 'Nuke Train', CodeTypes.UnitCodeType())

CancelInfestation = ButtonActionCommandDefinition('cancel_infestation', 'Cancel Infestation')
Rally = ButtonActionCommandDefinition('rally', 'Rally Point')
SelectLarva = ButtonActionCommandDefinition('select_larva', 'Select Larva')
Train = ButtonActionCommandDefinition('train', 'Create Unit', CodeTypes.UnitCodeType())
CancelTrain = ButtonActionCommandDefinition('cancel_train', 'Cancel Last', CodeTypes.QueueSlotCodeType())
Unsiege = ButtonActionCommandDefinition('unsiege', 'Tank Mode')
Siege = ButtonActionCommandDefinition('siege', 'Siege Mode', CodeTypes.TechCodeType())
CancelConstruction = ButtonActionCommandDefinition('cancel_construction', 'Cancel Construction')
CancelMorph = ButtonActionCommandDefinition('cancel_morph', 'Cancel Morph')
Move = ButtonActionCommandDefinition('move', 'Move')
Stop = ButtonActionCommandDefinition('stop', 'Stop')
Attack = ButtonActionCommandDefinition('attack', 'Attack')
AttackUnit = ButtonActionCommandDefinition('attack_unit', 'Attack(Suicide)')
AttackTower = ButtonActionCommandDefinition('attack_tower', 'Attack(Building)')
MoveCarrierReaver = ButtonActionCommandDefinition('move_carrier_reaver', 'Move (Carrier/Reaver)')
StopCarrier = ButtonActionCommandDefinition('stop_carrier', 'Stop Carrier')
StopReaver = ButtonActionCommandDefinition('stop_reaver', 'Stop Reaver')
AttackCarrier = ButtonActionCommandDefinition('attack_carrier', 'Attack Carrier')
AttackReaver = ButtonActionCommandDefinition('attack_reaver', 'Attack Reaver')
BuildSubunit = ButtonActionCommandDefinition('build_subunit', 'Build Subunit', CodeTypes.UnitCodeType())
Patrol = ButtonActionCommandDefinition('patrol', 'Patrol')
HoldPosition = ButtonActionCommandDefinition('hold_position', 'Hold Position')
Research = ButtonActionCommandDefinition('research', 'Research Technology', CodeTypes.TechCodeType())
CancelResearch = ButtonActionCommandDefinition('cancel_research', 'Cancel Technology Research')
UseTech = ButtonActionCommandDefinition('use_tech', 'Use Technology', CodeTypes.TechCodeType())
Stim = ButtonActionCommandDefinition('stim', 'StimPack', CodeTypes.TechCodeType())
Upgrade = ButtonActionCommandDefinition('upgrade', 'Research Upgrade', CodeTypes.UpgradeCodeType())
CancelUpgrade = ButtonActionCommandDefinition('cancel_upgrade', 'Cancel Upgrade Research')
CancelAddon = ButtonActionCommandDefinition('cancel_addon', 'Cancel AddOn')
BuildTerran = ButtonActionCommandDefinition('build_terran', 'Create Building - Terran', CodeTypes.UnitCodeType())
PlaceCop = ButtonActionCommandDefinition('place_cop', 'Place COP')
BuildProtoss = ButtonActionCommandDefinition('build_protoss', 'Create Building - Protoss', CodeTypes.UnitCodeType())
BuildAddon = ButtonActionCommandDefinition('build_addon', 'Create AddOn', CodeTypes.UnitCodeType())
BuildZerg = ButtonActionCommandDefinition('build_zerg', 'Create Building - Zerg', CodeTypes.UnitCodeType())
PlaceNydusExit = ButtonActionCommandDefinition('place_nydus_exit', 'Place Nydus Canal Exit', CodeTypes.UnitCodeType())
MorphBuilding = ButtonActionCommandDefinition('morph_building', 'Building Morph', CodeTypes.UnitCodeType())
Land = ButtonActionCommandDefinition('land', 'Land', CodeTypes.UnitCodeType())
Repair = ButtonActionCommandDefinition('repair', 'Repair')
Morph = ButtonActionCommandDefinition('morph', 'Unit Morph', CodeTypes.UnitCodeType())
Harvest = ButtonActionCommandDefinition('harvest', 'Gather')
ReturnHarvest = ButtonActionCommandDefinition('return_harvest', 'Return Cargo')
Burrow = ButtonActionCommandDefinition('burrow', 'Burrow', CodeTypes.TechCodeType())
Unburrow = ButtonActionCommandDefinition('unburrow', 'Unburrow')
Cloak = ButtonActionCommandDefinition('cloak', 'Cloak', CodeTypes.TechCodeType())
Decloak = ButtonActionCommandDefinition('decloak', 'Decloak')
LiftOff = ButtonActionCommandDefinition('lift_off', 'Lift Off')
Load = ButtonActionCommandDefinition('load', 'Load')
Unload = ButtonActionCommandDefinition('unload', 'Unload')
ArchonWarp = ButtonActionCommandDefinition('archon_warp', 'Archon Warp', CodeTypes.UnitCodeType())
DarkArchonMeld = ButtonActionCommandDefinition('dark_archon_meld', 'Dark Archon Meld', CodeTypes.UnitCodeType())
RechargeShields = ButtonActionCommandDefinition('recharge_shields', 'Recharge Shields')
Nuke = ButtonActionCommandDefinition('nuke', 'Nuclear Strike')
CancelNuke = ButtonActionCommandDefinition('cancel_nuke', 'Cancel Nuclear Strike')
Heal = ButtonActionCommandDefinition('heal', 'Heal', CodeTypes.TechCodeType())
SlowDownReplay = ButtonActionCommandDefinition('slow_down_replay', 'Slow Down Replay')
PlayPauseReplay = ButtonActionCommandDefinition('play_pause_replay', 'Play/Pause Replay')
SpeedUpReplay = ButtonActionCommandDefinition('speed_up_replay', 'Speed Up Replay')
CancelTargeting = ButtonActionCommandDefinition('cancel_targeting', 'Cancel')
CancelPlacement = ButtonActionCommandDefinition('cancel_placement', 'Cancel Place Building')
ShowButtonSet = ButtonActionCommandDefinition('show_button_set', 'Change Displayed Buttons', CodeTypes.ButtonCardCodeType())

# In the order of FireGraft and the hook's lookup tables in `grafting.cpp` (a button stores the index of its condition and action in these lists)
condition_commands: list[ButtonConditionCommandDefinition] = number_functions([
	CanSlowDownReplay,
	CanSpeedUpReplay,
	IsWatchingReplay,
	Always,
	CanCreate,
	CanBuildSubunit,
	CanMove,
	CanStop,
	CanAttack,
	CanTowerAttack,
	IsTraining,
	IsBuildingAddon,
	IsZergTownHall,
	CanRally,
	CanZergTownHallRally,
	IsConstructingOrMutating,
	IsUpgrading,
	IsResearching,
	CanHarvest,
	CanReturnHarvest,
	CanLoad,
	CanUnload,
	CanResearch,
	CanPlayerUseTech,
	CanUnitsUseTech,
	CanUpgrade,
	CanCloak,
	IsCloaked,
	CanCloakMixed,
	IsCloakedMixed,
	CanSiege,
	CanUnsiege,
	IsNotSieged,
	IsPlayerNukeReady,
	IsNotDisabled,
	IsLiftedOff,
	CanLand,
	CanLiftOff,
	CanBurrow,
	CanUnburrow,
	CanMorphLurker,
	IsNotBurrowed,
	CanAttackAndUnburrowed,
	CanHarvestAndUnburrowed,
	CanReturnHarvestAndUnburrowed,
	HasSameBurrowState,
	HasNoExit,
	CanBuildZergBasic,
	CanBuildZergAdvanced,
	HasInterceptors,
	HasScarabs,
	IsArchonUnresearched,
	CanArchonWarp,
	IsDarkArchonUnresearched,
	CanDarkArchonMeld,
	CanBuildProtossBasic,
	CanBuildProtossAdvanced,
	IsConstructing,
	IsNotConstructingMove,
	IsNotConstructingStop,
	IsNotConstructingAttack,
	IsNotConstructingRepair,
	CanHarvestAndNotConstructing,
	CanReturnHarvestAndNotConstructing,
	CanBuildTerranBasic,
	CanBuildTerranAdvanced,
	CanCreateSingle,
])

action_commands: list[ButtonActionCommandDefinition] = number_functions([
	CancelInfestation,
	Rally,
	SelectLarva,
	Train,
	CancelTrain,
	Unsiege,
	Siege,
	CancelConstruction,
	CancelMorph,
	Move,
	Stop,
	Attack,
	AttackUnit,
	AttackTower,
	MoveCarrierReaver,
	StopCarrier,
	StopReaver,
	AttackCarrier,
	AttackReaver,
	BuildSubunit,
	Patrol,
	HoldPosition,
	Research,
	CancelResearch,
	UseTech,
	Stim,
	Upgrade,
	CancelUpgrade,
	CancelAddon,
	BuildTerran,
	PlaceCop,
	BuildProtoss,
	BuildAddon,
	BuildZerg,
	PlaceNydusExit,
	MorphBuilding,
	Land,
	Repair,
	Morph,
	Harvest,
	ReturnHarvest,
	Burrow,
	Unburrow,
	Cloak,
	Decloak,
	LiftOff,
	Load,
	Unload,
	ArchonWarp,
	DarkArchonMeld,
	RechargeShields,
	Nuke,
	CancelNuke,
	Heal,
	SlowDownReplay,
	PlayPauseReplay,
	SpeedUpReplay,
	CancelTargeting,
	CancelPlacement,
	ShowButtonSet,
])

button_commands: list[CodeCommandDefinition] = [Icon, *condition_commands, *action_commands, EnabledStr, DisabledStr]

UseButtonSet = GraftCommandDefinition('use_button_set', 'The button card uses button set {1}', (CodeTypes.UnitButtonSetCodeType(),))
ConnectedUnit = GraftCommandDefinition('connected_unit', 'The button card is connected to {1}', (CodeTypes.ConnectedUnitCodeType(),))

button_card_commands: list[CodeCommandDefinition] = [UseButtonSet, ConnectedUnit]

# Buttons.graft struct blocks

ButtonConditionField = StructField('condition', tuple(condition_commands))
ButtonActionField = StructField('action', tuple(action_commands))

ButtonBlock = StructBlockDefinition('button', 'button', 'Button {0}', (CodeTypes.ButtonPositionCodeType(),), fields=(
	StructField(Icon.name, (Icon,)),
	ButtonConditionField,
	ButtonActionField,
	StructField(EnabledStr.name, (EnabledStr,)),
	StructField(DisabledStr.name, (DisabledStr,)),
))
ButtonSetBlock = StructBlockDefinition('button_set', 'button set', 'Button set {0}', (CodeTypes.ButtonSetCodeType(),), children=(ButtonBlock,))
ButtonCardBlock = StructBlockDefinition('button_card', 'button card', 'Button card {0}', (CodeTypes.ButtonCardIDCodeType(),), fields=tuple(StructField(cmd_def.name, (cmd_def,), required=False) for cmd_def in button_card_commands))
