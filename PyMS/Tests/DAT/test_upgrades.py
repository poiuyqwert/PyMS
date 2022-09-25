
from ...FileFormats.DAT import UpgradesDAT

from ..utils import resource_path

import unittest

class Test_Upgrades(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('upgrades.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = UpgradesDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
