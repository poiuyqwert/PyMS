
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *

from enum import Enum

class ContinueImportDialog(PyMSDialog):
	class Result(Enum):
		cancel = 0
		yes = 1
		yes_to_all = 2

	def __init__(self, parent: Misc, dattype: str, entry_id: int) -> None:
		self.dattype = dattype
		self.id = entry_id
		self.cont = ContinueImportDialog.Result.cancel
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self) -> Misc | None:
		Label(self, text=f"You are about to import the {self.dattype} entry {self.id}, overwrite existing data?").pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self) -> None:
		self.cont = ContinueImportDialog.Result.yes
		self.ok()

	def yestoall(self) -> None:
		self.cont = ContinueImportDialog.Result.yes_to_all
		self.ok()

	def cancel(self, _: Event | None = None) -> None:
		self.cont = ContinueImportDialog.Result.cancel
		self.ok()
