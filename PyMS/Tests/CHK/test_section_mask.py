
from .utils import make_chk_with_dim
from ...FileFormats.CHK.Sections.CHKSectionMASK import CHKSectionMASK

import struct
import unittest


class Test_CHKSectionMASK(unittest.TestCase):
	def _raw(self) -> bytes:
		# 2x2 grid, one mask byte per tile.
		return struct.pack('<4B', 0x0F, 0xF0, 0xAA, 0x55)

	def test_process_data_builds_rows(self) -> None:
		section = CHKSectionMASK(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertEqual(section.map, [[0x0F, 0xF0], [0xAA, 0x55]])

	def test_round_trip_is_byte_identical(self) -> None:
		raw = self._raw()
		section = CHKSectionMASK(make_chk_with_dim(2, 2))
		section.load_data(raw)
		section.process_data()
		self.assertEqual(section.save_data(), raw)

	def test_short_data_is_padded_with_full_mask(self) -> None:
		# Missing tiles default to a fully-set mask byte.
		section = CHKSectionMASK(make_chk_with_dim(2, 2))
		section.load_data(b'\x01\x02')
		section.process_data()
		self.assertEqual(section.map, [[0x01, 0x02], [0xFF, 0xFF]])

	def test_decompile(self) -> None:
		section = CHKSectionMASK(make_chk_with_dim(2, 2))
		section.load_data(self._raw())
		section.process_data()
		self.assertTrue(section.decompile().startswith('MASK:'))
