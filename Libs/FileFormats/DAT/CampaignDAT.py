
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Map(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.map_file = 0

	def load_values(self, values):
		self.map_file = values[0]

	def save_values(self):
		return (self.map_file,)

	def expand(self):
		self.map_file = self.map_file or 0

	def export_text(self, id):
		return """Map(%d):
	map_file %d""" % (
			id,
			self.map_file
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Map"
		data["_id"] = id
		data["map_file"] = self.map_file
		if not dump:
			return data
		return json.dumps(data, indent=indent)

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
