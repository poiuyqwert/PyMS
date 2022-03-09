
from ...FileFormats.DAT import PortraitsDAT

from ..utils import resource_path

import unittest

class Test_Portdata(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('portdata.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = PortraitsDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
