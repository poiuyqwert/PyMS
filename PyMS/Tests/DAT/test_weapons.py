
from ...FileFormats.DAT import WeaponsDAT
from ...Utilities import IO

from ..utils import resource_path

import unittest

class Test_Weapons(unittest.TestCase):
	def test_load_and_save(self) -> None:
		with open(resource_path('weapons.dat', __file__), 'rb') as f:
			expected = f.read()

		dat = WeaponsDAT()
		dat.load(expected)

		result = IO.output_to_bytes(dat.save)

		self.assertEqual(result, expected)
