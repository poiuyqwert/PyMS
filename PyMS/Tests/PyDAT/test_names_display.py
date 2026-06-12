
from ...PyDAT.NamesDisplay import NamesDisplaySetting
from ...FileFormats.DAT.Utilities import DataNamesUsage

import unittest


class Test_NamesDisplaySetting(unittest.TestCase):
	MAPPING = {
		NamesDisplaySetting.basic: DataNamesUsage.use,
		NamesDisplaySetting.tbl: DataNamesUsage.ignore,
		NamesDisplaySetting.combine: DataNamesUsage.combine,
	}

	def test_data_names_usage_mapping(self) -> None:
		for setting, usage in Test_NamesDisplaySetting.MAPPING.items():
			with self.subTest(setting=setting):
				self.assertEqual(setting.data_names_usage, usage)

	def test_from_data_names_usage_mapping(self) -> None:
		for setting, usage in Test_NamesDisplaySetting.MAPPING.items():
			with self.subTest(usage=usage):
				self.assertEqual(NamesDisplaySetting.from_data_names_usage(usage), setting)

	def test_round_trip_from_setting(self) -> None:
		for setting in NamesDisplaySetting:
			with self.subTest(setting=setting):
				self.assertEqual(NamesDisplaySetting.from_data_names_usage(setting.data_names_usage), setting)

	def test_round_trip_from_usage(self) -> None:
		for usage in DataNamesUsage:
			with self.subTest(usage=usage):
				self.assertEqual(NamesDisplaySetting.from_data_names_usage(usage).data_names_usage, usage)
