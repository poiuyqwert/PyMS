
from .. import Theme
from .Extensions import Extensions, WindowExtensions

import tkinter as _Tk


class Toplevel(_Tk.Toplevel, Extensions, WindowExtensions):
	def __init__(self, *args, **kwargs):
		_Tk.Toplevel.__init__(self, *args, **kwargs)
		Theme.apply_theme(self)

	def make_active(self):
		if self.state() == 'withdrawn':
			self.deiconify()
		self.lift()
		self.focus_force()
		if not self.grab_status():
			self.grab_set()
			self.grab_release()
