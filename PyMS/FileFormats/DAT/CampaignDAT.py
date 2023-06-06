
from . import AbstractDAT
from . import DATFormat

from typing import cast

class DATMap(AbstractDAT.AbstractDATEntry):
	class Property:
		map_file = 'map_file'

	def __init__(self):
		self.map_file = 0

	def load_values(self, values):
		self.map_file = values[0]

	def save_values(self):
		return (self.map_file,)

	EXPORT_NAME = 'Map'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, DATMap.Property.map_file, self.map_file, data)

	def _import_data(self, data):
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

	def get_entry(self, index): # type: (int) -> DATMap
		return cast(DATMap, super(CampaignDAT, self).get_entry(index))
