
from __future__ import annotations

import tkinter.font as _Fonts

from uuid import uuid4 as _uuid4

from typing import Sequence

class Font(_Fonts.Font):
	@staticmethod
	def named(name: str) -> Font | None:
		return Font(name=name, only_existing=True)

	@staticmethod
	def families() -> Sequence[str]:
		return _Fonts.families()

	@staticmethod
	def names() -> Sequence[str]:
		return _Fonts.names()

	# Default fonts
	@staticmethod
	def default() -> Font:
		return Font.named('TkDefaultFont') or Font()

	@staticmethod
	def text() -> Font:
		return Font.named('TkTextFont') or Font()

	@staticmethod
	def fixed() -> Font:
		return Font.named('TkFixedFont') or Font()

	@staticmethod
	def menu() -> Font:
		return Font.named('TkMenuFont') or Font()

	@staticmethod
	def heading() -> Font:
		return Font.named('TkHeadingFont') or Font()

	@staticmethod
	def caption() -> Font:
		return Font.named('TkCaptionFont') or Font()

	@staticmethod
	def small_caption() -> Font:
		return Font.named('TkSmallCaptionFont') or Font()

	@staticmethod
	def icon() -> Font:
		return Font.named('TkIconFont') or Font()

	@staticmethod
	def tooltip() -> Font:
		return Font.named('TkTooltipFont') or Font()

	def __init__(self, family: str | None = None, size: int | None = None, bold: bool | None = None, italic: bool | None = None, underline: bool | None = None, overstrike: bool | None = None, name: str | None = None, only_existing: bool = False) -> None:
		options: dict = {}
		if family is not None:
			options['family'] = family
		if size is not None:
			options['size'] = size
		if bold is not None:
			options['weight'] = _Fonts.BOLD if bold else _Fonts.NORMAL
		if italic is not None:
			options['slant'] = _Fonts.ITALIC if italic else _Fonts.ROMAN
		if underline is not None:
			options['underline'] = underline
		if overstrike is not None:
			options['overstrike'] = overstrike
		if not name:
			# In Python2.7 with Tkinter 8.5rev81008 (at least) the auto-generated `name` under the hood is somehow not unique, so we create our own unique name if None is supplied
			name = _uuid4().hex
		options['name'] = name
		options['exists'] = only_existing
		_Fonts.Font.__init__(self, **options)

	# Get settings
	def family(self) -> str:
		return self.cget('family')

	def size(self) -> int:
		return self.cget('size')

	def weight(self) -> str:
		return self.cget('weight')

	def is_bold(self) -> bool:
		return self.weight() == _Fonts.BOLD

	def slant(self) -> str:
		return self.cget('slant')

	def is_italic(self) -> bool:
		return self.slant() == _Fonts.ITALIC

	def is_underlined(self) -> bool:
		return bool(self.cget('underline'))

	def has_overstrike(self) -> bool:
		return bool(self.cget('overstrike'))

	# Get adjusted font
	def sized(self, size: int) -> Font:
		if size == self.size():
			return self
		return Font(family=self.family(), size=size, bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def scaled(self, scale: float) -> Font:
		if scale == 1:
			return self
		return Font(family=self.family(), size=int(self.size() * scale), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def bolded(self) -> Font:
		if self.is_bold():
			return self
		return Font(family=self.family(), size=self.size(), bold=True, italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike()) 

	def italicize(self) -> Font:
		if self.is_italic():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=True, underline=self.is_underlined(), overstrike=self.has_overstrike())

	def underline(self) -> Font:
		if self.is_underlined():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=True, overstrike=self.has_overstrike())

	def overstrike(self) -> Font:
		if self.has_overstrike():
			return self
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=True)

	def copy(self) -> Font:
		return Font(family=self.family(), size=self.size(), bold=self.is_bold(), italic=self.is_italic(), underline=self.is_underlined(), overstrike=self.has_overstrike())

	def __repr__(self) -> str:
		return "<Font family='%s' size=%d weight=%s slant=%s underline=%s overstrike=%s %s>" % (self.family(), self.size(), self.weight(), self.slant(), self.is_underlined(), self.has_overstrike(), self.actual())

	def __copy__(self) -> Font:
		return self.copy()

	def __deepcopy__(self, memo) -> Font:
		return self.copy()
