
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Sprite(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.image_file = 0
		self.health_bar = 0
		self.unused = 0
		self.is_visible = 0
		self.selection_circle_image = 0
		self.selection_circle_offset = 0

	def load_values(self, values):
		self.image_file,\
		self.health_bar,\
		self.unused,\
		self.is_visible,\
		self.selection_circle_image,\
		self.selection_circle_offset\
			= values

	def save_values(self):
		return (
			self.image_file,
			self.health_bar,
			self.unused,
			self.is_visible,
			self.selection_circle_image,
			self.selection_circle_offset,
		)

	def expand(self):
		self.image_file = self.image_file or 0
		self.health_bar = self.health_bar or 0
		self.unused = self.unused or 0
		self.is_visible = self.is_visible or 0
		self.selection_circle_image = self.selection_circle_image or 0
		self.selection_circle_offset = self.selection_circle_offset or 0

	def export_text(self, id):
		return """Sprite(%d):
	image_file %d
	health_bar %d
	unused %d
	is_visible %d
	selection_circle_image %d
	selection_circle_offset %d""" % (
			id,
			self.image_file,
			self.health_bar,
			self.unused,
			self.is_visible,
			self.selection_circle_image,
			self.selection_circle_offset
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Sprite"
		data["_id"] = id
		data["image_file"] = self.image_file
		data["health_bar"] = self.health_bar
		data["unused"] = self.unused
		data["is_visible"] = self.is_visible
		data["selection_circle_image"] = self.selection_circle_image
		data["selection_circle_offset"] = self.selection_circle_offset
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# sprites.dat file handler
class SpritesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 517,
			"properties": [
				{
					"name": "image_file",
					"type": "short"
				},
				{
					"name": "health_bar",
					"type": "byte",
					"entry_offset": 130,
					"entry_count": 387
				},
				{
					"name": "unused",
					"type": "byte"
				},
				{
					"name": "is_visible",
					"type": "byte"
				},
				{
					"name": "selection_circle_image",
					"type": "byte",
					"entry_offset": 130,
					"entry_count": 387
				},
				{
					"name": "selection_circle_offset",
					"type": "byte",
					"entry_offset": 130,
					"entry_count": 387
				}
			]
		})
	ENTRY_STRUCT = Sprite
	FILE_NAME = "sprites.dat"
