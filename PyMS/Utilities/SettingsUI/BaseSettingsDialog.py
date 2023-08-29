
from .SettingsTab import SettingsTab

from ..PyMSDialog import PyMSDialog
from ..ErrorDialog import ErrorDialog
from ..UIKit import *
from ..Config import Config
from ..PyMSError import PyMSError
from ..EditedState import EditedState

from typing import Protocol, TypeVar, Generic

class SettingsDialogDelegate(Protocol):
	def open_files(self) -> PyMSError | None:
		...

	def exit(self) -> None:
		...

C = TypeVar('C', bound=Config)
class BaseSettingsDialog(PyMSDialog, Generic[C]):
	def __init__(self, parent: Misc, delegate: SettingsDialogDelegate, config: C, err: PyMSError | None = None) -> None:
		self.delegate = delegate
		self.config_ = config
		self.err = err
		self.tabs: list[SettingsTab] = []
		self.edited_state = EditedState()
		self.edited_state.callback += self.edited_updated
		PyMSDialog.__init__(self, parent, 'Settings')

	def widgetize(self) -> Misc | None:
		self.notebook = Notebook(self)
		self.notebook.pack(fill=BOTH, expand=1, padx=5, pady=5)

		btns = Frame(self)
		self.ok_button = Button(btns, text='Ok', width=10, command=self.ok, state=DISABLED)
		self.ok_button.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		if self.err:
			self.after(1, self.showerr)
		return self.ok_button

	def edited_updated(self, edited: bool) -> None:
		self.ok_button['state'] = NORMAL if edited else DISABLED

	def showerr(self) -> None:
		if self.err is None:
			return
		ErrorDialog(self, self.err)

	def cancel(self, event: Event | None = None) -> None:
		if self.err:
			if MessageBox.askyesno(parent=self, title='Exit?', message="One or more files required for this program can not be found and must be chosen. Canceling will close the program, do you wish to continue?"):
				self.parent.after(1, self.delegate.exit)
				PyMSDialog.cancel(self)
			else:
				pass
		elif not self.edited_state.is_edited or MessageBox.askyesno(parent=self, title='Cancel?', message="Are you sure you want to cancel?\nAll unsaved changes will be lost."):
			PyMSDialog.cancel(self)

	def add_tab(self, name: str, tab: SettingsTab) -> None:
		self.notebook.add_tab(tab, name)
		self.tabs.append(tab)

	def save(self):
		for tab in self.tabs:
			tab.save()

	def ok(self):
		if self.edited_state.is_edited:
			self.config_.save_state()
			self.save()
			if err := self.delegate.open_files():
				self.config_.reset_state()
				ErrorDialog(self, err)
				return
		PyMSDialog.ok(self)
