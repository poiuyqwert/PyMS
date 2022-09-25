
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.FileType import FileType

class ImportListDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self):
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', Key.Delete, enabled=False, tags='item_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Selected Script', Ctrl.i, enabled=False, tags='item_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, expand=1)

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall, state=[NORMAL,DISABLED][not self.parent.imports])
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.parent.imports:
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		return ok

	def setup_complete(self):
		self.minsize(200,150)
		self.parent.settings.windows.load_window_size('list_import', self)

	def is_item_selected(self):
		return not not self.listbox.curselection()

	def can_import(self):
		return not not self.parent.imports

	def action_states(self):
		self.toolbar.tag_enabled('item_selected', self.is_item_selected())
		self.importbtn['state'] = NORMAL if self.can_import() else DISABLED

	def add(self, key=None):
		iimport = self.parent.settings.lastpath.txt.select_open_files(self, key='import', title='Add Imports', filetypes=[FileType.txt()])
		if iimport:
			for i in iimport:
				if i not in self.parent.imports:
					self.parent.imports.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		index = int(self.listbox.curselection()[0])
		del self.parent.imports[index]
		if self.parent.imports and index == len(self.parent.imports):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, key=None):
		self.parent.iimport(iimport=self.listbox.get(self.listbox.curselection()[0]), parent=self)

	def iimportall(self):
		self.parent.iimport(iimport=self.parent.imports, parent=self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.imports:
			for file in self.parent.imports:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def dismiss(self):
		self.parent.settings.windows.save_window_size('list_import', self)
		PyMSDialog.dismiss(self)
