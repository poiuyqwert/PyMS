
from ..Utils import remove_bind
from ..EventPattern import WidgetEvent

import tkinter as _Tk

from typing import Any, Callable

class Extensions(_Tk.Misc):
	def remove_bind(self, sequence: str, funcid: str) -> None:
		"""Unbind for this widget for event SEQUENCE  the
		function identified with FUNCID."""
		remove_bind(self, sequence, funcid)

	def after_managed(self, ms: int, func: Callable[..., Any], *args: Any) -> str:
		"""Schedule `func` after `ms` milliseconds and auto-cancel if this widget is destroyed first."""
		if not hasattr(self, '_managed_after_ids'):
			self._managed_after_ids: set[str] = set()
			self.bind(WidgetEvent.Destroy(), self._cancel_managed_afters, '+')
		holder: list[str] = ['']
		def wrapper() -> None:
			self._managed_after_ids.discard(holder[0])
			func(*args)
		after_id = self.after(ms, wrapper)
		holder[0] = after_id
		self._managed_after_ids.add(after_id)
		return after_id

	def after_managed_cancel(self, after_id: str | None) -> None:
		if after_id is None:
			return
		if hasattr(self, '_managed_after_ids'):
			self._managed_after_ids.discard(after_id)
		try:
			self.after_cancel(after_id)
		except Exception:
			pass

	def _cancel_managed_afters(self, _event: Any = None) -> None:
		for after_id in list(getattr(self, '_managed_after_ids', ())):
			try:
				self.after_cancel(after_id)
			except Exception:
				pass
		self._managed_after_ids = set()

	def apply_cursor(self, cursors: list[str]) -> (str | None):
		for cursor in reversed(cursors):
			try:
				self.configure(cursor=cursor) # type: ignore[call-arg]
				return cursor
			except:
				pass
		return None

	def clipboard_not_empty(self) -> bool:
		return not not self.clipboard_get()

	def clipboard_set(self, text: str) -> None:
		self.clipboard_clear()
		self.clipboard_append(text)

class WindowExtensions(_Tk.Misc, _Tk.Wm):
	def maxsize(self, width: int | None = None, height: int | None = None) -> tuple[int, int]: # type: ignore[override]
		if width and height and not hasattr(self, '_initial_max_size'):
			self._initial_max_size: tuple[int, int] | None = _Tk.Toplevel.maxsize(self) # pylint: disable=attribute-defined-outside-init
		return _Tk.Toplevel.maxsize(self, width, height) # type: ignore[arg-type]

	# `wm_state` will be `'zoomed'` when `window.size == window.maxsize`, not just when it is maximized
	def is_maximized(self) -> bool:
		is_maximized = (self.wm_state() == 'zoomed')
		if is_maximized and hasattr(self, '_initial_max_size') and self._initial_max_size is not None:
			cur_max_width, cur_max_height = self.maxsize()
			initial_max_width, initial_max_height = self._initial_max_size
			is_maximized = (cur_max_width >= initial_max_width and cur_max_height >= initial_max_height)
		return is_maximized
