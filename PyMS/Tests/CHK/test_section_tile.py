
from .utils import make_chk_with_dim
from ...FileFormats.CHK.Sections.CHKSectionTILE import CHKSectionTILE

import struct
import unittest


class Test_CHKSectionTILE(unittest.TestCase):
	def _raw(self) -> bytes:
		return struct.pack('<4H', 0x12, 0x34, 0x56, 0x78)

	def test_process_data_splits_group_and_misc(self) -> None:
		section = CHKSectionTILE(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertEqual(section.map, [[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

	def test_round_trip_is_byte_identical(self) -> None:
		raw = self._raw()
		section = CHKSectionTILE(make_chk_with_dim(2, 2))
		section.load_data(raw)
		section.process_data()
		self.assertEqual(section.save_data(), raw)

	def test_decompile(self) -> None:
		section = CHKSectionTILE(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertTrue(section.decompile().startswith('TILE:'))
