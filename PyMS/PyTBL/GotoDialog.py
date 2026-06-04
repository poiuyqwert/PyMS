
from .Delegates import MainDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI

class GotoDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.goto = UI.IntegerVar(val_range=(0,65535), allow_hex=True)
		self.gotohistory: list[str] = []
		PyMSDialog.__init__(self, parent, 'Goto', grabwait=False, escape=True, resizable=(False,False))

	def widgetize(self) -> (UI.Misc | None):
		f = UI.Frame(self)
		UI.Label(f, text='Index:').grid(row=0,column=0)
		self.gotoentry = UI.TextDropDown(f, self.goto, self.gotohistory, 5)
		self.gotoentry.entry.selection_range(0, UI.END)
		self.gotoentry.grid(row=0,column=1)

		UI.Button(f, text='Goto', command=self.jump).grid(row=0,column=2, padx=(4,0))
		f.pack(padx=4,pady=4)

		self.bind(UI.Key.Return(), self.jump)

		return self.gotoentry

	def setup_complete(self) -> None:
		self.delegate.config_.windows.goto.load_size(self)

	def jump(self, _event: UI.Event | None = None) -> None:
		if not self.delegate.tbl:
			return
		s = self.goto.get(True)
		if not s in self.gotohistory:
			self.gotohistory.insert(0, s)
		i = min(self.goto.get(), len(self.delegate.tbl.strings)-1)
		self.delegate.listbox.select_clear(0,UI.END)
		self.delegate.listbox.select_set(i)
		self.delegate.listbox.see(i)
		self.delegate.update()

	def dismiss(self) -> None:
		self.delegate.config_.windows.goto.save_size(self)
		PyMSDialog.dismiss(self)
