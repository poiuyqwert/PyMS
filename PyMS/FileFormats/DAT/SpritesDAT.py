
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Sprite(AbstractDAT.AbstractDATEntry):
	class Property:
		image = 'image'
		health_bar = 'health_bar'
		unused = 'unused'
		is_visible = 'is_visible'
		selection_circle_image = 'selection_circle_image'
		selection_circle_offset = 'selection_circle_offset'

	def __init__(self):
		self.image = 0
		self.health_bar = 0
		self.unused = 0
		self.is_visible = 0
		self.selection_circle_image = 0
		self.selection_circle_offset = 0

	def load_values(self, values):
		self.image,\
		self.health_bar,\
		self.unused,\
		self.is_visible,\
		self.selection_circle_image,\
		self.selection_circle_offset\
			= values

	def save_values(self):
		return (
			self.image,
			self.health_bar,
			self.unused,
			self.is_visible,
			self.selection_circle_image,
			self.selection_circle_offset,
		)

	def limit(self, id):
		if not SpritesDAT.FORMAT.get_property('health_bar').is_on_entry(id):
			self.health_bar = None
		if not SpritesDAT.FORMAT.get_property('selection_circle_image').is_on_entry(id):
			self.selection_circle_image = None
		if not SpritesDAT.FORMAT.get_property('selection_circle_offset').is_on_entry(id):
			self.selection_circle_offset = None

	def expand(self):
		self.health_bar = self.health_bar or 0
		self.selection_circle_image = self.selection_circle_image or 0
		self.selection_circle_offset = self.selection_circle_offset or 0

	EXPORT_NAME = 'Sprite'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Sprite.Property.image, self.image, data)
		self._export_property_value(export_properties, Sprite.Property.health_bar, self.health_bar, data)
		self._export_property_value(export_properties, Sprite.Property.unused, self.unused, data, _SpritePropertyCoder.unused)
		self._export_property_value(export_properties, Sprite.Property.is_visible, self.is_visible, data, _SpritePropertyCoder.is_visible)
		self._export_property_value(export_properties, Sprite.Property.selection_circle_image, self.selection_circle_image, data)
		self._export_property_value(export_properties, Sprite.Property.selection_circle_offset, self.selection_circle_offset, data)

	def _import_data(self, data):
		image = self._import_property_value(data, Sprite.Property.image)
		health_bar = self._import_property_value(data, Sprite.Property.health_bar, allowed=(self.health_bar != None))
		unused = self._import_property_value(data, Sprite.Property.unused, _SpritePropertyCoder.unused)
		is_visible = self._import_property_value(data, Sprite.Property.is_visible, _SpritePropertyCoder.is_visible)
		selection_circle_image = self._import_property_value(data, Sprite.Property.selection_circle_image, allowed=(self.selection_circle_image != None))
		selection_circle_offset = self._import_property_value(data, Sprite.Property.selection_circle_offset, allowed=(self.selection_circle_offset != None))

		if image != None:
			self.image = image
		if health_bar != None:
			self.health_bar = health_bar
		if unused != None:
			self.unused = unused
		if is_visible != None:
			self.is_visible = is_visible
		if selection_circle_image != None:
			self.selection_circle_image = selection_circle_image
		if selection_circle_offset != None:
			self.selection_circle_offset = selection_circle_offset

class _SpritePropertyCoder:
	unused = DATCoders.DATBoolCoder()
	is_visible = DATCoders.DATBoolCoder()

# sprites.dat file handler
class SpritesDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 517,
			"expanded_max_entries": 65536,
			"properties": [
				{
					"name": "image", # Pointer to images.dat
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
					"name": "selection_circle_image", # Pointer to images.dat (starting at 561)
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

	def get_entry(self, index): # type: (int) -> Sprite
		return super(SpritesDAT, self).get_entry(index)
