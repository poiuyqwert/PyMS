
from .Delegates import MainDelegate
from .Config import PyAIConfig

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets

import os

class ImportListDialog(PyMSDialog):
	def __init__(self, parent: UI.AnyWindow, delegate: MainDelegate, config: PyAIConfig):
		self.delegate = delegate
		self.config_ = config
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self) -> UI.Widget:
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', UI.Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', UI.Key.Delete, enabled=False, tags='item_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Selected Script', UI.Ctrl.i, enabled=False, tags='item_selected')
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=1)

		self.listbox = UI.ScrolledListbox(self, font=UI.Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=UI.BOTH, expand=1)

		buttons = UI.Frame(self)
		ok = UI.Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=3, pady=3)
		self.importbtn = UI.Button(buttons, text='Import All', width=10, command=self.iimportall)
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
		self.importbtn['state'] = UI.NORMAL if self.can_import() else UI.DISABLED

	def add(self, _event: UI.Event | None = None) -> None:
		iimport = self.config_.last_path.txt.import_.select_open_multiple(self, title='Add Imports')
		if iimport:
			for i in iimport:
				if i not in self.config_.imports.data:
					self.config_.imports.data.append(i)
			self.update()
			self.listbox.select_clear(0,UI.END)
			self.listbox.select_set(UI.END)
			self.listbox.see(UI.END)

	def remove(self, _event: UI.Event | None = None) -> None:
		index = int(self.listbox.curselection()[0])
		del self.config_.imports.data[index]
		if self.config_.imports.data and index == len(self.config_.imports.data):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, _event: UI.Event | None = None) -> None:
		self.delegate.iimport([self.listbox.get(self.listbox.curselection()[0])], self)

	def iimportall(self) -> None:
		self.delegate.iimport(self.config_.imports.data, self)

	def update(self) -> None:
		sel = 0
		if self.listbox.size():
			selection = self.listbox.curselection()
			if selection:
				sel = selection[0]
			self.listbox.delete(0, UI.END)
		if self.config_.imports.data:
			for file in self.config_.imports.data:
				self.listbox.insert(UI.END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def dismiss(self) -> None:
		self.config_.windows.list_import.save_size(self)
		PyMSDialog.dismiss(self)
