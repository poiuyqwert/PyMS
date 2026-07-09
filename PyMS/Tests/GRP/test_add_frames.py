
from ...FileFormats import GRP
from ...Utilities.PyMSError import PyMSError

import unittest, io

def make_frame(width: int, height: int, index: int = 1) -> list[list[int]]:
	return [[index] * width for _ in range(height)]

class Test_Add_Frames(unittest.TestCase):
	def test_add_frame_sets_dimensions(self) -> None:
		grp = GRP.GRP()
		grp.add_frame(make_frame(8, 16))

		self.assertEqual(grp.frames, 1)
		self.assertEqual(grp.width, 8)
		self.assertEqual(grp.height, 16)

	def test_add_frame_multiple_frames(self) -> None:
		frames = [make_frame(8, 16, 1), make_frame(8, 16, 2)]

		grp = GRP.GRP()
		for frame in frames:
			grp.add_frame(frame)

		self.assertEqual(grp.frames, 2)
		self.assertEqual(grp.images, frames)

	def test_add_frame_round_trip(self) -> None:
		frames = [make_frame(8, 16, 1), make_frame(8, 16, 2)]

		save_grp = GRP.GRP()
		for frame in frames:
			save_grp.add_frame(frame)
		saved_file = io.BytesIO()
		save_grp.save(saved_file)

		saved_file.seek(0)
		load_grp = GRP.GRP()
		load_grp.load(saved_file)

		self.assertEqual(load_grp.width, 8)
		self.assertEqual(load_grp.height, 16)
		self.assertEqual(load_grp.images, frames)

	def test_add_frame_mismatched_height_raises(self) -> None:
		grp = GRP.GRP()
		grp.add_frame(make_frame(8, 16))

		with self.assertRaises(PyMSError) as cm:
			grp.add_frame(make_frame(8, 8))
		self.assertIn('has unexpected height', str(cm.exception))

	def test_add_frame_mismatched_width_raises(self) -> None:
		grp = GRP.GRP()
		grp.add_frame(make_frame(8, 16))

		with self.assertRaises(PyMSError) as cm:
			grp.add_frame(make_frame(16, 16))
		self.assertIn('has unexpected width', str(cm.exception))

	def test_add_frame_inconsistent_line_widths_raises(self) -> None:
		frame = make_frame(8, 16)
		frame[4] = [1] * 4

		grp = GRP.GRP()
		with self.assertRaises(PyMSError) as cm:
			grp.add_frame(frame)
		self.assertIn('has unexpected width', str(cm.exception))

	def test_add_frames_vertical(self) -> None:
		frames = [make_frame(8, 16, 1), make_frame(8, 16, 2)]
		sheet = frames[0] + frames[1]

		grp = GRP.GRP()
		grp.add_frames(sheet, 2, vertical=True)

		self.assertEqual(grp.frames, 2)
		self.assertEqual(grp.width, 8)
		self.assertEqual(grp.height, 16)
		self.assertEqual(grp.images, frames)

	def test_add_frames_framesets(self) -> None:
		frames = [make_frame(8, 16, 1), make_frame(8, 16, 2)]
		sheet = [frames[0][y] + frames[1][y] for y in range(16)]

		grp = GRP.GRP()
		grp.add_frames(sheet, 2, vertical=False)

		self.assertEqual(grp.frames, 2)
		self.assertEqual(grp.width, 8)
		self.assertEqual(grp.height, 16)
		self.assertEqual(grp.images, frames)
