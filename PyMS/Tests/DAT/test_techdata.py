
from ...FileFormats.DAT import TechDAT

from ..utils import resource_path

import unittest

class Test_Techdata(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('techdata.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = TechDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
