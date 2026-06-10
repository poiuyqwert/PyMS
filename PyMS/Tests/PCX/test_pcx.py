
from ...FileFormats.PCX import PCX
from ...Utilities.PyMSError import PyMSError

import io
import struct
import unittest
from unittest import mock

PALETTE = [(i % 256, (i * 2) % 256, (i * 3) % 256) for i in range(256)]
# Exercises a run (1,1,1), a high escaped value (200 >= 192), and a full run row.
IMAGE = [[1, 1, 1, 200], [5, 5, 5, 5]]
PCX_HEADER = b'\x0A\x05\x01\x08'


def _save_bytes(pcx: PCX) -> bytes:
	buffer = io.BytesIO()
	writer = mock.MagicMock()
	writer.write.side_effect = buffer.write
	with mock.patch('PyMS.FileFormats.PCX.AtomicWriter', return_value=writer):
		pcx.save_file('out.pcx')
	return buffer.getvalue()


def _sample() -> PCX:
	pcx = PCX()
	pcx.load_pixels(IMAGE, PALETTE)
	return pcx


class Test_load_pixels(unittest.TestCase):
	def test_sets_dimensions_and_image(self) -> None:
		pcx = PCX()
		pcx.load_pixels(IMAGE, PALETTE)
		self.assertEqual((pcx.width, pcx.height), (4, 2))
		self.assertEqual(pcx.image, IMAGE)
		self.assertEqual(pcx.palette, PALETTE)

	def test_copies_image_rows(self) -> None:
		rows = [[1, 2], [3, 4]]
		pcx = PCX()
		pcx.load_pixels(rows, PALETTE)
		pcx.image[0][0] = 99
		self.assertEqual(rows[0][0], 1)


class Test_save_file(unittest.TestCase):
	def test_writes_pcx_header(self) -> None:
		self.assertEqual(_save_bytes(_sample())[:4], PCX_HEADER)

	def test_rle_encodes_runs_and_escapes(self) -> None:
		data = _save_bytes(_sample())
		image_region = data[128:len(data) - 769]
		# C3 01 = run of 3 ones; C1 C8 = escaped single 200; C4 05 = run of 4 fives
		self.assertEqual(image_region, bytes.fromhex('c301c1c8c405'))

	def test_writes_palette_marker_and_data(self) -> None:
		data = _save_bytes(_sample())
		self.assertEqual(data[-769], 0x0C)
		expected_palette = b''.join(struct.pack('3B', *c) for c in PALETTE)
		self.assertEqual(data[-768:], expected_palette)


class Test_load_data(unittest.TestCase):
	def test_round_trip(self) -> None:
		loaded = PCX()
		loaded.load_data(_save_bytes(_sample()))
		self.assertEqual(loaded.image, IMAGE)
		self.assertEqual((loaded.width, loaded.height), (4, 2))
		self.assertEqual(loaded.palette, PALETTE)

	def test_load_file_accepts_binary_io(self) -> None:
		loaded = PCX()
		loaded.load_file(io.BytesIO(_save_bytes(_sample())))
		self.assertEqual(loaded.image, IMAGE)

	def test_invalid_header_raises(self) -> None:
		data = _save_bytes(_sample())
		with self.assertRaises(PyMSError):
			PCX().load_data(b'XXXX' + data[4:])

	def test_missing_palette_marker_raises(self) -> None:
		data = bytearray(_save_bytes(_sample()))
		data[-769] = 0x00  # corrupt the 0x0C palette marker
		with self.assertRaises(PyMSError):
			PCX().load_data(bytes(data))

	def test_pal_mode_accepts_small_image(self) -> None:
		loaded = PCX()
		loaded.load_data(_save_bytes(_sample()), pal=True)
		self.assertEqual(loaded.width, 4)

	def test_pal_mode_rejects_oversized_image(self) -> None:
		wide = PCX()
		wide.load_pixels([[0] * 257], PALETTE)
		with self.assertRaises(PyMSError):
			PCX().load_data(_save_bytes(wide), pal=True)
