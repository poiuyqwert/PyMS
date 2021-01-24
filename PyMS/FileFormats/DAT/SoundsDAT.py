
import AbstractDAT
import DATFormat

from collections import OrderedDict
import json

class Sound(AbstractDAT.AbstractDATEntry):
	class Flag:
		preload       = 1 << 0
		unit_speech   = 1 << 1
		_internal     = 1 << 2
		_internal2    = 1 << 3
		one_at_a_time = 1 << 4
		never_preempt = 1 << 5

	def __init__(self):
		self.sound_file = 0
		self.priority = 0
		self.flags = 0
		self.length_adjust = 0
		self.minimum_volume = 0

	def load_values(self, values):
		self.sound_file,\
		self.priority,\
		self.flags,\
		self.length_adjust,\
		self.minimum_volume\
			= values

	def save_values(self):
		return (
			self.sound_file,
			self.priority,
			self.flags,
			self.length_adjust,
			self.minimum_volume
		)

	def expand(self):
		self.sound_file = self.sound_file or 0
		self.priority = self.priority or 0
		self.flags = self.flags or 0
		self.length_adjust = self.length_adjust or 0
		self.minimum_volume = self.minimum_volume or 0

	def export_text(self, id):
		return """Sound(%d):
	sound_file %d
	priority %d
	flags %d
	length_adjust %d
	minimum_volume %d""" % (
			id,
			self.sound_file,
			self.priority,
			self.flags,
			self.length_adjust,
			self.minimum_volume
		)

	def export_json(self, id, dump=True, indent=4):
		data = OrderedDict()
		data["_type"] = "Sound"
		data["_id"] = id
		data["sound_file"] = self.sound_file
		data["priority"] = self.priority
		data["flags"] = self.flags
		data["length_adjust"] = self.length_adjust
		data["minimum_volume"] = self.minimum_volume
		if not dump:
			return data
		return json.dumps(data, indent=indent)

# sfxdata.dat file handler
class SoundsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 1144,
			"properties": [
				{
					"name": "sound_file",
					"type": "long"
				},
				{
					"name": "priority",
					"type": "byte"
				},
				{
					"name": "flags",
					"type": "byte"
				},
				{
					"name": "length_adjust",
					"type": "short"
				},
				{
					"name": "minimum_volume",
					"type": "byte"
				}
			]
		})
	ENTRY_STRUCT = Sound
	FILE_NAME = "sfxdata.dat"
