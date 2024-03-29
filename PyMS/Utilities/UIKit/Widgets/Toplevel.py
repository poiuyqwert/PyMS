
from .. import Theme
from .Extensions import Extensions

try: # Python 2
	import Tkinter as _Tk
except: # Python 3
	import tkinter as _Tk


class Toplevel(_Tk.Toplevel, Extensions):
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
