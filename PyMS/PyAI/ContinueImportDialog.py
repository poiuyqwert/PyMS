
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

from enum import Enum

class ContinueImportDialog(PyMSDialog):
	class Result(Enum):
		cancel = 0
		yes = 1
		yes_to_all = 2

	def __init__(self, parent: AnyWindow, script_id: str):
		self.script_id = script_id
		self.cont = ContinueImportDialog.Result.cancel
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self):
		Label(self, text="The AI Script with ID '%s' already exists, overwrite it?" % self.script_id).pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self):
		self.cont = ContinueImportDialog.Result.yes
		self.ok()

	def yestoall(self):
		self.cont = ContinueImportDialog.Result.yes_to_all
		self.ok()

	def cancel(self):
		self.cont = ContinueImportDialog.Result.cancel
		self.ok()
