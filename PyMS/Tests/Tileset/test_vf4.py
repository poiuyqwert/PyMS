
from ...FileFormats.Tileset.VF4 import VF4, VF4Megatile
from ...Utilities.PyMSError import PyMSError
from .utils import save_to_bytes

import io
import struct
import unittest


class Test_VF4Megatile(unittest.TestCase):
	def test_load_data(self) -> None:
		megatile = VF4Megatile()
		megatile.load_data(struct.pack('<16H', *range(16)))
		self.assertEqual(megatile.flags, list(range(16)))

	def test_save_data_round_trip(self) -> None:
		megatile = VF4Megatile()
		megatile.flags = [n * 2 for n in range(16)]
		reloaded = VF4Megatile()
		reloaded.load_data(megatile.save_data())
		self.assertEqual(reloaded, megatile)

	def test_equality(self) -> None:
		a = VF4Megatile()
		a.flags = [1] * 16
		b = VF4Megatile()
		b.flags = [1] * 16
		self.assertEqual(a, b)
		b.flags[0] = 2
		self.assertNotEqual(a, b)


class Test_VF4(unittest.TestCase):
	def _megatile(self, value: int) -> VF4Megatile:
		megatile = VF4Megatile()
		megatile.flags = [value] * 16
		return megatile

	def test_defaults(self) -> None:
		vf4 = VF4()
		self.assertEqual(vf4.megatile_count(), 0)
		self.assertEqual(vf4.megatiles_remaining(), VF4.MAX_ID + 1)

	def test_add_megatile(self) -> None:
		vf4 = VF4()
		megatile = self._megatile(0x1F)
		tile_id = vf4.add_megatile(megatile)
		self.assertEqual(tile_id, 0)
		self.assertEqual(vf4.megatile_count(), 1)
		self.assertIs(vf4.get_megatile(0), megatile)

	def test_save_load_round_trip(self) -> None:
		vf4 = VF4()
		vf4.add_megatile(self._megatile(0x01))
		vf4.add_megatile(self._megatile(0x1F))
		loaded = VF4()
		loaded.load_file(io.BytesIO(save_to_bytes(vf4)))
		self.assertEqual(loaded.megatile_count(), 2)
		self.assertEqual(loaded.get_megatile(0), self._megatile(0x01))
		self.assertEqual(loaded.get_megatile(1), self._megatile(0x1F))

	def test_load_empty(self) -> None:
		vf4 = VF4()
		vf4.load_file(io.BytesIO(b''))
		self.assertEqual(vf4.megatile_count(), 0)

	def test_load_invalid_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			VF4().load_file(io.BytesIO(b'\x00' * 33))
