
from . import UIKit as UI
from .PyMSDialog import PyMSDialog

class ReusablePyMSDialog(PyMSDialog):
	"""A modeless `PyMSDialog` that is hidden instead of destroyed when closed, so it can be reused.

	Closing the dialog (`ok`/`cancel`/window close) dismisses it, which only withdraws it. The
	owning window keeps the instance, re-shows the same window with `show()`, and destroys it
	as usual with `destroy()` when it is no longer needed.

	Subclasses hook into the lifecycle with `on_show` (e.g. restore focus) and `on_hide`
	(e.g. cancel timers, save state).
	"""

	def __init__(self, parent: UI.Misc, title: str, *, center: bool = True, escape: bool = False, resizable: tuple[bool, bool] = (True,True), set_min_size: tuple[bool, bool] = (False,False)) -> None:
		PyMSDialog.__init__(self, parent, title, center=center, grabwait=False, escape=escape, resizable=resizable, set_min_size=set_min_size)

	def show(self) -> None:
		self.make_active()
		self.on_show()

	def on_show(self) -> None:
		pass

	def on_hide(self) -> None:
		pass

	def dismiss(self) -> None:
		self.on_hide()
		self.withdraw()
		self.update_idletasks()
		self.master.focus_set()
