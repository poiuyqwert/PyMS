
from ...FileFormats.DAT import CampaignDAT

from ..utils import resource_path

import unittest

class Test_Mapdata(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('mapdata.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = CampaignDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
