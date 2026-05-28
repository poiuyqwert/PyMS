
from .UIKit import *
#
class PyMSDialog(Toplevel):
	def __init__(self, parent: Misc, title: str, *, center: bool = True, grabwait: bool = True, escape: bool = False, resizable: tuple[bool, bool] = (True,True), set_min_size: tuple[bool, bool] = (False,False)) -> None:
		Toplevel.__init__(self, parent)
		self.title(title)
		self.protocol('WM_DELETE_WINDOW', self.cancel)
		if escape:
			self.bind(Shortcut.Close(), self.cancel)
		self.parent = parent
		focus: Misc | None = self.widgetize()
		self.update_idletasks()
		geometry = Geometry.of(self)
		if set_min_size[0] or set_min_size[1]:
			self.minsize(geometry.size.width if set_min_size[0] else 0, geometry.size.height if set_min_size[1] else 0)
		screen_size = Size(self.winfo_screenwidth(), self.winfo_screenheight())
		if center:
			self.geometry(GeometryAdjust(pos=geometry.size.centered_in(screen_size)).text)
		self.resizable(*resizable)
		self.setup_complete()
		if grabwait:
			self.grab_wait()
		if not focus:
			focus = self
		focus.focus_set()

	def widgetize(self) -> Misc | None:
		return None
	def setup_complete(self) -> None:
		pass

	def dismiss(self) -> None:
		self.withdraw()
		self.update_idletasks()
		self.master.focus_set()
		self.destroy()

	def ok(self, _event: Event | None = None) -> None:
		self.dismiss()

	def cancel(self, _event: Event | None = None) -> None:
		self.dismiss()
