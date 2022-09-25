
from ...FileFormats.DAT import UnitsDAT

from ..utils import resource_path

import unittest

class Test_Units(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('units.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = UnitsDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
