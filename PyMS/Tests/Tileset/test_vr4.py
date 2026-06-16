
from ...FileFormats.Tileset.VR4 import VR4
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import struct
import unittest


def _image(base: int) -> tuple[tuple[int, ...], ...]:
	return tuple(tuple(base + y * 8 + x for x in range(8)) for y in range(8))


class Test_VR4(unittest.TestCase):
	def test_defaults(self) -> None:
		vr4 = VR4()
		self.assertEqual(vr4.image_count(), 0)
		self.assertEqual(vr4.images_remaining(), VR4.MAX_ID + 1)

	def test_add_image(self) -> None:
		vr4 = VR4()
		vr4.add_image(_image(0))
		self.assertEqual(vr4.image_count(), 1)
		self.assertEqual(vr4.get_image(0), _image(0))

	def test_add_wrong_size_raises(self) -> None:
		vr4 = VR4()
		with self.assertRaises(PyMSError):
			vr4.add_image(tuple([0] * 8 for _ in range(7)))  # 7 rows
		with self.assertRaises(PyMSError):
			vr4.add_image(tuple([0] * 7 for _ in range(8)))  # 7 columns

	def test_find_image_ids_normal_only(self) -> None:
		vr4 = VR4()
		vr4.add_image(_image(0))  # asymmetric rows
		normal, flipped = vr4.find_image_ids(_image(0))
		self.assertEqual(normal, [0])
		self.assertEqual(flipped, [])

	def test_find_image_ids_symmetric(self) -> None:
		vr4 = VR4()
		symmetric = tuple((1, 2, 3, 4, 4, 3, 2, 1) for _ in range(8))
		vr4.add_image(symmetric)
		normal, flipped = vr4.find_image_ids(symmetric)
		self.assertEqual(normal, [0])
		self.assertEqual(flipped, [0])

	def test_set_image_updates_lookup(self) -> None:
		vr4 = VR4()
		vr4.add_image(_image(0))
		vr4.set_image(0, _image(100))
		self.assertEqual(vr4.find_image_ids(_image(0))[0], [])
		self.assertEqual(vr4.find_image_ids(_image(100))[0], [0])

	def test_load(self) -> None:
		vr4 = VR4()
		vr4.load(struct.pack('64B', *range(64)))
		self.assertEqual(vr4.get_image(0), _image(0))

	def test_save_load_round_trip(self) -> None:
		vr4 = VR4()
		vr4.add_image(_image(0))
		vr4.add_image(_image(50))
		loaded = VR4()
		loaded.load(IO.output_to_bytes(vr4.save))
		self.assertEqual(loaded.image_count(), 2)
		self.assertEqual(loaded.get_image(1), _image(50))

	def test_load_invalid_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			VR4().load(b'\x00' * 65)

	def test_load_indexes_duplicate_images(self) -> None:
		# Two identical images must both be found, not just the last one.
		image = struct.pack('64B', *range(64))
		vr4 = VR4()
		vr4.load(image + image)
		self.assertEqual(vr4.find_image_ids(vr4.get_image(0))[0], [0, 1])

	def test_reload_rebuilds_lookup(self) -> None:
		# Loading into an already-populated VR4 must not carry over the old lookup.
		image = struct.pack('64B', *range(64))
		vr4 = VR4()
		vr4.load(image)
		vr4.load(image + image)
		self.assertEqual(vr4.image_count(), 2)
		self.assertEqual(vr4.find_image_ids(vr4.get_image(0))[0], [0, 1])
