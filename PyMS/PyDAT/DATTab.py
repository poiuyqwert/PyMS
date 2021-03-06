
from ContinueImportDialog import ContinueImportDialog

from ..Utilities.utils import fit, couriernew
from ..Utilities.Notebook import NotebookTab
from ..Utilities.Tooltip import Tooltip
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.UIKit import *

import copy

class DATTab(NotebookTab):
	DAT_ID = None

	def __init__(self, parent, toplevel):
		self.id = 0
		self.toplevel = toplevel
		self.icon = self.toplevel.icon
		self.used_by_references = None
		self.used_by_listbox = None
		self.used_by_data = []
		self.edited = False
		self.dattabs = None
		NotebookTab.__init__(self, parent)

	def tip(self, obj, tipname, hint):
		obj.tooltip = Tooltip(obj, '%s:\n' % tipname + fit('  ', self.toplevel.data_context.hints[hint], end=True)[:-1], mouse=True)

	def makeCheckbox(self, frame, var, txt, hint):
		c = Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def get_dat_data(self):
		return self.toplevel.data_context.dat_data(self.DAT_ID)

	def setup_used_by(self, references):
		self.used_by_references = references

		f = LabelFrame(self, text='Used By:')
		self.used_by_listbox = ScrolledListbox(f, {'bd': 2, 'relief': SUNKEN}, font=couriernew, width=1, height=6, bd=0, highlightthickness=0, exportselection=0, activestyle=DOTBOX)
		self.used_by_listbox.bind(Double.Click, self.used_by_jump)
		self.used_by_listbox.bind(Key.Return, self.used_by_jump)
		self.used_by_listbox.pack(fill=X, padx=2, pady=2)
		f.pack(side=BOTTOM, fill=X, padx=2, pady=2)

	def check_used_by_references(self, lookup_id=None, used_by=None):
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

	def updated_data_files(self, dataids):
		pass

	def updated_entry_names(self, datids):
		pass

	def updated_entry_counts(self, datids):
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
		# TODO
		self.toplevel.tab_activated()

	def reload(self):
		self.get_dat_data().dat.set_entry(self.id, copy.deepcopy(self.get_dat_data().default_dat.get_entry(self.id)))
		self.toplevel.tab_activated()

	def new(self, key=None):
		if not self.unsaved():
			self.get_dat_data().new_file()
			self.id = 0
			self.toplevel.tab_activated()

	def open(self, file, save=True):
		if not save or not self.unsaved():
			self.get_dat_data().load_file(file)
			self.id = 0
			if self.toplevel.dattabs.active == self:
				self.toplevel.tab_activated()

	def iimport(self, key=None, file=None, c=True, parent=None):
		if parent == None:
			parent = self
		if not file:
			file = self.toplevel.data_context.settings.lastpath.txt.select_file('import', self, 'Import TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return
		entries = copy.deepcopy(self.get_dat_data().dat.entries)
		try:
			ids = self.get_dat_data().dat.interpret(file)
		except PyMSError, e:
			self.get_dat_data().dat.entries = entries
			ErrorDialog(self, e)
			return
		cont = c
		for n,_entry in enumerate(entries):
			if cont != 3 and n in ids:
				if cont != 2:
					x = ContinueImportDialog(parent, self.get_dat_data().dat.FILE_NAME, n)
					cont = x.cont
					if cont in [0,3]:
						self.get_dat_data().dat.entries[n] = entries[n]
			else:
				self.get_dat_data().dat.entries[n] = entries[n]
		return cont

	def save(self, key=None):
		if self.get_dat_data().file_path == None:
			self.saveas()
			return
		try:
			self.get_dat_data().dat.compile(self.get_dat_data().file_path)
		except PyMSError, e:
			ErrorDialog(self, e)
		else:
			self.edited = False
			self.toplevel.update_status_bar()

	def saveas(self, key=None):
		file = self.toplevel.data_context.settings.lastpath.dat.save.select_file(self.get_dat_data().dat.FILE_NAME, self, 'Save %s As' % self.get_dat_data().dat.FILE_NAME, '*.dat', [('StarCraft %s files' % self.get_dat_data().dat.FILE_NAME,'*.dat'),('All Files','*')], save=True)
		if not file:
			return True
		self.get_dat_data().file_path = file
		self.save()
		self.toplevel.update_status_bar()

	def export(self, key=None):
		file = self.toplevel.data_context.settings.lastpath.txt.select_file('export', self, 'Export TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')], save=True)
		if not file:
			return True
		try:
			self.get_dat_data().dat.decompile(file)
		except PyMSError, e:
			ErrorDialog(self, e)
