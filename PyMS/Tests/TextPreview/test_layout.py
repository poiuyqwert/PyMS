from .utils import stub_font, stub_colors, letter

from ...Utilities.TextPreview.Layout import TextStyle, HAlign, VAlign, InlineImage, GlyphItem, ImageItem, TextLayout
from ...FileFormats import FNT

import unittest
from typing import Any

def _style(**kwargs: Any) -> TextStyle:
	kwargs.setdefault('font', stub_font())
	kwargs.setdefault('colors', stub_colors())
	kwargs.setdefault('remap', FNT.COLOR_CODES_INGAME)
	return TextStyle(**kwargs)

def _positions(text: str, style: TextStyle, **kwargs: Any) -> list[tuple[int, int]]:
	return [(item.x, item.y) for item in TextLayout.from_runs(text, style, **kwargs).items]

def _colors(text: str, style: TextStyle) -> list[int]:
	return [item.color for item in TextLayout.from_runs(text, style).items if isinstance(item, GlyphItem)]

class Test_Positions(unittest.TestCase):
	def test_left_aligned_advances_by_letter_width_and_spacing(self) -> None:
		# Each letter occupies width+1 = 10px
		self.assertEqual(_positions('AB', _style(), box_width=100), [(0, 0), (10, 0)])

	def test_center_alignment(self) -> None:
		self.assertEqual(_positions('AB', _style(align=HAlign.center), box_width=100), [(40, 0), (50, 0)])

	def test_right_alignment(self) -> None:
		self.assertEqual(_positions('AB', _style(align=HAlign.right), box_width=100), [(80, 0), (90, 0)])

	def test_alignment_without_a_box_uses_the_widest_line(self) -> None:
		positions = _positions('ABC\nA', _style(align=HAlign.right))
		self.assertEqual(positions[-1], (20, 10))

	def test_wraps_words_to_the_next_line(self) -> None:
		# Width 25 fits two 10px letters ('AB') then wraps the next word to y=height
		positions = _positions('AB CD', _style(wrap_width=25), box_width=25)
		self.assertEqual(sorted({y for _, y in positions}), [0, 10])

	def test_no_wrapping_without_a_wrap_width(self) -> None:
		positions = _positions('AB CD EF GH', _style())
		self.assertEqual({y for _, y in positions}, {0})

	def test_line_break_characters_start_new_lines(self) -> None:
		positions = _positions('A\nB', _style())
		self.assertEqual(positions[0][1], 0)
		self.assertEqual(positions[-1], (0, 10))
		# The line breaks are configurable (strings in the game also break on `<12>`)
		positions = _positions('A\x0cB', _style(line_breaks='\x0a\x0c'))
		self.assertEqual(positions[-1], (0, 10))

	def test_empty_lines_take_space(self) -> None:
		layout = TextLayout.from_runs('A\n\nB', _style())
		self.assertEqual(layout.items[-1].y, 20)
		self.assertEqual(layout.height, 30)

	def test_middle_and_bottom_alignment_in_the_box(self) -> None:
		self.assertEqual(_positions('A', _style(valign=VAlign.middle), box_width=100, box_height=100), [(0, 45)])
		self.assertEqual(_positions('A', _style(valign=VAlign.bottom), box_width=100, box_height=100), [(0, 90)])
		# Vertical alignment needs a box height
		self.assertEqual(_positions('A', _style(valign=VAlign.bottom)), [(0, 0)])

	def test_size_is_the_widest_line_by_every_line(self) -> None:
		layout = TextLayout.from_runs('ABC\nA', _style())
		self.assertEqual((layout.width, layout.height), (30, 20))

class Test_Spaces(unittest.TestCase):
	def test_zero_width_space_uses_the_average_letter_width_without_changing_the_font(self) -> None:
		font = stub_font()
		style = _style(font=font)
		self.assertEqual(style.effective_space_width(), 9)
		self.assertEqual(_positions('A B', style), [(0, 0), (10, 0), (20, 0)])
		self.assertEqual(font.sizes[0][0], 0)

	def test_fixed_space_width(self) -> None:
		self.assertEqual(_positions('A B', _style(space_width=4)), [(0, 0), (10, 0), (15, 0)])

	def test_font_space_width_when_it_has_one(self) -> None:
		font = stub_font()
		font.sizes[0] = (3, 10, 0, 0)
		self.assertEqual(_style(font=font).effective_space_width(), 3)

class Test_Colors(unittest.TestCase):
	def test_letters_start_in_the_default_color(self) -> None:
		self.assertEqual(_colors('AB', _style(default_color=3)), [3, 3])

	def test_color_code_changes_following_letters_and_is_not_drawn(self) -> None:
		self.assertEqual(_colors('A\x04B', _style()), [2, 4])

	def test_color_code_one_returns_to_the_default_color(self) -> None:
		self.assertEqual(_colors('\x04A\x01B', _style(default_color=3)), [4, 3])

	def test_colors_after_an_unchangeable_color_are_ignored(self) -> None:
		# 5 is in COLOR_OVERPOWER
		self.assertEqual(_colors('\x05\x04A', _style()), [5])

	def test_only_codes_of_the_remap_change_the_color(self) -> None:
		# 8 is an in game color, but not a menu color
		self.assertEqual(_colors('\x08A', _style()), [8])
		self.assertEqual(_colors('\x08A', _style(remap=FNT.COLOR_CODES_GLUE)), [2])

	def test_letter_indexes_are_relative_to_the_font_start(self) -> None:
		items = TextLayout.from_runs('AZ', _style()).items
		self.assertEqual([item.letter_index for item in items if isinstance(item, GlyphItem)], [letter('A'), letter('Z')])

class Test_InlineImages(unittest.TestCase):
	def test_images_are_placed_like_letters(self) -> None:
		image = InlineImage(object(), width=14, height=12) # type: ignore[arg-type]
		layout = TextLayout.from_runs(['A', image, 'B'], _style())
		self.assertEqual(layout.items[1], ImageItem(image, 10, 0))
		# The image advances by its width plus the letter spacing
		self.assertEqual((layout.items[2].x, layout.items[2].y), (25, 0))
		self.assertEqual(layout.width, 35)

	def test_images_follow_line_breaks(self) -> None:
		image = InlineImage(object(), width=14, height=12) # type: ignore[arg-type]
		layout = TextLayout.from_runs(['A\n', image], _style())
		self.assertEqual(layout.items[-1], ImageItem(image, 0, 10))
