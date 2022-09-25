
from ...FileFormats.GRP import image_bounds

import unittest

class Test_Image_Bounds(unittest.TestCase):
	def test_empty(self):
		image = (
				(0,0,0,0,0),
				(0,0,0,0,0),
				(0,0,0,0,0),
				(0,0,0,0,0),
				(0,0,0,0,0)
			)
		expected = (0,0,0,0)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_slash(self):
		image = (
				(0,0,0,0,0),
				(0,0,0,1,0),
				(0,0,1,0,0),
				(0,1,0,0,0),
				(0,0,0,0,0)
			)
		expected = (1,1,4,4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_transparent_index(self):
		image = (
				(1,1,1,1,1),
				(1,1,1,0,1),
				(1,1,0,1,1),
				(1,0,1,1,1),
				(1,1,1,1,1)
			)
		transparent_index = 1
		expected = (1,1,4,4)

		result = image_bounds(image, transparent_index)

		self.assertEqual(result, expected)

	def test_backslash(self):
		image = (
				(0,0,0,0,0),
				(0,1,0,0,0),
				(0,0,1,0,0),
				(0,0,0,1,0),
				(0,0,0,0,0)
			)
		expected = (1,1,4,4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_x(self):
		image = (
				(0,0,0,0,0),
				(0,1,0,1,0),
				(0,0,1,0,0),
				(0,1,0,1,0),
				(0,0,0,0,0)
			)
		expected = (1,1,4,4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_diamond(self):
		image = (
				(0,0,0,0,0),
				(0,0,1,0,0),
				(0,1,0,1,0),
				(0,0,1,0,0),
				(0,0,0,0,0)
			)
		expected = (1,1,4,4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_vertical_line(self):
		image = (
				(0,0,0,0,0),
				(0,0,1,0,0),
				(0,0,1,0,0),
				(0,0,1,0,0),
				(0,0,0,0,0)
			)
		expected = (2,1,3,4)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_horizontal_line(self):
		image = (
				(0,0,0,0,0),
				(0,0,0,0,0),
				(0,1,1,1,0),
				(0,0,0,0,0),
				(0,0,0,0,0)
			)
		expected = (1,2,4,3)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_dot(self):
		image = (
				(0,0,0,0,0),
				(0,0,0,0,0),
				(0,0,1,0,0),
				(0,0,0,0,0),
				(0,0,0,0,0)
			)
		expected = (2,2,3,3)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_crosshatch(self):
		image = (
				(0,1,0,1,0),
				(1,0,1,0,1),
				(0,1,0,1,0),
				(1,0,1,0,1),
				(0,1,0,1,0)
			)
		expected = (0,0,5,5)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)

	def test_crosshatch2(self):
		image = (
				(1,0,1,0,1),
				(0,1,0,1,0),
				(1,0,1,0,1),
				(0,1,0,1,0),
				(1,0,1,0,1)
			)
		expected = (0,0,5,5)

		result = image_bounds(image, 0)

		self.assertEqual(result, expected)
