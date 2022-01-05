
from ..FileFormats import DialogBIN, FNT

class StringPreview:
	# GLYPH_CACHE = {}

	def __init__(self, text, font, tfontgam, remap=None, remap_palette=None, default_color=1):
		self.text = text
		self.font = font
		self.tfontgam = tfontgam
		self.remap = remap
		self.remap_palette = remap_palette
		self.default_color = default_color
		self.glyphs = None

	def get_glyphs(self):
		if self.glyphs == None:
			self.glyphs = []
			color = self.default_color
			for c in self.text:
				a = ord(c)
				if a >= self.font.start and a < self.font.start + len(self.font.letters):
					a -= self.font.start
					self.glyphs.append(FNT.letter_to_photo(self.tfontgam, self.font.letters[a], color, self.remap, self.remap_palette))
				elif (a in self.remap or a in FNT.COLOR_CODES_INGAME) and not color in FNT.COLOR_OVERPOWER:
					color = a if a > 1 else self.default_color
		return self.glyphs

	def get_positions(self, x1,y1,x2,y2, align_flags):
		positions = []
		position = [x1,y1]
		size = [x2-x1,y2-y1]
		line = []
		line_width = [0]
		word = []
		word_width = [0]
		def add_line():
			if line:
				o = 0
				if align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_CENTER:
					o = int((size[0] - line_width[0]) / 2.0)
				elif align_flags & DialogBIN.BINWidget.FLAG_TEXT_ALIGN_RIGHT:
					o = size[0] - line_width[0]
				for w in line:
					positions.append([position[0] + o, position[1]])
					o += w
				del line[:]
				line_width[0] = 0
			position[1] += self.font.height
		def add_word():
			line.extend(word)
			line_width[0] += word_width[0]
			word_width[0] = 0
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
					self.font.sizes[a][0] = w
				w += 1
				word.append(w)
				word_width[0] += w
			if c == ' ':
				if line and line_width[0] + word_width[0] >= size[0]:
					add_line()
				add_word()
				if line_width[0] >= size[0]:
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
			offset = height - (position[1]-y1)
			if align_flags & DialogBIN.BINWidget.FLAG_ALIGN_MIDDLE:
				offset /= 2
			for position in positions:
				position[1] += offset
		return positions
