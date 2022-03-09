
from ...FileFormats.GRP import RLE

from ..utils import data_to_hex

import unittest

class Test_RLE_Encode_Repeat(unittest.TestCase):
	def test_length_one(self):
		length = 1
		expected = '41 01'

		result = data_to_hex(RLE.encode_repeat(1, length))

		self.assertEqual(result, expected)

	def test_index_two(self):
		index = 2
		expected = '41 02'

		result = data_to_hex(RLE.encode_repeat(index, 1))

		self.assertEqual(result, expected)

	def test_length_two(self):
		length = 2
		expected = '42 01'

		result = data_to_hex(RLE.encode_repeat(1, length))

		self.assertEqual(result, expected)

	def test_max_length(self):
		length = 63
		expected = '7F 01'

		result = data_to_hex(RLE.encode_repeat(1, length))

		self.assertEqual(result, expected)

	def test_over_max_length(self):
		length = 64
		expected = '7F 01 41 01'

		result = data_to_hex(RLE.encode_repeat(1, length))

		self.assertEqual(result, expected)

	def test_over_max_length_twice(self):
		length = 127
		expected = '7F 01 7F 01 41 01'

		result = data_to_hex(RLE.encode_repeat(1, length))

		self.assertEqual(result, expected)
