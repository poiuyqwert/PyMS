
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

class Sound(AbstractDAT.AbstractDATEntry):
	class Property:
		sound_file = 'sound_file'
		priority = 'priority'
		flags = 'flags'
		portrait_length_adjust = 'portrait_length_adjust'
		minimum_volume = 'minimum_volume'

	class Flag:
		preload       = 1 << 0
		unit_speech   = 1 << 1
		one_at_a_time = 1 << 4
		never_preempt = 1 << 5

		ALL_FLAGS = (preload | unit_speech | one_at_a_time | never_preempt)

	def __init__(self):
		self.sound_file = 0
		self.priority = 0
		self.flags = 0
		self.portrait_length_adjust = 0
		self.minimum_volume = 0

	def load_values(self, values):
		self.sound_file,\
		self.priority,\
		self.flags,\
		self.portrait_length_adjust,\
		self.minimum_volume\
			= values

	def save_values(self):
		return (
			self.sound_file,
			self.priority,
			self.flags,
			self.portrait_length_adjust,
			self.minimum_volume
		)

	EXPORT_NAME = 'Sound'
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Sound.Property.sound_file, self.sound_file, data)
		self._export_property_value(export_properties, Sound.Property.priority, self.priority, data)
		self._export_property_value(export_properties, Sound.Property.flags, self.flags, data, _SoundPropertyCoder.flags)
		self._export_property_value(export_properties, Sound.Property.portrait_length_adjust, self.portrait_length_adjust, data)
		self._export_property_value(export_properties, Sound.Property.minimum_volume, self.minimum_volume, data)

	def _import_data(self, data):
		sound_file = self._import_property_value(data, Sound.Property.sound_file)
		priority = self._import_property_value(data, Sound.Property.priority)
		flags = self._import_property_value(data, Sound.Property.flags, _SoundPropertyCoder.flags)
		portrait_length_adjust = self._import_property_value(data, Sound.Property.portrait_length_adjust)
		minimum_volume = self._import_property_value(data, Sound.Property.minimum_volume)

		if sound_file != None:
			self.sound_file = sound_file
		if priority != None:
			self.priority = priority
		if flags != None:
			self.flags = flags
		if portrait_length_adjust != None:
			self.portrait_length_adjust = portrait_length_adjust
		if minimum_volume != None:
			self.minimum_volume = minimum_volume

class _SoundPropertyCoder:
	flags = DATCoders.DATFlagsCoder(6, {
		Sound.Flag.preload: 'preload',
		Sound.Flag.unit_speech: 'unit_speech',
		Sound.Flag.one_at_a_time: 'one_at_a_time',
		Sound.Flag.never_preempt: 'never_preempt'
	})

# sfxdata.dat file handler
class SoundsDAT(AbstractDAT.AbstractDAT):
	FORMAT = DATFormat.DATFormat({
			"entries": 1144,
			"expanded_max_entries": 65536,
			"properties": [
				{
					"name": "sound_file", # Pointer to sfxdata.tbl
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
					"name": "portrait_length_adjust",
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

	def get_entry(self, index): # type: (int) -> Sound
		return super(SoundsDAT, self).get_entry(index)
