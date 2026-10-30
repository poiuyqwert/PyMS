
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

class LayerCountDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc) -> None:
		self.result = UI.IntegerVar(5, [1,5])
		PyMSDialog.__init__(self, parent, 'How many layers?')

	def widgetize(self) -> (UI.Misc | None):
		UI.Label(self, text='How many layers are contained in the BMP?').pack(padx=5, pady=5)
		UI.Entry(self, textvariable=self.result).pack(padx=5, fill=UI.X)

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.result.set(0)
		PyMSDialog.cancel(self)
