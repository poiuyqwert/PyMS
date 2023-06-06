
from . import AbstractDAT
from . import DATFormat

from typing import cast

class DATFlingy(AbstractDAT.AbstractDATEntry):
	class Property:
		sprite = 'sprite'
		speed = 'speed'
		acceleration = 'acceleration'
		halt_distance = 'halt_distance'
		turn_radius = 'turn_radius'
		iscript_mask = 'iscript_mask'
		movement_control = 'movement_control'

	def __init__(self):
		self.sprite = 0
		self.speed = 0
		self.acceleration = 0
		self.halt_distance = 0
		self.turn_radius = 0
		self.iscript_mask = 0
		self.movement_control = 0

	def load_values(self, values):
		self.sprite,\
		self.speed,\
		self.acceleration,\
		self.halt_distance,\
		self.turn_radius,\
		self.iscript_mask,\
		self.movement_control\
			= values

	def save_values(self):
		return (
			self.sprite,
			self.speed,
			self.acceleration,
			self.halt_distance,
			self.turn_radius,
			self.iscript_mask,
			self.movement_control
		)

	EXPORT_NAME = 'Flingy'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, DATFlingy.Property.sprite, self.sprite, data)
		self._export_property_value(export_properties, DATFlingy.Property.speed, self.speed, data)
		self._export_property_value(export_properties, DATFlingy.Property.acceleration, self.acceleration, data)
		self._export_property_value(export_properties, DATFlingy.Property.halt_distance, self.halt_distance, data)
		self._export_property_value(export_properties, DATFlingy.Property.turn_radius, self.turn_radius, data)
		self._export_property_value(export_properties, DATFlingy.Property.iscript_mask, self.iscript_mask, data)
		self._export_property_value(export_properties, DATFlingy.Property.movement_control, self.movement_control, data)

	def _import_data(self, data):
		sprite = self._import_property_value(data, DATFlingy.Property.sprite)
		speed = self._import_property_value(data, DATFlingy.Property.speed)
		acceleration = self._import_property_value(data, DATFlingy.Property.acceleration)
		halt_distance = self._import_property_value(data, DATFlingy.Property.halt_distance)
		turn_radius = self._import_property_value(data, DATFlingy.Property.turn_radius)
		iscript_mask = self._import_property_value(data, DATFlingy.Property.iscript_mask)
		movement_control = self._import_property_value(data, DATFlingy.Property.movement_control)

		if sprite is not None:
			self.sprite = sprite
		if speed is not None:
			self.speed = speed
		if acceleration is not None:
			self.acceleration = acceleration
		if halt_distance is not None:
			self.halt_distance = halt_distance
		if turn_radius is not None:
			self.turn_radius = turn_radius
		if iscript_mask is not None:
			self.iscript_mask = iscript_mask
		if movement_control is not None:
			self.movement_control = movement_control

# flingy.dat file handler
class FlingyDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 209,
			"expanded_max_entries": 65536,
			"properties": [
				{
					"name": "sprite", # Pointer to sprites.dat
					"type": "short"
				},
				{
					"name": "speed",
					"type": "long"
				},
				{
					"name": "acceleration",
					"type": "short"
				},
				{
					"name": "halt_distance",
					"type": "long"
				},
				{
					"name": "turn_radius",
					"type": "byte"
				},
				{
					"name": "iscript_mask",
					"type": "byte"
				},
				{
					"name": "movement_control",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = DATFlingy
	FILE_NAME = "flingy.dat"

	def get_entry(self, index): # type: (int) -> DATFlingy
		return cast(DATFlingy, super(FlingyDAT, self).get_entry(index))
