
from .utils import make_chk_with_dim
from ...FileFormats.CHK.Sections.CHKSectionMTXM import CHKSectionMTXM

import struct
import unittest


class Test_CHKSectionMTXM(unittest.TestCase):
	def _raw(self) -> bytes:
		# 2x2 tiles, each value = (group << 4) | misc.
		return struct.pack('<4H', 0x12, 0x34, 0x56, 0x78)

	def test_process_data_splits_group_and_misc(self) -> None:
		section = CHKSectionMTXM(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertEqual(section.map, [[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

	def test_round_trip_is_byte_identical(self) -> None:
		raw = self._raw()
		section = CHKSectionMTXM(make_chk_with_dim(2, 2))
		section.load_data(raw)
		section.process_data()
		self.assertEqual(section.save_data(), raw)

	def test_process_data_is_idempotent(self) -> None:
		section = CHKSectionMTXM(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		first = section.map
		section.process_data()
		self.assertIs(section.map, first)

	def test_decompile(self) -> None:
		section = CHKSectionMTXM(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertTrue(section.decompile().startswith('MTXM:'))
