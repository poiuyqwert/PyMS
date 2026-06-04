
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

class UpdateFiles(PyMSDialog):
	def __init__(self, parent: UI.Misc, files: list[str]) -> None:
		self.files = files
		PyMSDialog.__init__(self, parent, 'Files Edited', resizable=(False, False))

	def widgetize(self) -> UI.Widget | None:
		UI.Label(self, text='These files have been modified since they were extracted.\n\nChoose which files to update the archive with:', justify=UI.LEFT, anchor=UI.W).pack(fill=UI.X)

		self.listbox = UI.ScrolledListbox(self, selectmode=UI.MULTIPLE, font=UI.Font.fixed(), width=20, height=10)
		self.listbox.pack(fill=UI.BOTH, expand=1, padx=5)

		sel = UI.Frame(self)
		UI.Button(sel, text='Select All', command=lambda: self.listbox.select_set(0,UI.END)).pack(side=UI.LEFT, fill=UI.X, expand=1)
		UI.Button(sel, text='Unselect All', command=lambda: self.listbox.select_clear(0,UI.END)).pack(side=UI.LEFT, fill=UI.X, expand=1)
		sel.pack(fill=UI.X, padx=5)
		for f in self.files:
			self.listbox.insert(UI.END,f)
			self.listbox.select_set(UI.END)
		btns = UI.Frame(self)
		save = UI.Button(btns, text='Ok', width=10, command=self.ok)
		save.pack(side=UI.LEFT, pady=5, padx=3)
		UI.Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT, pady=5, padx=3)
		btns.pack()
		return save

	def cancel(self, _event: UI.Event | None = None) -> None:
		self.files = []
		PyMSDialog.ok(self)

	def ok(self, _event: UI.Event | None = None) -> None:
		self.files = []
		for i in self.listbox.curselection():
			self.files.append(self.listbox.get(i))
		PyMSDialog.ok(self)
