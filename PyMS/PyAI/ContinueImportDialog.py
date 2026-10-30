
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

from enum import Enum

class ContinueImportDialog(PyMSDialog):
	class Result(Enum):
		cancel = 0
		yes = 1
		yes_to_all = 2

	def __init__(self, parent: UI.AnyWindow, script_id: str):
		self.script_id = script_id
		self.cont = ContinueImportDialog.Result.cancel
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self) -> UI.Widget:
		UI.Label(self, text=f"The AI Script with ID '{self.script_id}' already exists, overwrite it?").pack(pady=10)
		frame = UI.Frame(self)
		yes = UI.Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=UI.LEFT, padx=3)
		UI.Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=UI.LEFT, padx=3)
		UI.Button(frame, text='No', width=10, command=self.ok).pack(side=UI.LEFT, padx=3)
		UI.Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self) -> None:
		self.cont = ContinueImportDialog.Result.yes
		self.ok()

	def yestoall(self) -> None:
		self.cont = ContinueImportDialog.Result.yes_to_all
		self.ok()

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.cont = ContinueImportDialog.Result.cancel
		self.ok()
