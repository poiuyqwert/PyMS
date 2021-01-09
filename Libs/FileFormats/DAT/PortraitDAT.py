
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Portrait(object):
	def __init__(self):
		self.portrait_file = 0
		self.smk_change = 0
		self.unknown = 0

class Portraits(AbstractDAT.AbstractDATEntry):
	def __init__(self):
		self.idle = Portrait()
		self.talking = Portrait()
		# self.idle_portrait_file = 0
		# self.talking_portrait_file = 0
		# self.idle_smk_change = 0
		# self.talking_smk_change = 0
		# self.idle_unknown = 0
		# self.talking_unknown = 0

	def load_values(self, values):
		self.idle.portrait_file,\
		self.talking.portrait_file,\
		self.idle.smk_change,\
		self.talking.smk_change,\
		self.idle.unknown,\
		self.talking.unknown\
			= values
		# self.idle_portrait_file,\
		# self.talking_portrait_file,\
		# self.idle_smk_change,\
		# self.talking_smk_change,\
		# self.idle_unknown,\
		# self.talking_unknown\
		#	= values

	def save_values(self):
		return (
			self.idle.portrait_file,
			self.talking.portrait_file,
			self.idle.smk_change,
			self.talking.smk_change,
			self.idle.unknown,
			self.talking.unknown
			# self.idle_portrait_file,
			# self.talking_portrait_file,
			# self.idle_smk_change,
			# self.talking_smk_change,
			# self.idle_unknown,
			# self.talking_unknown
		)

	def expand(self):
		self.idle = self.idle or Portrait()
		self.talking = self.talking or Portrait()
		self.idle.portrait_file = self.idle.portrait_file or 0
		self.talking.portrait_file = self.talking.portrait_file or 0
		self.idle.smk_change = self.idle.smk_change or 0
		self.talking.smk_change = self.talking.smk_change or 0
		self.idle.unknown = self.idle.unknown or 0
		self.talking.unknown = self.talking.unknown or 0
		# self.idle_portrait_file = self.idle_portrait_file or 0
		# self.talking_portrait_file = self.talking_portrait_file or 0
		# self.idle_smk_change = self.idle_smk_change or 0
		# self.talking_smk_change = self.talking_smk_change or 0
		# self.idle_unknown = self.idle_unknown or 0
		# self.talking_unknown = self.talking_unknown or 0

	def export_text(self, id):
		return """Portraits(%d):
	idle.portrait_file %d
	idle.smk_change %d
	idle.unknown %d
	talking.portrait_file %d
	talking.smk_change %d
	talking.unknown %d""" % (
			id,
			self.idle.portrait_file,
			self.idle.smk_change,
			self.idle.unknown,
			self.talking.portrait_file,
			self.talking.smk_change,
			self.talking.unknown
			# self.idle_portrait_file,
			# self.idle_smk_change,
			# self.idle_unknown,
			# self.talking_portrait_file,
			# self.talking_smk_change,
			# self.talking_unknown
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Portraits"
		data["_id"] = id
		idle = OrderedDict()
		idle["portrait_file"] = self.idle.portrait_file
		idle["smk_change"] = self.idle.smk_change
		idle["unknown"] = self.idle.unknown
		# idle["portrait_file"] = self.idle_portrait_file
		# idle["smk_change"] = self.idle_smk_change
		# idle["unknown"] = self.idle_unknown
		data["idle"] = idle
		talking = OrderedDict()
		talking["portrait_file"] = self.talking.portrait_file
		talking["smk_change"] = self.talking.smk_change
		talking["unknown"] = self.talking.unknown
		# talking["portrait_file"] = self.talking_portrait_file
		# talking["smk_change"] = self.talking_smk_change
		# talking["unknown"] = self.talking_unknown
		data["talking"] = talking
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# portdata.dat file handler
class PortraitDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 110,
			"properties": [
				{
					"name": "idle_portrait_file",
					"type": "long"
				},
				{
					"name": "talking_portrait_file",
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
