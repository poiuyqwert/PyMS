
from __future__ import annotations

from .Constants import ConditionType

from ...Utilities import Struct

class Condition(Struct.Struct):
	fields: list[int]

	_fields = (
		('fields', Struct.MixedInts((Struct.t_au32(3), Struct.t_u16, Struct.t_au8(4), Struct.t_u16))),
	)

	def __init__(self) -> None:
		self.fields: list[int] = [0] * 9

	@staticmethod
	def no_condition() -> Condition:
		return Condition()

	@staticmethod
	def is_mission_briefing() -> Condition:
		condition = Condition()
		condition.condition_type = ConditionType.is_mission_briefing
		return condition

	@property
	def location_index(self) -> int:
		return self.fields[0]
	@location_index.setter
	def location_index(self, index: int) -> None:
		self.fields[0] = index

	@property
	def player_group(self) -> int:
		return self.fields[1]
	@player_group.setter
	def player_group(self, group: int) -> None:
		self.fields[1] = group

	@property
	def number(self) -> int:
		return self.fields[2]
	@number.setter
	def number(self, value: int) -> None:
		self.fields[2] = value

	@property
	def unit_type(self) -> int:
		return self.fields[3]
	@unit_type.setter
	def unit_type(self, unit_type: int) -> None:
		self.fields[3] = unit_type

	@property
	def comparison(self) -> int:
		return self.fields[4]
	@comparison.setter
	def comparison(self, comparison: int) -> None:
		self.fields[4] = comparison

	@property
	def switch_state(self) -> int:
		return self.fields[4]
	@switch_state.setter
	def switch_state(self, state: int) -> None:
		self.fields[4] = state

	@property
	def condition_type(self) -> int:
		return self.fields[5]
	@condition_type.setter
	def condition_type(self, condition_type: int) -> None:
		self.fields[5] = condition_type

	@property
	def resource_type(self) -> int:
		return self.fields[6]
	@resource_type.setter
	def resource_type(self, resource_type: int) -> None:
		self.fields[6] = resource_type

	@property
	def score_type(self) -> int:
		return self.fields[6]
	@score_type.setter
	def score_type(self, score_type: int) -> None:
		self.fields[6] = score_type

	@property
	def switch_index(self) -> int:
		return self.fields[6]
	@switch_index.setter
	def switch_index(self, index: int) -> None:
		self.fields[6] = index

	@property
	def flags(self) -> int:
		return self.fields[7]
	@flags.setter
	def flags(self, flags: int) -> None:
		self.fields[7] = flags

	@property
	def masked(self) -> int:
		return self.fields[8]
	@masked.setter
	def masked(self, masked: int) -> None:
		self.fields[8] = masked

	def __eq__(self, other) -> bool:
		if not isinstance(other, Condition):
			return False
		if other.fields != self.fields:
			return False
		return True

	def __repr__(self) -> str:
		from .Conditions import get_definition
		definition = get_definition(self)
		return f'<{definition.name} condition = {self.fields}>'
