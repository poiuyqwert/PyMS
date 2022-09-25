
from ...FileFormats.GRP import RLE

from ..utils import data_to_hex

import unittest

class Test_RLE_Compress_Line(unittest.TestCase):
	def test_encoding_permutation_0_1_2(self):
		line = (0, 0, 0, 0, 1, 1, 1, 1, 2, 3, 4, 5)
		expected = '84 44 01 04 02 03 04 05'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_encoding_permutation_1_0_2(self):
		line = (1, 1, 1, 1, 0, 0, 0, 0, 2, 3, 4, 5)
		expected = '44 01 84 04 02 03 04 05'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_encoding_permutation_2_0_1(self):
		line = (2, 3, 4, 5, 0, 0, 0, 0, 1, 1, 1, 1)
		expected = '04 02 03 04 05 84 44 01'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_encoding_permutation_0_2_1(self):
		line = (0, 0, 0, 0, 2, 3, 4, 5, 1, 1, 1, 1)
		expected = '84 04 02 03 04 05 44 01'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_encoding_permutation_1_2_0(self):
		line = (1, 1, 1, 1, 2, 3, 4, 5, 0, 0, 0, 0)
		expected = '44 01 04 02 03 04 05 84'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_encoding_permutation_2_1_0(self):
		line = (2, 3, 4, 5, 1, 1, 1, 1, 0, 0, 0, 0)
		expected = '04 02 03 04 05 44 01 84'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_transparent_index(self):
		line = (0, 0, 0, 0, 1, 1, 1, 1, 2, 3, 4, 5)
		transparent_index = 1
		expected = '44 00 84 04 02 03 04 05'

		result = data_to_hex(RLE.compress_line(line, transparent_index))

		self.assertEqual(result, expected)

	def test_short_repeats_in_static_runs(self):
		line = (1, 2, 3, 3, 4, 5, 6, 6, 6, 7, 8)
		expected = '06 01 02 03 03 04 05 43 06 02 07 08'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_ending_in_short_repeats(self):
		line = (1, 1, 1, 2, 2)
		expected = '43 01 42 02'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_ending_in_static_run_with_short_repeat(self):
		line = (1, 2, 3, 3)
		expected = '04 01 02 03 03'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)

	def test_general(self):
		line = (0,1,2,3,3,4,5,6,6,6,0,0,0,7,7,7,8,9,10,10,0,11,12,13,0,14,15)
		expected = '81 06 01 02 03 03 04 05 43 06 83 43 07 04 08 09 0A 0A 81 03 0B 0C 0D 81 02 0E 0F'

		result = data_to_hex(RLE.compress_line(line, 0))

		self.assertEqual(result, expected)
