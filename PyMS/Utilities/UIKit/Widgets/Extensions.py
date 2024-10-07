
from ..Utils import remove_bind

import tkinter as _Tk

class Extensions(_Tk.Misc):
	def remove_bind(self, sequence, funcid): # type: (str, str) -> None
		"""Unbind for this widget for event SEQUENCE  the
		function identified with FUNCID."""
		remove_bind(self, sequence, funcid)

	def apply_cursor(self, cursors): # type: (list[str]) -> (str | None)
		for cursor in reversed(cursors):
			try:
				self.configure(cursor=cursor) # type: ignore[call-arg]
				return cursor
			except:
				pass
		return None

	def clipboard_not_empty(self) -> bool:
		return not not self.clipboard_get()

	def clipboard_set(self, text):
		self.clipboard_clear()
		self.clipboard_append(text)

class WindowExtensions(_Tk.Misc, _Tk.Wm):
	def maxsize(self, width: int | None = None, height: int | None = None) -> tuple[int, int]: # type: ignore[override]
		if width and height and not hasattr(self, '_initial_max_size'):
			self._initial_max_size = _Tk.Toplevel.maxsize(self)
		return _Tk.Toplevel.maxsize(self, width, height) # type: ignore[arg-type]

	# `wm_state` will be `'zoomed'` when `window.size == window.maxsize`, not just when it is maximized
	def is_maximized(self): # type: () -> bool
		is_maximized = (self.wm_state() == 'zoomed')
		if is_maximized and hasattr(self, '_initial_max_size'):
			cur_max_width, cur_max_height = self.maxsize()
			initial_max_width, initial_max_height = self._initial_max_size
			is_maximized = (cur_max_width >= initial_max_width and cur_max_height >= initial_max_height)
		return is_maximized
