
from ...FileFormats.BMP import RLE

import unittest

class Test_Decompress(unittest.TestCase):
	def test_eof_immediate(self) -> None:
		data = b'\x00\x01'
		expected = [[0,0,0,0,0],[0,0,0,0,0]]

		result = RLE.decompress(data, 5, 2)

		self.assertEqual(result, expected)

	def test_eol_on_empty_line(self) -> None:
		data = b'\x00\x00\x00\x01'
		expected = [[0,0,0,0,0],[0,0,0,0,0]]

		result = RLE.decompress(data, 5, 2)

		self.assertEqual(result, expected)

	def test_trailing_eol_before_eof_does_not_add_a_row(self) -> None:
		# A full row of pixels, then EOL, then EOF.
		# The decoded image should contain exactly `height` rows.
		data = b'\x02\xFF\x00\x00\x00\x01'
		expected = [[0xFF, 0xFF]]

		result = RLE.decompress(data, 2, 1)

		self.assertEqual(result, expected)

	def test_eol_after_each_row_yields_declared_height(self) -> None:
		# Every row terminated with EOL, including the final row.
		# Row count must match the declared height regardless of trailing EOL.
		data = b'\x02\xAA\x00\x00\x02\xBB\x00\x00\x00\x01'
		# BMP stores bottom-up; result is top-down after the decoder reverses.
		expected = [[0xBB, 0xBB], [0xAA, 0xAA]]

		result = RLE.decompress(data, 2, 2)

		self.assertEqual(result, expected)

	def test_eof_directly_after_final_row_yields_declared_height(self) -> None:
		# Final row not terminated with an EOL; EOF immediately follows pixel data.
		# Decoder must still produce exactly `height` rows.
		data = b'\x02\xAA\x00\x00\x02\xBB\x00\x01'
		expected = [[0xBB, 0xBB], [0xAA, 0xAA]]

		result = RLE.decompress(data, 2, 2)

		self.assertEqual(result, expected)

	def test_eof_pads_short_stream_to_declared_height(self) -> None:
		# Only one row of pixels followed by EOF for a 2-row image.
		# Missing rows are filled with zero pixels up to `height`.
		data = b'\x02\xAA\x00\x01'
		expected = [[0, 0], [0xAA, 0xAA]]

		result = RLE.decompress(data, 2, 2)

		self.assertEqual(result, expected)

	def test_row_overshoot_is_clipped_to_declared_width(self) -> None:
		# An absolute-mode run that writes more pixels than the declared width
		# is clipped at `width`; trailing pixels in the run are discarded.
		data = b'\x00\x04\xAA\xBB\xCC\xDD\x00\x01'
		expected = [[0xAA, 0xBB]]

		result = RLE.decompress(data, 2, 1)

		self.assertEqual(result, expected)
