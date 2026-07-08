
from .Delegates import MainDelegate

from ..Utilities.ReusablePyMSDialog import ReusablePyMSDialog
from ..Utilities.FindReplaceDialog import FindReplaceDialog
from ..Utilities import UIKit as UI

class GotoDialog(ReusablePyMSDialog):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.goto = UI.IntegerVar(val_range=(0,65535), allow_hex=True)
		self.gotohistory: list[str] = []
		ReusablePyMSDialog.__init__(self, parent, 'Goto', escape=True, resizable=(False,False))

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

	def on_show(self) -> None:
		self.gotoentry.focus_set(highlight=True)

	def jump(self, _event: UI.Event | None = None) -> None:
		if not self.delegate.tbl or not self.delegate.listbox.size():
			return
		index = self.goto.get()
		FindReplaceDialog.record_history(self.gotohistory, str(index))
		i = max(0, min(index, len(self.delegate.tbl.strings)-1))
		self.delegate.listbox.select_clear(0,UI.END)
		self.delegate.listbox.select_set(i)
		self.delegate.listbox.see(i)
		self.delegate.update()

	def on_hide(self) -> None:
		self.delegate.config_.windows.goto.save_size(self)
