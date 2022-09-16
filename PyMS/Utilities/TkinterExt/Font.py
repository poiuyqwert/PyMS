
try:
	import tkFont as _Fonts
except:
	import tkinter.font as _Fonts

from uuid import uuid4 as _uuid4

class Font(_Fonts.Font):
	@staticmethod
	def named(name): # type: (str) -> (Font | None)
		return Font(name=name, only_existing=True)

	@staticmethod
	def families(): # type: () -> list[str]
		return _Fonts.families()

	@staticmethod
	def names(): # type: () -> list[str]
		return _Fonts.names()

	# Default fonts
	@staticmethod
	def default(): # type: () -> Font
		return Font.named('TkDefaultFont')

	@staticmethod
	def text(): # type: () -> Font
		return Font.named('TkTextFont')

	@staticmethod
	def fixed(): # type: () -> Font
		return Font.named('TkFixedFont')

	@staticmethod
	def menu(): # type: () -> Font
		return Font.named('TkMenuFont')

	@staticmethod
	def heading(): # type: () -> Font
		return Font.named('TkHeadingFont')

	@staticmethod
	def caption(): # type: () -> Font
		return Font.named('TkCaptionFont')

	@staticmethod
	def small_caption(): # type: () -> Font
		return Font.named('TkSmallCaptionFont')

	@staticmethod
	def icon(): # type: () -> Font
		return Font.named('TkIconFont')

	@staticmethod
	def tooltip(): # type: () -> Font
		return Font.named('TkTooltipFont')

	def __init__(self, family=None, size=None, bold=None, italic=None, underline=None, overstrike=None, name=None, only_existing=False): # type: (str, int, bool, bool, bool, bool, str, bool) -> Font
		options = {}
		if family != None:
			options['family'] = family
		if size != None:
			options['size'] = size
		if bold != None:
			options['weight'] = _Fonts.BOLD if bold else _Fonts.NORMAL
		if italic != None:
			options['slant'] = _Fonts.ITALIC if italic else _Fonts.ROMAN
		if underline != None:
			options['underline'] = underline
		if overstrike != None:
			options['overstrike'] = overstrike
		if not name:
			# In Python2.7 with Tkinter 8.5rev81008 (at least) the auto-generated `name` under the hood is somehow not unique, so we create our own unique name if None is supplied
			name = _uuid4().hex
		options['name'] = name
		options['exists'] = only_existing
		_Fonts.Font.__init__(self, **options)

	# Get settings
	def family(self): # type: () -> str
		return self.cget('family')

	def size(self): # type: () -> int
		return self.cget('size')

	def weight(self): # type: () -> str
		return self.cget('weight')

	def is_bold(self): # type: () -> bool
		return self.weight() == _Fonts.BOLD

	def slant(self): # type: () -> str
		return self.cget('slant')

	def is_italic(self): # type: () -> bool
		return self.slant() == _Fonts.ITALIC

	def is_underlined(self): # type: () -> bool
		return bool(self.cget('underline'))

	def has_overstrike(self): # type: () -> bool
		return bool(self.cget('overstrike'))

	# Get adjusted font
	def sized(self, size): # type: (int) -> Font
		if size == self.size():
			return self
		return Font(family=self.family(), size=size, bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def scaled(self, scale): # type: (float) -> Font
		if scale == 1:
			return self
		return Font(family=self.family(), size=int(self.size() * scale), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def bolded(self): # type: () -> Font
		if self.is_bold():
			return self
		return Font(family=self.family(), size=self.size(), bold=True, italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike()) 

	def italicize(self): # type: () -> Font
		if self.is_italic():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=True, underline=self.is_underlined(), overstrike=self.has_overstrike())

	def underline(self): # type: () -> Font
		if self.is_underlined():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=True, overstrike=self.has_overstrike())

	def overstrike(self): # type: () -> Font
		if self.has_overstrike():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=True)

	def copy(self): # type: () -> Font
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def __repr__(self): # type: () -> str
		return "<Font family='%s' size=%d weight=%s slant=%s underline=%s overstrike=%s %s>" % (self.family(), self.size(), self.weight(), self.slant(), self.is_underlined(), self.has_overstrike(), self.actual())
