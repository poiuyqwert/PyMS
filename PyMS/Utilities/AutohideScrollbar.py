
from .UIKit import Scrollbar

class AutohideScrollbar(Scrollbar):
	def __init__(self, parent, **kwargs):
		Scrollbar.__init__(self, parent, **kwargs)
		self._hide = None
		self._show = None

	def place(self, **kwargs):
		self._hide = self.place_forget
		self._show = self.place
		Scrollbar.place(self, **kwargs)

	def pack(self, **kwargs):
		self._hide = self.pack_forget
		self._show = self.pack
		Scrollbar.pack(self, **kwargs)

	def grid(self, **kwargs):
		self._hide = self.grid_remove
		self._show = self.grid
		Scrollbar.grid(self, **kwargs)

	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			if self._hide:
				self._hide()
		elif self._show:
			self._show()
		Scrollbar.set(self, lo, hi)
