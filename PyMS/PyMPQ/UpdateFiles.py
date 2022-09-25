
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.ScrolledListbox import ScrolledListbox

class UpdateFiles(PyMSDialog):
	def __init__(self, parent, files):
		self.files = files
		PyMSDialog.__init__(self, parent, 'Files Edited', resizable=(False, False))

	def widgetize(self):
		Label(self, text='These files have been modified since they were extracted.\n\nChoose which files to update the archive with:', justify=LEFT, anchor=W).pack(fill=X)

		self.listbox = ScrolledListbox(self, selectmode=MULTIPLE, font=Font.fixed(), width=20, height=10)
		self.listbox.pack(fill=BOTH, expand=1, padx=5)

		sel = Frame(self)
		Button(sel, text='Select All', command=lambda: self.listbox.select_set(0,END)).pack(side=LEFT, fill=X, expand=1)
		Button(sel, text='Unselect All', command=lambda: self.listbox.select_clear(0,END)).pack(side=LEFT, fill=X, expand=1)
		sel.pack(fill=X, padx=5)
		for f in self.files:
			self.listbox.insert(END,f)
			self.listbox.select_set(END)
		btns = Frame(self)
		save = Button(btns, text='Ok', width=10, command=self.ok)
		save.pack(side=LEFT, pady=5, padx=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, pady=5, padx=3)
		btns.pack()
		return save

	def cancel(self):
		self.files = []
		PyMSDialog.ok(self)

	def ok(self):
		self.files = []
		for i in self.listbox.curselection():
			self.files.append(self.listbox.get(i))
		PyMSDialog.ok(self)
