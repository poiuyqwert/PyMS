
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar

class FramesDialog(PyMSDialog):
	def __init__(self, parent):
		self.result = IntegerVar(1, [1,None])
		PyMSDialog.__init__(self, parent, 'How many frames?', resizable=(True,False))

	def widgetize(self):
		Label(self, text='How many frames are contained in the BMP?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self):
		self.parent.settings.window.load_window_size('frames', self)

	def cancel(self):
		self.result.check = False
		self.result.set(0)
		PyMSDialog.cancel(self)

	def dismiss(self):
		self.parent.settings.window.save_window_size('frames', self)
		PyMSDialog.dismiss(self)
