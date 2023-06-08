
from __future__ import annotations

from ..DATTabConveniences import DATTabConveniences
from ..EntryCountDialog import EntryCountDialog
from ..DataID import DATID, AnyID

from ...Utilities.PyMSError import PyMSError
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities.UIKit import *
from ...Utilities import Assets
from ...Utilities.fileutils import check_allow_overwrite_internal_file

import copy

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate
	from ..DATRef import DATRefs, DATRefMatch
	from ..DATData import DATData

class DATTab(NotebookTab, DATTabConveniences):
	ARROWS_LOADED = False
	ARROW_DOWN: Image
	ARROW_UP: Image
	DAT_ID: DATID

	def __init__(self, parent, delegate): # type: (Misc, MainDelegate) -> None
		self.id = 0
		self.delegate = delegate
		self.used_by_references = None # type: tuple[DATRefs, ...] | None
		self.used_by_collapse_button = None # type: Button | None
		self.used_by_listbox = None # type: ScrolledListbox | None
		self.used_by_data = [] # type: list[DATRefMatch]
		self.used_by_header = None # type: StringVar | None
		self.edited = False
		self.page_title = ''
		NotebookTab.__init__(self, parent)

	def get_dat_data(self): # type: () -> DATData
		return self.delegate.data_context.dat_data(self.DAT_ID)

	def update_used_by_header(self): # type: () -> None
		if not self.used_by_header:
			return
		text = 'Used By (%d)' % len(self.used_by_data)
		if  self.delegate.data_context.settings.get('show_used_by', True):
			text += ':'
		self.used_by_header.set(text)

	def toggle_used_by(self, toggle=True): # type: (bool) -> None
		visible = self.delegate.data_context.settings.get('show_used_by', True)
		if toggle:
			visible = not visible
			self.delegate.data_context.settings.show_used_by = visible
			self.update_used_by_header()
		assert self.used_by_listbox is not None
		assert self.used_by_collapse_button is not None
		if not visible:
			self.used_by_listbox.pack_forget()
			self.used_by_collapse_button['image'] = DATTab.ARROW_UP
		else:
			self.used_by_listbox.pack(side=BOTTOM, fill=X, padx=2, pady=2)
			self.used_by_collapse_button['image'] = DATTab.ARROW_DOWN

	def setup_used_by(self, references): # type: (tuple[DATRefs, ...]) -> None
		self.used_by_references = references

		f = Frame(self)
		h  = Frame(f)
		if not DATTab.ARROWS_LOADED:
			DATTab.ARROW_DOWN = Assets.get_image('arrow')
			DATTab.ARROW_UP = Assets.get_image('arrowup')
			DATTab.ARROWS_LOADED = True
		self.used_by_collapse_button = Button(h, image=DATTab.ARROW_DOWN,  command=self.toggle_used_by)
		self.used_by_collapse_button.pack(side=LEFT, padx=(0, 5))
		self.used_by_header = StringVar()
		Label(h, textvariable=self.used_by_header).pack(side=LEFT)
		h.pack(side=TOP, fill=X)
		self.used_by_listbox = ScrolledListbox(f, font=Font.fixed(), width=1, height=6)
		self.used_by_listbox.bind(Double.Click_Left(), self.used_by_jump)
		self.used_by_listbox.bind(Key.Return(), self.used_by_jump)
		f.pack(side=BOTTOM, fill=X, padx=2, pady=2)
		self.toggle_used_by(toggle=False)
		self.update_used_by_header()

	def check_used_by_references(self, lookup_id=None, used_by=None, force_open=False): # type: (int | None, tuple[DATRefs, ...] | None, bool) -> None
		self.used_by_data = []
		if not self.used_by_listbox:
			return
		self.used_by_listbox.delete(0,END)
		if not used_by:
			used_by = self.used_by_references
		assert used_by is not None
		if not lookup_id:
			lookup_id = self.id
		for dat_refs in used_by:
			self.used_by_data.extend(dat_refs.matching(self.delegate.data_context, lookup_id))
		if self.used_by_data:
			self.used_by_listbox.insert(END, *self.used_by_data)
		self.update_used_by_header()
		if force_open and not self.delegate.data_context.settings.get('show_used_by', True):
			self.toggle_used_by()

	def used_by_jump(self, *_): # type: (Event) -> None
		if not self.used_by_listbox:
			return
		selections = cast(list[int], self.used_by_listbox.curselection())
		if not selections:
			return
		selected = selections[0]
		if selected < len(self.used_by_data):
			match = self.used_by_data[selected]
			tab = cast(DATTab, self.delegate.change_tab(match.dat_id))
			self.delegate.change_id(match.entry_id)
			if match.dat_sub_tab_id:
				tab.change_sub_tab(match.dat_sub_tab_id)

	def jump(self, datid, entry_id): # type: (DATID, int) -> None
		if entry_id < self.delegate.data_context.dat_data(datid).entry_count() - 1:
			self.delegate.change_tab(datid)
			self.delegate.change_id(entry_id)

	def change_sub_tab(self, sub_tab_id):
		pass

	def updated_pointer_entries(self, ids): # type: (list[AnyID]) -> None
		pass

	def deactivate(self): # type: () -> None
		self.save_data()

	def load_data(self, id=None): # type: (int | None) -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		if id is not None:
			self.id = id
		entry = dat.get_entry(self.id)
		self.load_entry(entry)
		self.check_used_by_references()

	def load_entry(self, entry):
		pass

	def save_data(self): # type: () -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		entry = dat.get_entry(self.id)
		self.save_entry(entry)
		self.check_used_by_references()
		if self.edited:
			self.delegate.update_status_bar()

	def save_entry(self, entry):
		pass

	def unsaved(self): # type: () -> (bool | None)
		dat = self.get_dat_data().dat
		if not dat:
			return None
		if self == self.delegate.active_tab():
			self.save_data()
		if self.edited:
			file = self.get_dat_data().file_path
			if not file:
				file = dat.FILE_NAME
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				self.save()
		return None

	def copy(self): # type: () -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		text = dat.export_entry(self.id)
		self.clipboard_set(text) # type: ignore[attr-defined]

	def paste(self): # type: () -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		text = self.clipboard_get()
		dat.import_entry(self.id, text)
		self.edited = True
		self.delegate.refresh()

	def reload(self): # type: () -> None
		dat = self.get_dat_data().dat
		default_dat = self.get_dat_data().default_dat
		if not dat or not default_dat:
			return
		dat.set_entry(self.id, copy.deepcopy(default_dat.get_entry(self.id)))
		self.delegate.refresh()

	def _expand_entries(self, add): # type: (int) -> None
		dat_data = self.get_dat_data()
		if not dat_data.expand_entries(add):
			return
		self.edited = True
		self.delegate.update_status_bar()
		entry_count = dat_data.entry_count()
		self.delegate.change_id(entry_count - 1)

	def add_entry(self): # type: () -> None
		dat_data = self.get_dat_data()
		if not dat_data.dat:
			return
		if not dat_data.is_expanded() and not MessageBox.askyesno(parent=self, title='Expand %s?' % dat_data.dat.FILE_NAME, message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		self._expand_entries(1)

	def set_entry_count(self): # type: () -> None
		dat_data = self.get_dat_data()
		if not dat_data.dat:
			return
		if not dat_data.is_expanded() and not MessageBox.askyesno(parent=self, title='Expand %s?' % dat_data.dat.FILE_NAME, message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		def _set_entry_count(count):
			add = count - dat_data.entry_count()
			if add < 1:
				return
			self._expand_entries(add)
		EntryCountDialog(self, _set_entry_count, dat_data, self.delegate.data_context.settings)

	def new(self, key=None): # type: (Event | None) -> None
		if not self.unsaved():
			self.get_dat_data().new_file()
			self.id = 0
			self.delegate.refresh()

	def open_file(self, file, save=True): # type: (str, bool) -> None
		if not save or not self.unsaved():
			self.get_dat_data().load_file(file)
			self.id = 0
			if self.delegate.active_tab() == self:
				self.delegate.refresh()

	def open_data(self, file_data, save=True): # type: (bytes, bool) -> None
		if not save or not self.unsaved():
			self.get_dat_data().load_data(file_data)
			self.id = 0
			if self.delegate.active_tab() == self:
				self.delegate.refresh()

	def iimport(self): # type: () -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		file = self.delegate.data_context.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[FileType.txt()])
		if not file:
			return
		dat.import_file(file)
		self.edited = True
		self.delegate.refresh()

	def save(self, key=None): # type: (Event | None) -> None
		self.saveas(file_path=self.get_dat_data().file_path)

	def saveas(self, key=None, file_path=None): # type: (Event | None, str | None) -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		if not file_path:
			file_path = self.delegate.data_context.settings.lastpath.dat.save.select_save_file(self, key=dat.FILE_NAME, title='Save %s As' % dat.FILE_NAME, filetypes=[FileType.dat('StarCraft %s files' % dat.FILE_NAME)], filename=dat.FILE_NAME)
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
		self.delegate.update_status_bar()

	def export(self, key=None): # type: (Event | None) -> None
		dat = self.get_dat_data().dat
		if not dat:
			return
		file = self.delegate.data_context.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			dat.export_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
