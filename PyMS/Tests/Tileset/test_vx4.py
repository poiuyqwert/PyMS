
from ...FileFormats.Tileset.VX4 import VX4, VX4Megatile, VX4Minitile
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import struct
import unittest


class Test_VX4Minitile(unittest.TestCase):
	def test_save_packs_image_id_and_flip(self) -> None:
		# Bit 0 is the flip flag; the image id is shifted up by one.
		self.assertEqual(VX4Minitile(image_id=5, flipped=True).save_data(False), struct.pack('<H', 1 | (5 << 1)))
		self.assertEqual(VX4Minitile(image_id=5, flipped=False).save_data(False), struct.pack('<H', 5 << 1))

	def test_load_unpacks_image_id_and_flip(self) -> None:
		minitile = VX4Minitile()
		minitile.load_data(struct.pack('<H', 1 | (9 << 1)))
		self.assertEqual(minitile.image_id, 9)
		self.assertTrue(minitile.flipped)

	def test_round_trip_normal_and_expanded(self) -> None:
		for expanded in (False, True):
			original = VX4Minitile(image_id=1234, flipped=True)
			reloaded = VX4Minitile()
			reloaded.load_data(original.save_data(expanded))
			self.assertEqual(reloaded, original)

	def test_expanded_uses_four_bytes(self) -> None:
		self.assertEqual(len(VX4Minitile(image_id=70000).save_data(True)), 4)
		self.assertEqual(len(VX4Minitile(image_id=5).save_data(False)), 2)


class Test_VX4Megatile(unittest.TestCase):
	def test_round_trip(self) -> None:
		megatile = VX4Megatile([VX4Minitile(image_id=n, flipped=bool(n % 2)) for n in range(16)])
		reloaded = VX4Megatile()
		reloaded.load_data(megatile.save_data(False))
		self.assertEqual(reloaded, megatile)


class Test_VX4(unittest.TestCase):
	def _megatile(self, base: int) -> VX4Megatile:
		return VX4Megatile([VX4Minitile(image_id=base + n) for n in range(16)])

	def test_defaults(self) -> None:
		vx4 = VX4()
		self.assertEqual(vx4.megatile_count(), 0)
		self.assertEqual(vx4.megatiles_remaining(), VX4.MAX_ID + 1)
		self.assertFalse(vx4.is_expanded())

	def test_add_and_find(self) -> None:
		vx4 = VX4()
		vx4.add_megatile(self._megatile(0))
		vx4.add_megatile(self._megatile(100))
		self.assertEqual(vx4.find_megatile_ids(self._megatile(100)), [1])
		self.assertEqual(vx4.find_megatile_ids(self._megatile(999)), [])

	def test_find_returns_all_duplicates(self) -> None:
		vx4 = VX4()
		vx4.add_megatile(self._megatile(0))
		vx4.add_megatile(self._megatile(0))
		self.assertEqual(vx4.find_megatile_ids(self._megatile(0)), [0, 1])

	def test_set_megatile_updates_lookup(self) -> None:
		vx4 = VX4()
		vx4.add_megatile(self._megatile(0))
		vx4.set_megatile(0, self._megatile(50))
		self.assertEqual(vx4.find_megatile_ids(self._megatile(0)), [])
		self.assertEqual(vx4.find_megatile_ids(self._megatile(50)), [0])

	def test_save_load_round_trip(self) -> None:
		vx4 = VX4()
		vx4.add_megatile(self._megatile(0))
		vx4.add_megatile(self._megatile(100))
		loaded = VX4()
		loaded.load(IO.output_to_bytes(vx4.save), expanded=False)
		self.assertEqual(loaded.megatile_count(), 2)
		self.assertEqual(loaded.get_megatile(1), self._megatile(100))

	def test_expanded_save_load_round_trip(self) -> None:
		vx4 = VX4(expanded=True)
		vx4.add_megatile(VX4Megatile([VX4Minitile(image_id=70000 + n) for n in range(16)]))
		loaded = VX4()
		loaded.load(IO.output_to_bytes(vx4.save), expanded=True)
		self.assertEqual(loaded.get_megatile(0), vx4.get_megatile(0))

	def test_expand(self) -> None:
		vx4 = VX4()
		vx4.expand()
		self.assertTrue(vx4.is_expanded())

	def test_load_invalid_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			VX4().load(b'\x00' * 33, expanded=False)
