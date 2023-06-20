
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings

class FramesDialog(PyMSDialog):
	def __init__(self, parent: Misc, settings: Settings):
		self.settings = settings
		self.result = IntegerVar(1, [1,None])
		PyMSDialog.__init__(self, parent, 'How many frames?', resizable=(True,False))

	def widgetize(self) -> (Misc | None):
		Label(self, text='How many frames are contained in the BMP?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self) -> None:
		self.settings.window.load_window_size('frames', self)

	def cancel(self, e: Event | None = None) -> None:
		self.result.set(0)
		PyMSDialog.cancel(self)

	def dismiss(self) -> None:
		self.settings.window.save_window_size('frames', self)
		PyMSDialog.dismiss(self)
