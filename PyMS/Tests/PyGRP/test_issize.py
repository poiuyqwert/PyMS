
from ...PyGRP.utils import BMPStyle, check_frame_bmp, bmp_sheet_to_frames
from ...FileFormats import BMP
from ...Utilities.PyMSError import PyMSError

import unittest

def _bmp(width: int, height: int) -> BMP.BMP:
	bmp = BMP.BMP()
	bmp.set_pixels([[0] * width for _ in range(height)])
	return bmp

class Test_Check_Frame_BMP(unittest.TestCase):
	def test_matching_size_is_accepted(self) -> None:
		check_frame_bmp(_bmp(64, 64), 'frame.bmp', None, (64, 64))
		check_frame_bmp(_bmp(64, 64), 'frame.bmp', (64, 64), (64, 64))

	def test_single_dimension_mismatch_is_rejected(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			check_frame_bmp(_bmp(64, 32), 'frame.bmp', None, (64, 64))
		self.assertIn("Invalid dimensions in the BMP 'frame.bmp' (Expected 64x64, got 64x32)", str(cm.exception))

	def test_frame_not_matching_first_frame_is_rejected(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			check_frame_bmp(_bmp(64, 32), 'frame.bmp', (64, 64), None)
		self.assertIn("Incorrect frame dimensions in BMP 'frame.bmp' (Expected 64x64, got 64x32)", str(cm.exception))

	def test_oversized_first_frame_is_rejected(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			check_frame_bmp(_bmp(300, 10), 'frame.bmp', None, None)
		self.assertIn('Frames have a maximum size of 256x256', str(cm.exception))

class Test_Sheet_IsSize(unittest.TestCase):
	def test_single_dimension_mismatch_is_rejected(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			bmp_sheet_to_frames(_bmp(64, 64), 2, BMPStyle.single_bmp_framesets, 'sheet.bmp', issize=(32, 32))
		self.assertIn("Invalid dimensions in the BMP 'sheet.bmp' (Expected 32x32, got 32x64)", str(cm.exception))

	def test_matching_size_is_accepted(self) -> None:
		frames = bmp_sheet_to_frames(_bmp(64, 64), 2, BMPStyle.single_bmp_framesets, 'sheet.bmp', issize=(32, 64))
		self.assertEqual(len(frames), 2)
