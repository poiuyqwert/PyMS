
from ..Utilities.UIKit import *
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.FileType import FileType

class ListfileSettings(Frame):
	def __init__(self, parent, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		Frame.__init__(self, parent)
		Label(self, text='File Lists', font=Font.default().bolded(), anchor=W).pack(fill=X)
		Label(self, text="Note: Each file list added will increase the load time for archives", anchor=W, justify=LEFT).pack(fill=X)
		self.listbox = ScrolledListbox(self, width=35, height=1)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select, lambda *e: self.action_states())
		for l in self.setdlg.settings.settings.get('listfiles', []):
			self.listbox.insert(0,l)
		if self.listbox.size():
			self.listbox.select_set(0)

		self.toolbar = Toolbar(self)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add MPQ', Key.Insert)
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove MPQ', Key.Delete, enabled=False, tags='listfile_selected')
		self.toolbar.add_spacer(0, flexible=True)
		self.toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def is_listfile_selected(self):
		return not not self.listbox.curselection()

	def action_states(self):
		self.toolbar.tag_enabled('listfile_selected', self.is_listfile_selected())

	def add(self, key=None):
		add = self.setdlg.settings.lastpath.settings.select_open_files(self, key='listfiles', title='Add Listfiles', filetypes=[FileType.txt()])
		if add:
			for i in add:
				self.listbox.insert(END,i)
			self.action_states()
			self.setdlg.edited = True

	def remove(self, key=None):
		if not self.is_listfile_selected():
			return
		i = int(self.listbox.curselection()[0])
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.setdlg.edited = True

	def save(self, page_data, mpq_dir, settings):
		settings.settings.listfiles = []
		for i in range(self.listbox.size()):
			settings.settings.listfiles.append(self.listbox.get(i))
