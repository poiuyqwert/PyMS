
try:
	import Tkinter as Tk
except:
	import tkinter as Tk

class Toplevel(Tk.Toplevel):
	def make_active(self):
		if self.state() == 'withdrawn':
			self.deiconify()
		self.lift()
		self.focus_force()
		if not self.grab_status():
			self.grab_set()
			self.grab_release()
