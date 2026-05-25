

from ...FileFormats import GRP

import unittest


def _build_frame_with_partial_failure() -> GRP.CacheGRP:
	"""
	Build a CacheGRP whose single frame's compressed decode succeeds on
	the first two lines, then raises an IndexError on the third line.

	Layout of the databuffer (width = 4, linewidth = 1, lines = 4):

	  offset 0: b'\\x01\\x05'   -> compressed: static read 1 byte -> [5]
	  offset 2: b'\\x01\\x06'   -> compressed: static read 1 byte -> [6]
	  offset 4: b'\\x01\\x07'   -> compressed: static read 1 byte -> [7]
	  offset 6: b'\\x04'        -> compressed: static read 4 bytes
	                              past end of buffer -> IndexError

	The frame's per-line offsets are ordered so that the failing offset
	(6) is the *third* line of the frame, after two successful lines.
	"""
	databuffer = b'\x01\x05\x01\x06\x01\x07\x04'

	width = 4
	height = 4
	xoffset = 0
	yoffset = 0
	linewidth = 1
	lines = 4
	line_offsets = (0, 2, 6, 4)

	grp = GRP.CacheGRP()
	grp.frames = 1
	grp.width = width
	grp.height = height
	grp.imagebuffer = [((xoffset, yoffset, linewidth, lines), line_offsets)]
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

		# Uncompressed interpretation: each line is `linewidth` raw bytes
		# at its offset, padded out to `width` with transparent (0).
		expected = [
			[0x01, 0, 0, 0],  # offset 0
			[0x01, 0, 0, 0],  # offset 2
			[0x04, 0, 0, 0],  # offset 6
			[0x01, 0, 0, 0],  # offset 4
		]

		actual = grp[0]

		self.assertEqual(
			actual,
			expected,
			msg=f'Frame contains partial compressed rows mixed with the uncompressed retry. Got rows={actual}'
		)

	def test_uncompressed_fallback_returns_correct_row_count(self) -> None:
		"""
		The returned frame must have exactly ``height`` rows. Today the
		bug accumulates compressed + uncompressed rows into one list and
		truncates with ``image[:height]``, which masks the row-count
		mismatch but still surfaces as a wrong-content check.
		"""
		grp = _build_frame_with_partial_failure()

		actual = grp[0]

		self.assertEqual(len(actual), grp.height)
		# Every row should be width-wide.
		for row in actual:
			self.assertEqual(len(row), grp.width)

	def test_uncompressed_sentinel_set_after_partial_failure(self) -> None:
		"""
		After the fallback fires, ``self.uncompressed`` should reflect
		that this GRP needs the uncompressed path. (This part of the
		current behavior is fine — included so the fix doesn't
		accidentally regress it.)
		"""
		grp = _build_frame_with_partial_failure()
		_ = grp[0]
		self.assertTrue(grp.uncompressed)


if __name__ == '__main__':
	unittest.main()
