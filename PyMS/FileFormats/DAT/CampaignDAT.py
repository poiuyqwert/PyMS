
from . import AbstractDAT
from . import DATFormat

from collections import OrderedDict

from typing import cast, Any

class DATMap(AbstractDAT.AbstractDATEntry):
	class Property:
		map_file = 'map_file'

	def __init__(self) -> None:
		self.map_file: int = 0

	def load_values(self, values: tuple[int | DATFormat.DATType | None, ...]) -> None:
		self.map_file = values[0] # type: ignore[assignment]

	def save_values(self) -> tuple[int | DATFormat.DATType | None, ...]:
		return (self.map_file,)

	EXPORT_NAME = 'Map'
	def _export_data(self, export_properties: list[str] | None, data: OrderedDict[str, Any]) -> None:
		self._export_property_value(export_properties, DATMap.Property.map_file, self.map_file, data)

	def _import_data(self, data: dict[str, Any]) -> None:
		map_file = self._import_property_value(data, DATMap.Property.map_file)

		if map_file is not None:
			self.map_file = map_file

# mapdata.dat file handler
class CampaignDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 65,
			"properties": [
				{
					"name": "map_file", # Pointer to mapdata.tbl
					"type": "long"
				}
			]
		})
	ENTRY_STRUCT = DATMap
	FILE_NAME = "mapdata.dat"

	def get_entry(self, index: int) -> DATMap:
		return cast(DATMap, super(CampaignDAT, self).get_entry(index))
