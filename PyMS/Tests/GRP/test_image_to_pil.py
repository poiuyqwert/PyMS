
from ...FileFormats.GRP import image_to_pil, rle_normal, rle_shadow
from ...FileFormats.Images import Bounds

import unittest

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

TRANSPARENT = (0,0,0,0)

class Test_Image_To_PIL(unittest.TestCase):
	def test_maps_palette_indexes_to_opaque_colors(self) -> None:
		palette = [BLACK, RED, GREEN, BLUE]
		image = [
				[1, 2],
				[3, 1],
			]

		pil = image_to_pil(image, palette)

		self.assertEqual(pil.size, (2, 2))
		self.assertEqual(list(pil.getdata()), [(255,0,0,255), (0,255,0,255), (0,0,255,255), (255,0,0,255)])

	def test_default_transparent_index(self) -> None:
		palette = [BLACK, RED]
		image = [[0, 1]]

		pil = image_to_pil(image, palette)

		self.assertEqual(list(pil.getdata()), [TRANSPARENT, (255,0,0,255)])

	def test_custom_transparent_index(self) -> None:
		palette = [BLACK, RED]
		image = [[0, 1]]

		pil = image_to_pil(image, palette, transindex=1)

		self.assertEqual(list(pil.getdata()), [(0,0,0,255), TRANSPARENT])

	def test_no_transparency(self) -> None:
		palette = [BLACK, RED]
		image = [[0, 1]]

		pil = image_to_pil(image, palette, transindex=None)

		self.assertEqual(list(pil.getdata()), [(0,0,0,255), (255,0,0,255)])

	def test_flip_horizontal(self) -> None:
		palette = [BLACK, RED, GREEN, BLUE]
		image = [
				[1, 2],
				[3, 1],
			]

		pil = image_to_pil(image, palette, flipHor=True)

		self.assertEqual(list(pil.getdata()), [(0,255,0,255), (255,0,0,255), (255,0,0,255), (0,0,255,255)])

	def test_bounds_crop_is_exclusive(self) -> None:
		palette = [BLACK, RED, GREEN, BLUE]
		image = [
				[0, 0, 0, 0],
				[0, 1, 2, 0],
				[0, 3, 1, 0],
				[0, 0, 0, 0],
			]

		pil = image_to_pil(image, palette, bounds=Bounds(x_min=1, y_min=1, x_max=3, y_max=3))

		self.assertEqual(pil.size, (2, 2))
		self.assertEqual(list(pil.getdata()), [(255,0,0,255), (0,255,0,255), (0,0,255,255), (255,0,0,255)])

	def test_custom_draw_function(self) -> None:
		palette = [BLACK, RED, GREEN]
		image = [[0, 1, 2]]
		shadow = (50,50,50, 255)

		pil = image_to_pil(image, palette, draw_function=rle_shadow, draw_info=shadow)

		self.assertEqual(list(pil.getdata()), [TRANSPARENT, shadow, shadow])

	def test_player_colors_remap(self) -> None:
		palette = [BLACK] * 16
		player_colors = [RED, GREEN, BLUE, BLACK, BLACK, BLACK, BLACK, BLACK]
		image = [[7, 8, 9, 15, 1]]

		pil = image_to_pil(image, palette, draw_function=rle_normal, draw_info=player_colors)

		self.assertEqual(list(pil.getdata()), [(0,0,0,255), (255,0,0,255), (0,255,0,255), (0,0,0,255), (0,0,0,255)])
