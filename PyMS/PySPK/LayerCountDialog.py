
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class LayerCountDialog(PyMSDialog):
	def __init__(self, parent: Misc) -> None:
		self.result = IntegerVar(5, [1,5])
		PyMSDialog.__init__(self, parent, 'How many layers?')

	def widgetize(self) -> (Misc | None):
		Label(self, text='How many layers are contained in the BMP?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.result).pack(padx=5, fill=X)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def cancel(self, event: Event | None = None) -> None:
		self.result.set(0)
		PyMSDialog.cancel(self)
