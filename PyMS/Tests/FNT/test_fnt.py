
from ...FileFormats.FNT import FNT, fnttobmp, bmptofnt
from ...FileFormats import BMP
from ...FileFormats.Images import Pixels
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import io
import struct
import unittest

PALETTE = [(0, 0, 0)] * 256


def _make_fnt(width: int, height: int, start: int, letters: list[Pixels]) -> FNT:
	fnt = FNT()
	fnt.width = width
	fnt.height = height
	fnt.start = start
	fnt.letters = letters
	return fnt


class Test_save_load_round_trip(unittest.TestCase):
	def test_letters_round_trip(self) -> None:
		letters: list[Pixels] = [
			[[1, 0, 2], [0, 3, 0]],   # fills the full cell
			[[0, 0, 0], [0, 1, 0]],   # single offset glyph
			[[0, 0, 0], [0, 0, 0]],   # empty glyph
		]
		fnt = _make_fnt(3, 2, 1, letters)
		loaded = FNT()
		loaded.load(io.BytesIO(IO.output_to_bytes(fnt.save)))
		self.assertEqual(loaded.letters, letters)

	def test_dimensions_and_start_round_trip(self) -> None:
		fnt = _make_fnt(3, 2, 5, [[[1, 0, 2], [0, 3, 0]]])
		loaded = FNT()
		loaded.load(io.BytesIO(IO.output_to_bytes(fnt.save)))
		self.assertEqual((loaded.width, loaded.height, loaded.start), (3, 2, 5))

	def test_sizes_capture_bounding_boxes(self) -> None:
		letters: list[Pixels] = [
			[[1, 0, 2], [0, 3, 0]],
			[[0, 0, 0], [0, 1, 0]],
			[[0, 0, 0], [0, 0, 0]],
		]
		fnt = _make_fnt(3, 2, 1, letters)
		loaded = FNT()
		loaded.load(io.BytesIO(IO.output_to_bytes(fnt.save)))
		self.assertEqual(loaded.sizes, [(3, 2, 0, 0), (1, 1, 1, 1), (0, 0, 0, 0)])

	def test_identical_letters_are_deduplicated(self) -> None:
		fnt = _make_fnt(3, 2, 1, [[[1, 0, 2], [0, 3, 0]], [[1, 0, 2], [0, 3, 0]]])
		data = IO.output_to_bytes(fnt.save)
		first_offset = struct.unpack('<L', data[8:12])[0]
		second_offset = struct.unpack('<L', data[12:16])[0]
		self.assertEqual(first_offset, second_offset)

	def test_empty_glyph_uses_zero_offset(self) -> None:
		fnt = _make_fnt(3, 2, 1, [[[0, 0, 0], [0, 0, 0]]])
		data = IO.output_to_bytes(fnt.save)
		self.assertEqual(struct.unpack('<L', data[8:12])[0], 0)


class Test_load(unittest.TestCase):
	def test_header_prefix(self) -> None:
		data = IO.output_to_bytes(_make_fnt(3, 2, 1, [[[1, 0, 2], [0, 3, 0]]]).save)
		self.assertEqual(data[:4], b'FONT')
		self.assertEqual(struct.unpack('<4B', data[4:8]), (1, 1, 3, 2))

	def test_invalid_header_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FNT().load(io.BytesIO(b'XXXX0000'))

	def test_corrupt_data_raises(self) -> None:
		# Valid header claiming 4 glyphs but no offset table follows.
		with self.assertRaises(PyMSError):
			FNT().load(io.BytesIO(b'FONT' + struct.pack('<4B', 1, 4, 3, 2)))


class Test_fnttobmp(unittest.TestCase):
	def test_concatenates_letters_horizontally(self) -> None:
		fnt = _make_fnt(2, 2, 1, [[[1, 2], [3, 4]], [[5, 6], [7, 0]]])
		bmp = fnttobmp(fnt, PALETTE)
		assert bmp is not None
		self.assertEqual(bmp.image, [[1, 2, 5, 6], [3, 4, 7, 0]])
		self.assertEqual(bmp.width, 4)
		self.assertEqual(bmp.height, 2)

	def test_single_letter(self) -> None:
		fnt = _make_fnt(2, 2, 1, [[[1, 2], [3, 4]]])
		bmp = fnttobmp(fnt, PALETTE)
		assert bmp is not None
		self.assertEqual(bmp.image, [[1, 2], [3, 4]])
		self.assertEqual(bmp.width, 2)


class Test_bmptofnt(unittest.TestCase):
	def test_splits_into_equal_width_letters(self) -> None:
		bmp = BMP.BMP()
		bmp.set_pixels([[1, 2, 5, 6], [3, 4, 7, 0]], PALETTE)
		fnt = bmptofnt(bmp, 1, 2)
		assert fnt is not None
		self.assertEqual(fnt.letters, [[[1, 2], [3, 4]], [[5, 6], [7, 0]]])
		self.assertEqual((fnt.width, fnt.height, fnt.start), (2, 2, 1))

	def test_round_trips_with_fnttobmp(self) -> None:
		fnt = _make_fnt(2, 2, 3, [[[1, 2], [3, 4]], [[5, 6], [7, 0]]])
		bmp = fnttobmp(fnt, PALETTE)
		assert bmp is not None
		result = bmptofnt(bmp, fnt.start, len(fnt.letters))
		assert result is not None
		self.assertEqual(result.letters, fnt.letters)
		self.assertEqual((result.width, result.height, result.start), (2, 2, 3))
