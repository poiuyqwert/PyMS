
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

class FlagEditor(PyMSDialog):
	def __init__(self, parent, flags):
		self.flags = flags
		self.location = IntVar()
		self.location.set(not not flags & 1)
		self.visible = IntVar()
		self.visible.set(not not flags & 2)
		self.bwonly = IntVar()
		self.bwonly.set(not not flags & 4)
		PyMSDialog.__init__(self, parent, 'Flag Editor', resizable=(False, False))

	def widgetize(self):
		choices = Frame(self)
		Checkbutton(choices, text='Requires a Location', variable=self.location).grid(sticky=W)
		Checkbutton(choices, text='Invisible in StarEdit', variable=self.visible).grid(sticky=W)
		Checkbutton(choices, text='BroodWar Only', variable=self.bwonly).grid(sticky=W)
		choices.pack(pady=3, padx=3)
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=1, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=1, pady=3)
		buttons.pack(pady=3, padx=3)
		return ok

	def ok(self):
		self.flags = self.location.get() + 2 * self.visible.get() + 4 * self.bwonly.get()
		PyMSDialog.ok(self)
