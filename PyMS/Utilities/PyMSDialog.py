
from .UIKit import *

class PyMSDialog(Toplevel):
	def __init__(self, parent, title, center=True, grabwait=True, hidden=False, escape=False, resizable=(True,True), set_min_size=(False,False)): # type: (Misc, str, bool, bool, bool, bool, tuple[bool,bool], tuple[bool,bool]) -> None
		self._initial_max_size = None # type: tuple[int, int] | None
		Toplevel.__init__(self, parent)
		self.title(title)
		self.protocol('WM_DELETE_WINDOW', self.cancel)
		if escape:
			self.bind(Shortcut.Close(), self.cancel)
		#self.transient(parent)
		self.parent = parent
		focus: Misc | None = self.widgetize()
		self.update_idletasks()
		if not focus:
			focus = self
		focus.focus_set()
		screen_size = Size(self.winfo_screenwidth(), self.winfo_screenheight())
		geometry = Geometry.of(self)
		assert geometry.size is not None
		if center:
			self.geometry(GeometryAdjust(pos=geometry.size.centered_in(screen_size)).text)
		self.resizable(*resizable)
		min_w = 0
		max_w = screen_size.width
		min_h = 0
		max_h = screen_size.height
		if not resizable[0]:
			min_w = max_w = geometry.size.width
		elif set_min_size[0]:
			min_w = geometry.size.width
		if not resizable[1]:
			min_h = max_h = geometry.size.height
		elif set_min_size[1]:
			min_h = geometry.size.height
		self.minsize(min_w, min_h)
		self.maxsize(max_w, max_h)
		self.setup_complete()
		if grabwait:
			self.grab_wait()

	def grab_wait(self): # type: () -> None
		self.grab_set()
		self.wait_window(self)

	def widgetize(self): # type: () -> (Misc | None)
		return None
	def setup_complete(self): # type: () -> None
		pass

	def dismiss(self): # type: () -> None
		self.withdraw()
		self.update_idletasks()
		self.master.focus_set()
		self.destroy()

	def ok(self, event=None): # type: (Event | None) -> None
		self.dismiss()

	def cancel(self, event=None): # type: (Event | None) -> None
		self.dismiss()

	def maxsize(self, width: int | None = None, height: int | None = None) -> tuple[int, int]: # type: ignore[override]
		if width and height and self._initial_max_size is None:
			self._initial_max_size = Toplevel.maxsize(self)
		return Toplevel.maxsize(self, width, height) # type: ignore

	# `wm_state` will be `'zoomed'` when `window.size == window.maxsize`, not just when it is maximized
	def is_maximized(self): # type: () -> bool
		is_maximized = (self.wm_state() == 'zoomed')
		if is_maximized and self._initial_max_size is not None:
			cur_max_width, cur_max_height = self.maxsize()
			initial_max_width, initial_max_height = self._initial_max_size
			is_maximized = (cur_max_width >= initial_max_width and cur_max_height >= initial_max_height)
		return is_maximized
