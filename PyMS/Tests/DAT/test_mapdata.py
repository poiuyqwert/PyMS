
from ...FileFormats.DAT import CampaignDAT
from ...Utilities import IO

from ..utils import resource_path

import unittest

class Test_Mapdata(unittest.TestCase):
	def test_load_and_save(self) -> None:
		with open(resource_path('mapdata.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = CampaignDAT()
		dat.load(expected)

		result = IO.output_to_bytes(dat.save)

		self.assertEqual(result, expected)
