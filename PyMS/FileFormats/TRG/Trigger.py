
from __future__ import annotations

from .Condition import Condition
from . import Conditions
from .Action import Action
from . import Actions
from .Parameters import PlayerParameter
from .Constants import ConditionType, ActionType

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import IO
from ...Utilities import Struct

# import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .TRG import TRG

class Execution(Struct.Struct):
	flags: int
	player_groups: list[int]

	_fields = (
		('flags', Struct.t_u32),
		('player_groups', Struct.t_au8(28))
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
		self.player_groups = [0] * 28

	# STRUCT = struct.Struct('<L28B')
	# def load_data(self, scanner: BytesScanner) -> None:
	# 	fields = scanner.scan_ints(Execution.STRUCT)
	# 	self.flags = fields[0]
	# 	self.player_groups = list(fields[1:])

	# def save_data(self, output: IO.AnyOutputBytes):
	# 	with IO.OutputBytes(output) as f:
	# 		f.write(Execution.STRUCT.pack(self.flags, *self.player_groups))

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

	@property
	def conditions_free(self) -> int:
		return Trigger.CONDITION_COUNT - len(self.conditions)

	@property
	def actions_free(self) -> int:
		return Trigger.ACTION_COUNT - len(self.actions)

	@property
	def is_missing_briefing(self) -> bool:
		for condition in self.conditions:
			if condition.condition_type == ConditionType.is_mission_briefing:
				return True
		return False

	# def load_data(self, scanner: BytesScanner) -> None:
	# 	conditions: list[Condition] = []
	# 	actions: list[Action] = []
	# 	execution = Execution()
	# 	for _ in range(16):
	# 		condition = Condition()
	# 		condition.load_data(scanner)
	# 		if condition.condition_type != ConditionType.no_condition:
	# 			conditions.append(condition)
	# 	for _ in range(64):
	# 		action = Action()
	# 		action.load_data(scanner)
	# 		if action.action_type != ActionType.no_action:
	# 			actions.append(action)
	# 	execution.load_data(scanner)

	# 	self.conditions = conditions
	# 	self.actions = actions
	# 	self.execution = execution

	# def save_data(self, output: IO.AnyOutputBytes):
	# 	with IO.OutputBytes(output) as f:
	# 		for condition in self.conditions:
	# 			condition.save_data(f)
	# 		if len(self.conditions) < Trigger.CONDITION_COUNT:
	# 			no_condition = Condition.no_condition()
	# 			for _ in range(self.conditions_free):
	# 				no_condition.save_data(f)
	# 		for action in self.actions:
	# 			action.save_data(f)
	# 		if len(self.actions) < Trigger.ACTION_COUNT:
	# 			no_action = Action.no_action()
	# 			for _ in range(self.actions_free):
	# 				no_action.save_data(f)
	# 		self.execution.save_data(f)

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
				action_definition = Actions.get_definition(no_action)
				action_definition.decompile(no_action, trg, f)
			else:
				has_action = False
				for action in self.actions:
					if has_action:
						f.write('\n')
					f.write('    ')
					action_definition = Actions.get_definition(action)
					action_definition.decompile(action, trg, f)
					has_action = True
