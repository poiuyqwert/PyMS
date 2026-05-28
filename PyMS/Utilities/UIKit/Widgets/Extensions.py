
from ..Utils import remove_bind
from ..EventPattern import WidgetEvent
from ...utils import is_mac

import tkinter as _Tk

from typing import Any, Callable

class MiscExtensions(_Tk.Misc):
	def remove_bind(self, sequence: str, funcid: str) -> None:
		"""Unbind for this widget for event SEQUENCE  the
		function identified with FUNCID."""
		remove_bind(self, sequence, funcid)

	def after_managed(self, ms: int, func: Callable[..., Any], *args: Any) -> str:
		"""Schedule `func` after `ms` milliseconds and auto-cancel if this widget is destroyed first."""
		if not hasattr(self, '_managed_after_ids'):
			self._managed_after_ids: set[str] = set() # pylint: disable=attribute-defined-outside-init
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
		except:
			pass

	def _cancel_managed_afters(self, _event: Any = None) -> None:
		for after_id in list(getattr(self, '_managed_after_ids', ())):
			try:
				self.after_cancel(after_id)
			except:
				pass
		self._managed_after_ids = set() # pylint: disable=attribute-defined-outside-init

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

class WindowExtensions(MiscExtensions, _Tk.Wm):
	def make_active(self) -> None:
		if self.state() == 'withdrawn':
			self.deiconify()
		self.lift()
		self.focus_force()
		if not self.grab_status():
			self.grab_set()
			self.grab_release()

	def make_frameless(self, parent_toplevel: _Tk.Wm | None = None) -> None:
		self.wm_overrideredirect(True)
		if is_mac():
			if parent_toplevel is not None:
				self.wm_transient(parent_toplevel)
			try:
				# Tk 9.0 / macOS Big Sur+ renders borderless NSWindows with a 26pt
				# rounded-corner mask and exposes no Tcl knob to disable it.
				from ._macos_corners import disable_rounded_corners
				disable_rounded_corners(self)
			except:
				pass

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

	def grab_wait(self) -> None:
		self.grab_set()
		self.wait_window(self)
