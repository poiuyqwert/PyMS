
from .Delegates import MainDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *

class GotoDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.goto = IntegerVar(range=(0,65535), allow_hex=True)
		self.gotohistory: list[str] = []
		PyMSDialog.__init__(self, parent, 'Goto', grabwait=False, escape=True, resizable=(False,False))

	def widgetize(self) -> (Misc | None):
		f = Frame(self)
		Label(f, text='Index:').grid(row=0,column=0)
		self.gotoentry = TextDropDown(f, self.goto, self.gotohistory, 5)
		self.gotoentry.entry.selection_range(0, END)
		self.gotoentry.grid(row=0,column=1)

		Button(f, text='Goto', command=self.jump).grid(row=0,column=2, padx=(4,0))
		f.pack(padx=4,pady=4)

		self.bind(Key.Return(), self.jump)

		return self.gotoentry

	def setup_complete(self) -> None:
		self.delegate.config_.windows.goto.load(self)

	def jump(self, event: Event | None = None) -> None:
		if not self.delegate.tbl:
			return
		s = self.goto.get(True)
		if not s in self.gotohistory:
			self.gotohistory.insert(0, s)
		i = min(self.goto.get(), len(self.delegate.tbl.strings)-1)
		self.delegate.listbox.select_clear(0,END)
		self.delegate.listbox.select_set(i)
		self.delegate.listbox.see(i)
		self.delegate.update()

	def dismiss(self) -> None:
		self.delegate.config_.windows.goto.save(self)
		PyMSDialog.dismiss(self)
