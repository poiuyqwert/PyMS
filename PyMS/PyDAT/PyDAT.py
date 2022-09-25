
from .UnitsTab import UnitsTab
from .WeaponsTab import WeaponsTab
from .FlingyTab import FlingyTab
from .SpritesTab import SpritesTab
from .ImagesTab import ImagesTab
from .UpgradesTab import UpgradesTab
from .TechnologyTab import TechnologyTab
from .SoundsTab import SoundsTab
from .PortraitsTab import PortraitsTab
from .MapsTab import MapsTab
from .OrdersTab import OrdersTab
from .DataContext import DataContext
from .DATData import NamesDisplaySetting
from .SaveMPQDialog import SaveMPQDialog
from .DATSettingsDialog import DATSettingsDialog
from .EntryNameOverrides import EntryNameOverrides

from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats.DAT import *

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry, lpad
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.TextDropDown import TextDropDown
from ..Utilities.Notebook import Notebook
from ..Utilities.PyMSError import PyMSError
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.StatusBar import StatusBar
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.UIKit import *
from ..Utilities.CollapseView import CollapseView
from ..Utilities.DropDown import DropDown
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.FileType import FileType

import os

LONG_VERSION = 'v%s' % Assets.version('PyDAT')

class PyDAT(MainWindow):
	def __init__(self, guifile=None):
		MainWindow.__init__(self)
		self.title('PyDAT %s' % LONG_VERSION)
		self.set_icon('PyDAT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyDAT', Assets.version('PyDAT'))
		ga.track(GAScreen('PyDAT'))
		setup_trace('PyDAT', self)

		self.data_context = DataContext()
	
		self.updates = []
		self.update_after_id = None
		def buffer_updates(id):
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
		toolbar.add_button(Assets.get_image('asc3topyai'), self.mpqtbl, 'Manage MPQ and TBL files', Ctrl.m)
		toolbar.add_button(Assets.get_image('debug'), self.open_files, 'Reload data files', Ctrl.r)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.dat editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		toolbar.add_button(Assets.get_image('about'), self.about, 'About PyDAT')
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.hor_pane = PanedWindow(self, orient=HORIZONTAL)
		left = Frame(self.hor_pane)
		self.listbox = ScrolledListbox(left, scroll_speed=2, font=Font.fixed(), width=45, height=1)
		self.listbox.pack(side=TOP, fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(ButtonRelease.Click_Right, self.popup)
		self.listbox.bind(WidgetEvent.Listbox.Select, lambda *e: self.changeid())

		f = Frame(left)
		collapse_button = CollapseView.Button(f)
		collapse_button.pack(side=TOP)
		f.pack(fill=X, pady=2)

		def _update_collapse_setting(collapsed):
			self.data_context.settings.show_listbox_options = not collapsed
		collapse_view = CollapseView(left, collapse_button, callback=_update_collapse_setting)
		collapse_view.pack(fill=X, padx=2, pady=2)

		collapse_view.set_collapsed(not self.data_context.settings.get('show_listbox_options', True))

		self.findhistory = []
		self.find = StringVar()
		Label(collapse_view, text='Find:').grid(column=0,row=0, sticky=E)
		find = Frame(collapse_view)
		find_tdd = TextDropDown(find, self.find, self.findhistory, 5)
		find_tdd.pack(side=LEFT, fill=X, expand=1)
		find_tdd.entry.bind(Key.Return, self.findnext)
		Button(find, text='Next', command=self.findnext).pack(side=LEFT)
		find.grid(column=1,row=0, sticky=EW)

		collapse_view.grid_columnconfigure(1, weight=1)

		self.jumpid = IntegerVar('', [0,0], allow_hex=True)
		Label(collapse_view, text='ID Jump:').grid(column=0,row=1, sticky=E)
		jump = Frame(collapse_view)
		jump_entry = Entry(jump, textvariable=self.jumpid, width=5)
		jump_entry.pack(side=LEFT)
		jump_entry.bind(Key.Return, self.jump)
		Button(jump, text='Go', command=self.jump).pack(side=LEFT)
		jump.grid(column=1,row=1, sticky=W)

		self.names_display = IntVar()
		self.names_display.trace('w', self.change_names_display)
		self.simple_names = BooleanVar()
		self.simple_names.trace('w', self.change_simple_names)
		Label(collapse_view, text='Names:').grid(column=0,row=2, sticky=E)
		DropDown(collapse_view, self.names_display, ['Basic', 'TBL Based', 'Combined']).grid(column=1,row=2, sticky=EW)
		self.simple_names_checkbox = Checkbutton(collapse_view, text='Simple TBL Names', variable=self.simple_names)
		self.simple_names_checkbox.grid(column=1,row=3, sticky=W)

		self.hor_pane.add(left, sticky=NSEW, minsize=300)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Copy Entry to Clipboard', command=self.copy, shortcut=Shift.Ctrl.c)
		self.listmenu.add_command(label='Copy Sub-Tab to Clipboard', command=self.copy_subtab, shortcut=Ctrl.y, tags='can_copy_sub_tab')
		self.listmenu.add_command(label='Paste from Clipboard', command=self.paste, shortcut=Shift.Ctrl.p)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Reload Entry', command=self.reload, shortcut=Ctrl.r)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Add Entry (DatExtend)', command=self.add_entry, shortcut=Shift.Ctrl.a, tags='can_expand')
		self.listmenu.add_command(label='Set Entry Count (DatExtend)', command=self.set_entry_count, shortcut=Shift.Ctrl.s, tags='can_expand')
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Override Name', command=self.override_name, shortcut=Shift.Ctrl.n)

		self.status = StringVar()
		self.expanded = StringVar()

		self.dattabs = Notebook(self.hor_pane)
		self.pages = []
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
		self.dattabs.bind('<<TabActivated>>', self.tab_activated)
		self.hor_pane.add(self.dattabs.notebook, sticky=NSEW)
		self.hor_pane.pack(fill=BOTH, expand=1)

		#Statusbar
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=0.60)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.expanded)
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpq_export = self.data_context.settings.get('mpqexport',[])

		self.data_context.load_mpqs()

		e = self.open_files(dat_files=True)
		if e:
			self.mpqtbl(err=e)

		self.data_context.settings.windows.load_window_size('main', self)
		self.data_context.settings.load_pane_size('list_size', self.hor_pane, 300)

		if guifile:
			self.open(file_path=guifile)

		UpdateDialog.check_update(self, 'PyDAT')

	def tab_activated(self, event=None):
		self.update_entry_listing(True)
		self.update_name_settings()
		self.update_status_bar()
		self.dattabs.active.load_data()

	def update_entry_listing(self, update_scroll=False):
		self.listbox.delete(0,END)
		tab = self.dattabs.active
		dat_data = tab.get_dat_data()
		if dat_data.dat:
			max_id = dat_data.dat.entry_count() - 1
			self.jumpid.range[1] = max_id
			self.jumpid.editvalue()
			self.listbox.insert(END, *[' %s  %s' % (lpad(id, min(4,len(str(max_id)))), name) for id,name in enumerate(dat_data.names)])
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
	def update_name_settings(self):
		name_settings = self.data_context.settings.names[self.dattabs.active.DAT_ID.id]
		self.names_display.set(PyDAT.NAMES_SETTING_TO_OPTION[name_settings.display])
		if 'simple' in name_settings:
			self.simple_names_checkbox['state'] = NORMAL
			self.simple_names.set(name_settings.simple)
		else:
			self.simple_names_checkbox['state'] = DISABLED
			self.simple_names.set(False)
	def change_names_display(self, *_):
		name_settings = self.data_context.settings.names[self.dattabs.active.DAT_ID.id]
		new_setting = PyDAT.NAMES_OPTION_TO_SETTING[self.names_display.get()]
		if new_setting == name_settings.display:
			return
		name_settings.display = new_setting
		self.dattabs.active.get_dat_data().update_names()
	def change_simple_names(self, *_):
		name_settings = self.data_context.settings.names[self.dattabs.active.DAT_ID.id]
		if not 'simple' in name_settings or self.simple_names.get() == name_settings.simple:
			return
		name_settings.simple = self.simple_names.get()
		self.dattabs.active.get_dat_data().update_names()

	def update_status_bar(self):
		tab = self.dattabs.active
		dat_data = tab.get_dat_data()
		if dat_data.file_path:
			self.status.set(dat_data.file_path)
		else:
			self.status.set(dat_data.dat.FILE_NAME)
		self.editstatus['state'] = NORMAL if tab.edited else DISABLED
		if dat_data.is_expanded():
			self.expanded.set('%s expanded' % dat_data.dat_type.FILE_NAME)
		else:
			self.expanded.set('')

	def updated_pointer_entries(self, ids):
		for page in self.pages:
			page.updated_pointer_entries(ids)
			if self.dattabs.active == page and page.page_title in ids:
				self.update_entry_listing(True)

	def open_files(self, dat_files=False):
		err = None
		try:
			self.data_context.load_additional_files()
		except PyMSError as e:
			err = e
		else:
			if dat_files:
				self.data_context.load_dat_files()
			self.tab_activated()
		return err

	def unsaved(self):
		for page in self.pages:
			if page.unsaved():
				return True

	def load_data(self, id=None):
		self.dattabs.active.load_data(id)
	def save_data(self):
		self.dattabs.active.save_data()
		self.update_status_bar()

	def changeid(self, entry_id=None, focus_list=True):
		show_selection = True
		if entry_id == None:
			entry_id = int(self.listbox.curselection()[0])
			show_selection = False
		if entry_id != self.dattabs.active.id:
			self.save_data()
			self.load_data(entry_id)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(entry_id)
			if show_selection:
				self.listbox.see(entry_id)
			if focus_list:
				self.listbox.focus_set()

	def findnext(self, key=None):
		find = self.find.get()
		if find in self.findhistory:
			self.findhistory.remove(find)
		self.findhistory.insert(0, find)
		find = find.lower()
		start = int(self.listbox.curselection()[0])
		cur = (start + 1) % self.listbox.size()
		while cur != start:
			if find in self.listbox.get(cur).lower():
				self.changeid(cur, focus_list=False)
				return
			cur = (cur+1) % self.listbox.size()
		MessageBox.showinfo('Find', "Can't find '%s'." % self.find.get())

	def jump(self, key=None):
		self.changeid(self.jumpid.get())

	def popup(self, e):
		self.listmenu.tag_enabled('can_copy_sub_tab', hasattr(self.dattabs.active, 'copy_subtab'))
		self.listmenu.tag_enabled('can_expand', self.dattabs.active.get_dat_data().dat.can_expand())
		self.listmenu.post(e.x_root, e.y_root)

	def copy(self):
		self.dattabs.active.copy()

	def copy_subtab(self):
		self.dattabs.active.copy_subtab()

	def paste(self):
		try:
			self.dattabs.active.paste()
		except PyMSError as e:
			ErrorDialog(self, e)
		except:
			raise

	def reload(self):
		self.dattabs.active.reload()

	def add_entry(self):
		self.dattabs.active.add_entry()

	def set_entry_count(self):
		self.dattabs.active.set_entry_count()

	def override_name(self):
		EntryNameOverrides(self, self.data_context, self.dattabs.active.DAT_ID, self.dattabs.active.id)

	def new(self, key=None):
		self.dattabs.active.new()

	def open(self, key=None, file_path=None):
		if file_path == None:
			file_path = self.data_context.settings.lastpath.dat.select_open_file(self, title='Open DAT file', filetypes=[FileType.dat()])
			if not file_path:
				return
		filename = os.path.basename(file_path)
		for page,_ in sorted(self.dattabs.pages.values(), key=lambda d: d[1]):
			if filename == page.get_dat_data().dat_type.FILE_NAME:
				try:
					page.open_file(file_path)
				except PyMSError as e:
					ErrorDialog(self, e)
				else:
					self.dattabs.display(page.page_title)
					if page.get_dat_data().dat.is_expanded():
						self.data_context.settings.dont_warn.warn('expanded_dat', self, "This %s file is expanded and will require a plugin like 'DatExtend'." % filename)
				break
		else:
			ErrorDialog(self, PyMSError('Open',"Unrecognized DAT filename '%s'" % file_path))

	def _open_all(self, path, ismpq):
		if not path:
			return
		mpq = None
		if ismpq:
			mpq = MPQ.of(path)
			mpq.open()
		found_normal = [] # type: list[str]
		found_expanded = [] # type: list[str]
		for _,(tab,_) in self.dattabs.pages.iteritems():
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

	def openmpq(self, event=None):
		path = self.data_context.settings.lastpath.mpq.select_open_file(self, title='Open MPQ', filetypes=[FileType.mpq(),FileType.exe_mpq()])
		self._open_all(path, True)

	def opendirectory(self, event=None):
		path = self.data_context.settings.lastpath.select_directory(self, title='Open Directory')
		self._open_all(path, False)

	def iimport(self, key=None):
		self.dattabs.active.iimport()

	def save(self, key=None):
		self.save_data()
		self.dattabs.active.save()

	def saveas(self, key=None):
		self.save_data()
		self.dattabs.active.saveas()

	def export(self, key=None):
		self.save_data()
		self.dattabs.active.export()

	def savempq(self, key=None):
		if MPQ.supported():
			self.save_data()
			SaveMPQDialog(self)

	def mpqtbl(self, key=None, err=None):
		data = [
			('TBL Settings',[
				('stat_txt.tbl', 'Contains Unit, Weapon, Upgrade, Tech, and Order names', 'stat_txt', 'TBL'),
				('unitnames.tbl', 'Contains Unit names for expanded dat files', 'unitnamestbl', 'TBL'),
				('images.tbl', 'Contains GPR mpq file paths', 'imagestbl', 'TBL'),
				('sfxdata.tbl', 'Contains Sound mpq file paths', 'sfxdatatbl', 'TBL'),
				('portdata.tbl', 'Contains Portrait mpq file paths', 'portdatatbl', 'TBL'),
				('mapdata.tbl', 'Contains Campign map mpq file paths', 'mapdatatbl', 'TBL'),
			]),
			('Other Settings',[
				('cmdicons.grp', 'Contains icon images', 'cmdicons', 'CacheGRP'),
				('iscript.bin', 'Contains iscript entries for images.dat', 'iscriptbin', 'IScript'),
			]),
			('Palette Settings',[
				('Unit', 'Used to display normal graphics previews', 'Units', 'Palette'),
				('bfire', 'Used to display graphics previews with bfire.pcx remapping', 'bfire', 'Palette'),
				('gfire', 'Used to display graphics previews with gfire.pcx remapping', 'gfire', 'Palette'),
				('ofire', 'Used to display graphics previews with ofire.pcx remapping', 'ofire', 'Palette'),
				('Terrain', 'Used to display terrain based graphics previews', 'Terrain', 'Palette'),
				('Icons', 'Used to display icon previews', 'Icons', 'Palette')
			])
		]
		DATSettingsDialog(self, data, (640,600), err, settings=self.data_context.settings, mpqhandler=self.data_context.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyDAT', 'dat', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.data_context.settings, 'Help/Programs/PyDAT.md')

	def about(self, key=None):
		AboutDialog(self, 'PyDAT', LONG_VERSION, [('BroodKiller',"DatEdit, its design, format specs, and data files.")])

	def exit(self, e=None):
		if not self.unsaved():
			self.data_context.settings.windows.save_window_size('main', self)
			self.data_context.settings.save_pane_size('list_size', self.hor_pane)
			self.data_context.settings.mpqexport = self.mpq_export
			self.data_context.settings.save()
			self.destroy()
