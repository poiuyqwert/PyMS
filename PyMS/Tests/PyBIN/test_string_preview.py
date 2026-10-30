
from ...PyBIN import StringPreview as StringPreviewMod
from ...PyBIN.StringPreview import StringPreview
from ...FileFormats import FNT, PCX
from ...FileFormats.DialogBIN import BINWidget

import unittest
from unittest.mock import Mock, patch
from typing import cast


class _StubFont:
	# Minimal stand-in for FNT.FNT: glyphs 'A'..'Z' plus space, each a fixed width.
	def __init__(self, glyph_width: int = 9, height: int = 10) -> None:
		self.start = ord(' ')
		self.height = height
		count = ord('Z') - ord(' ') + 1
		self.letters = [object() for _ in range(count)]
		# Size = (width, height, xoffset, yoffset); space starts at width 0 to trigger averaging.
		self.sizes: list[tuple[int, int, int, int]] = []
		for i in range(count):
			width = 0 if i == 0 else glyph_width
			self.sizes.append((width, height, 0, 0))


def _font() -> FNT.FNT:
	return cast(FNT.FNT, _StubFont())


def _preview(text: str, font: FNT.FNT, *, default_color: int = 2, remap: FNT.Remapping | None = None) -> StringPreview:
	return StringPreview(text, font, cast(PCX.PCX, Mock()), remap=remap, default_color=default_color)


class Test_get_positions(unittest.TestCase):
	def test_left_aligned_advances_by_glyph_width(self) -> None:
		# Each glyph occupies width+1 = 10px.
		positions = _preview('AB', _font()).get_positions(0, 0, 100, 100, align_flags=0)
		self.assertEqual(positions, [(0, 0), (10, 0)])

	def test_center_alignment(self) -> None:
		positions = _preview('AB', _font()).get_positions(0, 0, 100, 100, align_flags=BINWidget.FLAG_TEXT_ALIGN_CENTER)
		self.assertEqual(positions, [(40, 0), (50, 0)])

	def test_right_alignment(self) -> None:
		positions = _preview('AB', _font()).get_positions(0, 0, 100, 100, align_flags=BINWidget.FLAG_TEXT_ALIGN_RIGHT)
		self.assertEqual(positions, [(80, 0), (90, 0)])

	def test_wraps_to_next_line(self) -> None:
		# Width 25 fits two 10px glyphs ('AB') then wraps the next word to y=height.
		positions = _preview('AB CD', _font()).get_positions(0, 0, 25, 100, align_flags=0)
		ys = sorted({y for _, y in positions})
		self.assertEqual(ys, [0, 10])

	def test_explicit_newline_starts_new_line(self) -> None:
		positions = _preview('A\nB', _font()).get_positions(0, 0, 100, 100, align_flags=0)
		self.assertEqual(positions[0][1], 0)
		self.assertEqual(positions[-1][1], 10)

	def test_middle_alignment_offsets_vertically(self) -> None:
		top = _preview('A', _font()).get_positions(0, 0, 100, 100, align_flags=0)
		middle = _preview('A', _font()).get_positions(0, 0, 100, 100, align_flags=BINWidget.FLAG_ALIGN_MIDDLE)
		self.assertGreater(middle[0][1], top[0][1])

	def test_space_width_averaging_side_effect(self) -> None:
		font = _font()
		# The space glyph starts at width 0; rendering a space computes and caches the average
		# width into the width slot so subsequent spaces reuse it.
		_preview('A B', font).get_positions(0, 0, 100, 100, align_flags=0)
		self.assertEqual(font.sizes[0][0], 9)


class Test_get_glyphs(unittest.TestCase):
	def _glyphs(self, text: str, *, default_color: int = 2):
		font = _font()
		preview = _preview(text, font, default_color=default_color, remap=FNT.COLOR_CODES_INGAME)
		with patch.object(StringPreviewMod.FNT, 'letter_to_photo', side_effect=lambda pal, letter, color, remap, remap_palette: ('glyph', color)):
			return preview.get_glyphs()

	def test_emits_one_glyph_per_printable_char(self) -> None:
		glyphs = self._glyphs('AB')
		self.assertEqual(glyphs, [('glyph', 2), ('glyph', 2)])

	def test_color_code_changes_subsequent_color(self) -> None:
		# chr(4) is a color code in COLOR_CODES_INGAME; it is consumed (no glyph) and recolors.
		glyphs = self._glyphs('\x04A')
		self.assertEqual(glyphs, [('glyph', 4)])

	def test_color_overpower_locks_further_changes(self) -> None:
		# Color 5 is in COLOR_OVERPOWER, so a following color code is ignored.
		glyphs = self._glyphs('\x05\x04A')
		self.assertEqual(glyphs, [('glyph', 5)])

	def test_color_code_one_resets_to_default(self) -> None:
		glyphs = self._glyphs('\x01A', default_color=2)
		self.assertEqual(glyphs, [('glyph', 2)])

	def test_glyphs_are_cached(self) -> None:
		preview = _preview('A', _font(), remap=FNT.COLOR_CODES_INGAME)
		with patch.object(StringPreviewMod.FNT, 'letter_to_photo', side_effect=lambda *a, **k: ('glyph', 0)):
			first = preview.get_glyphs()
			second = preview.get_glyphs()
		self.assertIs(first, second)
