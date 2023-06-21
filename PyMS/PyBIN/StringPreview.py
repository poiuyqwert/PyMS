
from __future__ import annotations

from ..FileFormats import DialogBIN, FNT, PCX

from ..Utilities.UIKit import ImageTk

class StringPreview:
	# GLYPH_CACHE = {}

	def __init__(self, text: str, font: FNT.FNT, tfontgam: PCX.PCX, remap: FNT.Remapping | None = None, remap_palette: PCX.PCX | None = None, default_color: int = 1) -> None:
		self.text = text
		self.font = font
		self.tfontgam = tfontgam
		self.remap = remap
		self.remap_palette = remap_palette
		self.default_color = default_color
		self.glyphs: list[ImageTk.PhotoImage] | None = None

	def get_glyphs(self) -> list[ImageTk.PhotoImage]:
		if self.glyphs is None:
			self.glyphs = []
			color = self.default_color
			for c in self.text:
				a = ord(c)
				if a >= self.font.start and a < self.font.start + len(self.font.letters):
					a -= self.font.start
					self.glyphs.append(FNT.letter_to_photo(self.tfontgam, self.font.letters[a], color, self.remap, self.remap_palette))
				elif self.remap and (a in self.remap or a in FNT.COLOR_CODES_INGAME) and not color in FNT.COLOR_OVERPOWER:
					color = a if a > 1 else self.default_color
		return self.glyphs

	def get_positions(self, x1: int, y1: int , x2: int, y2: int, align_flags: int) -> list[tuple[int, int]]:
		positions: list[tuple[int, int]] = []
		x = x1
		y = y1
		width = x2-x1
		# height = y2-y1
		line: list[int] = []
		line_width = 0
		word: list[int] = []
		word_width = 0
		def add_line() -> None:
			nonlocal line_width, y
			if line:
				o = 0
				if align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER:
					o = int((width - line_width) / 2.0)
				elif align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT:
					o = width - line_width
				for w in line:
					positions.append((x + o, y))
					o += w
				del line[:]
				line_width = 0
			y += self.font.height
		def add_word() -> None:
			nonlocal line_width, word_width
			line.extend(word)
			line_width += word_width
			word_width = 0
			del word[:]
		for c in self.text:
			a = ord(c)
			if a >= self.font.start and a < self.font.start + len(self.font.letters):
				a -= self.font.start
				w = self.font.sizes[a][0]
				if c == ' ' and w == 0:
					w = 0
					count = 0
					for l in range(len(self.font.letters)):
						if l != a:
							w += self.font.sizes[l][0]
							count += 1
					w = int(round(w / float(count)))
					x,y,_,h = self.font.sizes[a]
					self.font.sizes[a] = (x,y,w,h)
				w += 1
				word.append(w)
				word_width += w
			if c == ' ':
				if line and line_width + word_width >= width:
					add_line()
				add_word()
				if line_width >= width:
					add_line()
			elif c in '\r\n':
				add_word()
				add_line()

		if word:
			add_word()
		if line:
			add_line()

		if align_flags & (DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE | DialogBIN.BINWidget.FLAG_ALIGN_BOTTOM):
			height = y2-y1
			offset = height - (y-y1)
			if align_flags & DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE:
				offset //= 2
			for i,position in enumerate(positions):
				positions[i] = (position[0], position[1] + offset)
		return positions
