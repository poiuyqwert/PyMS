
from __future__ import annotations

from PyMS.Utilities import IO

from .Parameters import *
from .Action import Action
from .Constants import ActionType, Matches

from ...Utilities import IO

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .TRG import TRG

class ActionDefinition(Protocol):
	name: str
	parameters: tuple[ActionParameter, ...]

	def matches(self, action: Action) -> int:
		...

	def decompile(self, action: Action, trg: TRG, output: IO.AnyOutputText):
		with IO.OutputText(output) as f:
			f.write(f'{self.name}(')
			has_parameters = False
			for parameter in self.parameters:
				if has_parameters:
					f.write(', ')
				f.write(parameter.action_decompile(action, trg))
				has_parameters = True
			f.write(')')

class BasicActionDefinition(ActionDefinition):
	def __init__(self, name: str, action_type: int, parameters: tuple[ActionParameter, ...] = ()) -> None:
		self.name = name
		self.action_type = action_type
		self.parameters = parameters

	def matches(self, action: Action) -> int:
		if action.action_type == self.action_type:
			return Matches.low
		return Matches.no

class RawActionDefinition(ActionDefinition):
	name = 'Raw'

	def __init__(self):
		self.parameters = tuple(RawFieldParameter(index) for index in range(11))

	def matches(self, action: Action) -> int:
		return 1

_ACTION_DEFINITIONS_REGISTRY: list[ActionDefinition] = [
	BasicActionDefinition('NoAction', ActionType.no_action),
	BasicActionDefinition('Victory', ActionType.victory),
	BasicActionDefinition('Defeat', ActionType.defeat),
	BasicActionDefinition('PreserveTrigger', ActionType.preserve_trigger),
	BasicActionDefinition('Wait', ActionType.wait, (TimeParameter(),)),
	BasicActionDefinition('PauseGame', ActionType.pause_game),
	BasicActionDefinition('UnpauseGame', ActionType.unpause_game),
	BasicActionDefinition('Transmission', ActionType.transmission, (StringParameter(), WAVParameter(), TimeParameter(), UnitParameter(), LocationParameter(), ModifierParameter(), TimeParameter())),
	BasicActionDefinition('PlayWAV', ActionType.play_wav, (WAVParameter(), TimeParameter())),
	BasicActionDefinition('DisplayTextMessage', ActionType.display_message, (StringParameter(), DisplayParameter())),
	BasicActionDefinition('CenterView', ActionType.center_view, (LocationParameter(),)),
	BasicActionDefinition('CreateUnitWithProperties', ActionType.create_unit_properties, (PlayerParameter(), NumberParameter(), UnitParameter(), LocationParameter(), PropertiesParameter())),
	BasicActionDefinition('SetMissionObjectives', ActionType.set_mission_objectives, (StringParameter(),)),
	BasicActionDefinition('SetSwitch', ActionType.set_switch, (SwitchParameter(), SwitchActionParameter())),
	BasicActionDefinition('SetCountdownTimer', ActionType.set_countdown_timer, (ModifierParameter(), TimeParameter())),
	BasicActionDefinition('RunAIScript', ActionType.run_aiscript, (AIScriptParameter(location_based=False),)),
	BasicActionDefinition('RunAIScriptAtLocation', ActionType.run_aiscript_at_location, (AIScriptParameter(location_based=True), LocationParameter())),
	BasicActionDefinition('LeaderboardControl', ActionType.leaderboard_control, (StringParameter(), UnitTypeParameter())),
	BasicActionDefinition('LeaderboardControlAtLocation', ActionType.leaderboard_control_at_location, (StringParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('LeaderboardResources', ActionType.leaderboard_resources, (StringParameter(), ResourceTypeParameter())),
	BasicActionDefinition('LeaderboardKills', ActionType.leaderboard_kills, (StringParameter(), UnitTypeParameter())),
	BasicActionDefinition('LeaderboardPoints', ActionType.leaderboard_points, (StringParameter(), ScoreTypeParameter())),
	BasicActionDefinition('KillUnit', ActionType.kill_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('KillUnitsAtLocation', ActionType.kill_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('RemoveUnit', ActionType.remove_unit, (PlayerParameter(), UnitTypeParameter())),
	BasicActionDefinition('RemoveUnitsAtLocation', ActionType.remove_unit_at_location, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('SetResources', ActionType.set_resources, (PlayerParameter(), ModifierParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicActionDefinition('SetScore', ActionType.set_score, (PlayerParameter(), ModifierParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicActionDefinition('MinimapPing', ActionType.minimap_ping, (LocationParameter(),)),
	BasicActionDefinition('TalkingPortrait', ActionType.talking_portrait, (UnitParameter(), TimeParameter())),
	BasicActionDefinition('MuteUnitSpeech', ActionType.mute_unit_speech),
	BasicActionDefinition('UnmuteUnitSpeech', ActionType.mute_unit_speech),
	BasicActionDefinition('LeaderboardComputerPlayers', ActionType.leaderboard_computer_players, (StateActionParameter(),)),
	BasicActionDefinition('LeaderboardGoalControl', ActionType.leaderboard_goal_control, (StringParameter(), NumberParameter(), UnitTypeParameter())),
	BasicActionDefinition('LeaderboardGoalControlAtLocation', ActionType.leaderboard_goal_control_at_location, (StringParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter())),
	BasicActionDefinition('LeaderboardGoalResources', ActionType.leaderboard_goal_resources, (StringParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicActionDefinition('LeaderboardGoalKills', ActionType.leaderboard_goal_kills, (StringParameter(), NumberParameter(), UnitTypeParameter())),
	BasicActionDefinition('LeaderboardGoalPoints', ActionType.leaderboard_goal_points, (StringParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicActionDefinition('MoveLocation', ActionType.move_location, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('MoveUnit', ActionType.move_unit, (PlayerParameter(), QuantityParameter(), UnitTypeParameter(), LocationParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('LeaderboardGreed', ActionType.leaderboard_greed, (NumberParameter(),)),
	BasicActionDefinition('SetNextScenario', ActionType.set_next_scenario, (StringParameter(),)),
	BasicActionDefinition('SetDoodadState', ActionType.set_doodad_state, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('SetInvincibility', ActionType.set_invincibility, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), StateActionParameter())),
	BasicActionDefinition('CreateUnit', ActionType.create_unit, (PlayerParameter(), NumberParameter(), UnitParameter(), LocationParameter())),
	BasicActionDefinition('SetDeaths', ActionType.set_deaths, (PlayerParameter(), UnitTypeParameter(), ModifierParameter(), NumberParameter())),
	BasicActionDefinition('Order', ActionType.order, (PlayerParameter(), UnitTypeParameter(), LocationParameter(), OrderParameter(), LocationParameter(destination=True))),
	BasicActionDefinition('Comment', ActionType.comment, (StringParameter(),)),
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
	BasicActionDefinition('DisableDebugMode', ActionType.disable_debug_mode),
	BasicActionDefinition('EnableDebugMode', ActionType.enable_debug_mode),
	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	_ACTION_DEFINITIONS_REGISTRY.append(definition)

def get_definition(condition: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in _ACTION_DEFINITIONS_REGISTRY:
		matches = definition.matches(condition)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition
