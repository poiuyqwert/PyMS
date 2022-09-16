
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

from ...Utilities.PyMSError import PyMSError

from collections import OrderedDict

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
	def _export_data(self, export_properties, data):
		self._export_property_value(export_properties, Portraits.Property.idle, self.idle, data, _PortraitsPropertyCoder.idle)
		self._export_property_value(export_properties, Portraits.Property.talking, self.talking, data, _PortraitsPropertyCoder.talking)

	def _import_data(self, data):
		idle = self._import_property_value(data, Portraits.Property.idle, _PortraitsPropertyCoder.idle)
		talking = self._import_property_value(data, Portraits.Property.talking, _PortraitsPropertyCoder.talking)

		if idle != None:
			self.idle = idle
		if talking != None:
			self.talking = talking

class DATPortraitCoder(DATCoders.DATPropertyCoder):
	def encode(self, portrait): # type: (Portrait) -> OrderedDict[str, int]
		values = OrderedDict()
		values['portrait_file'] = portrait.portrait_file
		values['smk_change'] = portrait.smk_change
		values['unknown'] = portrait.unknown
		return values

	def decode(self, values): # type: (dict[str, int]) -> Portrait
		if not 'portrait_file' in values:
			raise PyMSError('Decode', 'Portrait missing `portrait_file` value')
		if not 'smk_change' in values:
			raise PyMSError('Decode', 'Portrait missing `smk_change` value')
		if not 'unknown' in values:
			raise PyMSError('Decode', 'Portrait missing `unknown` value')
		portrait = Portrait()
		portrait.portrait_file = values['portrait_file']
		portrait.smk_change = values['smk_change']
		portrait.unknown = values['unknown']
		return portrait

class _PortraitsPropertyCoder:
	idle = DATPortraitCoder()
	talking = DATPortraitCoder()

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

	def get_entry(self, index): # type: (int) -> Portraits
		return super(PortraitsDAT, self).get_entry(index)
