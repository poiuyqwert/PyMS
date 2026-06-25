
from .Config import PyDATConfig
from . import Tabs
from .Tabs.DATTab import DATTab
from .DataContext import DataContext
from .NamesDisplay import NamesDisplaySetting
from .SaveMPQDialog import SaveMPQDialog
from .SettingsUI.SettingsDialog import SettingsDialog
from .EntryNameOverrides import EntryNameOverrides
from .DataID import DATID, AnyID
from .Delegates import MainDelegate

from ..FileFormats.MPQ.MPQ import MPQ

from ..Utilities.utils import lpad
from ..Utilities import registry
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.PyMSError import PyMSError
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities import Assets
from ..Utilities import UIKit as UI
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate
from ..Utilities.SponsorDialog import SponsorDialog

import os

from typing import cast, Any

LONG_VERSION = 'v' + Assets.version('PyDAT')

class PyDAT(UI.MainWindow, MainDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile
		UI.MainWindow.__init__(self)
		self.title(f'PyDAT {LONG_VERSION}')
		self.set_icon('PyDAT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyDAT', Assets.version('PyDAT'))
		ga.track(GAScreen('PyDAT'))
		setup_trace('PyDAT', self)

		self.data_context = DataContext()
		UI.Theme.load_theme(self.data_context.config.theme.value, self)

		self.updates: list[AnyID] = []
		self.update_after_id = None
		def buffer_updates(update_id: AnyID) -> None:
			if update_id in self.updates:
				return
			self.updates.append(update_id)
			if self.update_after_id:
				self.after_managed_cancel(self.update_after_id)
			def perform_updates() -> None:
				self.update_after_id = None
				updates = self.updates
				self.updates = []
				self.updated_pointer_entries(updates)
			self.update_after_id = self.after_managed(1, perform_updates)
		self.data_context.update_cb += buffer_updates

		self.data_context.load_palettes()

		toolbar = UI.Toolbar(self)
		toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n)
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o)
		toolbar.add_button(Assets.get_image('openfolder'), self.opendirectory, 'Open Directory', UI.Ctrl.d)
		toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import from TXT', UI.Ctrl.i)
		toolbar.add_button(Assets.get_image('openmpq'), self.openmpq, 'Open MPQ', UI.Ctrl.Alt.o, enabled=MPQ.supported())
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('save'), self.save, 'Save', UI.Ctrl.s)
		toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', UI.Ctrl.Alt.s)
		toolbar.add_button(Assets.get_image('export'), self.export, 'Export to TXT', UI.Ctrl.e)
		toolbar.add_button(Assets.get_image('savempq'), self.savempq, 'Save MPQ', UI.Ctrl.Alt.m, enabled=MPQ.supported())
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('idsort'), self.override_name, 'Name Overrides', UI.Shift.Ctrl.n)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage MPQ and TBL files', UI.Ctrl.m)
		def reload_files() -> None:
			self.open_files()
		toolbar.add_button(Assets.get_image('debug'), reload_files, 'Reload data files', UI.Ctrl.r)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.dat editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		toolbar.add_button(Assets.get_image('help'), self.help, 'Help', UI.Key.F1)
		toolbar.add_button(Assets.get_image('about'), self.about, 'About PyDAT')
		toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit)
		toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		self.hor_pane = UI.PanedWindow(self, orient=UI.HORIZONTAL)
		left = UI.Frame(self.hor_pane)
		self.listbox = UI.ScrolledListbox(left, scroll_speed=2, font=UI.Font.fixed(), width=45, height=1)
		self.listbox.pack(side=UI.TOP, fill=UI.BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(UI.ButtonRelease.Click_Right(), self.popup)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), lambda *e: self.changeid())

		f = UI.Frame(left)
		collapse_button = UI.CollapseView.Button(f)
		collapse_button.pack(side=UI.TOP)
		f.pack(fill=UI.X, pady=2)

		def _update_collapse_setting(collapsed: bool) -> None:
			self.data_context.config.show_listbox_options.value = not collapsed
		collapse_view = UI.CollapseView(left, collapse_button, callback=_update_collapse_setting)
		collapse_view.pack(fill=UI.X, padx=2, pady=2)

		collapse_view.set_collapsed(not self.data_context.config.show_listbox_options.value)

		self.findhistory: list[str] = []
		self.find = UI.StringVar()
		UI.Label(collapse_view, text='Find:').grid(column=0,row=0, sticky=UI.E)
		find = UI.Frame(collapse_view)
		find_tdd = UI.TextDropDown(find, self.find, self.findhistory, 5)
		find_tdd.pack(side=UI.LEFT, fill=UI.X, expand=1)
		find_tdd.entry.bind(UI.Key.Return(), self.findnext)
		UI.Button(find, text='Next', command=self.findnext).pack(side=UI.LEFT)
		find.grid(column=1,row=0, sticky=UI.EW)

		collapse_view.grid_columnconfigure(1, weight=1)

		self.jumpid = UI.IntegerVar('', [0,0], allow_hex=True)
		UI.Label(collapse_view, text='ID Jump:').grid(column=0,row=1, sticky=UI.E)
		jump = UI.Frame(collapse_view)
		jump_entry = UI.Entry(jump, textvariable=self.jumpid, width=5)
		jump_entry.pack(side=UI.LEFT)
		jump_entry.bind(UI.Key.Return(), self.jump)
		UI.Button(jump, text='Go', command=self.jump).pack(side=UI.LEFT)
		jump.grid(column=1,row=1, sticky=UI.W)

		self.names_display = UI.IntVar()
		self.names_display.trace_add('write', self.change_names_display)
		self.simple_names = UI.BooleanVar()
		self.simple_names.trace_add('write', self.change_simple_names)
		UI.Label(collapse_view, text='Names:').grid(column=0,row=2, sticky=UI.E)
		UI.DropDown(collapse_view, self.names_display, ['Basic', 'TBL d', 'Combined']).grid(column=1,row=2, sticky=UI.EW)
		self.simple_names_checkbox = UI.Checkbutton(collapse_view, text='Simple TBL Names', variable=self.simple_names)
		self.simple_names_checkbox.grid(column=1,row=3, sticky=UI.W)

		self.hor_pane.add(left, sticky=UI.NSEW, minsize=300)

		self.listmenu = UI.Menu(self, tearoff=0)
		self.listmenu.add_command(label='Copy Entry to Clipboard', command=self.copy, shortcut=UI.Shift.Ctrl.c) # type: ignore[call-arg]
		self.listmenu.add_command(label='Copy Sub-Tab to Clipboard', command=self.copy_subtab, shortcut=UI.Ctrl.y, tags='can_copy_sub_tab') # type: ignore[call-arg]
		self.listmenu.add_command(label='Paste from Clipboard', command=self.paste, shortcut=UI.Shift.Ctrl.p) # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Reload Entry', command=self.reload, shortcut=UI.Ctrl.r) # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Add Entry (DatExtend)', command=self.add_entry, shortcut=UI.Shift.Ctrl.a, tags='can_expand') # type: ignore[call-arg]
		self.listmenu.add_command(label='Set Entry Count (DatExtend)', command=self.set_entry_count, shortcut=UI.Shift.Ctrl.s, tags='can_expand') # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Override Name', command=self.override_name, shortcut=UI.Shift.Ctrl.n) # type: ignore[call-arg]

		self.status = UI.StringVar()
		self.expanded = UI.StringVar()

		self.dattabs = UI.Notebook(self.hor_pane)
		self.pages: list[DATTab] = []
		tabs = (
			('Units', Tabs.UnitsTab),
			('Weapons', Tabs.WeaponsTab),
			('Flingy', Tabs.FlingyTab),
			('Sprites', Tabs.SpritesTab),
			('Images', Tabs.ImagesTab),
			('Upgrades', Tabs.UpgradesTab),
			('Techdata', Tabs.TechnologyTab),
			('Sfxdata', Tabs.SoundsTab),
			('Portdata', Tabs.PortraitsTab),
			('Mapdata', Tabs.MapsTab),
			('Orders', Tabs.OrdersTab),
		)
		for name,tab in tabs:
			page = tab(self.dattabs, self)
			page.page_title = name
			self.pages.append(page)
			self.dattabs.add_tab(page, name)
		self.dattabs.bind(UI.WidgetEvent.Notebook.TabActivated(), lambda _: self.refresh())
		self.hor_pane.add(self.dattabs.notebook, sticky=UI.NSEW)
		self.hor_pane.pack(fill=UI.BOTH, expand=1)

		#Statusbar
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, weight=0.60)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.expanded)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.data_context.load_mpqs()

		self.data_context.config.windows.main.load_size(self)
		self.data_context.config.list_size.load_size(self.hor_pane)

	def initialize(self) -> None:
		e = self.open_files(dat_files=True)
		if e:
			self.settings(err=e)
		if self.guifile:
			self.open(file_path=self.guifile)
		UpdateDialog.check_update(self, 'PyDAT')

	def active_tab(self) -> DATTab:
		return cast(DATTab, self.dattabs.active)

	def refresh(self) -> None:
		self.update_entry_listing(True)
		self.update_name_settings()
		self.update_status_bar()
		self.active_tab().load_data()

	def update_entry_listing(self, update_scroll: bool = False) -> None:
		self.listbox.delete(0,UI.END)
		tab = self.active_tab()
		dat_data = tab.get_dat_data()
		if dat_data.dat:
			max_id = dat_data.dat.entry_count() - 1
			self.jumpid.range[1] = max_id
			self.jumpid.editvalue()
			self.listbox.insert(UI.END, *[f' {lpad(str(id), min(4,len(str(max_id))))}  {name}' for id,name in enumerate(dat_data.names)])
			self.listbox.select_set(tab.id)
			if update_scroll:
				self.listbox.see(tab.id)

	NAMES_SETTING_TO_OPTION = {
		NamesDisplaySetting.basic: 0,
		NamesDisplaySetting.tbl: 1,
		NamesDisplaySetting.combine: 2
	}
	NAMES_OPTION_TO_SETTING = [
		NamesDisplaySetting.basic,
		NamesDisplaySetting.tbl,
		NamesDisplaySetting.combine
	]
	def update_name_settings(self) -> None:
		name_settings = self.active_tab().get_names_settings()
		self.names_display.set(PyDAT.NAMES_SETTING_TO_OPTION[name_settings.display.value])
		if isinstance(name_settings, PyDATConfig.Names.SimpleOptions):
			self.simple_names_checkbox['state'] = UI.NORMAL
			self.simple_names.set(name_settings.simple.value)
		else:
			self.simple_names_checkbox['state'] = UI.DISABLED
			self.simple_names.set(False)
	def change_names_display(self, *_: Any) -> None:
		name_settings = self.active_tab().get_names_settings()
		new_setting = PyDAT.NAMES_OPTION_TO_SETTING[self.names_display.get()]
		if new_setting == name_settings.display.value:
			return
		name_settings.display.value = new_setting
		self.active_tab().get_dat_data().update_names()
	def change_simple_names(self, *_: Any) -> None:
		name_settings = self.active_tab().get_names_settings()
		if not isinstance(name_settings, PyDATConfig.Names.SimpleOptions) or self.simple_names.get() == name_settings.simple.value:
			return
		name_settings.simple.value = self.simple_names.get()
		self.active_tab().get_dat_data().update_names()

	def update_status_bar(self) -> None:
		tab = self.active_tab()
		dat_data = tab.get_dat_data()
		if dat_data.file_path:
			self.status.set(dat_data.file_path)
		elif dat_data.dat:
			self.status.set(dat_data.dat.FILE_NAME)
		else:
			self.status.set('')
		self.editstatus['state'] = UI.NORMAL if tab.edited else UI.DISABLED
		if dat_data.is_expanded():
			self.expanded.set(f'{dat_data.dat_type.FILE_NAME} expanded')
		else:
			self.expanded.set('')

	def updated_pointer_entries(self, ids: list[AnyID]) -> None:
		for page in self.pages:
			page.updated_pointer_entries(ids)
			if self.active_tab() == page and page.DAT_ID in ids:
				self.update_entry_listing(True)

	def open_files(self, dat_files: bool = False) -> PyMSError | None:
		err = None
		try:
			self.data_context.load_additional_files()
		except PyMSError as e:
			err = e
		else:
			if dat_files:
				self.data_context.load_dat_files()
			self.refresh()
		return err

	def check_saved(self) -> CheckSaved:
		for page in self.pages:
			if page.check_saved() == CheckSaved.cancelled:
				return CheckSaved.cancelled
		return CheckSaved.saved

	def load_data(self, entry_id: int | None = None) -> None:
		self.active_tab().load_data(entry_id)
	def save_data(self) -> None:
		self.active_tab().save_data()
		self.update_status_bar()

	def changeid(self, entry_id: int | None = None, focus_list: bool = True) -> None:
		show_selection = True
		if entry_id is None:
			selection = self.listbox.curselection()
			if not selection:
				return
			entry_id = int(selection[0])
			show_selection = False
		if entry_id != self.active_tab().id:
			self.save_data()
			self.load_data(entry_id)
			self.listbox.select_clear(0,UI.END)
			self.listbox.select_set(entry_id)
			if show_selection:
				self.listbox.see(entry_id)
			if focus_list:
				self.listbox.focus_set()

	def change_tab(self, dat_id: DATID) -> DATTab:
		return cast(DATTab, self.dattabs.display(dat_id.tab_id))

	def change_id(self, entry_id: int) -> None:
		self.changeid(entry_id)

	def findnext(self, _event: UI.Event | None = None) -> None:
		find = self.find.get()
		if find in self.findhistory:
			self.findhistory.remove(find)
		self.findhistory.insert(0, find)
		find = find.lower()
		selection = self.listbox.curselection()
		start = int(selection[0]) if selection else 0
		cur = (start + 1) % self.listbox.size() # type: ignore[operator]
		while cur != start:
			if find in self.listbox.get(cur).lower():
				self.changeid(cur, focus_list=False)
				return
			cur = (cur+1) % self.listbox.size() # type: ignore[operator]
		UI.MessageBox.showinfo('Find', f"Can't find '{self.find.get()}'.")

	def jump(self, _event: UI.Event | None = None) -> None:
		self.changeid(self.jumpid.get())

	def popup(self, event: UI.Event) -> None:
		can_expand = False
		dat = self.active_tab().get_dat_data().dat
		if dat:
			can_expand = dat.can_expand()
		self.listmenu.tag_enabled('can_copy_sub_tab', hasattr(self.active_tab(), 'copy_subtab')) # type: ignore[attr-defined]
		self.listmenu.tag_enabled('can_expand', can_expand) # type: ignore[attr-defined]
		self.listmenu.post(event.x_root, event.y_root)

	def copy(self) -> None:
		self.active_tab().copy()

	def copy_subtab(self) -> None:
		tab = cast(Tabs.UnitsTab, self.dattabs.active)
		tab.copy_subtab()

	def paste(self) -> None:
		try:
			self.active_tab().paste()
		except PyMSError as e:
			ErrorDialog(self, e)

	def reload(self) -> None:
		self.active_tab().reload()

	def add_entry(self) -> None:
		self.active_tab().add_entry()

	def set_entry_count(self) -> None:
		self.active_tab().set_entry_count()

	def override_name(self) -> None:
		EntryNameOverrides(self, self.data_context, self.active_tab().DAT_ID, self.active_tab().id)

	def new(self, _event: UI.Event | None = None) -> None:
		self.active_tab().new()

	def open(self, _event: UI.Event | None = None, file_path: str | None = None) -> None:
		if file_path is None:
			file_path = self.data_context.config.last_path.dat.select_open(self)
			if not file_path:
				return
		filename = os.path.basename(file_path)
		for frame,_ in sorted(list(self.dattabs.pages.values()), key=lambda d: d[1]):
			page = cast(DATTab, frame)
			if filename == page.get_dat_data().dat_type.FILE_NAME:
				try:
					page.open(file_path)
				except PyMSError as e:
					ErrorDialog(self, e)
				else:
					self.dattabs.display(page.page_title)
					if (dat := page.get_dat_data().dat) and dat.is_expanded():
						self.data_context.config.dont_warn.expanded_dat.present(self)
				break
		else:
			ErrorDialog(self, PyMSError('Open', f"Unrecognized DAT filename '{file_path}'"))

	def _open_all(self, path: str, ismpq: bool) -> None:
		if not path:
			return
		mpq = None
		if ismpq:
			mpq = MPQ.of(path)
			mpq.open()
		found_normal: list[str] = []
		found_expanded: list[str] = []
		for _,(tab,_) in self.dattabs.pages.items():
			tab = cast(DATTab, tab)
			filename = tab.get_dat_data().dat_type.FILE_NAME
			if mpq:
				try:
					file_data = mpq.read_file('arr\\' + filename)
					tab.open(file_data)
				except Exception:
					continue
			else:
				filepath = os.path.join(path, filename)
				if not os.path.exists(filepath):
					continue
				try:
					tab.open(filepath)
				except Exception:
					continue
			if tab.get_dat_data().is_expanded():
				found_expanded.append(filename)
			else:
				found_normal.append(filename)
		if mpq:
			mpq.close()
		if not found_normal and not found_expanded:
			ErrorDialog(self, PyMSError('Open', f'No DAT files found in {"MPQ" if ismpq else "directory"} "{path}"'))
			return
		message = ''
		if found_normal:
			message += f'DAT Files found:\n\t{", ".join(found_normal)}'
		if found_expanded:
			if message:
				message += '\n\n'
			message += f"Expanded DAT Files found:\n\t{', '.join(found_expanded)}\n\nExpanded DAT files require a plugin like 'DatExtend'."
		UI.MessageBox.showinfo('DAT Files Found', message)

	def openmpq(self, _event: UI.Event | None = None) -> None:
		path = self.data_context.config.last_path.mpq.select_open(self, filetypes=[UI.FileType.mpq(),UI.FileType.exe_mpq()])
		if path:
			self._open_all(path, True)

	def opendirectory(self, _event: UI.Event | None = None) -> None:
		path = self.data_context.config.last_path.dir.select_open(self)
		if path:
			self._open_all(path, False)

	def iimport(self, _event: UI.Event | None = None) -> None:
		self.active_tab().iimport()

	def save(self, _event: UI.Event | None = None) -> None:
		self.save_data()
		self.active_tab().save()

	def saveas(self, _event: UI.Event | None = None) -> None:
		self.save_data()
		self.active_tab().saveas()

	def export(self, _event: UI.Event | None = None) -> None:
		self.save_data()
		self.active_tab().export()

	def savempq(self, _event: UI.Event | None = None) -> None:
		if MPQ.supported():
			self.save_data()
			SaveMPQDialog(self, self)

	def settings(self, _event: UI.Event | None = None, err: PyMSError | None = None) -> None:
		SettingsDialog(self, config=self.data_context.config, delegate=self, err=err, mpq_handler=self.data_context.mpq_handler)

	def register_registry(self, _event: UI.Event | None = None) -> None:
		try:
			registry.register('PyDAT', 'dat', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, _event: UI.Event | None = None) -> None:
		HelpDialog(self, self.data_context.config.windows.help, 'Help/Programs/PyDAT.md')

	def about(self, _event: UI.Event | None = None) -> None:
		AboutDialog(self, 'PyDAT', LONG_VERSION, [('BroodKiller',"DatEdit, its design, format specs, and data files.")])

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self, _event: UI.Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.data_context.config.windows.main.save_size(self)
		self.data_context.config.list_size.save_size(self.hor_pane)
		self.data_context.config.save()
		self.destroy()
