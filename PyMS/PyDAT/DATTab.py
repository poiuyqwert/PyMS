
from .DATTabConveniences import DATTabConveniences
from .EntryCountDialog import EntryCountDialog

from ..Utilities.Notebook import NotebookTab
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.FileType import FileType
from ..Utilities.fileutils import check_allow_overwrite_internal_file

import copy

class DATTab(NotebookTab, DATTabConveniences):
	ARROW_DOWN = None
	ARROW_UP = None
	DAT_ID = None

	def __init__(self, parent, toplevel):
		self.id = 0
		self.toplevel = toplevel
		self.used_by_references = None
		self.used_by_collapse_button = None
		self.used_by_listbox = None
		self.used_by_data = []
		self.used_by_header = None
		self.edited = False
		NotebookTab.__init__(self, parent)

	def get_dat_data(self):
		return self.toplevel.data_context.dat_data(self.DAT_ID)

	def update_used_by_header(self):
		text = 'Used By (%d)' % len(self.used_by_data)
		if  self.toplevel.data_context.settings.get('show_used_by', True):
			text += ':'
		self.used_by_header.set(text)

	def toggle_used_by(self, toggle=True):
		visible = self.toplevel.data_context.settings.get('show_used_by', True)
		if toggle:
			visible = not visible
			self.toplevel.data_context.settings.show_used_by = visible
			self.update_used_by_header()
		if not visible:
			self.used_by_listbox.pack_forget()
			self.used_by_collapse_button['image'] = DATTab.ARROW_UP
		else:
			self.used_by_listbox.pack(side=BOTTOM, fill=X, padx=2, pady=2)
			self.used_by_collapse_button['image'] = DATTab.ARROW_DOWN

	def setup_used_by(self, references):
		self.used_by_references = references

		f = Frame(self)
		h  = Frame(f)
		if DATTab.ARROW_DOWN == None:
			DATTab.ARROW_DOWN = Assets.get_image('arrow')
		if DATTab.ARROW_UP == None:
			DATTab.ARROW_UP = Assets.get_image('arrowup')
		self.used_by_collapse_button = Button(h, image=DATTab.ARROW_DOWN,  command=self.toggle_used_by)
		self.used_by_collapse_button.pack(side=LEFT, padx=(0, 5))
		self.used_by_header = StringVar()
		Label(h, textvariable=self.used_by_header).pack(side=LEFT)
		h.pack(side=TOP, fill=X)
		self.used_by_listbox = ScrolledListbox(f, font=Font.fixed(), width=1, height=6)
		self.used_by_listbox.bind(Double.Click_Left, self.used_by_jump)
		self.used_by_listbox.bind(Key.Return, self.used_by_jump)
		f.pack(side=BOTTOM, fill=X, padx=2, pady=2)
		self.toggle_used_by(toggle=False)
		self.update_used_by_header()

	def check_used_by_references(self, lookup_id=None, used_by=None, force_open=False):
		self.used_by_data = []
		if not self.used_by_listbox:
			return
		self.used_by_listbox.delete(0,END)
		if not used_by:
			used_by = self.used_by_references
		if not lookup_id:
			lookup_id = self.id
		for dat_refs in used_by:
			self.used_by_data.extend(dat_refs.matching(self.toplevel.data_context, lookup_id))
		if self.used_by_data:
			self.used_by_listbox.insert(END, *self.used_by_data)
		self.update_used_by_header()
		if force_open and not self.toplevel.data_context.settings.get('show_used_by', True):
			self.toggle_used_by()

	def used_by_jump(self, *_):
		selections = self.used_by_listbox.curselection()
		if not selections:
			return
		selected = selections[0]
		if selected < len(self.used_by_data):
			match = self.used_by_data[selected]
			tab = self.toplevel.dattabs.display(match.dat_id.tab_id)
			self.toplevel.changeid(match.entry_id)
			if match.dat_sub_tab_id:
				tab.change_sub_tab(match.dat_sub_tab_id)

	def jump(self, datid, entry_id):
		if entry_id < self.toplevel.data_context.dat_data(datid).entry_count() - 1:
			self.toplevel.dattabs.display(datid.tab_id)
			self.toplevel.changeid(entry_id)

	def change_sub_tab(self, sub_tab_id):
		pass

	def updated_pointer_entries(self, ids):
		pass

	def deactivate(self):
		self.save_data()

	def load_data(self, id=None):
		if not self.get_dat_data().dat:
			return
		if id != None:
			self.id = id
		entry = self.get_dat_data().dat.get_entry(self.id)
		self.load_entry(entry)
		self.check_used_by_references()

	def load_entry(self, entry):
		pass

	def save_data(self):
		if not self.get_dat_data().dat:
			return
		entry = self.get_dat_data().dat.get_entry(self.id)
		self.save_entry(entry)
		self.check_used_by_references()
		if self.edited:
			self.toplevel.update_status_bar()

	def save_entry(self, entry):
		pass

	def unsaved(self):
		if self == self.toplevel.dattabs.active:
			self.save_data()
		if self.edited:
			file = self.get_dat_data().file_path
			if not file:
				file = self.get_dat_data().dat.FILE_NAME
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				self.save()

	def copy(self):
		text = self.get_dat_data().dat.export_entry(self.id)
		self.clipboard_set(text)

	def paste(self):
		text = self.clipboard_get()
		self.get_dat_data().dat.import_entry(self.id, text)
		self.edited = True
		self.toplevel.update_status_bar()
		self.toplevel.tab_activated()

	def reload(self):
		self.get_dat_data().dat.set_entry(self.id, copy.deepcopy(self.get_dat_data().default_dat.get_entry(self.id)))
		self.toplevel.tab_activated()

	def _expand_entries(self, add):
		dat_data = self.get_dat_data()
		if not dat_data.expand_entries(add):
			return
		self.edited = True
		self.toplevel.update_status_bar()
		entry_count = dat_data.entry_count()
		self.toplevel.changeid(entry_count - 1)

	def add_entry(self):
		dat_data = self.get_dat_data()
		if not dat_data.is_expanded() and not MessageBox.askyesno(parent=self, title='Expand %s?' % dat_data.dat.FILE_NAME, message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		self._expand_entries(1)

	def set_entry_count(self):
		dat_data = self.get_dat_data()
		if not dat_data.is_expanded() and not MessageBox.askyesno(parent=self, title='Expand %s?' % dat_data.dat.FILE_NAME, message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		def _set_entry_count(count):
			add = count - dat_data.entry_count()
			if add < 1:
				return
			self._expand_entries(add)
		EntryCountDialog(self, _set_entry_count, dat_data, self.toplevel.data_context.settings)

	def new(self, key=None):
		if not self.unsaved():
			self.get_dat_data().new_file()
			self.id = 0
			self.toplevel.tab_activated()

	def open_file(self, file, save=True):
		if not save or not self.unsaved():
			self.get_dat_data().load_file(file)
			self.id = 0
			if self.toplevel.dattabs.active == self:
				self.toplevel.tab_activated()

	def open_data(self, file_data, save=True):
		if not save or not self.unsaved():
			self.get_dat_data().load_data(file_data)
			self.id = 0
			if self.toplevel.dattabs.active == self:
				self.toplevel.tab_activated()

	def iimport(self):
		file = self.toplevel.data_context.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[FileType.txt()])
		if not file:
			return
		self.get_dat_data().dat.import_file(file)
		self.edited = True
		self.toplevel.update_status_bar()
		self.toplevel.tab_activated()

	def save(self, key=None):
		self.saveas(file_path=self.get_dat_data().file_path)

	def saveas(self, key=None, file_path=None):
		if not file_path:
			file_path = self.toplevel.data_context.settings.lastpath.dat.save.select_save_file(self, key=self.get_dat_data().dat.FILE_NAME, title='Save %s As' % self.get_dat_data().dat.FILE_NAME, filetypes=[FileType.dat('StarCraft %s files' % self.get_dat_data().dat.FILE_NAME)], filename=self.get_dat_data().dat.FILE_NAME)
			if not file_path:
				return
		elif not check_allow_overwrite_internal_file(file_path):
			return
		try:
			self.get_dat_data().save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.get_dat_data().file_path = file_path
		self.edited = False
		self.toplevel.update_status_bar()

	def export(self, key=None):
		file = self.toplevel.data_context.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return True
		try:
			self.get_dat_data().dat.export_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
