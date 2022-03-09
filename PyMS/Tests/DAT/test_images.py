
from ...FileFormats.DAT import ImagesDAT

from ..utils import resource_path

import unittest

class Test_Images(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('images.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = ImagesDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
