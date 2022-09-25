
from ...FileFormats.BMP import BMP

from ..utils import resource_path

import unittest

class Test_New_Headers(unittest.TestCase):
	def test_load(self):
		expected = [
			[138, 138, 117, 117, 117, 117, 117, 117, 138, 138],
			[138, 117, 117, 255, 117, 117, 255, 117, 117, 138],
			[117, 117, 117, 255, 117, 117, 255, 117, 117, 117],
			[117, 117, 117, 255, 117, 117, 255, 117, 117, 117],
			[117, 117, 117, 117, 117, 117, 117, 117, 117, 117],
			[117, 255, 117, 117, 117, 117, 117, 117, 255, 117],
			[117, 117, 255, 117, 117, 117, 117, 255, 117, 117],
			[138, 117, 117, 255, 255, 255, 255, 117, 117, 138],
			[138, 138, 117, 117, 117, 117, 117, 117, 138, 138],
			[138, 138, 138, 138, 138, 138, 138, 138, 138, 138]
		]

		bmp = BMP()
		bmp.load_file(resource_path('new_header.bmp', __file__))

		self.assertEqual(bmp.image, expected)
