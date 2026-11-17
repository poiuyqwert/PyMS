
from ...FileFormats import GRP
from ...Utilities import Assets

import unittest


def _build_frame_with_partial_failure() -> GRP.CacheGRP:
	"""
	Build a CacheGRP whose single frame's compressed decode succeeds on
	the first two lines, then raises an IndexError on the third line.

	Layout of the databuffer (width = 4, linewidth = 1, lines = 4, frame data at 0):

	  offset 0: b'\\x08\\x00\\x0A\\x00\\x0C\\x00\\x08\\x00'
	                          -> compressed: line offset table (8, 10, 12, 8)
	  offset 8: b'\\x01\\x05'   -> compressed: static read 1 byte -> [5]
	  offset 10: b'\\x01\\x06'  -> compressed: static read 1 byte -> [6]
	  offset 12: b'\\x04'       -> compressed: static read 4 bytes
	                              past end of buffer -> IndexError

	Read as uncompressed, each line is the next `linewidth` raw bytes from
	the frame data, so the rows are the first 4 bytes of the offset table.
	"""
	databuffer = b'\x08\x00\x0A\x00\x0C\x00\x08\x00' + b'\x01\x05\x01\x06\x04'

	grp = GRP.CacheGRP()
	grp.frames = 1
	grp.width = 4
	grp.height = 4
	grp.imagebuffer = [(GRP.Bounds(x_min=0, y_min=0, x_max=1, y_max=4), 0)]
	grp.databuffer = databuffer
	grp.uncompressed = None
	return grp


class Test_CacheGRP(unittest.TestCase):
	def test_uncompressed_fallback_does_not_mix_with_partial_compressed(self) -> None:
		"""
		When the compressed decoder fails part-way through a frame, the
		uncompressed fallback should produce a frame containing *only*
		the uncompressed interpretation of the data — not the partial
		compressed rows followed by the uncompressed rows.
		"""
		grp = _build_frame_with_partial_failure()

		expected = [
			[0x08, 0, 0, 0],
			[0x00, 0, 0, 0],
			[0x0A, 0, 0, 0],
			[0x00, 0, 0, 0],
		]

		self.assertEqual(grp[0], expected)

	def test_uncompressed_fallback_returns_correct_row_count(self) -> None:
		grp = _build_frame_with_partial_failure()

		actual = grp[0]

		self.assertEqual(len(actual), grp.height)
		for row in actual:
			self.assertEqual(len(row), grp.width)

	def test_uncompressed_sentinel_set_after_partial_failure(self) -> None:
		grp = _build_frame_with_partial_failure()
		_ = grp[0]
		self.assertTrue(grp.uncompressed)

	def test_uncompressed_rows_step_by_frame_width(self) -> None:
		"""
		Uncompressed rows are read sequentially from the frame data at the
		frame's full width, even when the frame is clipped to the GRP width.
		"""
		grp = GRP.CacheGRP()
		grp.frames = 1
		grp.width = 3
		grp.height = 3
		# Frame at x=1, 3 pixels wide (clipped to 2), 2 lines, starting at y=1
		grp.imagebuffer = [(GRP.Bounds(x_min=1, y_min=1, x_max=4, y_max=3), 2)]
		grp.databuffer = b'\xFF\xFF' + b'\x01\x02\x03' + b'\x04\x05\x06'
		grp.uncompressed = True

		self.assertEqual(grp[0], [
			[0, 0, 0],
			[0, 1, 2],
			[0, 4, 5],
		])

	def test_icons_grp_matches_grp(self) -> None:
		"""
		icons.grp is uncompressed; every CacheGRP frame should be a full
		width x height image matching GRP's decode.
		"""
		path = Assets.mpq_file_path('game', 'icons.grp')
		cache_grp = GRP.CacheGRP()
		cache_grp.load(path)
		grp = GRP.GRP()
		grp.load(path)

		self.assertEqual(cache_grp.frames, grp.frames)
		for frame in range(cache_grp.frames):
			image = cache_grp[frame]
			self.assertEqual(len(image), cache_grp.height, f'frame {frame}')
			for row in image:
				self.assertEqual(len(row), cache_grp.width, f'frame {frame}')
			self.assertEqual(image, grp.images[frame], f'frame {frame}')
		self.assertTrue(cache_grp.uncompressed)


if __name__ == '__main__':
	unittest.main()
