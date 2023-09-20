
from ..FileFormats.DAT.Utilities import DataNamesUsage

from enum import Enum

class NamesDisplaySetting(Enum):
	basic = 'basic'
	tbl = 'tbl'
	combine = 'combine'

	@property
	def data_names_usage(self) -> DataNamesUsage:
		match self:
			case NamesDisplaySetting.basic:
				return DataNamesUsage.use
			case NamesDisplaySetting.tbl:
				return DataNamesUsage.ignore
			case NamesDisplaySetting.combine:
				return DataNamesUsage.combine

	@staticmethod
	def from_data_names_usage(data_names_usage: DataNamesUsage) -> 'NamesDisplaySetting':
		match data_names_usage:
			case DataNamesUsage.use:
				return NamesDisplaySetting.basic
			case DataNamesUsage.ignore:
				return NamesDisplaySetting.tbl
			case DataNamesUsage.combine:
				return NamesDisplaySetting.combine
