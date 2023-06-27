
from __future__ import annotations

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import IO

import struct

class Action:
	def __init__(self):
		self._fields = [0] * 11

	@staticmethod
	def no_action() -> Action:
		return Action()

	@property
	def location_index(self) -> int:
		return self._fields[0]
	@location_index.setter
	def location_index(self, index: int) -> None:
		self._fields[0] = index

	@property
	def string_index(self) -> int:
		return self._fields[1]
	@string_index.setter
	def string_index(self, index: int) -> None:
		self._fields[1] = index

	@property
	def wav_string_index(self) -> int:
		return self._fields[2]
	@wav_string_index.setter
	def wav_string_index(self, index: int) -> None:
		self._fields[2] = index

	@property
	def duration(self) -> int:
		return self._fields[3]
	@duration.setter
	def duration(self, duration: int) -> None:
		self._fields[3] = duration

	@property
	def player_group(self) -> int:
		return self._fields[4]
	@player_group.setter
	def player_group(self, group: int) -> None:
		self._fields[4] = group

	@property
	def slot(self) -> int:
		return self._fields[4]
	@slot.setter
	def slot(self, slot: int) -> None:
		self._fields[4] = slot

	@property
	def target_player_group(self) -> int:
		return self._fields[5]
	@target_player_group.setter
	def target_player_group(self, group: int) -> None:
		self._fields[5] = group

	@property
	def destination_location_index(self) -> int:
		return self._fields[5]
	@destination_location_index.setter
	def destination_location_index(self, index: int) -> None:
		self._fields[5] = index

	@property
	def unit_properties_index(self) -> int:
		return self._fields[5]
	@unit_properties_index.setter
	def unit_properties_index(self, index: int) -> None:
		self._fields[5] = index

	@property
	def number(self) -> int:
		return self._fields[5]
	@number.setter
	def number(self, number: int) -> None:
		self._fields[5] = number

	@property
	def ai_script_id(self) -> int:
		return self._fields[5]
	@ai_script_id.setter
	def ai_script_id(self, script_id: int) -> None:
		self._fields[5] = script_id

	@property
	def switch_index(self) -> int:
		return self._fields[5]
	@switch_index.setter
	def switch_index(self, index: int) -> None:
		self._fields[5] = index

	@property
	def unit_type(self) -> int:
		return self._fields[6]
	@unit_type.setter
	def unit_type(self, unit_type: int) -> None:
		self._fields[6] = unit_type

	@property
	def score_type(self) -> int:
		return self._fields[6]
	@score_type.setter
	def score_type(self, score_type: int) -> None:
		self._fields[6] = score_type

	@property
	def resource_type(self) -> int:
		return self._fields[6]
	@resource_type.setter
	def resource_type(self, resource_type: int) -> None:
		self._fields[6] = resource_type

	@property
	def alliance_status(self) -> int:
		return self._fields[6]
	@alliance_status.setter
	def alliance_status(self, status: int) -> None:
		self._fields[6] = status

	@property
	def action_type(self) -> int:
		return self._fields[7]
	@action_type.setter
	def action_type(self, action_type: int) -> None:
		self._fields[7] = action_type

	@property
	def quantity(self) -> int:
		return self._fields[8]
	@quantity.setter
	def quantity(self, count: int) -> None:
		self._fields[8] = count

	@property
	def switch_action(self) -> int:
		return self._fields[8]
	@switch_action.setter
	def switch_action(self, state: int) -> None:
		self._fields[8] = state

	@property
	def state_action(self) -> int:
		return self._fields[8]
	@state_action.setter
	def state_action(self, state: int) -> None:
		self._fields[8] = state

	@property
	def order(self) -> int:
		return self._fields[8]
	@order.setter
	def order(self, order: int) -> None:
		self._fields[8] = order

	@property
	def number_modifier(self) -> int:
		return self._fields[8]
	@number_modifier.setter
	def number_modifier(self, modifier: int) -> None:
		self._fields[8] = modifier

	@property
	def flags(self) -> int:
		return self._fields[9]
	@flags.setter
	def flags(self, flags: int) -> None:
		self._fields[9] = flags

	@property
	def masked(self) -> int:
		return self._fields[10]
	@masked.setter
	def masked(self, masked: int) -> None:
		self._fields[10] = masked

	STRUCT = struct.Struct('<6LH3B1xH')
	def load_data(self, scanner: BytesScanner):
		self._fields = list(scanner.scan_ints(Action.STRUCT))

	def save_data(self, output: IO.AnyOutputBytes):
		with IO.OutputBytes(output) as f:
			f.write(Action.STRUCT.pack(*self._fields))
