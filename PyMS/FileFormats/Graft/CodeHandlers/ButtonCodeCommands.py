from __future__ import annotations

from . import CodeTypes
from .GraftCommandDefinition import GraftCommandDefinition, number_functions

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeStruct import StructBlockDefinition, StructField

# Buttons.graft commands

Icon = CodeCommandDefinition('icon', 'The button uses icon {1}', None, (CodeTypes.IconCodeType(),))
EnabledStr = CodeCommandDefinition('enabled_str', 'The button uses string {1} when enabled', None, (CodeTypes.StringIDCodeType(),))
DisabledStr = CodeCommandDefinition('disabled_str', 'The button uses string {1} when disabled', None, (CodeTypes.StringIDCodeType(),))

# Button conditions and actions

CanSlowDownReplay = GraftCommandDefinition('can_slow_down_replay', 'Slow Down Replay', 'Shown when watching a replay as the host. Greyed while paused or at the slowest speed.')
CanSpeedUpReplay = GraftCommandDefinition('can_speed_up_replay', 'Speed Up Replay', 'Shown when watching a replay as the host. Greyed while paused or at the fastest speed.')
IsWatchingReplay = GraftCommandDefinition('is_watching_replay', 'Play/Pause Replay', 'Shown when watching a replay as the host.')
Always = GraftCommandDefinition('always', 'Always', 'Always shown.')
CanCreateOrMorph = GraftCommandDefinition('can_create_or_morph', 'Can Create/Morph Unit/Building', 'Uses the requirements of {1} when one unit is selected (or a Larva, Hydralisk or Mutalisk). Otherwise hidden.', CodeTypes.UnitCodeType())
CanBuildSubunit = GraftCommandDefinition('can_build_subunit', 'Can Build Subunit', 'Uses the requirements of {1} when every selected unit is the same type. Otherwise hidden.', CodeTypes.UnitCodeType())
CanMove = GraftCommandDefinition('can_move', 'Mixed Group - Move/Patrol/Hold Position', 'Shown if any selected unit can move.')
CanStop = GraftCommandDefinition('can_stop', 'Mixed Group - Stop', 'Shown if any selected unit can move or is a tower.')
CanAttack = GraftCommandDefinition('can_attack', 'Unit Has A Weapon', 'Shown if any selected unit can move and attack.')
CanAttackInPlace = GraftCommandDefinition('can_attack_in_place', 'Can Attack In Place', "Shown if any selected unit can attack and isn't disabled (no movement needed).")
IsTraining = GraftCommandDefinition('is_training', 'Cancel Last', 'Shown if the unit has something in its training queue.')
IsConstructingAddon = GraftCommandDefinition('is_constructing_addon', 'Cancel AddOn', 'Shown if the unit is building an add-on.')
IsZergTownHall = GraftCommandDefinition('is_zerg_town_hall', 'Larva Exists(Upgrading Only)', 'Shown if the unit is a Hatchery, Lair or Hive.')
CanSetRallyPoint = GraftCommandDefinition('can_set_rally_point', 'Rally Point', 'Uses the requirements of the rally point order.')
CanZergTownHallSetRallyPoint = GraftCommandDefinition('can_zerg_town_hall_set_rally_point', 'Rally Point - While Upgrading Only', 'Uses the requirements of the rally point order if the unit is a Hatchery, Lair or Hive. Otherwise hidden.')
IsConstructingOrMutating = GraftCommandDefinition('is_constructing_or_mutating', 'Construction/Mutation Underway', 'Shown if the unit is under construction or mutating.')
IsResearchingUpgrade = GraftCommandDefinition('is_researching_upgrade', 'Upgrade Research Underway', 'Shown if the unit is researching an upgrade.')
IsResearchingTech = GraftCommandDefinition('is_researching_tech', 'Tech Research Underway', 'Shown if the unit is researching a technology.')
IsNotCarryingHarvest = GraftCommandDefinition('is_not_carrying_harvest', 'Not Carrying Minerals/Gas', "Shown if any selected unit isn't carrying minerals or gas.")
IsCarryingHarvest = GraftCommandDefinition('is_carrying_harvest', 'Carrying Minerals/Gas', 'Shown if any selected unit is carrying minerals or gas.')
CanLoad = GraftCommandDefinition('can_load', "Unit's Capacity Has Not Been Met", "Shown if any selected unit is a transport with free space. Hidden if any selected unit isn't a transport.")
CanUnload = GraftCommandDefinition('can_unload', 'Carrying Some Units', 'Shown if any selected unit is carrying units.')
CanResearchTech = GraftCommandDefinition('can_research_tech', 'Can Research Tech', 'Uses the research requirements of {1}.', CodeTypes.TechCodeType())
CanPlayerUseTech = GraftCommandDefinition('can_player_use_tech', 'Spell Researched', 'Uses the use requirements of {1}.', CodeTypes.TechCodeType())
CanUnitsUseTech = GraftCommandDefinition('can_units_use_tech', 'Has Spidermine and Is Researched', 'Shown if any selected unit meets the use requirements of {1}.', CodeTypes.TechCodeType())
CanUpgrade = GraftCommandDefinition('can_upgrade', 'Upgrade Not At Max Level', 'Uses the requirements of {1}.', CodeTypes.UpgradeCodeType())
CanCloak = GraftCommandDefinition('can_cloak', 'Can Cloak', 'Shown if every selected unit meets the use requirements of {1} and any of them can cloak.', CodeTypes.TechCodeType())
CanDecloak = GraftCommandDefinition('can_decloak', 'Can Decloak', 'Shown if every selected unit meets the use requirements of {1} and is cloaked.', CodeTypes.TechCodeType())
CanCloakMixed = GraftCommandDefinition('can_cloak_mixed', 'Can Cloak - Mixed', 'Shown if any selected unit meets the use requirements of its own cloaking technology and can cloak.')
CanDecloakMixed = GraftCommandDefinition('can_decloak_mixed', 'Can Decloak - Mixed', 'Shown if every selected unit meets the use requirements of its own cloaking technology and is cloaked.')
CanSiege = GraftCommandDefinition('can_siege', 'Tank Is In Tank Mode', 'Uses the use requirements of {1}. Hidden if any selected tank is already sieged.', CodeTypes.TechCodeType())
CanUnsiege = GraftCommandDefinition('can_unsiege', 'Tank Is In Siege Mode', 'Shown if the unit meets the use requirements of {1} and any selected tank is sieged.', CodeTypes.TechCodeType())
IsNotSieged = GraftCommandDefinition('is_not_sieged', 'Tank Is In Tank Mode(Move)', 'Shown unless any selected unit is a sieged tank.')
IsPlayerNukeReady = GraftCommandDefinition('is_player_nuke_ready', 'Nuke Available', 'Shown if the player has a Nuclear Silo with a nuke ready. Otherwise greyed.')
IsNotDisabled = GraftCommandDefinition('is_not_disabled', 'Recharge Shields', 'Shown unless the unit is disabled (unpowered, locked down, etc.).')
IsLiftedOff = GraftCommandDefinition('is_lifted_off', 'Building Can Move And Has Lifted Off', 'Shown if the building is lifted off.')
CanLand = GraftCommandDefinition('can_land', 'Building Has Lifted Off', "Shown if one unit is selected and it's a lifted off building.")
CanLiftOff = GraftCommandDefinition('can_lift_off', 'Building Has Landed', 'Shown if the building is landed and idle.')
CanBurrow = GraftCommandDefinition('can_burrow', 'Ability Is Researched', 'Shown if every selected burrower meets the use requirements of {1} and any of them is unburrowed.', CodeTypes.TechCodeType())
CanUnburrow = GraftCommandDefinition('can_unburrow', 'Is Using Ability', 'Shown if every selected burrower meets the use requirements of {1} and is burrowed.', CodeTypes.TechCodeType())
CanMorphLurker = GraftCommandDefinition('can_morph_lurker', 'Morph To Lurker', 'Uses the use requirements of Lurker Aspect.')
IsNotBurrowed = GraftCommandDefinition('is_not_burrowed', 'Not Burrowed(Move/Stop/Patrol/Hold Position)', 'Shown unless any selected unit is burrowed.')
CanAttackAndNotBurrowed = GraftCommandDefinition('can_attack_and_not_burrowed', 'Not Burrowed (Attack)', 'Shown if no selected unit is burrowed and any selected unit can move and attack.')
IsNotCarryingHarvestAndNotBurrowed = GraftCommandDefinition('is_not_carrying_harvest_and_not_burrowed', 'Not Carrying Minerals/Gas & Not Burrowed', "Shown if no selected unit is burrowed and any selected unit isn't carrying minerals or gas.")
IsCarryingHarvestAndNotBurrowed = GraftCommandDefinition('is_carrying_harvest_and_not_burrowed', 'Carrying Minerals/Gas & Not Burrowed', 'Shown if no selected unit is burrowed and any selected unit is carrying minerals or gas.')
HasSameBurrowState = GraftCommandDefinition('has_same_burrow_state', 'Burrowed (Stop - Lurker)', 'Shown if every selected unit is burrowed, or every selected unit is unburrowed.')
DoesNotHaveExit = GraftCommandDefinition('does_not_have_exit', 'Has No Exit', 'Shown if the Nydus Canal has no exit.')
CanBuildZergBasic = GraftCommandDefinition('can_build_zerg_basic', 'Zerg Basic Buildings', 'Shown if one unburrowed unit is selected and any basic Zerg building can be built.')
CanBuildZergAdvanced = GraftCommandDefinition('can_build_zerg_advanced', 'Zerg Advanced Buildings', 'Shown if one unburrowed unit is selected and any advanced Zerg building can be built.')
HasInterceptors = GraftCommandDefinition('has_interceptors', 'Has Interceptors', 'Shown if any selected unit is a Carrier with Interceptors. Otherwise greyed.')
HasScarabs = GraftCommandDefinition('has_scarabs', 'Has Scarabs', 'Shown if any selected unit is a Reaver with Scarabs. Otherwise greyed.')
IsTechUnusable = GraftCommandDefinition('is_tech_unusable', 'Tech Unusable', "Greyed while the use requirements of {1} grey it out (e.g. not researched). Otherwise hidden, so it's never enabled.", CodeTypes.TechCodeType())
CanArchonWarp = GraftCommandDefinition('can_archon_warp', '2 Units Selected (Archon Warp)', 'Hidden unless Archon Warp can be used. Greyed when only one unit is selected.')
IsTechUnusableB = GraftCommandDefinition('is_tech_unusable_b', 'Tech Unusable (B)', "Greyed while the use requirements of {1} grey it out (e.g. not researched). Otherwise hidden, so it's never enabled. Identical to `is_tech_unusable`.", CodeTypes.TechCodeType())
CanDarkArchonMeld = GraftCommandDefinition('can_dark_archon_meld', '2 Units Selected (Dark Archon Meld)', 'Hidden unless Dark Archon Meld can be used. Greyed when only one unit is selected.')
CanBuildProtossBasic = GraftCommandDefinition('can_build_protoss_basic', 'Protoss Basic Buildings', 'Shown if one unit is selected and any basic Protoss building can be built.')
CanBuildProtossAdvanced = GraftCommandDefinition('can_build_protoss_advanced', 'Protoss Advanced Buildings', 'Shown if one unit is selected and any advanced Protoss building can be built.')
IsConstructing = GraftCommandDefinition('is_constructing', 'Is Constructing (Halt - SCV)', 'Shown if every selected unit is constructing a building.')
IsNotConstructingMove = GraftCommandDefinition('is_not_constructing_move', 'Move (SCV)', "Shown if any selected unit isn't constructing a building.")
IsNotConstructingStop = GraftCommandDefinition('is_not_constructing_stop', 'Stop (SCV)', "Shown if any selected unit isn't constructing a building.")
IsNotConstructingAttack = GraftCommandDefinition('is_not_constructing_attack', 'Attack (SCV)', "Shown if any selected unit isn't constructing a building.")
IsNotConstructingRepair = GraftCommandDefinition('is_not_constructing_repair', 'Repair (SCV)', "Shown if any selected unit isn't constructing a building.")
IsNotCarryingHarvestAndNotConstructing = GraftCommandDefinition('is_not_carrying_harvest_and_not_constructing', 'Not Carrying Minerals/Gas & Not Constructing', "Shown if any selected unit isn't carrying minerals or gas, and any selected unit isn't constructing.")
IsCarryingHarvestAndNotConstructing = GraftCommandDefinition('is_carrying_harvest_and_not_constructing', 'Carrying Minerals/Gas & Not Constructing', "Shown if any selected unit is carrying minerals or gas, and any selected unit isn't constructing.")
CanBuildTerranBasic = GraftCommandDefinition('can_build_terran_basic', 'Terran Basic Buildings', "Shown if one unit is selected, it isn't constructing, and any basic Terran building can be built.")
CanBuildTerranAdvanced = GraftCommandDefinition('can_build_terran_advanced', 'Terran Advanced Buildings', "Shown if one unit is selected, it isn't constructing, and any advanced Terran building can be built.")
CanCreateSingle = GraftCommandDefinition('can_create_single', 'Nuke Train', 'Uses the requirements of {1} when one unit is selected. Otherwise hidden.', CodeTypes.UnitCodeType())

CancelInfestation = GraftCommandDefinition('cancel_infestation', 'Cancel Infestation', 'Believed to do nothing.')
Rally = GraftCommandDefinition('rally', 'Rally Point', 'Start targeting a rally point on a unit or the ground.')
SelectLarva = GraftCommandDefinition('select_larva', 'Select Larva', 'Select the Larvae of the selected building.')
Train = GraftCommandDefinition('train', 'Create Unit', 'Train {1}.', CodeTypes.UnitCodeType())
CancelTrain = GraftCommandDefinition('cancel_train', 'Cancel Last', 'Cancel training queue slot {1}.', CodeTypes.QueueSlotCodeType())
Unsiege = GraftCommandDefinition('unsiege', 'Tank Mode', 'Switch to tank mode.')
Siege = GraftCommandDefinition('siege', 'Siege Mode', 'Switch to siege mode. {1} is unused.', CodeTypes.TechCodeType())
CancelConstruction = GraftCommandDefinition('cancel_construction', 'Cancel Construction', 'Cancel construction or mutation of the selected building.')
CancelMorph = GraftCommandDefinition('cancel_morph', 'Cancel Morph', 'Cancel the morph of the selected Egg or Cocoon.')
Move = GraftCommandDefinition('move', 'Move', 'Start targeting a move.')
Stop = GraftCommandDefinition('stop', 'Stop', 'Stop the selected units.')
Attack = GraftCommandDefinition('attack', 'Attack', 'Start targeting an attack. Clicking the ground attack-moves if any selected unit can move.')
AttackDirect = GraftCommandDefinition('attack_direct', 'Direct Attack', 'Start targeting an attack, without attack-moving when the ground is clicked.')
AttackTower = GraftCommandDefinition('attack_tower', 'Attack(Building)', 'Start targeting a tower attack. Clicking the ground guards in place.')
MoveCarrierReaver = GraftCommandDefinition('move_carrier_reaver', 'Move (Carrier/Reaver)', 'Start targeting a Carrier or Reaver move.')
StopCarrier = GraftCommandDefinition('stop_carrier', 'Stop Carrier', 'Stop the selected Carriers.')
StopReaver = GraftCommandDefinition('stop_reaver', 'Stop Reaver', 'Stop the selected Reavers.')
AttackCarrier = GraftCommandDefinition('attack_carrier', 'Attack Carrier', 'Start targeting a Carrier attack.')
AttackReaver = GraftCommandDefinition('attack_reaver', 'Attack Reaver', 'Start targeting a Reaver attack.')
BuildSubunit = GraftCommandDefinition('build_subunit', 'Build Subunit', 'Build an Interceptor or Scarab. {1} is unused.', CodeTypes.UnitCodeType())
Patrol = GraftCommandDefinition('patrol', 'Patrol', 'Start targeting a patrol.')
HoldPosition = GraftCommandDefinition('hold_position', 'Hold Position', 'Hold position.')
ResearchTech = GraftCommandDefinition('research_tech', 'Research Technology', 'Research technology {1}.', CodeTypes.TechCodeType())
CancelResearchTech = GraftCommandDefinition('cancel_research_tech', 'Cancel Technology Research', 'Cancel the current technology research.')
UseTech = GraftCommandDefinition('use_tech', 'Use Technology', 'Start targeting technology {1}, if any selected unit has enough energy.', CodeTypes.TechCodeType())
Stim = GraftCommandDefinition('stim', 'StimPack', 'Use a Stim Pack, if any selected unit can. {1} is unused.', CodeTypes.TechCodeType())
Upgrade = GraftCommandDefinition('upgrade', 'Research Upgrade', 'Research upgrade {1}.', CodeTypes.UpgradeCodeType())
CancelUpgrade = GraftCommandDefinition('cancel_upgrade', 'Cancel Upgrade Research', 'Cancel the current upgrade.')
CancelAddon = GraftCommandDefinition('cancel_addon', 'Cancel AddOn', 'Cancel the add-on under construction.')
BuildTerran = GraftCommandDefinition('build_terran', 'Create Building - Terran', 'Open the placement box for an SCV to build {1}, if it can be afforded.', CodeTypes.UnitCodeType())
PlaceCop = GraftCommandDefinition('place_cop', 'Place COP', 'Open the placement box to place the selected Flag Beacon or COP unit.')
BuildProtoss = GraftCommandDefinition('build_protoss', 'Create Building - Protoss', 'Open the placement box for a Probe to warp in {1}, if it can be afforded.', CodeTypes.UnitCodeType())
BuildAddon = GraftCommandDefinition('build_addon', 'Create AddOn', 'Open the placement box to build add-on {1}, if it can be afforded.', CodeTypes.UnitCodeType())
BuildZerg = GraftCommandDefinition('build_zerg', 'Create Building - Zerg', 'Open the placement box for a Drone to mutate into {1}, if it can be afforded.', CodeTypes.UnitCodeType())
PlaceNydusExit = GraftCommandDefinition('place_nydus_exit', 'Place Nydus Canal Exit', 'Open the placement box to place {1} as a Nydus Canal exit.', CodeTypes.UnitCodeType())
MorphBuilding = GraftCommandDefinition('morph_building', 'Building Morph', 'Morph the selected building into {1}, if it can be afforded.', CodeTypes.UnitCodeType())
Land = GraftCommandDefinition('land', 'Land', 'Open the placement box to land as {1}.', CodeTypes.UnitCodeType())
Repair = GraftCommandDefinition('repair', 'Repair', 'Start targeting a repair.')
MorphUnit = GraftCommandDefinition('morph_unit', 'Unit Morph', 'Morph the selected units into {1}, if it can be afforded.', CodeTypes.UnitCodeType())
Harvest = GraftCommandDefinition('harvest', 'Gather', 'Start targeting a harvest.')
ReturnHarvest = GraftCommandDefinition('return_harvest', 'Return Cargo', 'Return cargo.')
Burrow = GraftCommandDefinition('burrow', 'Burrow', 'Burrow. {1} is unused.', CodeTypes.TechCodeType())
Unburrow = GraftCommandDefinition('unburrow', 'Unburrow', 'Unburrow.')
Cloak = GraftCommandDefinition('cloak', 'Cloak', 'Cloak, if any selected unit has enough energy. {1} is unused.', CodeTypes.TechCodeType())
Decloak = GraftCommandDefinition('decloak', 'Decloak', 'Decloak.')
LiftOff = GraftCommandDefinition('lift_off', 'Lift Off', 'Lift off.')
Load = GraftCommandDefinition('load', 'Load', 'Start targeting a unit to load.')
Unload = GraftCommandDefinition('unload', 'Unload', 'Unload. Buildings unload everything immediately, units start targeting where to unload.')
ArchonWarp = GraftCommandDefinition('archon_warp', 'Archon Warp', 'Warp in an Archon. {1} is unused.', CodeTypes.UnitCodeType())
DarkArchonMeld = GraftCommandDefinition('dark_archon_meld', 'Dark Archon Meld', 'Meld a Dark Archon. {1} is unused.', CodeTypes.UnitCodeType())
RechargeShields = GraftCommandDefinition('recharge_shields', 'Recharge Shields', 'Start targeting a unit to recharge shields on.')
Nuke = GraftCommandDefinition('nuke', 'Nuclear Strike', 'Start targeting a nuclear strike.')
CancelNuke = GraftCommandDefinition('cancel_nuke', 'Cancel Nuclear Strike', 'Cancel the nuclear strike in progress.')
Heal = GraftCommandDefinition('heal', 'Heal', 'Start targeting a heal-move. {1} is unused.', CodeTypes.TechCodeType())
SlowDownReplay = GraftCommandDefinition('slow_down_replay', 'Slow Down Replay', 'Slow down the replay.')
PlayPauseReplay = GraftCommandDefinition('play_pause_replay', 'Play/Pause Replay', 'Pause or resume the replay.')
SpeedUpReplay = GraftCommandDefinition('speed_up_replay', 'Speed Up Replay', 'Speed up the replay.')
CancelTargeting = GraftCommandDefinition('cancel_targeting', 'Cancel', 'Turn off targeting mode.')
CancelPlacement = GraftCommandDefinition('cancel_placement', 'Cancel Place Building', 'Close the placement box.')
ShowButtonCard = GraftCommandDefinition('show_button_card', 'Change Displayed Buttons', 'Show button card {1}.', CodeTypes.ButtonCardCodeType())

# In the order of FireGraft and the hook's lookup tables in `grafting.cpp` (a button stores the index of its condition and action in these lists)
condition_commands: list[GraftCommandDefinition] = number_functions([
	CanSlowDownReplay,
	CanSpeedUpReplay,
	IsWatchingReplay,
	Always,
	CanCreateOrMorph,
	CanBuildSubunit,
	CanMove,
	CanStop,
	CanAttack,
	CanAttackInPlace,
	IsTraining,
	IsConstructingAddon,
	IsZergTownHall,
	CanSetRallyPoint,
	CanZergTownHallSetRallyPoint,
	IsConstructingOrMutating,
	IsResearchingUpgrade,
	IsResearchingTech,
	IsNotCarryingHarvest,
	IsCarryingHarvest,
	CanLoad,
	CanUnload,
	CanResearchTech,
	CanPlayerUseTech,
	CanUnitsUseTech,
	CanUpgrade,
	CanCloak,
	CanDecloak,
	CanCloakMixed,
	CanDecloakMixed,
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
	CanAttackAndNotBurrowed,
	IsNotCarryingHarvestAndNotBurrowed,
	IsCarryingHarvestAndNotBurrowed,
	HasSameBurrowState,
	DoesNotHaveExit,
	CanBuildZergBasic,
	CanBuildZergAdvanced,
	HasInterceptors,
	HasScarabs,
	IsTechUnusable,
	CanArchonWarp,
	IsTechUnusableB,
	CanDarkArchonMeld,
	CanBuildProtossBasic,
	CanBuildProtossAdvanced,
	IsConstructing,
	IsNotConstructingMove,
	IsNotConstructingStop,
	IsNotConstructingAttack,
	IsNotConstructingRepair,
	IsNotCarryingHarvestAndNotConstructing,
	IsCarryingHarvestAndNotConstructing,
	CanBuildTerranBasic,
	CanBuildTerranAdvanced,
	CanCreateSingle,
])

action_commands: list[GraftCommandDefinition] = number_functions([
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
	AttackDirect,
	AttackTower,
	MoveCarrierReaver,
	StopCarrier,
	StopReaver,
	AttackCarrier,
	AttackReaver,
	BuildSubunit,
	Patrol,
	HoldPosition,
	ResearchTech,
	CancelResearchTech,
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
	MorphUnit,
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
	ShowButtonCard,
])

button_commands: list[CodeCommandDefinition] = [Icon, *condition_commands, *action_commands, EnabledStr, DisabledStr]

UseButtonSet = CodeCommandDefinition('use_button_set', 'The button card uses button set {1}', None, (CodeTypes.UnitButtonSetCodeType(),))
ConnectedUnit = CodeCommandDefinition('connected_unit', 'When selected together with {1}, the group uses the button card of {1} instead of the generic group card', None, (CodeTypes.ConnectedUnitCodeType(),))

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
