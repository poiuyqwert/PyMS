
from __future__ import annotations

from PyMS.Utilities import IO

from .Parameters import ActionParameter, LongParameter, ShortParamater, ByteParameter, MemoryParameter, ModifierParameter, NumberParameter, MaskParameter
from .Action import Action
from .Constants import Matches, ActionType, ActionFlag, PlayerGroup, Mask

from ...Utilities import IO

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .TRG import TRG

class ActionDefinition(Protocol):
	name: str
	description: str
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

	def new_action(self) -> Action:
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

class BasicActionDefinition(ActionDefinition):
	def __init__(self, name: str, description: str, action_type: int, parameters: tuple[ActionParameter, ...] = (), default_flags: int = ActionFlag.always_display) -> None:
		self.name = name
		self.description = description
		self.action_type = action_type
		self.parameters = parameters
		self.default_flags = default_flags

	def matches(self, action: Action) -> int:
		if action.action_type == self.action_type:
			return Matches.low
		return Matches.no

	def new_action(self) -> Action:
		action = Action()
		action.action_type = self.action_type
		action.flags = self.default_flags
		return action


class MemoryActionDefinition(ActionDefinition):
	name = 'SetMemory'
	description = 'Modify value at {0}: {1} {2} with {3}'
	parameters = (MemoryParameter(), ModifierParameter(), NumberParameter(), MaskParameter())

	def matches(self, action: Action) -> int:
		if action.action_type == ActionType.set_deaths and (action.player_group > PlayerGroup.non_allied_victory_players or action.masked == Mask.enabled):
			return Matches.low+1
		return Matches.no

	def new_action(self) -> Action:
		action = Action()
		action.action_type = ActionType.set_deaths
		return action

class RawActionDefinition(ActionDefinition):
	name = 'RawAction'
	description = 'Create an action from raw values'
	parameters = (LongParameter(0), LongParameter(1), LongParameter(2), LongParameter(3), LongParameter(4), LongParameter(5), ShortParamater(6), ByteParameter(7), ByteParameter(8))

	def matches(self, action: Action) -> int:
		return 1

	def new_action(self) -> Action:
		return Action()
