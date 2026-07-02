
from ...PyGRP.utils import BMPStyle, frames_to_sheet, grp_to_bmps, frame_bmp_name
from ...FileFormats import GRP

import unittest

def _frame(width: int, height: int, value: int) -> list[list[int]]:
	return [[value] * width for _ in range(height)]

def _palette() -> list[tuple[int, int, int]]:
	return [(i, i, i) for i in range(256)]

def _grp(frames: list[list[list[int]]]) -> GRP.GRP:
	grp = GRP.GRP()
	grp.load_frames(frames)
	return grp

class Test_GRP_To_BMPs(unittest.TestCase):
	def test_bmp_per_frame_exports_each_frame(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		bmps = grp_to_bmps(_grp(frames), _palette(), BMPStyle.bmp_per_frame)

		self.assertEqual(len(bmps), 3)
		for bmp,frame in zip(bmps, frames):
			self.assertEqual(bmp.width, 4)
			self.assertEqual(bmp.height, 2)
			self.assertEqual(bmp.image, frame)
			self.assertEqual(bmp.palette, _palette())

	def test_bmp_per_frame_exports_only_selected_frames(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		bmps = grp_to_bmps(_grp(frames), _palette(), BMPStyle.bmp_per_frame, [0, 2])

		self.assertEqual(len(bmps), 2)
		self.assertEqual(bmps[0].image, frames[0])
		self.assertEqual(bmps[1].image, frames[2])

	def test_selection_is_exported_in_frame_order(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		bmps = grp_to_bmps(_grp(frames), _palette(), BMPStyle.bmp_per_frame, [2, 0])

		self.assertEqual(bmps[0].image, frames[0])
		self.assertEqual(bmps[1].image, frames[2])

	def test_sheet_styles_produce_a_single_bmp(self) -> None:
		frames = [_frame(4, 2, value) for value in range(1, 21)]
		grp = _grp(frames)

		for style in (BMPStyle.single_bmp_framesets, BMPStyle.single_bmp_vertical):
			bmps = grp_to_bmps(grp, _palette(), style)

			self.assertEqual(len(bmps), 1)
			self.assertEqual(bmps[0].image, frames_to_sheet(frames, style, grp.transindex))

class Test_Frame_BMP_Name(unittest.TestCase):
	def test_frame_number_is_zero_padded(self) -> None:
		self.assertEqual(frame_bmp_name('name', 0), 'name 000.bmp')
		self.assertEqual(frame_bmp_name('name', 12), 'name 012.bmp')
		self.assertEqual(frame_bmp_name('name', 1234), 'name 1234.bmp')
