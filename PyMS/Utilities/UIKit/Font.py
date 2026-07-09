
from __future__ import annotations

import re as _re
import tkinter.font as _Fonts

from typing import Sequence

__all__ = [
	'Font',
]

class Font(_Fonts.Font):
	# Fonts are interned by their resolved Tcl font name, so every construction of
	# an equivalent font returns the same instance and the underlying named font is
	# created/configured exactly once. Re-creating an equivalent font would re-apply
	# its spec to the shared named font, invalidating Tk's font metrics and forcing a
	# re-resolution that is pathologically slow (multiple seconds) on macOS. Pooling
	# also keeps every Font alive for the interpreter's lifetime, so tkinter's
	# `__del__` never runs `font delete` on a font other widgets still reference.
	_pool: dict[str, Font] = {}

	@classmethod
	def clear_pool(cls) -> None:
		# Pooled fonts belong to the Tk interpreter that created them. The app uses a
		# single root for its lifetime, but tests (and anything that tears down and
		# recreates the root) must drop the stale instances so they are recreated
		# against the new interpreter.
		cls._pool.clear()

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

	@staticmethod
	def _pool_key(*, family: str | None, size: int | None, bold: bool | None, italic: bool | None, underline: bool | None, overstrike: bool | None, name: str | None) -> str:
		if name:
			return name
		family_part = _re.sub(r"\W+", "_", family) if family else "DEFAULT"
		size_part = size if size else "DEFAULT"
		return f"pyms_{family_part}_{size_part}_{bool(bold):d}{bool(italic):d}{bool(underline):d}{bool(overstrike):d}"

	def __new__(cls, *, family: str | None = None, size: int | None = None, bold: bool | None = None, italic: bool | None = None, underline: bool | None = None, overstrike: bool | None = None, name: str | None = None, only_existing: bool = False) -> Font:
		existing = cls._pool.get(cls._pool_key(family=family, size=size, bold=bold, italic=italic, underline=underline, overstrike=overstrike, name=name))
		if existing is not None:
			return existing
		return super().__new__(cls)

	def __init__(self, *, family: str | None = None, size: int | None = None, bold: bool | None = None, italic: bool | None = None, underline: bool | None = None, overstrike: bool | None = None, name: str | None = None, only_existing: bool = False) -> None:
		key = type(self)._pool_key(family=family, size=size, bold=bold, italic=italic, underline=underline, overstrike=overstrike, name=name)
		# `__new__` returns the already-pooled instance for an equivalent font; in
		# that case the Tcl font is already created, so skip re-initializing it.
		if type(self)._pool.get(key) is self:
			return
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
		options['name'] = key
		options['exists'] = only_existing or key in _Fonts.names()
		_Fonts.Font.__init__(self, **options)
		# Pool only after a successful init so a failed `only_existing` lookup is
		# not cached as a usable font.
		type(self)._pool[key] = self

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
		return f"<Font family='{self.family()}' size={self.size()} weight={self.weight()} slant={self.slant()} underline={self.is_underlined()} overstrike={self.has_overstrike()} {self.actual()}>"

	def __copy__(self) -> Font:
		return self.copy()

	def __deepcopy__(self, memo: None) -> Font:
		return self.copy()
