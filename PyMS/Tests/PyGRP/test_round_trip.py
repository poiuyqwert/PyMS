
from ...PyGRP.utils import BMPStyle, grp_to_bmps, bmp_sheet_to_frames, check_frame_bmp, frames_to_grp
from ...FileFormats import GRP
from ...FileFormats import BMP

import unittest, io

def _frame(width: int, height: int, value: int) -> list[list[int]]:
	return [[value] * width for _ in range(height)]

def _palette() -> list[tuple[int, int, int]]:
	return [(i, i, i) for i in range(256)]

def _bmp_bytes_round_trip(bmp: BMP.BMP) -> BMP.BMP:
	saved_file = io.BytesIO()
	bmp.save(saved_file)
	loaded = BMP.BMP()
	loaded.load(saved_file.getvalue())
	return loaded

def _grp_bytes(grp: GRP.GRP) -> bytes:
	saved_file = io.BytesIO()
	grp.save(saved_file)
	return saved_file.getvalue()

class Test_Export_Import_Round_Trip(unittest.TestCase):
	def _assert_round_trips(self, original: GRP.GRP, imported: GRP.GRP) -> None:
		self.assertEqual(imported.frames, original.frames)
		self.assertEqual(imported.width, original.width)
		self.assertEqual(imported.height, original.height)
		self.assertEqual(imported.images, original.images)
		self.assertEqual(_grp_bytes(imported), _grp_bytes(original))

	def test_bmp_per_frame(self) -> None:
		frames = [_frame(8, 4, value) for value in (1, 2, 3)]
		original = frames_to_grp(frames, _palette(), False)

		bmps = grp_to_bmps(original, _palette(), BMPStyle.bmp_per_frame)
		frame_images = []
		expected_size: tuple[int, int] | None = None
		for bmp in bmps:
			loaded = _bmp_bytes_round_trip(bmp)
			check_frame_bmp(loaded, 'frame.bmp', expected_size, None)
			if expected_size is None:
				expected_size = (loaded.width, loaded.height)
			frame_images.append(loaded.image)
		imported = frames_to_grp(frame_images, _palette(), False)

		self._assert_round_trips(original, imported)

	def test_single_bmp_framesets(self) -> None:
		frames = [_frame(8, 4, value) for value in range(1, 21)]
		original = frames_to_grp(frames, _palette(), False)

		bmps = grp_to_bmps(original, _palette(), BMPStyle.single_bmp_framesets)
		self.assertEqual(len(bmps), 1)
		loaded = _bmp_bytes_round_trip(bmps[0])
		frame_images = bmp_sheet_to_frames(loaded, len(frames), BMPStyle.single_bmp_framesets, 'sheet.bmp')
		imported = frames_to_grp(frame_images, _palette(), False)

		self._assert_round_trips(original, imported)

	def test_single_bmp_vertical(self) -> None:
		frames = [_frame(8, 4, value) for value in range(1, 21)]
		original = frames_to_grp(frames, _palette(), False)

		bmps = grp_to_bmps(original, _palette(), BMPStyle.single_bmp_vertical)
		self.assertEqual(len(bmps), 1)
		loaded = _bmp_bytes_round_trip(bmps[0])
		frame_images = bmp_sheet_to_frames(loaded, len(frames), BMPStyle.single_bmp_vertical, 'sheet.bmp')
		imported = frames_to_grp(frame_images, _palette(), False)

		self._assert_round_trips(original, imported)
