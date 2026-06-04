
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI

class InfoDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, need_size: bool = False) -> None:
		self.lowi = UI.IntegerVar(32, [1,255], callback=self.check)
		self.letters = UI.IntegerVar(208, [1,224])
		self.need_size: bool | None = need_size
		self.width = UI.IntegerVar(8, [1,255])
		self.height = UI.IntegerVar(11, [1,255])
		PyMSDialog.__init__(self, parent, 'FNT Specifications')

	def widgetize(self) -> (UI.Misc | None):
		UI.Label(self, text='Whats the ASCII code of the lowest character?').pack(padx=5, pady=5)
		UI.Entry(self, textvariable=self.lowi).pack(padx=5, fill=UI.X)
		UI.Label(self, text='How many letters are in the font?').pack(padx=5, pady=5)
		UI.Entry(self, textvariable=self.letters).pack(padx=5, fill=UI.X)
		if self.need_size:
			UI.Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			UI.Entry(self, textvariable=self.width).pack(padx=5, fill=UI.X)
			UI.Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			UI.Entry(self, textvariable=self.height).pack(padx=5, fill=UI.X)
		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def check(self, i: int) -> None:
		self.letters.range[1] = 256 - i
		self.letters.editvalue()

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.need_size = None
		PyMSDialog.cancel(self)
