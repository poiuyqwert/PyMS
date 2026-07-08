
from ...PyMPQ.CompressionSetting import CompressionOption, CompressionSetting
from ...FileFormats.MPQ.SFmpq import Z_DEFAULT_COMPRESSION, MAWA_QUALITY_MEDIUM
from ...Utilities.PyMSError import PyMSError

import unittest


class Test_parse_value(unittest.TestCase):
	def test_type_without_level(self) -> None:
		setting = CompressionSetting.parse_value('standard')
		self.assertEqual(setting.type, CompressionOption.Standard)
		self.assertEqual(setting.level, 0)

	def test_type_with_level(self) -> None:
		setting = CompressionSetting.parse_value('deflate:6')
		self.assertEqual(setting.type, CompressionOption.Deflate)
		self.assertEqual(setting.level, 6)

	def test_level_is_clamped(self) -> None:
		setting = CompressionSetting.parse_value('deflate:100')
		self.assertEqual(setting.type, CompressionOption.Deflate)
		self.assertEqual(setting.level, CompressionOption.Deflate.level_count() - 1)

	def test_negative_level_is_clamped(self) -> None:
		setting = CompressionSetting.parse_value('deflate:-5')
		self.assertEqual(setting.type, CompressionOption.Deflate)
		self.assertEqual(setting.level, 0)

	def test_unknown_type_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CompressionSetting.parse_value('bogus')
		self.assertIn('Invalid compression type', str(cm.exception))

	def test_unknown_type_with_level_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CompressionSetting.parse_value('bogus:3')
		self.assertIn('Invalid compression type', str(cm.exception))

	def test_non_numeric_level_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CompressionSetting.parse_value('deflate:high')
		self.assertIn("Invalid compression level 'high' for compression type 'deflate'", str(cm.exception))

	def test_empty_value_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CompressionSetting.parse_value('')
		self.assertIn('Invalid compression type', str(cm.exception))

	def test_round_trips_through_str(self) -> None:
		for option in CompressionOption:
			for level in range(max(1, option.level_count())):
				setting = option.setting(level)
				self.assertEqual(CompressionSetting.parse_value(str(setting)), setting)


class Test_display_name(unittest.TestCase):
	def test_every_option_has_a_name(self) -> None:
		for option in CompressionOption:
			self.assertTrue(option.display_name())


class Test_level_name(unittest.TestCase):
	def test_types_without_levels_have_no_level_name(self) -> None:
		for option in (CompressionOption.NoCompression, CompressionOption.Standard, CompressionOption.Auto):
			self.assertEqual(option.setting().level_name(), '')

	def test_deflate_default_level(self) -> None:
		levels = CompressionOption.Deflate.compression_levels()
		setting = CompressionOption.Deflate.setting(levels.index(Z_DEFAULT_COMPRESSION))
		self.assertEqual(setting.level_name(), 'Default')

	def test_audio_medium_level(self) -> None:
		levels = CompressionOption.Audio.compression_levels()
		setting = CompressionOption.Audio.setting(levels.index(MAWA_QUALITY_MEDIUM))
		self.assertEqual(setting.level_name(), 'Medium')
