
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, RawActionDefinition
from .Parameters import *
from .Action import Action
from .Constants import ActionType, Matches

action_definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition('NoAction', ActionType.no_action),
	BasicActionDefinition('Victory', ActionType.victory),
	BasicActionDefinition('Defeat', ActionType.defeat),
	BasicActionDefinition('PreserveTrigger', ActionType.preserve_trigger),
	BasicActionDefinition('Wait', ActionType.wait, (TimeParameter(),)),
	BasicActionDefinition('PauseGame', ActionType.pause_game),
	BasicActionDefinition('UnpauseGame', ActionType.unpause_game),
	BasicActionDefinition('Transmission', ActionType.transmission, (StringParameter(), DisplayParameter(), WAVParameter(), TimeParameter(wav=True), UnitParameter(), LocationParameter(), ModifierParameter(), TimeParameter())),
	BasicActionDefinition('PlayWAV', ActionType.play_wav, (WAVParameter(), TimeParameter())),
	BasicActionDefinition('DisplayTextMessage', ActionType.display_message, (StringParameter(), DisplayParameter())),
	BasicActionDefinition('CenterView', ActionType.center_view, (LocationParameter(),)),
	BasicActionDefinition('CreateUnitWithProperties', ActionType.create_unit_properties, (PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter(), PropertiesParameter())),
	BasicActionDefinition('SetMissionObjectives', ActionType.set_mission_objectives, (StringParameter(),), default_flags=0),
	BasicActionDefinition('SetSwitch', ActionType.set_switch, (SwitchParameter(), SwitchActionParameter())),
	BasicActionDefinition('SetCountdownTimer', ActionType.set_countdown_timer, (ModifierParameter(), TimeParameter())),
	BasicActionDefinition('RunAIScript', ActionType.run_aiscript, (AIScriptParameter(location_based=False),)),
	BasicActionDefinition('RunAIScriptAtLocation', ActionType.run_aiscript_at_location, (AIScriptParameter(location_based=True), LocationParameter())),
	BasicActionDefinition('LeaderboardControl', ActionType.leaderboard_control, (StringParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardControlAtLocation', ActionType.leaderboard_control_at_location, (StringParameter(), UnitTypeParameter(), LocationParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardResources', ActionType.leaderboard_resources, (StringParameter(), ResourceTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardKills', ActionType.leaderboard_kills, (StringParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardPoints', ActionType.leaderboard_points, (StringParameter(), ScoreTypeParameter()), default_flags=0),
	BasicActionDefinition('KillUnit', ActionType.kill_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('KillUnitsAtLocation', ActionType.kill_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('RemoveUnit', ActionType.remove_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('RemoveUnitsAtLocation', ActionType.remove_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('SetResources', ActionType.set_resources, (PlayerParameter(), ModifierParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicActionDefinition('SetScore', ActionType.set_score, (PlayerParameter(), ModifierParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicActionDefinition('MinimapPing', ActionType.minimap_ping, (LocationParameter(),)),
	BasicActionDefinition('TalkingPortrait', ActionType.talking_portrait, (UnitParameter(), TimeParameter())),
	BasicActionDefinition('MuteUnitSpeech', ActionType.mute_unit_speech),
	BasicActionDefinition('UnmuteUnitSpeech', ActionType.unmute_unit_speech),
	BasicActionDefinition('LeaderboardComputerPlayers', ActionType.leaderboard_computer_players, (StateActionParameter(),), default_flags=0),
	BasicActionDefinition('LeaderboardGoalControl', ActionType.leaderboard_goal_control, (StringParameter(), NumberParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalControlAtLocation', ActionType.leaderboard_goal_control_at_location, (StringParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalResources', ActionType.leaderboard_goal_resources, (StringParameter(), NumberParameter(), ResourceTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalKills', ActionType.leaderboard_goal_kills, (StringParameter(), NumberParameter(), UnitTypeParameter()), default_flags=0),
	BasicActionDefinition('LeaderboardGoalPoints', ActionType.leaderboard_goal_points, (StringParameter(), NumberParameter(), ScoreTypeParameter()), default_flags=0),
	BasicActionDefinition('MoveLocation', ActionType.move_location, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('MoveUnit', ActionType.move_unit, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('LeaderboardGreed', ActionType.leaderboard_greed, (NumberParameter(),)),
	BasicActionDefinition('SetNextScenario', ActionType.set_next_scenario, (StringParameter(),)),
	BasicActionDefinition('SetDoodadState', ActionType.set_doodad_state, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('SetInvincibility', ActionType.set_invincibility, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('CreateUnit', ActionType.create_unit, (PlayerParameter(), QuantityParameter(), UnitParameter(), LocationParameter())),
	BasicActionDefinition('SetDeaths', ActionType.set_deaths, (PlayerParameter(), UnitTypeParameter(), ModifierParameter(), NumberParameter())),
	BasicActionDefinition('Order', ActionType.order, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), OrderParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('Comment', ActionType.comment, (StringParameter(),), default_flags=0),
	BasicActionDefinition('GiveUnitsToPlayer', ActionType.give_units, (PlayerParameter(), PlayerParameter(target=True), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('ModifyUnitHitPoints', ActionType.modify_unit_hit_points, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitEnergy', ActionType.modify_unit_energy, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitShieldPoints', ActionType.modify_unit_shield_points, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), PercentageParameter())),
	BasicActionDefinition('ModifyUnitResourceAmount', ActionType.modify_unit_resources, (PlayerParameter(), QuantityParameter(), LocationParameter(), NumberParameter())),
	BasicActionDefinition('ModifyUnitHangerCount', ActionType.modify_unit_hanger_count, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), NumberParameter())),
	BasicActionDefinition('PauseTimer', ActionType.pause_timer),
	BasicActionDefinition('UnpauseTimer', ActionType.unpause_timer),
	BasicActionDefinition('Draw', ActionType.draw),
	BasicActionDefinition('SetAllianceStatus', ActionType.set_alliance_status, (PlayerParameter(), AllianceStatusParameter())),
	BasicActionDefinition('DisableDebugMode', ActionType.disable_debug_mode, default_flags=0),
	BasicActionDefinition('EnableDebugMode', ActionType.enable_debug_mode, default_flags=0),

	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	action_definitions_registry.append(definition)

def get_definition(condition: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in action_definitions_registry:
		matches = definition.matches(condition)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_action_named(name: str) -> (ActionDefinition | None):
	for definition in action_definitions_registry:
		if definition.name == name:
			return definition
	return None

briefing_action_definitions_registry: list[ActionDefinition] = [

]
