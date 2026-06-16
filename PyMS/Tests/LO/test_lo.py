
from ...FileFormats.LO import LO
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import io
import unittest

# 2 frames, 2 overlays each, including negative offsets.
FRAMES = [[[1, 2], [3, 4]], [[-1, -2], [5, 6]]]

# header (2 frames, 2 overlays) + frame offsets (16, 20) + overlay data
ENCODED = bytes.fromhex('0200000002000000100000001400000001020304fffe0506')

TEXT = 'Frame:\n    (1, 2)\n    (3, 4)\n\nFrame:\n    (-1, -2)\n    (5, 6)\n\n'


def _decompile(lo: LO) -> str:
	output = io.StringIO()
	lo.decompile(output)
	return output.getvalue()


def _interpret(text: str) -> LO:
	lo = LO()
	lo.interpret(io.StringIO(text))
	return lo


def _make(frames: list[list[list[int]]]) -> LO:
	lo = LO()
	lo.frames = frames
	return lo


class Test_load(unittest.TestCase):
	def test_reads_frames(self) -> None:
		lo = LO()
		lo.load(io.BytesIO(ENCODED))
		self.assertEqual(lo.frames, FRAMES)

	def test_round_trip_with_save(self) -> None:
		lo = LO()
		lo.load(io.BytesIO(IO.output_to_bytes(_make(FRAMES).save)))
		self.assertEqual(lo.frames, FRAMES)

	def test_truncated_raises(self) -> None:
		with self.assertRaises(PyMSError):
			LO().load(io.BytesIO(b''))


class Test_save(unittest.TestCase):
	def test_byte_layout(self) -> None:
		self.assertEqual(IO.output_to_bytes(_make(FRAMES).save), ENCODED)

	def test_round_trip_with_load(self) -> None:
		loaded = LO()
		loaded.load(io.BytesIO(IO.output_to_bytes(_make(FRAMES).save)))
		self.assertEqual(loaded.frames, FRAMES)

	def test_default_round_trips(self) -> None:
		loaded = LO()
		loaded.load(io.BytesIO(IO.output_to_bytes(LO().save)))
		self.assertEqual(loaded.frames, [[[0, 0]]])


class Test_decompile(unittest.TestCase):
	def test_text_layout(self) -> None:
		self.assertEqual(_decompile(_make(FRAMES)), TEXT)

	def test_round_trip_with_interpret(self) -> None:
		self.assertEqual(_interpret(_decompile(_make(FRAMES))).frames, FRAMES)


class Test_interpret(unittest.TestCase):
	def test_parses_frames(self) -> None:
		self.assertEqual(_interpret(TEXT).frames, FRAMES)

	def test_negative_offsets(self) -> None:
		self.assertEqual(_interpret('Frame:\n    (-12, -34)\n\n').frames, [[[-12, -34]]])

	def test_strips_comments_and_blank_lines(self) -> None:
		text = '# leading comment\nFrame:\n    (1, 2) # inline comment\n\n'
		self.assertEqual(_interpret(text).frames, [[[1, 2]]])

	def test_coordinates_before_frame_raises(self) -> None:
		with self.assertRaises(PyMSError):
			_interpret('    (1, 2)\n')

	def test_malformed_coordinate_raises(self) -> None:
		with self.assertRaises(PyMSError):
			_interpret('Frame:\n    not coordinates\n')

	def test_signed_byte_bounds_accepted(self) -> None:
		# -128 and 127 are the signed-byte extremes `compile` can pack.
		self.assertEqual(_interpret('Frame:\n    (-128, 127)\n\n').frames, [[[-128, 127]]])

	def test_out_of_range_coordinate_raises(self) -> None:
		for text in ('Frame:\n    (128, 0)\n\n', 'Frame:\n    (-129, 0)\n\n', 'Frame:\n    (0, 200)\n\n'):
			with self.subTest(text=text):
				with self.assertRaises(PyMSError):
					_interpret(text)

	def test_inconsistent_overlay_count_raises(self) -> None:
		# The middle frame has one overlay while the others have two.
		text = 'Frame:\n    (1, 2)\n    (3, 4)\n\nFrame:\n    (5, 6)\n\nFrame:\n    (7, 8)\n    (9, 10)\n\n'
		with self.assertRaises(PyMSError):
			_interpret(text)

	def test_too_many_overlays_raises(self) -> None:
		text = 'Frame:\n    (1, 2)\n    (3, 4)\n\nFrame:\n    (5, 6)\n    (7, 8)\n    (9, 10)\n\n'
		with self.assertRaises(PyMSError):
			_interpret(text)

	def test_round_trip_through_save(self) -> None:
		lo = _interpret(TEXT)
		reloaded = LO()
		reloaded.load(io.BytesIO(IO.output_to_bytes(lo.save)))
		self.assertEqual(reloaded.frames, FRAMES)
