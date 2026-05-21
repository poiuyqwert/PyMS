
from __future__ import annotations

from .. import Theme
from .Extensions import Extensions, WindowExtensions
from ...utils import is_mac

import tkinter as _Tk

from typing import Any


class Toplevel(_Tk.Toplevel, Extensions, WindowExtensions):
	def __init__(self, *args: Any, **kwargs: Any) -> None:
		_Tk.Toplevel.__init__(self, *args, **kwargs)
		Theme.apply_theme(self)

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
