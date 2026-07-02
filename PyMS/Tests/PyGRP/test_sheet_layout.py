
from ...PyGRP.utils import BMPStyle, FRAMESET_ROW_SIZE, frames_to_sheet, sheet_to_frames, sheet_frame_size
from ...Utilities.PyMSError import PyMSError

import unittest

def _frame(width: int, height: int, value: int) -> list[list[int]]:
	return [[value] * width for _ in range(height)]

class Test_Frames_To_Sheet(unittest.TestCase):
	def test_vertical_stacks_frames(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_vertical, 0)

		self.assertEqual(len(sheet), 6)
		self.assertEqual(sheet, [[1]*4, [1]*4, [2]*4, [2]*4, [3]*4, [3]*4])

	def test_framesets_single_row_is_not_padded(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 9)

		self.assertEqual(len(sheet), 2)
		self.assertEqual(sheet[0], [1]*4 + [2]*4 + [3]*4)
		self.assertEqual(sheet[1], [1]*4 + [2]*4 + [3]*4)

	def test_framesets_full_row_is_not_padded(self) -> None:
		frames = [_frame(4, 2, value) for value in range(1, FRAMESET_ROW_SIZE+1)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 9)

		self.assertEqual(len(sheet), 2)
		self.assertEqual(len(sheet[0]), 4 * FRAMESET_ROW_SIZE)

	def test_framesets_partial_last_row_is_padded_with_transindex(self) -> None:
		frames = [_frame(4, 2, value) for value in range(1, 21)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 9)

		self.assertEqual(len(sheet), 4)
		self.assertEqual(len(sheet[2]), 4 * FRAMESET_ROW_SIZE)
		self.assertEqual(sheet[2], [18]*4 + [19]*4 + [20]*4 + [9] * 4 * (FRAMESET_ROW_SIZE - 3))
		self.assertEqual(sheet[3], [18]*4 + [19]*4 + [20]*4 + [9] * 4 * (FRAMESET_ROW_SIZE - 3))

	def test_bmp_per_frame_can_not_make_a_sheet(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			frames_to_sheet([_frame(4, 2, 1)], BMPStyle.bmp_per_frame, 0)
		self.assertIn('Frames can not be combined into a sheet', str(cm.exception))

	def test_no_frames_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			frames_to_sheet([], BMPStyle.single_bmp_vertical, 0)
		self.assertIn('No frames to combine into a sheet', str(cm.exception))

class Test_Sheet_Frame_Size(unittest.TestCase):
	def test_vertical(self) -> None:
		self.assertEqual(sheet_frame_size(64, 640, 10, BMPStyle.single_bmp_vertical), (64, 64))

	def test_framesets_single_row(self) -> None:
		self.assertEqual(sheet_frame_size(12, 2, 3, BMPStyle.single_bmp_framesets), (4, 2))

	def test_framesets_multiple_rows(self) -> None:
		self.assertEqual(sheet_frame_size(68, 4, 20, BMPStyle.single_bmp_framesets), (4, 2))

	def test_bmp_per_frame_can_not_be_split(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			sheet_frame_size(4, 2, 1, BMPStyle.bmp_per_frame)
		self.assertIn('A sheet can not be split into frames', str(cm.exception))

class Test_Sheet_Round_Trip(unittest.TestCase):
	def test_vertical(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_vertical, 0)

		self.assertEqual(sheet_to_frames(sheet, len(frames), BMPStyle.single_bmp_vertical), frames)

	def test_framesets_single_row(self) -> None:
		frames = [_frame(4, 2, value) for value in (1, 2, 3)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 9)

		self.assertEqual(sheet_to_frames(sheet, len(frames), BMPStyle.single_bmp_framesets), frames)

	def test_framesets_multiple_rows(self) -> None:
		frames = [_frame(4, 2, value) for value in range(1, 21)]

		sheet = frames_to_sheet(frames, BMPStyle.single_bmp_framesets, 9)

		self.assertEqual(sheet_to_frames(sheet, len(frames), BMPStyle.single_bmp_framesets), frames)
