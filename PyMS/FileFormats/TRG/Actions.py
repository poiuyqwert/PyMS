
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, MemoryActionDefinition, RawActionDefinition
from .Parameters import AIScriptParameter, AllianceStatusParameter, DisplayParameter, LocationParameter, ModifierParameter, NumberParameter, OrderParameter, PercentageParameter, PlayerParameter, PropertiesParameter, QuantityParameter, ResourceTypeParameter, ScoreTypeParameter, StateActionParameter, StringParameter, SwitchActionParameter, SwitchParameter, TimeParameter, UnitParameter, UnitTypeParameter, WAVParameter
from .Action import Action
from .Constants import ActionType, Matches

definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition(
		name='NoAction',
		description='No action',
		action_type=ActionType.no_action
	),
	BasicActionDefinition(
		name='Victory',
		description='End scenario in victory for current player.',
		action_type=ActionType.victory
	),
	BasicActionDefinition(
		name='Defeat',
		description='End scenario in defeat for current player.',
		action_type=ActionType.defeat
	),
	BasicActionDefinition(
		name='PreserveTrigger',
		description='Preserve trigger.',
		action_type=ActionType.preserve_trigger
	),
	BasicActionDefinition(
		name='Wait',
		description='Wait for {1} milliseconds.',
		action_type=ActionType.wait,
		parameters=(TimeParameter(),)
	),
	BasicActionDefinition(
		name='PauseGame',
		description='Pause the game.',
		action_type=ActionType.pause_game
	),
	BasicActionDefinition(
		name='UnpauseGame',
		description='Unpause the game.',
		action_type=ActionType.unpause_game
	),
	BasicActionDefinition(
		name='Transmission',
		description='Send transmission to current player from {4} at {5}. Play {2} with duration {3}. Modify transmission duration: {6} {7} milliseconds. Display {0} when {1}.',
		action_type=ActionType.transmission,
		parameters=(StringParameter(), DisplayParameter(), WAVParameter(), TimeParameter(), UnitParameter(), LocationParameter(), ModifierParameter(), TimeParameter(transmission=True))
	),
	BasicActionDefinition(
		name='PlayWAV',
		description='Play {0} with duration {2}.',
		action_type=ActionType.play_wav,
		parameters=(WAVParameter(), TimeParameter())
	),
	BasicActionDefinition(
		name='DisplayTextMessage',
		description='Display {0} for current player when {1}.',
		action_type=ActionType.display_message,
		parameters=(StringParameter(), DisplayParameter())
	),
	BasicActionDefinition(
		name='CenterView',
		description='Center view for current player at {0}.',
		action_type=ActionType.center_view,
		parameters=(LocationParameter(),)
	),
	BasicActionDefinition(
		name='CreateUnitWithProperties',
		description='Create {1} {2} at {3} for {0}. Apply {4}.',
		action_type=ActionType.create_unit_properties,
		parameters=(PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter(), PropertiesParameter())
	),
	BasicActionDefinition(
		name='SetMissionObjectives',
		description='Set mission objectives to {0}.',
		action_type=ActionType.set_mission_objectives,
		parameters=(StringParameter(),),
		default_flags=0
	),
	BasicActionDefinition(
		name='SetSwitch',
		description='Modify switch: {1} {0}',
		action_type=ActionType.set_switch,
		parameters=(SwitchParameter(), SwitchActionParameter())
	),
	BasicActionDefinition(
		name='SetCountdownTimer',
		description='Modify countdown timer: {0} {1} seconds.',
		action_type=ActionType.set_countdown_timer,
		parameters=(ModifierParameter(), TimeParameter())
	),
	BasicActionDefinition(
		name='RunAIScript',
		description='Execute AI Script {0}.',
		action_type=ActionType.run_aiscript,
		parameters=(AIScriptParameter(location_based=False),)
	),
	BasicActionDefinition(
		name='RunAIScriptAtLocation',
		description='Execute AI Script {0} at {1}.',
		action_type=ActionType.run_aiscript_at_location,
		parameters=(AIScriptParameter(location_based=True), LocationParameter())
	),
	BasicActionDefinition(
		name='LeaderboardControl',
		description='Show Leader Board for most control of {1}. Display label {0}.',
		action_type=ActionType.leaderboard_control,
		parameters=(StringParameter(), UnitTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardControlAtLocation',
		description='Show Leader Board for most control of {1} at {2}. Display label {0}.',
		action_type=ActionType.leaderboard_control_at_location,
		parameters=(StringParameter(), UnitTypeParameter(), LocationParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardResources',
		description='Show Leader Board for accumulation of most {1}. Display label {0}.',
		action_type=ActionType.leaderboard_resources,
		parameters=(StringParameter(), ResourceTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardKills',
		description='Show Leader Board for accumulation of most kills of {1}. Display label {0}.',
		action_type=ActionType.leaderboard_kills,
		parameters=(StringParameter(), UnitTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardPoints',
		description='Show Leader Board for accumulation of most {1} points. Display label {0}.',
		action_type=ActionType.leaderboard_points,
		parameters=(StringParameter(), ScoreTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='KillUnit',
		description='Kill all {1} for {0}.',
		action_type=ActionType.kill_unit,
		parameters=(PlayerParameter(), UnitTypeParameter())
	),
	BasicActionDefinition(
		name='KillUnitsAtLocation',
		description='Kill {1} {2} for {0} at {3}.',
		action_type=ActionType.kill_unit_at_location,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())
	),
	BasicActionDefinition(
		name='RemoveUnit',
		description='Remove all {1} for {0}.',
		action_type=ActionType.remove_unit,
		parameters=(PlayerParameter(), UnitTypeParameter())
	),
	BasicActionDefinition(
		name='RemoveUnitsAtLocation',
		description='Remove {1} {2} for {0} at {3}.',
		action_type=ActionType.remove_unit_at_location,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())
	),
	BasicActionDefinition(
		name='SetResources',
		description='Modify resources for {0}: {1} {2} of {3}.',
		action_type=ActionType.set_resources,
		parameters=(PlayerParameter(), ModifierParameter(), NumberParameter(), ResourceTypeParameter())
	),
	BasicActionDefinition(
		name='SetScore',
		description='Modify score for {0}: {1} {3} of {3}.',
		action_type=ActionType.set_score,
		parameters=(PlayerParameter(), ModifierParameter(), NumberParameter(), ScoreTypeParameter())
	),
	BasicActionDefinition(
		name='MinimapPing',
		description='Show minimap ping for current player at {0}.',
		action_type=ActionType.minimap_ping,
		parameters=(LocationParameter(),)
	),
	BasicActionDefinition(
		name='TalkingPortrait',
		description='Show {0} talking to current player for {1} milliseconds.',
		action_type=ActionType.talking_portrait,
		parameters=(UnitParameter(), TimeParameter())
	),
	BasicActionDefinition(
		name='MuteUnitSpeech',
		description='Mute all non-trigger unit sounds for current player.',
		action_type=ActionType.mute_unit_speech
	),
	BasicActionDefinition(
		name='UnmuteUnitSpeech',
		description='Unmute all non-trigger unit sounds for current player.',
		action_type=ActionType.unmute_unit_speech
	),
	BasicActionDefinition(
		name='LeaderboardComputerPlayers',
		description='Set use of computer players in leaderboard calculations to {0}.',
		action_type=ActionType.leaderboard_computer_players,
		parameters=(StateActionParameter(),),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardGoalControl',
		description='Show Leader Board for player closest to control of {1} of {2}. Display label {0}.',
		action_type=ActionType.leaderboard_goal_control,
		parameters=(StringParameter(), NumberParameter(), UnitTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardGoalControlAtLocation',
		description='Show Leader Board for player closest to control of {1} of {2} at {3}. Display label {0}.',
		action_type=ActionType.leaderboard_goal_control_at_location,
		parameters=(StringParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardGoalResources',
		description='Show Leader Board for player closest to accumulation of {1} {2}. Display label {0}',
		action_type=ActionType.leaderboard_goal_resources,
		parameters=(StringParameter(), NumberParameter(), ResourceTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardGoalKills',
		description='Show Leader Board for player closest to {1} kills of {2}. Display label {0}.',
		action_type=ActionType.leaderboard_goal_kills,
		parameters=(StringParameter(), NumberParameter(), UnitTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='LeaderboardGoalPoints',
		description='Show Leader Board for player closest to {1} of {2}. Display label {0}.',
		action_type=ActionType.leaderboard_goal_points,
		parameters=(StringParameter(), NumberParameter(), ScoreTypeParameter()),
		default_flags=0
	),
	BasicActionDefinition(
		name='MoveLocation',
		description='Center location {2} on {1} owned by {0} at {3}.',
		action_type=ActionType.move_location,
		parameters=(PlayerParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))
	),
	BasicActionDefinition(
		name='MoveUnit',
		description='Move {1} {2} for {0} at {4} to {3}.',
		action_type=ActionType.move_unit,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))
	),
	BasicActionDefinition(
		name='LeaderboardGreed',
		description='Show Greed Leader Board for player closest to accumulation of {0} ore and gas.',
		action_type=ActionType.leaderboard_greed,
		parameters=(NumberParameter(),)
	),
	BasicActionDefinition(
		name='SetNextScenario',
		description='Load scenario {0} after completion of current game.',
		action_type=ActionType.set_next_scenario,
		parameters=(StringParameter(),)
	),
	BasicActionDefinition(
		name='SetDoodadState',
		description='Set doodad state for {1} for {0} at {2} to {3}.',
		action_type=ActionType.set_doodad_state,
		parameters=(PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())
	),
	BasicActionDefinition(
		name='SetInvincibility',
		description='Set invincibility for {1} owned by {0} at {2} to {3}.',
		action_type=ActionType.set_invincibility,
		parameters=(PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())
	),
	BasicActionDefinition(
		name='CreateUnit',
		description='Create {1} {2} at {3} for {0}.',
		action_type=ActionType.create_unit,
		parameters=(PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter())
	),
	BasicActionDefinition(
		name='SetDeaths',
		description='Modify death counts for {0}: {2} {3} for {1}.',
		action_type=ActionType.set_deaths,
		parameters=(PlayerParameter(), UnitTypeParameter(), ModifierParameter(), NumberParameter())
	),
	BasicActionDefinition(
		name='Order',
		description='Issue order to all {1} owned by {0} at {2}: {3} to {4}.',
		action_type=ActionType.order,
		parameters=(PlayerParameter(), UnitTypeParameter(), LocationParameter(), OrderParameter(), LocationParameter(destination=True))
	),
	BasicActionDefinition(
		name='Comment',
		description='Comment: {0}.',
		action_type=ActionType.comment,
		parameters=(StringParameter(),),
		default_flags=0
	),
	BasicActionDefinition(
		name='GiveUnitsToPlayer',
		description='Give {2} {3} owned by {0} at {4} to {1}.',
		action_type=ActionType.give_units,
		parameters=(PlayerParameter(), PlayerParameter(target=True), QuantityParameter(), UnitTypeParameter(), LocationParameter())
	),
	BasicActionDefinition(
		name='ModifyUnitHitPoints',
		description='Set hit points for {1} {2} owned by {0} at {3} to {4}.',
		action_type=ActionType.modify_unit_hit_points,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())
	),
	BasicActionDefinition(
		name='ModifyUnitEnergy',
		description='Set energy points for {1} {2} owned by {0} at {3} to {4}.',
		action_type=ActionType.modify_unit_energy,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())
	),
	BasicActionDefinition(
		name='ModifyUnitShieldPoints',
		description='Set shield points for {1} {2} owned by {0} at {3} to {4}',
		action_type=ActionType.modify_unit_shield_points,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())
	),
	BasicActionDefinition(
		name='ModifyUnitResourceAmount',
		description='Set resource amount for {1} resource sources owned by {0} at {2} to {3}.',
		action_type=ActionType.modify_unit_resources,
		parameters=(PlayerParameter(), QuantityParameter(), LocationParameter(), NumberParameter())
	),
	BasicActionDefinition(
		name='ModifyUnitHangerCount',
		description='Add at most {4} to hangar for {1} {2} at {3} owned by {0}.',
		action_type=ActionType.modify_unit_hanger_count,
		parameters=(PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), NumberParameter())
	),
	BasicActionDefinition(
		name='PauseTimer',
		description='Pause the countdown timer.',
		action_type=ActionType.pause_timer
	),
	BasicActionDefinition(
		name='UnpauseTimer',
		description='Unpause the countdown timer.',
		action_type=ActionType.unpause_timer
	),
	BasicActionDefinition(
		name='Draw',
		description='End the scenario in a draw for all players.',
		action_type=ActionType.draw
	),
	BasicActionDefinition(
		name='SetAllianceStatus',
		description='Set {0} to {1}.',
		action_type=ActionType.set_alliance_status,
		parameters=(PlayerParameter(), AllianceStatusParameter())
	),
	BasicActionDefinition(
		name='DisableDebugMode',
		description='Disable debug mode (does nothing?).',
		action_type=ActionType.disable_debug_mode,
		default_flags=0
	),
	BasicActionDefinition(
		name='EnableDebugMode',
		description='Enable debug mode (does nothing?).',
		action_type=ActionType.enable_debug_mode,
		default_flags=0
	),

	MemoryActionDefinition(),
	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	definitions_registry.append(definition)

def get_definition(action: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in definitions_registry:
		matches = definition.matches(action)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_definition_named(name: str) -> (ActionDefinition | None):
	for definition in definitions_registry:
		if definition.name == name:
			return definition
	return None


	# 'SetMemoryLocation':'Modify MemoryLocation(1): Modifier(1) NewValue(1).',
	# 'SetDuoMemoryLocation':'Modify MemoryLocationEnd(1): Modifier(1) MemoryLocation(1)',
	# 'SetLocationTo':'Modify LocationProps(1) for Location(1): Top left corner to (NewX1,NewY1) and top right corner to (NewX2,NewY2) and elevations LocationFlags(1).',
	# 'SetLocationFromDeath':'Modifier(1) LocationProps(1) for Location(1) from deaths of Unit(1) owned by Player(1).',
	# 'DCMath':'Do Math(1) to death count of DestUnit(1) owned by DestPlayer(1) with death count of Unit(1) owned by Player(1).',
	# 'DisplayStatTxtString':'Display stat_txt.tbl string StringID(1).',
	# 'SetGameSpeed':'Set game speed to Speed(1) Multiplier(1).',
	# 'SetSupplyValue':'Modify SupplyType(1) for Player(1): Modifier(1) NewValue(1).',
	# 'SendUnitOrder':'Modify order of TUnit(1) owned by Player(1) in Location(1) to OrderID(1).',
	# 'SetUnitTargetToUnit':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to TUnitEnd(1) owned by PlayerEnd(1) in EndLocation(1).',
	# 'SetUnitTargetToLocation':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to EndLocation(1).',
	# 'SetUnitTargetToCoords':'Modify order target of TUnit(1) owned by Player(1) in Location(1) to (NewX,NewY).',
	# 'SetUnitHP':'Modify hit points of TUnit(1) owned by Player(1) in Location(1): Modifier(1) Number(1)',
	# 'SetUnitShields':'Modify shield points of TUnit(1) owned by Player(1) in Location(1): Modifier(1) Number(1)',
	# 'SetPlayerVision':'Set Player(1) vision of PlayerEnd(1) to Vision(1)',
