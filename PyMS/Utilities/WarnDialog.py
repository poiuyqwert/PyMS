
from .PyMSDialog import PyMSDialog
from . import UIKit as UI

class WarnDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, message: str, title: str = 'Warning!', show_dont_warn: bool = False) -> None:
		self.message = message
		self.dont_warn = UI.IntVar()
		self.show_dont_warn = show_dont_warn
		PyMSDialog.__init__(self, parent, title, resizable=(False, False))

	def widgetize(self) -> UI.Misc | None:
		UI.Label(self, text=self.message).pack(side=UI.TOP, padx=20,pady=10)
		frame = UI.Frame(self)
		if self.show_dont_warn:
			UI.Checkbutton(frame, text="Don't warn me again", variable=self.dont_warn, anchor=UI.W).pack(side=UI.LEFT, padx=(0,10))
		ok = UI.Button(frame, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.RIGHT)
		frame.pack(side=UI.BOTTOM, fill=UI.BOTH, padx=20,pady=(0,10))
		return ok

	def setup_complete(self) -> None:
		self.minsize(300, 100)
