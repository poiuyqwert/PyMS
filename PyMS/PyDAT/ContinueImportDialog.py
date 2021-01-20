
from ..Utilities.PyMSDialog import PyMSDialog

from Tkinter import *

class ContinueImportDialog(PyMSDialog):
	def __init__(self, parent, dattype, id):
		self.dattype = dattype
		self.id = id
		self.cont = 0
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self):
		Label(self, text="You are about to import the %s entry %s, overwrite existing data?" % (self.dattype,self.id)).pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self):
		self.cont = 1
		self.ok()

	def yestoall(self):
		self.cont = 2
		self.ok()

	def cancel(self):
		self.cont = 3
		self.ok()
