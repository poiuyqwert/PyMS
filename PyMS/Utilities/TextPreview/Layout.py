from __future__ import annotations

from ...FileFormats import FNT
from ...FileFormats.PCX import PCX

from dataclasses import dataclass
from enum import Enum

from typing import TYPE_CHECKING, ClassVar, Sequence
if TYPE_CHECKING:
	from ..UIKit.Types import AnyPhotoImage

class HAlign(Enum):
	left = 0
	center = 1
	right = 2

class VAlign(Enum):
	top = 0
	middle = 1
	bottom = 2

@dataclass
class TextStyle:
	# How text is laid out and colored like the game draws it
	font: FNT.FNT
	# The color palette of the font (`tfontgam.pcx` in game, or a menu `tfont.pcx`), and the color codes it supports
	colors: PCX
	remap: FNT.Remapping
	# The color used at the start, and after the `<1>` color code
	default_color: int = 2
	# The pixels between letters
	letter_spacing: int = 1
	# The width of a space, `None` to use the font's (or the average letter width when the font's is 0)
	space_width: int | None = None
	# The characters that start a new line
	line_breaks: str = '\r\n'
	# Lines longer than this are wrapped at spaces, `None` to never wrap
	wrap_width: int | None = None
	align: HAlign = HAlign.left
	valign: VAlign = VAlign.top

	# The game uses a 4 pixel space in tooltips and the text of most screens
	INGAME_SPACE_WIDTH: ClassVar[int] = 4

	@classmethod
	def ingame(cls, font: FNT.FNT, colors: PCX) -> TextStyle:
		# How the game draws text in game (tooltips, and the text of most screens)
		return cls(font, colors, FNT.COLOR_CODES_INGAME, space_width=cls.INGAME_SPACE_WIDTH, line_breaks='\x0A\x0C')

	def effective_space_width(self) -> int:
		if self.space_width is not None:
			return self.space_width
		font = self.font
		index = ord(' ') - font.start
		if 0 <= index < len(font.sizes) and font.sizes[index][0]:
			return font.sizes[index][0]
		# The space has no width in some fonts, so the game uses the average width of the other letters
		widths = [size[0] for letter, size in enumerate(font.sizes) if letter != index]
		if not widths:
			return 0
		return int(round(sum(widths) / float(len(widths))))

@dataclass(frozen=True)
class InlineImage:
	# An image placed in the text like a letter, `width` pixels wide (before the letter spacing).
	# `x_offset` is how far left of its position the image is drawn (for images with transparent space at their left).
	image: AnyPhotoImage
	width: int
	height: int
	x_offset: int = 0

@dataclass(frozen=True)
class GlyphItem:
	letter_index: int
	color: int
	x: int
	y: int

@dataclass(frozen=True)
class ImageItem:
	image: InlineImage
	x: int
	y: int

LayoutItem = GlyphItem | ImageItem

@dataclass(frozen=True)
class TextLayout:
	style: TextStyle
	items: tuple[LayoutItem, ...]
	# The size of the laid out text (the widest line, and every line)
	width: int
	height: int

	@classmethod
	def from_runs(cls, runs: TextRuns, style: TextStyle, *, box_width: int | None = None, box_height: int | None = None) -> TextLayout:
		# Places each letter and image of the text.
		# Lines are aligned in `box_width` (or the widest line), and the text is aligned vertically in `box_height` (or the text height).
		font = style.font
		space = style.effective_space_width()
		if isinstance(runs, str):
			runs = (runs,)

		# The finished lines: their letters/images with their widths, and the line width
		lines: list[tuple[list[tuple[_Pending, int]], int]] = []
		line: list[tuple[_Pending, int]] = []
		line_width = 0
		word: list[tuple[_Pending, int]] = []
		word_width = 0
		color = style.default_color

		def add_line() -> None:
			nonlocal line, line_width
			lines.append((line, line_width))
			line = []
			line_width = 0

		def add_word() -> None:
			nonlocal word, word_width, line_width
			line.extend(word)
			line_width += word_width
			word = []
			word_width = 0

		def add(pending: _Pending, width: int) -> None:
			nonlocal word_width
			advance = width + style.letter_spacing
			word.append((pending, advance))
			word_width += advance

		for run in runs:
			if isinstance(run, InlineImage):
				add(run, run.width)
				continue
			for character in run:
				code = ord(character)
				letter_index = code - font.start
				if 0 <= letter_index < len(font.letters):
					width = space if character == ' ' else font.sizes[letter_index][0]
					add((letter_index, color), width)
				elif code in style.remap and color not in FNT.COLOR_OVERPOWER:
					color = code if code > 1 else style.default_color
				if character == ' ':
					if style.wrap_width is not None:
						if line and line_width + word_width >= style.wrap_width:
							add_line()
						add_word()
						if line_width >= style.wrap_width:
							add_line()
					else:
						add_word()
				elif character in style.line_breaks:
					add_word()
					add_line()
		if word:
			add_word()
		if line:
			add_line()

		width = max((line_width for _, line_width in lines), default=0)
		height = font.height * len(lines)
		align_width = width if box_width is None else box_width
		y_offset = 0
		if box_height is not None:
			if style.valign == VAlign.middle:
				y_offset = (box_height - height) // 2
			elif style.valign == VAlign.bottom:
				y_offset = box_height - height
		items: list[LayoutItem] = []
		for line_index, (pending_items, line_width) in enumerate(lines):
			x = 0
			if style.align == HAlign.center:
				x = int((align_width - line_width) / 2.0)
			elif style.align == HAlign.right:
				x = align_width - line_width
			y = y_offset + line_index * font.height
			for pending, advance in pending_items:
				if isinstance(pending, InlineImage):
					items.append(ImageItem(pending, x, y))
				else:
					letter_index, letter_color = pending
					items.append(GlyphItem(letter_index, letter_color, x, y))
				x += advance
		return cls(style, tuple(items), width, height)

TextRuns = str | Sequence[str | InlineImage]

# A letter (index into the font, color) or an image waiting for its position
_Pending = tuple[int, int] | InlineImage
