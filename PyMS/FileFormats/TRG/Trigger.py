
from __future__ import annotations

from .Condition import Condition
from . import Conditions
from .Action import Action
from . import Actions
from . import BriefingActions
from .Parameters import PlayerParameter
from .Constants import ConditionType, ActionType

from ...Utilities import IO
from ...Utilities import Struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .TRG import TRG

class Execution(Struct.Struct):
	flags: int
	player_groups: list[int]

	_fields = (
		('flags', Struct.t_u32),
		('player_groups', Struct.t_au8(27)),
		Struct.t_pad()
	)

	class Flags:
		executing_actions = (1 << 0)
		ignore_defeat_draw = (1 << 1)
		preserve_trigger = (1 << 2)
		ignore = (1 << 3)
		ignore_delay_actions = (1 << 4)
		paused_game = (1 << 5)

	def __init__(self) -> None:
		self.flags = 0
		self.player_groups = [0] * 27

	def __eq__(self, other) -> bool:
		if not isinstance(other, Execution):
			return False
		if other.flags != self.flags:
			return False
		if other.player_groups != self.player_groups:
			return False
		return True

class Trigger(Struct.Struct):
	CONDITION_COUNT = 16
	ACTION_COUNT = 64

	conditions: list[Condition]
	actions: list[Action]
	execution: Execution

	_fields = (
		('conditions', Struct.StructArray(Condition, 16)),
		('actions', Struct.StructArray(Action, 64)),
		('execution', Execution)
	)

	def __init__(self) -> None:
		self.conditions: list[Condition] = []
		self.actions: list[Action] = []
		self.execution = Execution()

	def post_unpack(self) -> None:
		self.conditions = list(condition for condition in self.conditions if condition.condition_type != ConditionType.no_condition)
		self.actions = list(action for action in self.actions if action.action_type != ActionType.no_action)

	def pre_pack(self) -> None:
		while self.conditions_free:
			self.conditions.append(Condition.no_condition())
		while self.actions_free:
			self.actions.append(Action.no_action())

	def post_pack(self) -> None:
		self.conditions = list(condition for condition in self.conditions if condition.condition_type != ConditionType.no_condition)
		self.actions = list(action for action in self.actions if action.action_type != ActionType.no_action)

	@property
	def conditions_free(self) -> int:
		return Trigger.CONDITION_COUNT - len(self.conditions)

	def add_condition(self, condition: Condition) -> bool:
		if not self.conditions_free:
			return False
		self.conditions.append(condition)
		return True

	@property
	def actions_free(self) -> int:
		return Trigger.ACTION_COUNT - len(self.actions)

	def add_action(self, action: Action) -> bool:
		if not self.actions_free:
			return False
		self.actions.append(action)
		return True

	@property
	def is_missing_briefing(self) -> bool:
		for condition in self.conditions:
			if condition.condition_type == ConditionType.is_mission_briefing:
				return True
		return False

	def decompile(self, trg: TRG, output: IO.AnyOutputText):
		with IO.OutputText(output) as f:
			if self.is_missing_briefing:
				f.write('BriefingTrigger():\n')
			else:
				f.write('Trigger(')
				param = PlayerParameter()
				add_comma = False
				for player_group,enabled in enumerate(self.execution.player_groups):
					if not enabled:
						continue
					if add_comma:
						f.write(', ')
					f.write(param.decompile(player_group))
					add_comma = True
				f.write('):\n  Conditions:\n')
				if not self.conditions:
					no_condition = Condition.no_condition()
					f.write('    ')
					condition_definition = Conditions.get_definition(no_condition)
					condition_definition.decompile(no_condition, trg, f)
					f.write('\n')
				else:
					for condition in self.conditions:
						f.write('    ')
						condition_definition = Conditions.get_definition(condition)
						condition_definition.decompile(condition, trg, f)
						f.write('\n')
				f.write('  Actions:\n')
			if not self.actions:
				no_action = Action.no_action()
				f.write('    ')
				if self.is_missing_briefing:
					action_definition = BriefingActions.get_definition(no_action)
				else:
					action_definition = Actions.get_definition(no_action)
				action_definition.decompile(no_action, trg, f)
			else:
				has_action = False
				for action in self.actions:
					if has_action:
						f.write('\n')
					f.write('    ')
					if self.is_missing_briefing:
						action_definition = BriefingActions.get_definition(action)
					else:
						action_definition = Actions.get_definition(action)
					action_definition.decompile(action, trg, f)
					has_action = True

	def __eq__(self, other) -> bool:
		if not isinstance(other, Trigger):
			return False
		if other.execution != self.execution:
			return False
		if other.conditions != self.conditions:
			return False
		if other.actions != self.actions:
			return False
		return True
