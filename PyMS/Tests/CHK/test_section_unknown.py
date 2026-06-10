
from .utils import make_chk
from ...FileFormats.CHK.CHKSectionUnknown import CHKSectionUnknown
from ...FileFormats.CHK.CHKSection import CHKSection

import unittest


class Test_CHKSectionUnknown(unittest.TestCase):
	def test_preserves_name_and_raw_data(self) -> None:
		section = CHKSectionUnknown(make_chk(), b'XXXX')
		section.load_data(b'arbitrary')
		self.assertEqual(section.NAME, b'XXXX')
		self.assertEqual(section.save_data(), b'arbitrary')

	def test_round_trip_is_byte_identical(self) -> None:
		section = CHKSectionUnknown(make_chk(), b'ZZZZ')
		data = bytes(range(64))
		section.load_data(data)
		self.assertEqual(section.save_data(), data)


class Test_CHKSection(unittest.TestCase):
	def test_base_methods_raise(self) -> None:
		section = CHKSection(make_chk())
		self.assertRaises(NotImplementedError, section.load_data, b'')
		self.assertRaises(NotImplementedError, section.save_data)
		self.assertRaises(NotImplementedError, section.decompile)

	def test_default_no_post_processing(self) -> None:
		self.assertFalse(CHKSection(make_chk()).requires_post_processing())
