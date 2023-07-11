
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

class BasicConditionDefinition(ConditionDefinition):
	def __init__(self, name: str, condition_type: int, parameters: tuple[ConditionParameter, ...] = ()) -> None:
		self.name = name
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

class RawConditionDefinition(ConditionDefinition):
	name = 'Raw'

	def __init__(self):
		self.parameters = tuple(RawFieldParameter(index) for index in range(9))

	def matches(self, condition: Condition) -> int:
		return 1

	def new_condition(self) -> Condition:
		return Condition()

condition_definitions_registry: list[ConditionDefinition] = [
	BasicConditionDefinition('NoCondition', ConditionType.no_condition),
	BasicConditionDefinition('CountdownTimer', ConditionType.countdown_timer, (ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Command', ConditionType.command, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter())),
	BasicConditionDefinition('Bring', ConditionType.bring, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('Accumulate', ConditionType.accumulate, (PlayerParameter(), ComparisonParameter(), NumberParameter(), ResourceTypeParameter())),
	BasicConditionDefinition('Kill', ConditionType.kill, (PlayerParameter(), ComparisonParameter(), NumberParameter(), UnitTypeParameter())),
	BasicConditionDefinition('CommandTheMost', ConditionType.commands_the_most, (UnitTypeParameter(),)),
	BasicConditionDefinition('CommandsTheMostAt', ConditionType.commands_the_most_at, (UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('MostKills', ConditionType.most_kills, (UnitTypeParameter(),)),
	BasicConditionDefinition('HighestScore', ConditionType.highest_score, (ScoreTypeParameter(),)),
	BasicConditionDefinition('MostResources', ConditionType.most_resources, (ResourceTypeParameter(),)),
	BasicConditionDefinition('Switch', ConditionType.switch, (SwitchParameter(), SwitchStateParameter())),
	BasicConditionDefinition('ElapsedTime', ConditionType.elapsed_time, (ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Opponents', ConditionType.opponents, (PlayerParameter(), ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('Deaths', ConditionType.deaths, (PlayerParameter(), UnitTypeParameter(), ComparisonParameter(), NumberParameter())),
	BasicConditionDefinition('CommandTheLeast', ConditionType.commands_the_least, (UnitTypeParameter(),)),
	BasicConditionDefinition('CommandTheLeastAt', ConditionType.commands_the_least_at, (UnitTypeParameter(), LocationParameter())),
	BasicConditionDefinition('LeastKills', ConditionType.least_kills, (UnitTypeParameter(),)),
	BasicConditionDefinition('LowestScore', ConditionType.lowest_score, (ScoreTypeParameter(),)),
	BasicConditionDefinition('LeastResources', ConditionType.least_resources, (ResourceTypeParameter(),)),
	BasicConditionDefinition('Score', ConditionType.score, (PlayerParameter(), ComparisonParameter(), NumberParameter(), ScoreTypeParameter())),
	BasicConditionDefinition('Always', ConditionType.always),
	BasicConditionDefinition('Never', ConditionType.never),

	RawConditionDefinition()
]

def register_definition(definition: ConditionDefinition) -> None:
	condition_definitions_registry.append(definition)

def get_definition(condition: Condition) -> ConditionDefinition:
	result_definition: ConditionDefinition
	result_matches = Matches.no
	for definition in condition_definitions_registry:
		matches = definition.matches(condition)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_definition_named(name: str) -> (ConditionDefinition | None):
	for definition in condition_definitions_registry:
		if definition.name == name:
			return definition
	return None
