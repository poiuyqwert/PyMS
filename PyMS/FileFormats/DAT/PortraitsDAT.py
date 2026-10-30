
from . import AbstractDAT
from . import DATFormat
from . import DATCoders

from ...Utilities.PyMSError import PyMSError

from collections import OrderedDict

from typing import cast, Any

class DATPortrait:
	def __init__(self) -> None:
		self.portrait_file: int = 0
		self.smk_change: int = 0
		self.unknown: int = 0

class DATPortraits(AbstractDAT.AbstractDATEntry):
	class Property:
		idle = 'idle'
		talking = 'talking'

	def __init__(self) -> None:
		self.idle = DATPortrait()
		self.talking = DATPortrait()

	def load_values(self, values: tuple[int | DATFormat.DATType | None, ...]) -> None:
		self.idle.portrait_file,\
		self.talking.portrait_file,\
		self.idle.smk_change,\
		self.talking.smk_change,\
		self.idle.unknown,\
		self.talking.unknown\
			= values # type: ignore[assignment]

	def save_values(self) -> tuple[int | DATFormat.DATType | None, ...]:
		return (
			self.idle.portrait_file,
			self.talking.portrait_file,
			self.idle.smk_change,
			self.talking.smk_change,
			self.idle.unknown,
			self.talking.unknown
		)

	EXPORT_NAME = 'Portraits'
	def _export_data(self, export_properties: list[str] | None, data: OrderedDict[str, Any]) -> None:
		self._export_property_value(export_properties, DATPortraits.Property.idle, self.idle, data, property_encoder=_PortraitsPropertyCoder.idle)
		self._export_property_value(export_properties, DATPortraits.Property.talking, self.talking, data, property_encoder=_PortraitsPropertyCoder.talking)

	def _import_data(self, data: dict[str, Any]) -> None:
		idle = self._import_property_value(data, DATPortraits.Property.idle, _PortraitsPropertyCoder.idle)
		talking = self._import_property_value(data, DATPortraits.Property.talking, _PortraitsPropertyCoder.talking)

		if idle is not None:
			self.idle = idle
		if talking is not None:
			self.talking = talking

class DATPortraitCoder(DATCoders.DATPropertyCoder):
	def encode(self, portrait: DATPortrait) -> OrderedDict[str, int]:
		values = OrderedDict()
		values['portrait_file'] = portrait.portrait_file
		values['smk_change'] = portrait.smk_change
		values['unknown'] = portrait.unknown
		return values

	def decode(self, values: dict[str, int]) -> DATPortrait:
		if not 'portrait_file' in values:
			raise PyMSError('Decode', 'Portrait missing `portrait_file` value')
		if not 'smk_change' in values:
			raise PyMSError('Decode', 'Portrait missing `smk_change` value')
		if not 'unknown' in values:
			raise PyMSError('Decode', 'Portrait missing `unknown` value')
		portrait = DATPortrait()
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
	ENTRY_STRUCT = DATPortraits
	FILE_NAME = "portdata.dat"

	def get_entry(self, index: int) -> DATPortraits:
		return cast(DATPortraits, super().get_entry(index))
