
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Flingy(AbstractDAT.AbstractDATEntry):
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

	def expand(self):
		self.sprite = self.sprite or 0
		self.speed = self.speed or 0
		self.acceleration = self.acceleration or 0
		self.halt_distance = self.halt_distance or 0
		self.turn_radius = self.turn_radius or 0
		self.iscript_mask = self.iscript_mask or 0
		self.movement_control = self.movement_control or 0

	def export_text(self, id):
		return """Flingy(%d):
	sprite %d
	speed %d
	acceleration %d
	halt_distance %d
	turn_radius %d
	iscript_mask %d
	movement_control %d""" % (
			id,
			self.sprite,
			self.speed,
			self.acceleration,
			self.halt_distance,
			self.turn_radius,
			self.iscript_mask,
			self.movement_control
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Flingy"
		data["_id"] = id
		data["sprite"] = self.sprite
		data["speed"] = self.speed
		data["acceleration"] = self.acceleration
		data["halt_distance"] = self.halt_distance
		data["turn_radius"] = self.turn_radius
		data["iscript_mask"] = self.iscript_mask
		data["movement_control"] = self.movement_control
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# flingy.dat file handler
class FlingyDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 209,
			"properties": [
				{
					"name": "sprite",
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
