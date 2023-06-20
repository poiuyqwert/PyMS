
from ..Widgets import *

from typing import Callable

class AutohideScrollbar(Scrollbar):
	def __init__(self, parent: Misc, **kwargs):
		Scrollbar.__init__(self, parent, **kwargs)
		self._hide: Callable[[], None] | None = None
		self._show: Callable[[], None] | None = None

	def place(self, **kwargs) -> None: # type: ignore[override]
		self._hide = self.place_forget
		self._show = self.place
		Scrollbar.place(self, **kwargs)

	def pack(self, **kwargs) -> None: # type: ignore[override]
		self._hide = self.pack_forget
		self._show = self.pack
		Scrollbar.pack(self, **kwargs)

	def grid(self, **kwargs) -> None: # type: ignore[override]
		self._hide = self.grid_remove
		self._show = self.grid
		Scrollbar.grid(self, **kwargs)

	def set(self, lo: float, hi: float) -> None:
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			if self._hide:
				self._hide()
		elif self._show:
			self._show()
		Scrollbar.set(self, lo, hi)
