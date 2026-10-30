
from ...FileFormats.Images import Bounds

import unittest

class Test_Bounds(unittest.TestCase):
	def test_fields(self) -> None:
		bounds = Bounds(x_min=1, y_min=2, x_max=4, y_max=7)

		self.assertEqual(bounds.x_min, 1)
		self.assertEqual(bounds.y_min, 2)
		self.assertEqual(bounds.x_max, 4)
		self.assertEqual(bounds.y_max, 7)

	def test_equality(self) -> None:
		self.assertEqual(Bounds(x_min=1, y_min=2, x_max=4, y_max=7), Bounds(x_min=1, y_min=2, x_max=4, y_max=7))
		self.assertNotEqual(Bounds(x_min=1, y_min=2, x_max=4, y_max=7), Bounds(x_min=2, y_min=1, x_max=7, y_max=4))

	def test_width_and_height(self) -> None:
		bounds = Bounds(x_min=1, y_min=2, x_max=4, y_max=7)

		self.assertEqual(bounds.width, 3)
		self.assertEqual(bounds.height, 5)
