
from ...FileFormats.DAT import SpritesDAT

from ..utils import resource_path

import unittest

class Test_Sprites(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('sprites.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = SpritesDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
