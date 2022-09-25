
from ...FileFormats.DAT import SoundsDAT

from ..utils import resource_path

import unittest

class Test_SFXData(unittest.TestCase):
	def test_load_and_save(self):
		with open(resource_path('sfxdata.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = SoundsDAT()
		dat.load_data(expected)

		result = dat.save_data()

		self.assertEqual(result, expected)
