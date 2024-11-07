
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
