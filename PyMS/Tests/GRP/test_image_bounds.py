
from ...FileFormats.GRP import image_bounds
from ...FileFormats.Images import Bounds

import unittest

class Test_Image_Bounds(unittest.TestCase):
	def test_empty(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=0, y_min=0, x_max=0, y_max=0)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_slash(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,0,1,0],
				[0,0,1,0,0],
				[0,1,0,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=1, y_min=1, x_max=4, y_max=4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_transparent_index(self) -> None:
		image = [
				[1,1,1,1,1],
				[1,1,1,0,1],
				[1,1,0,1,1],
				[1,0,1,1,1],
				[1,1,1,1,1],
			]
		transparent_index = 1
		expected = Bounds(x_min=1, y_min=1, x_max=4, y_max=4)

		result = image_bounds(image, transparent_index)

		self.assertEqual(result, expected)

	def test_backslash(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,1,0,0,0],
				[0,0,1,0,0],
				[0,0,0,1,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=1, y_min=1, x_max=4, y_max=4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_x(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,1,0,1,0],
				[0,0,1,0,0],
				[0,1,0,1,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=1, y_min=1, x_max=4, y_max=4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_diamond(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,1,0,0],
				[0,1,0,1,0],
				[0,0,1,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=1, y_min=1, x_max=4, y_max=4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_vertical_line(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,1,0,0],
				[0,0,1,0,0],
				[0,0,1,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=2, y_min=1, x_max=3, y_max=4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_horizontal_line(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,1,1,1,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=1, y_min=2, x_max=4, y_max=3)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_dot(self) -> None:
		image = [
				[0,0,0,0,0],
				[0,0,0,0,0],
				[0,0,1,0,0],
				[0,0,0,0,0],
				[0,0,0,0,0],
			]
		expected = Bounds(x_min=2, y_min=2, x_max=3, y_max=3)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_crosshatch(self) -> None:
		image = [
				[0,1,0,1,0],
				[1,0,1,0,1],
				[0,1,0,1,0],
				[1,0,1,0,1],
				[0,1,0,1,0],
			]
		expected = Bounds(x_min=0, y_min=0, x_max=5, y_max=5)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_crosshatch2(self) -> None:
		image = [
				[1,0,1,0,1],
				[0,1,0,1,0],
				[1,0,1,0,1],
				[0,1,0,1,0],
				[1,0,1,0,1],
			]
		expected = Bounds(x_min=0, y_min=0, x_max=5, y_max=5)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)
