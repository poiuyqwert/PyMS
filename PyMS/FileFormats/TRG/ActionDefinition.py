
from __future__ import annotations

from PyMS.Utilities import IO

from .Parameters import ActionParameter, RawFieldParameter
from .Action import Action
from .Constants import Matches, ActionFlag

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

	def new_action(self) -> Action:
		...

class BasicActionDefinition(ActionDefinition):
	def __init__(self, name: str, action_type: int, parameters: tuple[ActionParameter, ...] = (), default_flags: int = ActionFlag.always_display) -> None:
		self.name = name
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

class RawActionDefinition(ActionDefinition):
	name = 'Raw'

	def __init__(self):
		self.parameters = tuple(RawFieldParameter(index) for index in range(11))

	def matches(self, action: Action) -> int:
		return 1

	def new_action(self) -> Action:
		return Action()
