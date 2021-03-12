
import AbstractDAT
import DATFormat

class Flingy(AbstractDAT.AbstractDATEntry):
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
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Flingy.Property.sprite, self.sprite, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.speed, self.speed, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.acceleration, self.acceleration, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.halt_distance, self.halt_distance, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.turn_radius, self.turn_radius, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.iscript_mask, self.iscript_mask, export_type, data)
		self._export_property_value(export_properties, Flingy.Property.movement_control, self.movement_control, export_type, data)

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
	ENTRY_STRUCT = Flingy
	FILE_NAME = "flingy.dat"
