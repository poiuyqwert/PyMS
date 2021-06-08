
from UnitsTab import UnitsTab
from WeaponsTab import WeaponsTab
from FlingyTab import FlingyTab
from SpritesTab import SpritesTab
from ImagesTab import ImagesTab
from UpgradesTab import UpgradesTab
from TechnologyTab import TechnologyTab
from SoundsTab import SoundsTab
from PortraitsTab import PortraitsTab
from MapsTab import MapsTab
from OrdersTab import OrdersTab
from DataContext import DataContext
from SaveMPQDialog import SaveMPQDialog
from DATSettingsDialog import DATSettingsDialog
from EntryNameOverrides import EntryNameOverrides

from ..FileFormats.MPQ.SFmpq import *
from ..FileFormats.DAT import *

from ..Utilities.utils import VERSIONS, BASE_DIR, WIN_REG_AVAILABLE, couriernew, register_registry, lpad
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
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.UIKit import *

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyDAT']

class PyDAT(MainWindow):
	def __init__(self, guifile=None):
		MainWindow.__init__(self)
		self.title('PyDAT %s' % LONG_VERSION)
		self.set_icon('PyDAT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyDAT', VERSIONS['PyDAT'])
		ga.track(GAScreen('PyDAT'))
		setup_trace(self, 'PyDAT')

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
		toolbar.add_button('new', self.new, 'New', Ctrl.n)
		toolbar.add_gap()
		toolbar.add_button('open', self.open, 'Open', Ctrl.o)
		toolbar.add_button('openfolder', self.opendirectory, 'Open Directory', Ctrl.d)
		toolbar.add_button('import', self.iimport, 'Import from TXT', Ctrl.i)
		toolbar.add_button('openmpq', self.openmpq, 'Open MPQ', Ctrl.Alt.o, enabled=SFMPQ_LOADED)
		toolbar.add_gap()
		toolbar.add_button('save', self.save, 'Save', Ctrl.s)
		toolbar.add_button('saveas', self.saveas, 'Save As', Ctrl.Alt.s)
		toolbar.add_button('export', self.export, 'Export to TXT', Ctrl.e)
		toolbar.add_button('savempq', self.savempq, 'Save MPQ', Ctrl.Alt.m, enabled=SFMPQ_LOADED)
		toolbar.add_section()
		toolbar.add_button('idsort', self.override_name, 'Name Overrides', Shift.Ctrl.n)
		toolbar.add_section()
		toolbar.add_button('asc3topyai', self.mpqtbl, 'Manage MPQ and TBL files', Ctrl.m)
		toolbar.add_button('debug', self.open_files, 'Reload data files', Ctrl.r)
		toolbar.add_section()
		toolbar.add_button('register', self.register, 'Set as default *.dat editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		toolbar.add_button('help', self.help, 'Help', Key.F1)
		toolbar.add_button('about', self.about, 'About PyDAT')
		toolbar.add_section()
		toolbar.add_button('exit', self.exit, 'Exit', Alt.F4)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.hor_pane = PanedWindow(self, orient=HORIZONTAL)
		left = Frame(self.hor_pane)
		self.listbox = ScrolledListbox(left, scroll_speed=2, font=couriernew, width=45, height=1, bd=0, highlightthickness=0, exportselection=0, activestyle=DOTBOX)
		self.listbox.pack(side=TOP, fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(ButtonRelease.Right_Click, self.popup)
		self.listbox.bind('<<ListboxSelect>>', lambda *e: self.changeid())

		self.findhistory = []
		self.find = StringVar()
		self.jumpid = IntegerVar('', [0,0], allow_hex=True)

		search = Frame(left)
		tdd = TextDropDown(search, self.find, self.findhistory, 5)
		tdd.pack(side=LEFT, fill=X, expand=1)
		tdd.entry.bind(Key.Return, self.findnext)
		Button(search, text='Find Next', command=self.findnext).pack(side=LEFT)
		right = Frame(search)
		entry = Entry(right, textvariable=self.jumpid, width=4)
		entry.pack(side=LEFT)
		entry.bind(Key.Return, self.jump)
		Button(right, text='ID Jump', command=self.jump).pack(side=LEFT)
		right.pack(side=RIGHT)
		search.pack(fill=X, padx=2, pady=2)
		self.bind(Ctrl.f, lambda e: tdd.focus_set(highlight=True))

		self.hor_pane.add(left, sticky=NSEW, minsize=300)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Copy Entry to Clipboard', command=self.copy, shortcut=Shift.Ctrl.c)
		self.listmenu_command_copy_sub_tab = self.listmenu.add_command(label='Copy Sub-Tab to Clipboard', command=self.copy_subtab, shortcut=Ctrl.y)
		self.listmenu_command_paste = self.listmenu.add_command(label='Paste from Clipboard', command=self.paste, shortcut=Shift.Ctrl.p)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Reload Entry', command=self.reload, shortcut=Ctrl.r)
		self.listmenu.add_separator()
		self.listmenu_command_add_entry = self.listmenu.add_command(label='Add Entry (DatExtend)', command=self.add_entry, shortcut=Shift.Ctrl.a)
		self.listmenu_command_set_entry_count = self.listmenu.add_command(label='Set Entry Count (DatExtend)', command=self.set_entry_count, shortcut=Shift.Ctrl.s)
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
		# self.dattabs.bind('<<TabDeactivated>>', self.tab_deactivated)
		self.dattabs.bind('<<TabActivated>>', self.tab_activated)
		self.hor_pane.add(self.dattabs.notebook, sticky=NSEW)
		self.hor_pane.pack(fill=BOTH, expand=1)

		#Statusbar
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=0.60)
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','save.gif')))
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
			for title,tab in self.dattabs.pages.iteritems():
				try:
					tab[0].open(guifile, save=False)
					self.dattabs.display(title)
					break
				except PyMSError, e:
					pass
			else:
				ErrorDialog(self, PyMSError('Load',"'%s' is not a valid StarCraft *.dat file, could possibly be corrupt" % guifile))

		UpdateDialog.check_update(self, 'PyDAT')

	def tab_activated(self, event=None):
		self.update_entry_listing(True)
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
		except PyMSError, e:
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
		MessageBox.askquestion(parent=self, title='Find', message="Can't find '%s'." % self.find.get(), type=MessageBox.OK)

	def jump(self, key=None):
		self.changeid(self.jumpid.get())

	def popup(self, e):
		self.listmenu_command_paste['state'] = DISABLED # TODO
		self.listmenu_command_copy_sub_tab['state'] = NORMAL if hasattr(self.dattabs.active, 'copy_subtab') else DISABLED
		can_expand = self.dattabs.active.get_dat_data().dat.can_expand()
		self.listmenu_command_add_entry['state'] = NORMAL if can_expand else DISABLED
		self.listmenu_command_set_entry_count['state'] = DISABLED # TODO: NORMAL if can_expand else DISABLED
		self.listmenu.post(e.x_root, e.y_root)

	def copy(self):
		self.dattabs.active.copy()

	def copy_subtab(self):
		self.dattabs.active.copy_subtab()

	def paste(self):
		try:
			self.dattabs.active.paste()
		except PyMSError, e:
			ErrorDialog(self, e)
		except:
			raise

	def reload(self):
		self.dattabs.active.reload()

	def add_entry(self):
		self.dattabs.active.add_entry()

	def set_entry_count(self):
		pass

	def override_name(self):
		EntryNameOverrides(self, self.data_context, self.dattabs.active.DAT_ID, self.dattabs.active.id)

	def new(self, key=None):
		self.dattabs.active.new()

	def open(self, key=None):
		path = self.data_context.settings.lastpath.dat.select_file('open', self, 'Open DAT file', '*.dat', [('StarCraft DAT files','*.dat'),('All Files','*')])
		if not path:
			return
		filename = os.path.basename(path)
		for page,_ in sorted(self.dattabs.pages.values(), key=lambda d: d[1]):
			if filename == page.get_dat_data().dat_type.FILE_NAME:
				try:
					page.open(path)
				except PyMSError, e:
					ErrorDialog(self, e)
				else:
					self.dattabs.display(page.page_title)
					if page.get_dat_data().dat.is_expanded():
						self.data_context.settings.dont_warn.warn('expanded_dat', self, 'This %s file is expanded.' % filename)
				break
		else:
			ErrorDialog(self, PyMSError('Open',"Unrecognized DAT filename '%s'" % path))

	# TODO
	def openmpq(self, event=None):
		file = self.data_context.settings.lastpath.mpq.select_file('open', self, 'Open MPQ', '.mpq', [('MPQ Files','*.mpq'),('Embedded MPQ Files','*.exe'),('All Files','*')])
		if not file:
			return
		h = SFileOpenArchive(file)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Open','Could not open MPQ "%s"' % file))
			return
		l = []
		found = []
		p = SFile()
		for _,d in self.dats.iteritems():
			entries = list(d.entries)
			p.text = ''
			f = SFileOpenFileEx(h, 'arr\\' + d.FILE_NAME)
			if f in [None,-1]:
				continue
			r = SFileReadFile(f)
			SFileCloseFile(f)
			p.text = r[0]
			try:
				d.load_file(p)
			except:
				d.entries = entries
				continue
			l.append(d.FILE_NAME)
			found.append((d,'%s:arr\\%s' % (file, d.FILE_NAME)))
		SFileCloseArchive(h)
		if not found:
			ErrorDialog(self, PyMSError('Open','No DAT files found in MPQ "%s"' % file))
			return
		MessageBox.showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (file, ', '.join(l)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(d)

	# TODO
	def opendirectory(self, event=None):
		dir = self.data_context.settings.lastpath.select_directory('dir', self, 'Open Directory')
		if not dir:
			return
		dats = [UnitsDAT(),WeaponsDAT(),FlingyDAT(),SpritesDAT(),ImagesDAT(),UpgradesDAT(),TechDAT(),SoundsDAT(),PortraitsDAT(),CampaignDAT(),OrdersDAT()]
		found = [None] * len(dats)
		files = [None] * len(dats)
		for f in os.listdir(dir):
			for n,d in enumerate(dats):
				if d == None:
					continue
				ff = os.path.join(dir,f)
				try:
					d.load_file(ff)
				except PyMSError:
					continue
				found[n] = (d,ff)
				name = f
				if name != d.FILE_NAME:
					name += ' (%s)' % d.FILE_NAME
				files[n] = name
				dats[n] = None
				break
			if not dats:
				break
		found = (f for f in found if f != None)
		if not found:
			ErrorDialog(self, PyMSError('Open','No DAT files found in directory "%s"' % dir))
			return
		files = [f for f in files if f != None]
		MessageBox.showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (dir, ', '.join(files)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(d)

	# TODO
	def iimport(self, key=None):
		self.dattabs.active.iimport()

	def save(self, key=None):
		self.save_data()
		self.dattabs.active.save()

	def saveas(self, key=None):
		self.save_data()
		self.dattabs.active.saveas()

	# TODO
	def export(self, key=None):
		self.save_data()
		self.dattabs.active.export()

	# TODO
	def savempq(self, key=None):
		if SFMPQ_LOADED:
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
			register_registry('PyDAT','','dat',os.path.join(BASE_DIR, 'PyDAT.pyw'),os.path.join(BASE_DIR,'PyMS','Images','PyDAT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyDAT.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyDAT', LONG_VERSION, [('BroodKiller',"DatEdit, its design, format specs, and data files.")])

	def exit(self, e=None):
		if not self.unsaved():
			self.data_context.settings.windows.save_window_size('main', self)
			self.data_context.settings.save_pane_size('list_size', self.hor_pane)
			self.data_context.settings.mpqexport = self.mpq_export
			self.data_context.settings.save()
			self.destroy()
