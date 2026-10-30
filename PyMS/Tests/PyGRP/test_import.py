
from ...PyGRP.utils import BMPStyle, frames_to_sheet, bmp_sheet_to_frames, frames_to_grp
from ...FileFormats import GRP
from ...FileFormats import BMP
from ...Utilities.PyMSError import PyMSError

import unittest, io

def _frame(width: int, height: int, value: int) -> list[list[int]]:
	return [[value] * width for _ in range(height)]

def _palette() -> list[tuple[int, int, int]]:
	return [(i, i, i) for i in range(256)]

class Test_Frames_To_GRP(unittest.TestCase):
	def test_each_frame_is_kept_separate(self) -> None:
		frames = [_frame(8, 4, value) for value in (1, 2, 3, 4, 5)]

		grp = frames_to_grp(frames, _palette(), False)

		self.assertEqual(grp.frames, 5)
		self.assertEqual(grp.width, 8)
		self.assertEqual(grp.height, 4)
		self.assertEqual(grp.images, frames)

	def test_all_frames_survive_save_load_round_trip(self) -> None:
		frames = [_frame(8, 4, value) for value in (1, 2, 3, 4, 5)]
		grp = frames_to_grp(frames, _palette(), False)

		saved_file = io.BytesIO()
		grp.save(saved_file)
		saved_file.seek(0)
		loaded = GRP.GRP()
		loaded.load(saved_file)

		self.assertEqual(loaded.frames, 5)
		self.assertEqual(loaded.width, 8)
		self.assertEqual(loaded.height, 4)
		self.assertEqual(loaded.images, frames)

	def test_transindex_is_kept_and_used_for_bounds(self) -> None:
		frames = [_frame(8, 4, 5)]

		grp = frames_to_grp(frames, _palette(), False, transindex=5)

		self.assertEqual(grp.transindex, 5)
		self.assertEqual(grp.images_bounds[0], GRP.Bounds(x_min=0, y_min=0, x_max=0, y_max=0))

	def test_mismatched_frame_dimensions_raise(self) -> None:
		frames = [_frame(4, 2, 1), _frame(4, 3, 2)]

		with self.assertRaises(PyMSError) as cm:
			frames_to_grp(frames, _palette(), False)
		self.assertIn('has unexpected height', str(cm.exception))

class Test_BMP_Sheet_To_Frames(unittest.TestCase):
	def test_sheet_import_recovers_all_frames(self) -> None:
		frames = [_frame(8, 4, value) for value in range(1, 21)]
		sheet_bmp = BMP.BMP(_palette())
		sheet_bmp.set_pixels(frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 0))

		imported = bmp_sheet_to_frames(sheet_bmp, len(frames), BMPStyle.single_bmp_framesets, 'sheet.bmp')

		self.assertEqual(imported, frames)

	def test_vertical_sheet_import_recovers_all_frames(self) -> None:
		frames = [_frame(8, 4, value) for value in (1, 2, 3)]
		sheet_bmp = BMP.BMP(_palette())
		sheet_bmp.set_pixels(frames_to_sheet(frames, BMPStyle.single_bmp_vertical, 0))

		imported = bmp_sheet_to_frames(sheet_bmp, len(frames), BMPStyle.single_bmp_vertical, 'sheet.bmp')

		self.assertEqual(imported, frames)

	def test_sheet_import_to_grp_round_trips(self) -> None:
		frames = [_frame(8, 4, value) for value in range(1, 21)]
		sheet_bmp = BMP.BMP(_palette())
		sheet_bmp.set_pixels(frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 0))

		imported = bmp_sheet_to_frames(sheet_bmp, len(frames), BMPStyle.single_bmp_framesets, 'sheet.bmp')
		grp = frames_to_grp(imported, _palette(), False)
		saved_file = io.BytesIO()
		grp.save(saved_file)
		saved_file.seek(0)
		loaded = GRP.GRP()
		loaded.load(saved_file)

		self.assertEqual(loaded.frames, 20)
		self.assertEqual(loaded.images, frames)

	def test_oversized_frames_are_rejected(self) -> None:
		sheet_bmp = BMP.BMP(_palette())
		sheet_bmp.set_pixels(_frame(300, 10, 1))

		with self.assertRaises(PyMSError) as cm:
			bmp_sheet_to_frames(sheet_bmp, 1, BMPStyle.single_bmp_framesets, 'sheet.bmp')
		self.assertIn('Frames have a maximum size of 256x256', str(cm.exception))
