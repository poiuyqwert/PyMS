
from .Config import PyDATConfig
from .Tabs import *
from .Tabs.DATTab import DATTab
from .DataContext import DataContext
from .DATData import NamesDisplaySetting
from .SaveMPQDialog import SaveMPQDialog
from .SettingsUI.SettingsDialog import SettingsDialog
from .EntryNameOverrides import EntryNameOverrides
from .DataID import DataID, DATID, AnyID
from .Delegates import MainDelegate

from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats.DAT import *

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry, lpad
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.PyMSError import PyMSError
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities import Assets
from ..Utilities.UIKit import *
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate

import os

from typing import cast, Callable

LONG_VERSION = 'v%s' % Assets.version('PyDAT')

class PyDAT(MainWindow, MainDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile=None): # type: (str | None) -> None
		self.guifile = guifile
		MainWindow.__init__(self)
		self.title('PyDAT %s' % LONG_VERSION)
		self.set_icon('PyDAT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyDAT', Assets.version('PyDAT'))
		ga.track(GAScreen('PyDAT'))
		setup_trace('PyDAT', self)

		self.data_context = DataContext()
		Theme.load_theme(self.data_context.config.theme.value, self)
	
		self.updates = [] # type: list[AnyID]
		self.update_after_id = None
		def buffer_updates(id: AnyID) -> None:
			if id in self.updates:
				return
			self.updates.append(id)
			if self.update_after_id:
				self.after_cancel(self.update_after_id)
			def perform_updates():
				self.update_after_id = None
				updates = self.updates
				self.updates = []
				self.updated_pointer_entries(updates)
			self.update_after_id = self.after(1, perform_updates)
		self.data_context.update_cb += buffer_updates

		self.data_context.load_palettes()

		toolbar = Toolbar(self)
		toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		toolbar.add_button(Assets.get_image('openfolder'), self.opendirectory, 'Open Directory', Ctrl.d)
		toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import from TXT', Ctrl.i)
		toolbar.add_button(Assets.get_image('openmpq'), self.openmpq, 'Open MPQ', Ctrl.Alt.o, enabled=MPQ.supported())
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s)
		toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.s)
		toolbar.add_button(Assets.get_image('export'), self.export, 'Export to TXT', Ctrl.e)
		toolbar.add_button(Assets.get_image('savempq'), self.savempq, 'Save MPQ', Ctrl.Alt.m, enabled=MPQ.supported())
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('idsort'), self.override_name, 'Name Overrides', Shift.Ctrl.n)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage MPQ and TBL files', Ctrl.m)
		def open_files_callback(): # type: () -> Callable[[], None]
			def open_files(): # type: () -> None
				self.open_files()
			return open_files
		toolbar.add_button(Assets.get_image('debug'), open_files_callback(), 'Reload data files', Ctrl.r)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.dat editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		toolbar.add_button(Assets.get_image('about'), self.about, 'About PyDAT')
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.hor_pane = PanedWindow(self, orient=HORIZONTAL)
		left = Frame(self.hor_pane)
		self.listbox = ScrolledListbox(left, scroll_speed=2, font=Font.fixed(), width=45, height=1)
		self.listbox.pack(side=TOP, fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(ButtonRelease.Click_Right(), self.popup)
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda *e: self.changeid())

		f = Frame(left)
		collapse_button = CollapseView.Button(f)
		collapse_button.pack(side=TOP)
		f.pack(fill=X, pady=2)

		def _update_collapse_setting(collapsed):
			self.data_context.settings.show_listbox_options = not collapsed
		collapse_view = CollapseView(left, collapse_button, callback=_update_collapse_setting)
		collapse_view.pack(fill=X, padx=2, pady=2)

		collapse_view.set_collapsed(not self.data_context.config.show_listbox_options.value)

		self.findhistory = [] # type: list[str]
		self.find = StringVar()
		Label(collapse_view, text='Find:').grid(column=0,row=0, sticky=E)
		find = Frame(collapse_view)
		find_tdd = TextDropDown(find, self.find, self.findhistory, 5)
		find_tdd.pack(side=LEFT, fill=X, expand=1)
		find_tdd.entry.bind(Key.Return(), self.findnext)
		Button(find, text='Next', command=self.findnext).pack(side=LEFT)
		find.grid(column=1,row=0, sticky=EW)

		collapse_view.grid_columnconfigure(1, weight=1)

		self.jumpid = IntegerVar('', [0,0], allow_hex=True)
		Label(collapse_view, text='ID Jump:').grid(column=0,row=1, sticky=E)
		jump = Frame(collapse_view)
		jump_entry = Entry(jump, textvariable=self.jumpid, width=5)
		jump_entry.pack(side=LEFT)
		jump_entry.bind(Key.Return(), self.jump)
		Button(jump, text='Go', command=self.jump).pack(side=LEFT)
		jump.grid(column=1,row=1, sticky=W)

		self.names_display = IntVar()
		self.names_display.trace('w', self.change_names_display)
		self.simple_names = BooleanVar()
		self.simple_names.trace('w', self.change_simple_names)
		Label(collapse_view, text='Names:').grid(column=0,row=2, sticky=E)
		DropDown(collapse_view, self.names_display, ['Basic', 'TBL d', 'Combined']).grid(column=1,row=2, sticky=EW)
		self.simple_names_checkbox = Checkbutton(collapse_view, text='Simple TBL Names', variable=self.simple_names)
		self.simple_names_checkbox.grid(column=1,row=3, sticky=W)

		self.hor_pane.add(left, sticky=NSEW, minsize=300)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Copy Entry to Clipboard', command=self.copy, shortcut=Shift.Ctrl.c) # type: ignore[call-arg]
		self.listmenu.add_command(label='Copy Sub-Tab to Clipboard', command=self.copy_subtab, shortcut=Ctrl.y, tags='can_copy_sub_tab') # type: ignore[call-arg]
		self.listmenu.add_command(label='Paste from Clipboard', command=self.paste, shortcut=Shift.Ctrl.p) # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Reload Entry', command=self.reload, shortcut=Ctrl.r) # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Add Entry (DatExtend)', command=self.add_entry, shortcut=Shift.Ctrl.a, tags='can_expand') # type: ignore[call-arg]
		self.listmenu.add_command(label='Set Entry Count (DatExtend)', command=self.set_entry_count, shortcut=Shift.Ctrl.s, tags='can_expand') # type: ignore[call-arg]
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Override Name', command=self.override_name, shortcut=Shift.Ctrl.n) # type: ignore[call-arg]

		self.status = StringVar()
		self.expanded = StringVar()

		self.dattabs = Notebook(self.hor_pane)
		self.pages = [] # type: list[DATTab]
		tabs = (
			('Units', UnitsTab),
			('Weapons', WeaponsTab),
			('Flingy', FlingyTab),
			('Sprites', SpritesTab),
			('Images', ImagesTab),
			('Upgrades', UpgradesTab),
			('Techdata', TechnologyTab),
			('Sfxdata', SoundsTab),
			('Portdata', PortraitsTab),
			('Mapdata', MapsTab),
			('Orders', OrdersTab),
		) 
		for name,tab in tabs:
			page = tab(self.dattabs, self)
			page.page_title = name
			self.pages.append(page)
			self.dattabs.add_tab(page, name)
		self.dattabs.bind('<<TabActivated>>', lambda _: self.refresh())
		self.hor_pane.add(self.dattabs.notebook, sticky=NSEW)
		self.hor_pane.pack(fill=BOTH, expand=1)

		#Statusbar
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=0.60)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.expanded)
		statusbar.pack(side=BOTTOM, fill=X)

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

	def active_tab(self): # type: () -> DATTab
		return cast(DATTab, self.dattabs.active)

	def refresh(self): # type: () -> None
		self.update_entry_listing(True)
		self.update_name_settings()
		self.update_status_bar()
		self.active_tab().load_data()

	def update_entry_listing(self, update_scroll=False): # type: (bool) -> None
		self.listbox.delete(0,END)
		tab = self.active_tab()
		dat_data = tab.get_dat_data()
		if dat_data.dat:
			max_id = dat_data.dat.entry_count() - 1
			self.jumpid.range[1] = max_id
			self.jumpid.editvalue()
			self.listbox.insert(END, *[' %s  %s' % (lpad(str(id), min(4,len(str(max_id)))), name) for id,name in enumerate(dat_data.names)])
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
	def update_name_settings(self): # type: () -> None
		name_settings = self.active_tab().get_names_settings()
		self.names_display.set(PyDAT.NAMES_SETTING_TO_OPTION[name_settings.display.value])
		if isinstance(name_settings, PyDATConfig.Names.SimpleOptions):
			self.simple_names_checkbox['state'] = NORMAL
			self.simple_names.set(name_settings.simple.value)
		else:
			self.simple_names_checkbox['state'] = DISABLED
			self.simple_names.set(False)
	def change_names_display(self, *_): # type: (Any) -> None
		name_settings = self.active_tab().get_names_settings()
		new_setting = PyDAT.NAMES_OPTION_TO_SETTING[self.names_display.get()]
		if new_setting == name_settings.display.value:
			return
		name_settings.display.value = new_setting
		self.active_tab().get_dat_data().update_names()
	def change_simple_names(self, *_): # type: (Any) -> None
		name_settings = self.active_tab().get_names_settings()
		if not isinstance(name_settings, PyDATConfig.Names.SimpleOptions) or self.simple_names.get() == name_settings.simple.value:
			return
		name_settings.simple.value = self.simple_names.get()
		self.active_tab().get_dat_data().update_names()

	def update_status_bar(self): # type: () -> None
		tab = self.active_tab()
		dat_data = tab.get_dat_data()
		if dat_data.file_path:
			self.status.set(dat_data.file_path)
		elif dat_data.dat:
			self.status.set(dat_data.dat.FILE_NAME)
		self.editstatus['state'] = NORMAL if tab.edited else DISABLED
		if dat_data.is_expanded():
			self.expanded.set('%s expanded' % dat_data.dat_type.FILE_NAME)
		else:
			self.expanded.set('')

	def updated_pointer_entries(self, ids): # type: (list[AnyID]) -> None
		for page in self.pages:
			page.updated_pointer_entries(ids)
			if self.active_tab() == page and page.page_title in ids:
				self.update_entry_listing(True)

	def open_files(self, dat_files=False): # type: (bool) -> (PyMSError | None)
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

	def unsaved(self): # type: () -> (bool | None)
		for page in self.pages:
			if page.unsaved():
				return True
		return None

	def load_data(self, id=None): # type: (int | None) -> None
		self.active_tab().load_data(id)
	def save_data(self): # type: () -> None
		self.active_tab().save_data()
		self.update_status_bar()

	def changeid(self, entry_id=None, focus_list=True): # type: (int | None, bool) -> None
		show_selection = True
		if entry_id is None:
			entry_id = int(self.listbox.curselection()[0])
			show_selection = False
		if entry_id != self.active_tab().id:
			self.save_data()
			self.load_data(entry_id)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(entry_id)
			if show_selection:
				self.listbox.see(entry_id)
			if focus_list:
				self.listbox.focus_set()

	def change_tab(self, dat_id: DATID) -> DATTab:
		return cast(DATTab, self.dattabs.display(dat_id.tab_id))

	def change_id(self, entry_id): # type: (int) -> None
		self.changeid(entry_id)

	def findnext(self, key=None): # type: (Event | None) -> None
		find = self.find.get()
		if find in self.findhistory:
			self.findhistory.remove(find)
		self.findhistory.insert(0, find)
		find = find.lower()
		start = int(self.listbox.curselection()[0])
		cur = (start + 1) % self.listbox.size() # type: ignore[operator]
		while cur != start:
			if find in self.listbox.get(cur).lower():
				self.changeid(cur, focus_list=False)
				return
			cur = (cur+1) % self.listbox.size() # type: ignore[operator]
		MessageBox.showinfo('Find', "Can't find '%s'." % self.find.get())

	def jump(self, key=None): # type: (Event | None) -> None
		self.changeid(self.jumpid.get())

	def popup(self, e): # type: (Event) -> None
		can_expand = False
		dat = self.active_tab().get_dat_data().dat
		if dat:
			can_expand = dat.can_expand()
		self.listmenu.tag_enabled('can_copy_sub_tab', hasattr(self.active_tab(), 'copy_subtab')) # type: ignore[attr-defined]
		self.listmenu.tag_enabled('can_expand', can_expand) # type: ignore[attr-defined]
		self.listmenu.post(e.x_root, e.y_root)

	def copy(self): # type: () -> None
		self.active_tab().copy()

	def copy_subtab(self): # type: () -> None
		tab = cast(UnitsTab, self.dattabs.active)
		tab.copy_subtab()

	def paste(self): # type: () -> None
		try:
			self.active_tab().paste()
		except PyMSError as e:
			ErrorDialog(self, e)
		except:
			raise

	def reload(self): # type: () -> None
		self.active_tab().reload()

	def add_entry(self): # type: () -> None
		self.active_tab().add_entry()

	def set_entry_count(self): # type: () -> None
		self.active_tab().set_entry_count()

	def override_name(self): # type: () -> None
		EntryNameOverrides(self, self.data_context, self.active_tab().DAT_ID, self.active_tab().id)

	def new(self, key=None): # type: (Event | None) -> None
		self.active_tab().new()

	def open(self, key=None, file_path=None): # type: (Event | None, str | None) -> None
		if file_path is None:
			file_path = self.data_context.config.last_path.dat.select_open(self)
			if not file_path:
				return
		filename = os.path.basename(file_path)
		for frame,_ in sorted(list(self.dattabs.pages.values()), key=lambda d: d[1]):
			page = cast(DATTab, frame)
			if filename == page.get_dat_data().dat_type.FILE_NAME:
				try:
					page.open_file(file_path)
				except PyMSError as e:
					ErrorDialog(self, e)
				else:
					self.dattabs.display(page.page_title)
					if (dat := page.get_dat_data().dat) and dat.is_expanded():
						self.data_context.config.dont_warn.expanded_dat.present(self)
				break
		else:
			ErrorDialog(self, PyMSError('Open',"Unrecognized DAT filename '%s'" % file_path))

	def _open_all(self, path, ismpq): # type: (str, bool) -> None
		if not path:
			return
		mpq = None
		if ismpq:
			mpq = MPQ.of(path)
			mpq.open()
		found_normal = [] # type: list[str]
		found_expanded = [] # type: list[str]
		for _,(tab,_) in self.dattabs.pages.items():
			tab = cast(DATTab, tab)
			filename = tab.get_dat_data().dat_type.FILE_NAME
			if mpq:
				try:
					file_data = mpq.read_file('arr\\' + filename)
					tab.open_data(file_data)
				except:
					continue
			else:
				filepath = os.path.join(path, filename)
				if not os.path.exists(filepath):
					continue
				try:
					tab.open_file(filepath)
				except:
					continue
			if tab.get_dat_data().is_expanded():
				found_expanded.append(filename)
			else:
				found_normal.append(filename)
		if mpq:
			mpq.close()
		if not found_normal and not found_expanded:
			ErrorDialog(self, PyMSError('Open','No DAT files found in %s "%s"' % ('MPQ' if ismpq else 'directory', path)))
			return
		message = ''
		if found_normal:
			message += 'DAT Files found:\n\t%s' % ', '.join(found_normal)
		if found_expanded:
			if message:
				message += '\n\n'
			message += "Expanded DAT Files found:\n\t%s\n\nExpanded DAT files require a plugin like 'DatExtend'." % ', '.join(found_expanded)
		MessageBox.showinfo('DAT Files Found', message)	

	def openmpq(self, event=None): # type: (Event | None) -> None
		path = self.data_context.config.last_path.mpq.select_open(self, filetypes=[FileType.mpq(),FileType.exe_mpq()])
		if path:
			self._open_all(path, True)

	def opendirectory(self, event=None): # type: (Event | None) -> None
		path = self.data_context.config.last_path.dir.select_open(self)
		if path:
			self._open_all(path, False)

	def iimport(self, key=None): # type: (Event | None) -> None
		self.active_tab().iimport()

	def save(self, key=None): # type: (Event | None) -> None
		self.save_data()
		self.active_tab().save()

	def saveas(self, key=None): # type: (Event | None) -> None
		self.save_data()
		self.active_tab().saveas()

	def export(self, key=None): # type: (Event | None) -> None
		self.save_data()
		self.active_tab().export()

	def savempq(self, key=None): # type: (Event | None) -> None
		if MPQ.supported():
			self.save_data()
			SaveMPQDialog(self, self)

	def settings(self, key=None, err=None): # type: (Event | None, PyMSError | None) -> None
		SettingsDialog(self, self.data_context.config, self, err, self.data_context.mpq_handler)

	def register_registry(self, e=None): # type: (Event | None) -> None
		try:
			register_registry('PyDAT', 'dat', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None): # type: (Event | None) -> None
		HelpDialog(self, self.data_context.config.windows.help, 'Help/Programs/PyDAT.md')

	def about(self, key=None): # type: (Event | None) -> None
		AboutDialog(self, 'PyDAT', LONG_VERSION, [('BroodKiller',"DatEdit, its design, format specs, and data files.")])

	def exit(self, e=None): # type: (Event | None) -> None
		if not self.unsaved():
			self.data_context.config.windows.main.save_size(self)
			self.data_context.config.list_size.save_size(self.hor_pane)
			self.data_context.config.save()
			self.destroy()
