
import AbstractDAT
import DATFormat

class Sound(AbstractDAT.AbstractDATEntry):
	class Property:
		sound_file = 'sound_file'
		priority = 'priority'
		flags = 'flags'
		length_adjust = 'length_adjust'
		minimum_volume = 'minimum_volume'

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

	EXPORT_NAME = 'Sound'
	def _export(self, export_properties, export_type, data):
		self._export_property_value(export_properties, Sound.Property.sound_file, self.sound_file, export_type, data)
		self._export_property_value(export_properties, Sound.Property.priority, self.priority, export_type, data)
		self._export_property_value(export_properties, Sound.Property.flags, self.flags, export_type, data)
		self._export_property_value(export_properties, Sound.Property.length_adjust, self.length_adjust, export_type, data)
		self._export_property_value(export_properties, Sound.Property.minimum_volume, self.minimum_volume, export_type, data)

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
