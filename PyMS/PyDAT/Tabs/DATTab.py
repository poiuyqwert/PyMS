
from __future__ import annotations

from ..Config import PyDATConfig
from ..DATTabConveniences import DATTabConveniences
from ..EntryCountDialog import EntryCountDialog
from ..DataID import DATID, AnyID, UnitsTabID

from ...FileFormats.DAT.AbstractDAT import AbstractDATEntry

from ...Utilities.PyMSError import PyMSError
from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities import IO
from ...Utilities.fileutils import check_allow_overwrite_internal_file

import copy

from typing import TYPE_CHECKING, cast, Generic, TypeVar
if TYPE_CHECKING:
	from ..Delegates import MainDelegate
	from ..DATRef import DATRefs, DATRefMatch
	from ..DATData import DATData

ET = TypeVar('ET', bound=AbstractDATEntry)
class DATTab(UI.NotebookTab, DATTabConveniences, Generic[ET]):
	ARROWS_LOADED = False
	ARROW_DOWN: UI.Image
	ARROW_UP: UI.Image
	DAT_ID: DATID

	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.id = 0
		self.delegate = delegate
		self.used_by_references: tuple[DATRefs, ...] | None = None
		self.used_by_collapse_button: UI.Button | None = None
		self.used_by_listbox: UI.ScrolledListbox | None = None
		self.used_by_data: list[DATRefMatch] = []
		self.used_by_header: UI.StringVar | None = None
		self.edited = False
		self.page_title = ''
		UI.NotebookTab.__init__(self, parent)

	def get_dat_data(self) -> DATData:
		return self.delegate.data_context.dat_data(self.DAT_ID)

	def get_names_settings(self) -> PyDATConfig.Names.Options | PyDATConfig.Names.SimpleOptions:
		match self.DAT_ID:
			case DATID.units:
				return self.delegate.data_context.config.names.units
			case DATID.weapons:
				return self.delegate.data_context.config.names.weapons
			case DATID.flingy:
				return self.delegate.data_context.config.names.flingy
			case DATID.sprites:
				return self.delegate.data_context.config.names.sprites
			case DATID.images:
				return self.delegate.data_context.config.names.images
			case DATID.upgrades:
				return self.delegate.data_context.config.names.upgrades
			case DATID.techdata:
				return self.delegate.data_context.config.names.techdata
			case DATID.sfxdata:
				return self.delegate.data_context.config.names.sfxdata
			case DATID.portdata:
				return self.delegate.data_context.config.names.portdata
			case DATID.mapdata:
				return self.delegate.data_context.config.names.mapdata
			case DATID.orders:
				return self.delegate.data_context.config.names.orders

	def update_used_by_header(self) -> None:
		if not self.used_by_header:
			return
		text = f'Used By ({len(self.used_by_data)})'
		if  self.delegate.data_context.config.show_used_by.value:
			text += ':'
		self.used_by_header.set(text)

	def toggle_used_by(self, toggle: bool = True) -> None:
		visible = self.delegate.data_context.config.show_used_by.value
		if toggle:
			visible = not visible
			self.delegate.data_context.config.show_used_by.value = visible
			self.update_used_by_header()
		assert self.used_by_listbox is not None
		assert self.used_by_collapse_button is not None
		if not visible:
			self.used_by_listbox.pack_forget()
			self.used_by_collapse_button['image'] = DATTab.ARROW_UP
		else:
			self.used_by_listbox.pack(side=UI.BOTTOM, fill=UI.X, padx=2, pady=2)
			self.used_by_collapse_button['image'] = DATTab.ARROW_DOWN

	def setup_used_by(self, references: tuple[DATRefs, ...]) -> None:
		self.used_by_references = references

		f = UI.Frame(self)
		h  = UI.Frame(f)
		if not DATTab.ARROWS_LOADED:
			DATTab.ARROW_DOWN = Assets.get_image('arrow')
			DATTab.ARROW_UP = Assets.get_image('arrowup')
			DATTab.ARROWS_LOADED = True
		self.used_by_collapse_button = UI.Button(h, image=DATTab.ARROW_DOWN,  command=self.toggle_used_by)
		self.used_by_collapse_button.pack(side=UI.LEFT, padx=(0, 5))
		self.used_by_header = UI.StringVar()
		UI.Label(h, textvariable=self.used_by_header).pack(side=UI.LEFT)
		h.pack(side=UI.TOP, fill=UI.X)
		self.used_by_listbox = UI.ScrolledListbox(f, font=UI.Font.fixed(), width=1, height=6)
		self.used_by_listbox.bind(UI.Double.Click_Left(), self.used_by_jump)
		self.used_by_listbox.bind(UI.Key.Return(), self.used_by_jump)
		f.pack(side=UI.BOTTOM, fill=UI.X, padx=2, pady=2)
		self.toggle_used_by(toggle=False)
		self.update_used_by_header()

	def check_used_by_references(self, lookup_id: int | None = None, used_by: tuple[DATRefs, ...] | None = None, force_open: bool = False) -> None:
		self.used_by_data = []
		if not self.used_by_listbox:
			return
		self.used_by_listbox.delete(0,UI.END)
		if not used_by:
			used_by = self.used_by_references
		assert used_by is not None
		if not lookup_id:
			lookup_id = self.id
		for dat_refs in used_by:
			self.used_by_data.extend(dat_refs.matching(self.delegate.data_context, lookup_id))
		if self.used_by_data:
			self.used_by_listbox.insert(UI.END, *tuple(str(r) for r in self.used_by_data))
		self.update_used_by_header()
		if force_open and not self.delegate.data_context.config.show_used_by.value:
			self.toggle_used_by()

	def used_by_jump(self, _event: UI.Event | None) -> None:
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

	def jump(self, datid: DATID, entry_id: int) -> None:
		if entry_id < self.delegate.data_context.dat_data(datid).entry_count() - 1:
			self.delegate.change_tab(datid)
			self.delegate.change_id(entry_id)

	def change_sub_tab(self, sub_tab_id: UnitsTabID) -> None:
		pass

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		pass

	def deactivate(self) -> None:
		self.save_data()

	def load_data(self, entry_id: int | None = None) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		if entry_id is not None:
			self.id = entry_id
		entry = dat.get_entry(self.id)
		self.load_entry(entry)
		self.check_used_by_references()

	def load_entry(self, entry: ET) -> None:
		pass

	def save_data(self) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		entry = dat.get_entry(self.id)
		self.save_entry(entry)
		self.check_used_by_references()
		if self.edited:
			self.delegate.update_status_bar()

	def save_entry(self, entry: ET) -> None:
		pass

	def check_saved(self) -> CheckSaved:
		dat = self.get_dat_data().dat
		if not dat:
			return CheckSaved.saved
		if self == self.delegate.active_tab():
			self.save_data()
		if not self.edited:
			return CheckSaved.saved
		file = self.get_dat_data().file_path
		if not file:
			file = dat.FILE_NAME
		save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{file}'?", default=UI.MessageBox.YES)
		if save is None:
			return CheckSaved.cancelled
		if not save:
			return CheckSaved.saved
		return self.save()

	def copy(self) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		text = dat.export_entry(self.id)
		self.clipboard_set(text) # type: ignore[attr-defined]

	def paste(self) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		text = self.clipboard_get()
		dat.import_entry(self.id, text)
		self.edited = True
		self.delegate.refresh()

	def reload(self) -> None:
		dat = self.get_dat_data().dat
		default_dat = self.get_dat_data().default_dat
		if not dat or not default_dat:
			return
		dat.set_entry(self.id, copy.deepcopy(default_dat.get_entry(self.id)))
		self.delegate.refresh()

	def _expand_entries(self, add: int) -> None:
		dat_data = self.get_dat_data()
		if not dat_data.expand_entries(add):
			return
		self.edited = True
		self.delegate.update_status_bar()
		entry_count = dat_data.entry_count()
		self.delegate.change_id(entry_count - 1)

	def add_entry(self) -> None:
		dat_data = self.get_dat_data()
		if not dat_data.dat:
			return
		if not dat_data.is_expanded() and not UI.MessageBox.askyesno(parent=self, title=f'Expand {dat_data.dat.FILE_NAME}?', message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		self._expand_entries(1)

	def set_entry_count(self) -> None:
		dat_data = self.get_dat_data()
		if not dat_data.dat:
			return
		if not dat_data.is_expanded() and not UI.MessageBox.askyesno(parent=self, title=f'Expand {dat_data.dat.FILE_NAME}?', message="Expanded dat files require you to use a plugin like 'DatExtend'. Are you sure you want to continue?"):
			return
		def _set_entry_count(count: int) -> None:
			add = count - dat_data.entry_count()
			if add < 1:
				return
			self._expand_entries(add)
		EntryCountDialog(self, _set_entry_count, dat_data, self.delegate.data_context.config.windows.entry_count)

	def new(self, _event: UI.Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.get_dat_data().new_file()
		self.id = 0
		self.delegate.refresh()

	def open(self, any_input: IO.AnyInputBytes, save: bool = True) -> None:
		if save and self.check_saved() == CheckSaved.cancelled:
			return
		self.get_dat_data().load(any_input)
		self.id = 0
		if self.delegate.active_tab() == self:
			self.delegate.refresh()

	def iimport(self) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		file = self.delegate.data_context.config.last_path.txt.select_open(self)
		if not file:
			return
		dat.import_file(file)
		self.edited = True
		self.delegate.refresh()

	def save(self, _event: UI.Event | None = None) -> CheckSaved:
		return self.saveas(file_path=self.get_dat_data().file_path)

	def saveas(self, _event: UI.Event | None = None, file_path: str | None = None) -> CheckSaved:
		dat = self.get_dat_data().dat
		if not dat:
			return CheckSaved.saved
		if not file_path:
			file_path = self.delegate.data_context.config.last_path.dat.select_save(self, title=f'Save {dat.FILE_NAME} As', filetypes=[UI.FileType.dat(f'StarCraft {dat.FILE_NAME} files')], filename=dat.FILE_NAME)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.get_dat_data().save_file(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.get_dat_data().file_path = file_path
		self.edited = False
		self.delegate.update_status_bar()
		return CheckSaved.saved

	def export(self, _event: UI.Event | None = None) -> None:
		dat = self.get_dat_data().dat
		if not dat:
			return
		file = self.delegate.data_context.config.last_path.txt.select_save(self)
		if not file:
			return
		try:
			dat.export_file(file)
		except PyMSError as e:
			ErrorDialog(self, e)
