
from .Delegates import MainDelegate
from .Config import PyAIConfig

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

import os

class ImportListDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, delegate: MainDelegate, config: PyAIConfig):
		self.delegate = delegate
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self) -> Widget:
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
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall)
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.config_.imports.data:
			self.config_.imports.data = list(file_path for file_path in self.config_.imports.data if os.path.exists(file_path))
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		return ok

	def setup_complete(self) -> None:
		self.minsize(200,150)
		self.config_.windows.list_import.load_size(self)

	def is_item_selected(self) -> bool:
		return not not self.listbox.curselection()

	def can_import(self) -> bool:
		return not not self.config_.imports.data

	def action_states(self) -> None:
		self.toolbar.tag_enabled('item_selected', self.is_item_selected())
		self.importbtn['state'] = NORMAL if self.can_import() else DISABLED

	def add(self, event: Event | None = None) -> None:
		iimport = self.config_.last_path.txt.import_.select_open_multiple(self, title='Add Imports')
		if iimport:
			for i in iimport:
				if i not in self.config_.imports.data:
					self.config_.imports.data.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, event: Event | None = None) -> None:
		index = int(self.listbox.curselection()[0])
		del self.config_.imports.data[index]
		if self.config_.imports.data and index == len(self.config_.imports.data):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, event: Event | None = None) -> None:
		self.delegate.iimport([self.listbox.get(self.listbox.curselection()[0])], self)

	def iimportall(self) -> None:
		self.delegate.iimport(self.config_.imports.data, self)

	def update(self) -> None:
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.config_.imports.data:
			for file in self.config_.imports.data:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def dismiss(self) -> None:
		self.config_.windows.list_import.save_size(self)
		PyMSDialog.dismiss(self)
