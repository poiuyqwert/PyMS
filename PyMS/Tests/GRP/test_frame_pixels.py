
from ...FileFormats import GRP
from ...FileFormats.BMP import BMP
from ...FileFormats.PCX import PCX

import unittest

class Test_Frame_Pixels(unittest.TestCase):
	def test_raw_pixels_passthrough(self) -> None:
		pixels = [
				[1, 2],
				[3, 4],
			]

		result, transindex = GRP.frame_pixels(pixels, None, 5)

		self.assertIs(result, pixels)
		self.assertEqual(transindex, 5)

	def test_grp_frame_uses_grp_transindex(self) -> None:
		grp = GRP.GRP()
		grp.load_frames([
				[[1, 2], [3, 4]],
				[[5, 6], [7, 8]],
			], transindex=2)

		result, transindex = GRP.frame_pixels(grp, 1)

		self.assertEqual(result, [[5, 6], [7, 8]])
		self.assertEqual(transindex, 2)

	def test_grp_defaults_to_first_frame(self) -> None:
		grp = GRP.GRP()
		grp.load_frames([
				[[1, 2], [3, 4]],
				[[5, 6], [7, 8]],
			])

		result, _ = GRP.frame_pixels(grp)

		self.assertEqual(result, [[1, 2], [3, 4]])

	def test_cache_grp_decodes_frame(self) -> None:
		grp = GRP.CacheGRP()
		grp.frames = 1
		grp.width = 2
		grp.height = 1
		# One frame, one line at absolute offset 0: static run of 2 pixels (5, 6)
		grp.imagebuffer = [(GRP.Bounds(x_min=0, y_min=0, x_max=2, y_max=1), (0,))]
		grp.databuffer = b'\x02\x05\x06'
		grp.uncompressed = False

		result, transindex = GRP.frame_pixels(grp, 0, 3)

		self.assertEqual(result, [[5, 6]])
		self.assertEqual(transindex, 3)

	def test_bmp_image(self) -> None:
		bmp = BMP()
		bmp.image = [[1, 2]]

		result, transindex = GRP.frame_pixels(bmp, None, 4)

		self.assertIs(result, bmp.image)
		self.assertEqual(transindex, 4)

	def test_pcx_image(self) -> None:
		pcx = PCX()
		pcx.image = [[1, 2]]

		result, transindex = GRP.frame_pixels(pcx, None, 4)

		self.assertIs(result, pcx.image)
		self.assertEqual(transindex, 4)
