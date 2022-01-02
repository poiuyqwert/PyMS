
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.UIKit import *

class InfoDialog(PyMSDialog):
	def __init__(self, parent, size=False):
		self.lowi = IntegerVar(32, [1,255], callback=self.check)
		self.letters = IntegerVar(208, [1,224])
		self.size = size
		self.width = IntegerVar(8, [1,255])
		self.height = IntegerVar(11, [1,255])
		PyMSDialog.__init__(self, parent, 'FNT Specifications')

	def widgetize(self):
		Label(self, text='Whats the ASCII code of the lowest character?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.lowi).pack(padx=5, fill=X)
		Label(self, text='How many letters are in the font?').pack(padx=5, pady=5)
		Entry(self, textvariable=self.letters).pack(padx=5, fill=X)
		if self.size:
			Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			Entry(self, textvariable=self.width).pack(padx=5, fill=X)
			Label(self, text='What is the max width of each character?').pack(padx=5, pady=5)
			Entry(self, textvariable=self.height).pack(padx=5, fill=X)
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def check(self,i):
		self.letters.range[1] = 256 - i
		self.letters.editvalue()

	def cancel(self):
		self.size = None
		PyMSDialog.cancel(self)
