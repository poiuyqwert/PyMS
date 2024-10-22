
from .Delegates import ImportListDelegate

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities import Config

class ImportListDialog(PyMSDialog):
	def __init__(self, parent: Misc, window_geometry_config: Config.WindowGeometry, txt_last_path_config: Config.SelectFile, delegate: ImportListDelegate) -> None:
		self.window_geometry_config = window_geometry_config
		self.txt_last_path_config = txt_last_path_config
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self) -> Misc | None:
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', Key.Delete, enabled=False, tags='has_selection')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Selected Script', Ctrl.i, enabled=False, tags='has_selection')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=1)
 
		##Listbox
		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, expand=1)

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall, state=DISABLED if not self.delegate.imports else NORMAL)
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.delegate.imports:
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		return ok

	def setup_complete(self) -> None:
		self.minsize(200,150)
		self.window_geometry_config.load_size(self)

	def add(self) -> None:
		iimport = self.txt_last_path_config.select_open_multiple(self)
		if iimport:
			for i in iimport:
				if i not in self.delegate.imports:
					self.delegate.imports.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self) -> None:
		index = int(self.listbox.curselection()[0])
		del self.delegate.imports[index]
		if self.delegate.imports and index == len(self.delegate.imports):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self) -> None:
		self.delegate.iimport(files=self.listbox.get(self.listbox.curselection()[0]), parent=self)

	def iimportall(self) -> None:
		self.delegate.iimport(files=self.delegate.imports, parent=self)

	def update_states(self) -> None:
		has_selection = not not self.listbox.curselection()
		self.toolbar.tag_enabled('has_selection', has_selection)

		can_import = not not self.delegate.imports
		self.toolbar.tag_enabled('can_import', can_import)
		self.importbtn['state'] = NORMAL if can_import else DISABLED

	def update(self) -> None:
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.delegate.imports:
			for file in self.delegate.imports:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		self.update_states()

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
