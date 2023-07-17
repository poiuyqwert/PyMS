
from __future__ import annotations

from PyMS.Utilities import IO

from .Parameters import *
from .Condition import Condition
from .Constants import ConditionType, Matches

from ...Utilities import IO

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .TRG import TRG

class ConditionDefinition(Protocol):
	name: str
	description: str
	parameters: tuple[ConditionParameter, ...]

	def matches(self, condition: Condition) -> int:
		...

	def decompile(self, condition: Condition, trg: TRG, output: IO.AnyOutputText):
		with IO.OutputText(output) as f:
			f.write(f'{self.name}(')
			has_parameters = False
			for parameter in self.parameters:
				if has_parameters:
					f.write(', ')
				f.write(parameter.condition_decompile(condition, trg))
				has_parameters = True
			f.write(')')

	def new_condition(self) -> Condition:
		...

	def help(self) -> str:
		help = f'{self.name}('
		description = self.description
		param_help = ''
		if self.parameters:
			type_counts: dict[str, int] = {}
			for parameter in self.parameters:
				type_counts[parameter.name()] = type_counts.get(parameter.name(), 0) + 1
			param_counts: dict[str, int] = {}
			for n,parameter in enumerate(self.parameters):
				param_name = parameter.name()
				param_counts[param_name] = param_counts.get(param_name, 0) + 1
				if param_counts[param_name] == 1:
					param_help += f'\n{param_name}: {parameter.help()}'
				if type_counts[param_name] > 1:
					param_name += f'({param_counts[param_name]})'
				description = description.replace(f'{{{n}}}', f'`{param_name}`')
				if n:
					help += ', '
				help += param_name
		help += f')\n    {description}'
		if param_help:
			help += f'\n{param_help}'
		return help

class BasicConditionDefinition(ConditionDefinition):
	def __init__(self, name: str, description: str, condition_type: int, parameters: tuple[ConditionParameter, ...] = ()) -> None:
		self.name = name
		self.description = description
		self.condition_type = condition_type
		self.parameters = parameters

	def matches(self, condition: Condition) -> int:
		if condition.condition_type == self.condition_type:
			return Matches.low
		return Matches.no

	def new_condition(self) -> Condition:
		condition = Condition()
		condition.condition_type = self.condition_type
		return condition

class MemoryConditionDefinition(ConditionDefinition):
	name = 'Memory'
	description = 'Check value at {0} is {1} {2}'
	parameters = (MemoryParameter(), ComparisonParameter(), NumberParameter())

	def matches(self, condition: Condition) -> int:
		if condition.condition_type == ConditionType.deaths and condition.player_group > PlayerGroup.non_allied_victory_players:
			return Matches.low+1
		return Matches.no

	def new_condition(self) -> Condition:
		condition = Condition()
		condition.condition_type = ConditionType.deaths
		return condition

class RawConditionDefinition(ConditionDefinition):
	name = 'RawCondition'
	description = 'Create a condition from raw values'
	parameters = (LongParameter(0), LongParameter(1), LongParameter(2), ShortParamater(3), ByteParameter(4), ByteParameter(5), ByteParameter(6), ByteParameter(7))

	def matches(self, condition: Condition) -> int:
		return 1

	def new_condition(self) -> Condition:
		return Condition()

definitions_registry: list[ConditionDefinition] = [
	BasicConditionDefinition('NoCondition', 'No condition.', ConditionType.no_condition),
	BasicConditionDefinition('CountdownTimer', 'Countdown timer is {0} {1} game seconds.', ConditionType.countdown_timer, (ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Command', '{0} commands {1} {2} {3}.', ConditionType.command, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter())),
	BasicConditionDefinition('Bring', '{0} brings {1} {2} {3} to {4}.', ConditionType.bring, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('Accumulate', '{0} accumulates {1} {2} {3}.', ConditionType.accumulate, (PlayerParameter(), ComparisonParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicConditionDefinition('Kill', '{0} kills {1} {2} {3}.', ConditionType.kill, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter())),
	BasicConditionDefinition('CommandTheMost', 'Current player commands the most {0}.', ConditionType.commands_the_most, (UnitTypeParameter(),)),
	BasicConditionDefinition('CommandsTheMostAt', 'Current player commands the most {0} at {1}.', ConditionType.commands_the_most_at, (UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('MostKills', 'Current player has most kills of {0}.', ConditionType.most_kills, (UnitTypeParameter(),)),
	BasicConditionDefinition('HighestScore', 'Current player has highest {0}.', ConditionType.highest_score, (ScoreTypeParameter(),)),
	BasicConditionDefinition('MostResources', 'Current player has most {0}.', ConditionType.most_resources, (ResourceTypeParameter(),)),
	BasicConditionDefinition('Switch', '{0} is {1}.', ConditionType.switch, (SwitchParameter(), SwitchStateParameter())),
	BasicConditionDefinition('ElapsedTime', 'Elapsed scenario time is {0} {1} game seconds.', ConditionType.elapsed_time, (ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Opponents', '{0} has {1} {2} opponents remaining in the game.', ConditionType.opponents, (PlayerParameter(), ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Deaths', '{0} has suffered {2} {3} deaths of {1}.', ConditionType.deaths, (PlayerParameter(), UnitTypeParameter(), ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('CommandTheLeast', 'Current player commands the least {0}.', ConditionType.commands_the_least, (UnitTypeParameter(),)),
	BasicConditionDefinition('CommandTheLeastAt', 'Current player commands the least {0} at {1}.', ConditionType.commands_the_least_at, (UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('LeastKills', 'Current player has least kills of {0}.', ConditionType.least_kills, (UnitTypeParameter(),)),
	BasicConditionDefinition('LowestScore', 'Current player has lowest {0}.', ConditionType.lowest_score, (ScoreTypeParameter(),)),
	BasicConditionDefinition('LeastResources', 'Current player has least {0}.', ConditionType.least_resources, (ResourceTypeParameter(),)),
	BasicConditionDefinition('Score', '{0} {3} score is {1} {2}.', ConditionType.score, (PlayerParameter(), ComparisonParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicConditionDefinition('Always', 'Always.', ConditionType.always),
	BasicConditionDefinition('Never', 'Never.', ConditionType.never),

	MemoryConditionDefinition(),
	RawConditionDefinition()
]

def register_definition(definition: ConditionDefinition) -> None:
	definitions_registry.append(definition)

def get_definition(condition: Condition) -> ConditionDefinition:
	result_definition: ConditionDefinition
	result_matches = Matches.no
	for definition in definitions_registry:
		matches = definition.matches(condition)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_definition_named(name: str) -> (ConditionDefinition | None):
	for definition in definitions_registry:
		if definition.name == name:
			return definition
	return None
