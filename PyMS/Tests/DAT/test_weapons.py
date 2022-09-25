
from ...FileFormats.DAT import WeaponsDAT

from ..utils import resource_path

import unittest

class Test_Weapons(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('weapons.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = WeaponsDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
