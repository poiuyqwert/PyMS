
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, MemoryActionDefinition, RawActionDefinition
from .Parameters import *
from .Action import Action
from .Constants import ActionType, Matches

definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition('NoAction', 'No action', ActionType.no_action),
	BasicActionDefinition('Victory', 'End scenario in victory for current player.', ActionType.victory),
	BasicActionDefinition('Defeat', 'End scenario in defeat for current player.', ActionType.defeat),
	BasicActionDefinition('PreserveTrigger', 'Preserve trigger.', ActionType.preserve_trigger),
	BasicActionDefinition('Wait', 'Wait for {1} milliseconds.', ActionType.wait, (TimeParameter(),)),
	BasicActionDefinition('PauseGame', 'Pause the game.', ActionType.pause_game),
	BasicActionDefinition('UnpauseGame', 'Unpause the game.', ActionType.unpause_game),
	BasicActionDefinition('Transmission', 'Send transmission to current player from {4} at {5}. Play {2} with duration {3}. Modify transmission duration: {6} {7} milliseconds. Display {0} when {1}.', ActionType.transmission, (StringParameter(), DisplayParameter(), WAVParameter(), TimeParameter(), UnitParameter(), LocationParameter(), ModifierParameter(), TimeParameter(transmission=True))),
	BasicActionDefinition('PlayWAV', 'Play {0} with duration {2}.', ActionType.play_wav, (WAVParameter(), TimeParameter())),
	BasicActionDefinition('DisplayTextMessage', 'Display {0} for current player when {1}.', ActionType.display_message, (StringParameter(), DisplayParameter())),
	BasicActionDefinition('CenterView', 'Center view for current player at {0}.', ActionType.center_view, (LocationParameter(),)),
	BasicActionDefinition('CreateUnitWithProperties', 'Create {1} {2} at {3} for {0}. Apply {4}.', ActionType.create_unit_properties, (PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter(), PropertiesParameter())),
	BasicActionDefinition('SetMissionObjectives', 'Set mission objectives to {0}.', ActionType.set_mission_objectives, (StringParameter(),), default_flags=0),
	BasicActionDefinition('SetSwitch', 'Modify switch: {1} {0}', ActionType.set_switch, (SwitchParameter(), SwitchActionParameter())),
	BasicActionDefinition('SetCountdownTimer', 'Modify countdown timer: {0} {1} seconds.', ActionType.set_countdown_timer, (ModifierParameter(), TimeParameter())),
	BasicActionDefinition('RunAIScript', 'Execute AI Script {0}.', ActionType.run_aiscript, (AIScriptParameter(location_based=False),)),
	BasicActionDefinition('RunAIScriptAtLocation', 'Execute AI Script {0} at {1}.', ActionType.run_aiscript_at_location, (AIScriptParameter(location_based=True), LocationParameter())),
	BasicActionDefinition('LeaderboardControl', 'Show Leader Board for most control of {1}. Display label {0}.', ActionType.leaderboard_control, (StringParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardControlAtLocation', 'Show Leader Board for most control of {1} at {2}. Display label {0}.', ActionType.leaderboard_control_at_location, (StringParameter(), UnitTypeParameter(), LocationParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardResources', 'Show Leader Board for accumulation of most {1}. Display label {0}.', ActionType.leaderboard_resources, (StringParameter(), ResourceTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardKills', 'Show Leader Board for accumulation of most kills of {1}. Display label {0}.', ActionType.leaderboard_kills, (StringParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardPoints', 'Show Leader Board for accumulation of most {1} points. Display label {0}.', ActionType.leaderboard_points, (StringParameter(), ScoreTypeParameter()), default_flags=0),
	BasicActionDefinition('KillUnit', 'Kill all {1} for {0}.', ActionType.kill_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('KillUnitsAtLocation', 'Kill {1} {2} for {0} at {3}.', ActionType.kill_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('RemoveUnit', 'Remove all {1} for {0}.',ActionType.remove_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('RemoveUnitsAtLocation', 'Remove {1} {2} for {0} at {3}.', ActionType.remove_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('SetResources', 'Modify resources for {0}: {1} {2} of {3}.', ActionType.set_resources, (PlayerParameter(), ModifierParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicActionDefinition('SetScore', 'Modify score for {0}: {1} {3} of {3}.', ActionType.set_score, (PlayerParameter(), ModifierParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicActionDefinition('MinimapPing', 'Show minimap ping for current player at {0}.', ActionType.minimap_ping, (LocationParameter(),)),
	BasicActionDefinition('TalkingPortrait', 'Show {0} talking to current player for {1} milliseconds.', ActionType.talking_portrait, (UnitParameter(), TimeParameter())),
	BasicActionDefinition('MuteUnitSpeech', 'Mute all non-trigger unit sounds for current player.', ActionType.mute_unit_speech),
	BasicActionDefinition('UnmuteUnitSpeech', 'Unmute all non-trigger unit sounds for current player.', ActionType.unmute_unit_speech),
	BasicActionDefinition('LeaderboardComputerPlayers', 'Set use of computer players in leaderboard calculations to {0}.', ActionType.leaderboard_computer_players, (StateActionParameter(),), default_flags=0),
	BasicActionDefinition('LeaderboardGoalControl', 'Show Leader Board for player closest to control of {1} of {2}. Display label {0}.', ActionType.leaderboard_goal_control, (StringParameter(), NumberParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalControlAtLocation', 'Show Leader Board for player closest to control of {1} of {2} at {3}. Display label {0}.', ActionType.leaderboard_goal_control_at_location, (StringParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalResources', 'Show Leader Board for player closest to accumulation of {1} {2}. Display label {0}', ActionType.leaderboard_goal_resources, (StringParameter(), NumberParameter(), ResourceTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalKills', 'Show Leader Board for player closest to {1} kills of {2}. Display label {0}.', ActionType.leaderboard_goal_kills, (StringParameter(), NumberParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalPoints', 'Show Leader Board for player closest to {1} of {2}. Display label {0}.', ActionType.leaderboard_goal_points, (StringParameter(), NumberParameter(), ScoreTypeParameter()), default_flags=0),
	BasicActionDefinition('MoveLocation', 'Center location {2} on {1} owned by {0} at {3}.', ActionType.move_location, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('MoveUnit', 'Move {1} {2} for {0} at {4} to {3}.', ActionType.move_unit, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('LeaderboardGreed', 'Show Greed Leader Board for player closest to accumulation of {0} ore and gas.', ActionType.leaderboard_greed, (NumberParameter(),)),
	BasicActionDefinition('SetNextScenario', 'Load scenario {0} after completion of current game.', ActionType.set_next_scenario, (StringParameter(),)),
	BasicActionDefinition('SetDoodadState', 'Set doodad state for {1} for {0} at {2} to {3}.', ActionType.set_doodad_state, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('SetInvincibility', 'Set invincibility for {1} owned by {0} at {2} to {3}.', ActionType.set_invincibility, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('CreateUnit', 'Create {1} {2} at {3} for {0}.', ActionType.create_unit, (PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter())),
	BasicActionDefinition('SetDeaths', 'Modify death counts for {0}: {2} {3} for {1}.', ActionType.set_deaths, (PlayerParameter(), UnitTypeParameter(), ModifierParameter(), NumberParameter())),
	BasicActionDefinition('Order', 'Issue order to all {1} owned by {0} at {2}: {3} to {4}.', ActionType.order, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), OrderParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('Comment', 'Comment: {0}.', ActionType.comment, (StringParameter(),), default_flags=0),
	BasicActionDefinition('GiveUnitsToPlayer', 'Give {2} {3} owned by {0} at {4} to {1}.', ActionType.give_units, (PlayerParameter(), PlayerParameter(target=True), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('ModifyUnitHitPoints', 'Set hit points for {1} {2} owned by {0} at {3} to {4}.', ActionType.modify_unit_hit_points, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitEnergy', 'Set energy points for {1} {2} owned by {0} at {3} to {4}.', ActionType.modify_unit_energy, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitShieldPoints', 'Set shield points for {1} {2} owned by {0} at {3} to {4}', ActionType.modify_unit_shield_points, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitResourceAmount', 'Set resource amount for {1} resource sources owned by {0} at {2} to {3}.', ActionType.modify_unit_resources, (PlayerParameter(), QuantityParameter(), LocationParameter(), NumberParameter())),
	BasicActionDefinition('ModifyUnitHangerCount', 'Add at most {4} to hangar for {1} {2} at {3} owned by {0}.', ActionType.modify_unit_hanger_count, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), NumberParameter())),
	BasicActionDefinition('PauseTimer', 'Pause the countdown timer.', ActionType.pause_timer),
	BasicActionDefinition('UnpauseTimer', 'Unpause the countdown timer.', ActionType.unpause_timer),
	BasicActionDefinition('Draw', 'End the scenario in a draw for all players.', ActionType.draw),
	BasicActionDefinition('SetAllianceStatus', 'Set {0} to {1}.', ActionType.set_alliance_status, (PlayerParameter(), AllianceStatusParameter())),
	BasicActionDefinition('DisableDebugMode', 'Disable debug mode (does nothing?).', ActionType.disable_debug_mode, default_flags=0),
	BasicActionDefinition('EnableDebugMode', 'Enable debug mode (does nothing?).', ActionType.enable_debug_mode, default_flags=0),

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