
from ...FileFormats.GRP import RLE

from ..utils import data_to_hex

import unittest

class Test_RLE_Encode_Transparent(unittest.TestCase):
	def test_length_one(self):
		length = 1
		expected = '81'

		result = data_to_hex(RLE.encode_transparent(length))

		self.assertEqual(result, expected)

	def test_length_two(self):
		length = 2
		expected = '82'

		result = data_to_hex(RLE.encode_transparent(length))

		self.assertEqual(result, expected)

	def test_length_max(self):
		length = 127
		expected = 'FF'

		result = data_to_hex(RLE.encode_transparent(length))

		self.assertEqual(result, expected)

	def test_over_max_length(self):
		length = 128
		expected = 'FF 81'

		result = data_to_hex(RLE.encode_transparent(length))

		self.assertEqual(result, expected)

	def test_over_max_length_twice(self):
		length = 255
		expected = 'FF FF 81'

		result = data_to_hex(RLE.encode_transparent(length))

		self.assertEqual(result, expected)
