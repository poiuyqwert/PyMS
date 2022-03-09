
from ...FileFormats.DAT import FlingyDAT

from ..utils import resource_path

import unittest

class Test_Flingy(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('flingy.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = FlingyDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
