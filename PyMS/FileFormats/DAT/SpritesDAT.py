
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

from collections import OrderedDict

from typing import cast, Any

class DATSprite(AbstractDAT.AbstractDATEntry):
	class Property:
		image = 'image'
		health_bar = 'health_bar'
		unused = 'unused'
		is_visible = 'is_visible'
		selection_circle_image = 'selection_circle_image'
		selection_circle_offset = 'selection_circle_offset'

	def __init__(self) -> None:
		self.image: int = 0
		self.health_bar: int | None = 0
		self.unused: int = 0
		self.is_visible: int = 0
		self.selection_circle_image: int | None = 0
		self.selection_circle_offset: int | None = 0

	def load_values(self, values: tuple[int | DATFormat.DATType | None, ...]) -> None:
		self.image,\
		self.health_bar,\
		self.unused,\
		self.is_visible,\
		self.selection_circle_image,\
		self.selection_circle_offset\
			= values # type: ignore[assignment]

	def save_values(self) -> tuple[int | DATFormat.DATType | None, ...]:
		return (
			self.image,
			self.health_bar,
			self.unused,
			self.is_visible,
			self.selection_circle_image,
			self.selection_circle_offset,
		)

	def limit(self, entry_id: int) -> None:
		health_bar_prop = SpritesDAT.FORMAT.get_property(DATSprite.Property.health_bar)
		assert health_bar_prop is not None
		if not health_bar_prop.is_on_entry(entry_id):
			self.health_bar = None

		selection_circle_image_prop = SpritesDAT.FORMAT.get_property(DATSprite.Property.selection_circle_image)
		assert selection_circle_image_prop is not None
		if not selection_circle_image_prop.is_on_entry(entry_id):
			self.selection_circle_image = None

		selection_circle_offset_prop = SpritesDAT.FORMAT.get_property(DATSprite.Property.selection_circle_offset)
		assert selection_circle_offset_prop is not None
		if not selection_circle_offset_prop.is_on_entry(entry_id):
			self.selection_circle_offset = None

	def expand(self) -> None:
		self.health_bar = self.health_bar or 0
		self.selection_circle_image = self.selection_circle_image or 0
		self.selection_circle_offset = self.selection_circle_offset or 0

	EXPORT_NAME = 'Sprite'
	def _export_data(self, export_properties: list[str] | None, data: OrderedDict[str, Any]) -> None:
		self._export_property_value(export_properties, DATSprite.Property.image, self.image, data)
		self._export_property_value(export_properties, DATSprite.Property.health_bar, self.health_bar, data)
		self._export_property_value(export_properties, DATSprite.Property.unused, self.unused, data, property_encoder=_SpritePropertyCoder.unused)
		self._export_property_value(export_properties, DATSprite.Property.is_visible, self.is_visible, data, property_encoder=_SpritePropertyCoder.is_visible)
		self._export_property_value(export_properties, DATSprite.Property.selection_circle_image, self.selection_circle_image, data)
		self._export_property_value(export_properties, DATSprite.Property.selection_circle_offset, self.selection_circle_offset, data)

	def _import_data(self, data: dict[str, Any]) -> None:
		image = self._import_property_value(data, DATSprite.Property.image)
		health_bar = self._import_property_value(data, DATSprite.Property.health_bar, allowed=(self.health_bar is not None))
		unused = self._import_property_value(data, DATSprite.Property.unused, _SpritePropertyCoder.unused)
		is_visible = self._import_property_value(data, DATSprite.Property.is_visible, _SpritePropertyCoder.is_visible)
		selection_circle_image = self._import_property_value(data, DATSprite.Property.selection_circle_image, allowed=(self.selection_circle_image is not None))
		selection_circle_offset = self._import_property_value(data, DATSprite.Property.selection_circle_offset, allowed=(self.selection_circle_offset is not None))

		if image is not None:
			self.image = image
		if health_bar is not None:
			self.health_bar = health_bar
		if unused is not None:
			self.unused = unused
		if is_visible is not None:
			self.is_visible = is_visible
		if selection_circle_image is not None:
			self.selection_circle_image = selection_circle_image
		if selection_circle_offset is not None:
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
	ENTRY_STRUCT = DATSprite
	FILE_NAME = "sprites.dat"

	def get_entry(self, index: int) -> DATSprite:
		return cast(DATSprite, super().get_entry(index))
