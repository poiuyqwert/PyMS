
import AbstractDAT
import DATFormat

class Portrait(object):
	def __init__(self):
		self.portrait_file = 0
		self.smk_change = 0
		self.unknown = 0

class Portraits(AbstractDAT.AbstractDATEntry):
	class Property:
		idle = 'idle'
		talking = 'talking'

	def __init__(self):
		self.idle = Portrait()
		self.talking = Portrait()

	def load_values(self, values):
		self.idle.portrait_file,\
		self.talking.portrait_file,\
		self.idle.smk_change,\
		self.talking.smk_change,\
		self.idle.unknown,\
		self.talking.unknown\
			= values

	def save_values(self):
		return (
			self.idle.portrait_file,
			self.talking.portrait_file,
			self.idle.smk_change,
			self.talking.smk_change,
			self.idle.unknown,
			self.talking.unknown
		)

	EXPORT_NAME = 'Portraits'
	def _export(self, export_properties, export_type, data):
		self._export_property_values(export_properties, Portraits.Property.idle, self.idle, lambda idle: (('portrait_file', idle.portrait_file), ('smk_change', idle.smk_change), ('unknown', idle.unknown)), export_type, data)
		self._export_property_values(export_properties, Portraits.Property.talking, self.talking, lambda talking: (('portrait_file', talking.portrait_file), ('smk_change', talking.smk_change), ('unknown', talking.unknown)), export_type, data)

# portdata.dat file handler
class PortraitsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 110,
			"expanded_max_entries": 65535,
			"properties": [
				{
					"name": "idle_portrait_file", # Pointer to portdata.tbl
					"type": "long"
				},
				{
					"name": "talking_portrait_file", # Pointer to portdata.tbl
					"type": "long"
				},
				{
					"name": "idle_smk_change",
					"type": "byte"
				},
				{
					"name": "talking_smk_change",
					"type": "byte"
				},
				{
					"name": "idle_unknown",
					"type": "byte"
				},
				{
					"name": "talking_unknown",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Portraits
	FILE_NAME = "portdata.dat"
