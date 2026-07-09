
from ...FileFormats.SPK import SPK
from ...FileFormats import BMP
from ...FileFormats.Images import Pixels
from ...Utilities import IO

import io
import unittest

PALETTE = [(0, 0, 0)] * 256


def _bmp_bytes(image: Pixels) -> bytes:
	bmp = BMP.BMP()
	bmp.set_pixels(image, PALETTE)
	return IO.output_to_bytes(bmp.save)


def _interpret(image: Pixels, layer_count: int = 1) -> SPK:
	spk = SPK()
	spk.interpret_file(io.BytesIO(_bmp_bytes(image)), layer_count)
	return spk


class Test_interpret_file(unittest.TestCase):
	def test_star_touching_right_edge_has_exact_width(self) -> None:
		# A run that reaches the final pixel of the row must end at that pixel,
		# not one past it, so the star is not padded with an extra column.
		spk = _interpret([[1, 1]])
		self.assertEqual(len(spk.images), 1)
		image = spk.images[0]
		self.assertEqual(image.width, 2)
		self.assertEqual(image.pixels, [[1, 1]])

	def test_multi_row_star_touching_right_edge(self) -> None:
		spk = _interpret([[1, 1], [1, 1]])
		self.assertEqual(len(spk.images), 1)
		image = spk.images[0]
		self.assertEqual((image.width, image.height), (2, 2))
		self.assertEqual(image.pixels, [[1, 1], [1, 1]])

	def test_star_not_touching_right_edge(self) -> None:
		# A run ending before the edge is unaffected.
		spk = _interpret([[1, 0]])
		image = spk.images[0]
		self.assertEqual(image.width, 1)
		self.assertEqual(image.pixels, [[1]])

	def test_interpreted_star_round_trips_through_save(self) -> None:
		spk = _interpret([[1, 1]])
		reloaded = SPK()
		reloaded.load(IO.output_to_bytes(spk.save))
		self.assertEqual(len(reloaded.images), 1)
		self.assertEqual(reloaded.images[0].width, 2)
		self.assertEqual(reloaded.images[0].pixels, [[1, 1]])
