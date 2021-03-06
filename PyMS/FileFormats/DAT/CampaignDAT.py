
import AbstractDAT
import DATFormat

class Map(AbstractDAT.AbstractDATEntry):
	class Property:
		map_file = 'map_file'

	def __init__(self):
		self.map_file = 0

	def load_values(self, values):
		self.map_file = values[0]

	def save_values(self):
		return (self.map_file,)

	EXPORT_NAME = 'Map'
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Map.Property.map_file, self.map_file, export_type, data)

# mapdata.dat file handler
class CampaignDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 65,
			"properties": [
				{
					"name": "map_file",
					"type": "long"
				}
			]
		})
	ENTRY_STRUCT = Map
	FILE_NAME = "mapdata.dat"
