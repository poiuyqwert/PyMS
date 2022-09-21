
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.FileType import FileType

class ExternalDefDialog(PyMSDialog):
	def __init__(self, parent, settings):
		self.settings = settings
		PyMSDialog.__init__(self, parent, 'External Definitions')

	def widgetize(self):
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add File', Key.Insert)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove File', Key.Insert, tags='def_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, expand=1)
		self.update()
		self.listbox.bind(WidgetEvent.Listbox.Select, lambda _: self.action_states())

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		buttons.pack()

		return ok

	def setup_complete(self):
		self.minsize(200,150)
		self.settings.windows.load_window_size('external_def', self)

	def def_selected(self):
		return not not self.listbox.curselection()

	def action_states(self):
		self.toolbar.tag_enabled('def_selected', self.def_selected())

	def add(self, key=None):
		iimport = self.settings.lastpath.def_txt.select_open_file(self, title='Add External Definition File', filetypes=[FileType.txt()])
		if iimport and iimport not in self.parent.extdefs:
			self.parent.extdefs.append(iimport)
			self.update()
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		if not self.def_selected():
			return
		index = int(self.listbox.curselection()[0])
		del self.parent.extdefs[index]
		if self.parent.extdefs and index == len(self.parent.extdefs):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.extdefs:
			for file in self.parent.extdefs:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		self.action_states()

	def ok(self):
		PyMSDialog.ok(self)

	def dismiss(self):
		self.settings.windows.save_window_size('external_def', self)
		PyMSDialog.dismiss(self)
