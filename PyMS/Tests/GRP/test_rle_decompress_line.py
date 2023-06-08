
from ...FileFormats.GRP import RLE

import unittest

class Test_RLE_Decompress_Line(unittest.TestCase):
	def test_permutation_0_1_2(self):
		line = b'\x84\x44\x01\x04\x02\x03\x04\x05'
		expected = [0, 0, 0, 0, 1, 1, 1, 1, 2, 3, 4, 5]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_permutation_1_0_2(self):
		line = b'\x44\x01\x84\x04\x02\x03\x04\x05'
		expected = [1, 1, 1, 1, 0, 0, 0, 0, 2, 3, 4, 5]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_permutation_2_0_1(self):
		line = b'\x04\x02\x03\x04\x05\x84\x44\x01'
		expected = [2, 3, 4, 5, 0, 0, 0, 0, 1, 1, 1, 1]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_permutation_0_2_1(self):
		line = b'\x84\x04\x02\x03\x04\x05\x44\x01'
		expected = [0, 0, 0, 0, 2, 3, 4, 5, 1, 1, 1, 1]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_permutation_1_2_0(self):
		line = b'\x44\x01\x04\x02\x03\x04\x05\x84'
		expected = [1, 1, 1, 1, 2, 3, 4, 5, 0, 0, 0, 0]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_permutation_2_1_0(self):
		line = b'\x04\x02\x03\x04\x05\x44\x01\x84'
		expected = [2, 3, 4, 5, 1, 1, 1, 1, 0, 0, 0, 0]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_transparent_index(self):
		line = b'\x44\x00\x84\x04\x02\x03\x04\x05'
		expected = [0, 0, 0, 0, 1, 1, 1, 1, 2, 3, 4, 5]
		transparent_index = 1

		result = RLE.decompress_line(line, len(expected), transparent_index)

		self.assertEqual(result, expected)

	def test_short_repeats_in_static_runs(self):
		line = b'\x06\x01\x02\x03\x03\x04\x05\x43\x06\x02\x07\x08'
		expected = [1, 2, 3, 3, 4, 5, 6, 6, 6, 7, 8]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_ending_in_short_repeats(self):
		line = b'\x43\x01\x42\x02'
		expected = [1, 1, 1, 2, 2]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_ending_in_static_run_with_short_repeat(self):
		line = b'\x04\x01\x02\x03\x03'
		expected = [1, 2, 3, 3]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)

	def test_general(self):
		line = b'\x81\x06\x01\x02\x03\x03\x04\x05\x43\x06\x83\x43\x07\x04\x08\x09\x0A\x0A\x81\x03\x0B\x0C\x0D\x81\x02\x0E\x0F'
		expected = [0,1,2,3,3,4,5,6,6,6,0,0,0,7,7,7,8,9,10,10,0,11,12,13,0,14,15]

		result = RLE.decompress_line(line, len(expected), transparent_index=0)

		self.assertEqual(result, expected)
