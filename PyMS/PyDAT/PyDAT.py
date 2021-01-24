
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

from ..FileFormats.Palette import Palette
from ..FileFormats.MPQ.SFmpq import *
from ..FileFormats.TBL import TBL
from ..FileFormats.DAT import *
from ..FileFormats.GRP import CacheGRP, frame_to_photo
from ..FileFormats.IScriptBIN import IScriptBIN

from ..Utilities.utils import VERSIONS, BASE_DIR, WIN_REG_AVAILABLE, couriernew, register_registry, ccopy
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Tooltip import Tooltip
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.TextDropDown import TextDropDown
from ..Utilities.Notebook import Notebook
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.DataCache import DATA_CACHE
from ..Utilities.AboutDialog import AboutDialog

from Tkinter import *
from tkMessageBox import askquestion, showinfo, OK

import os, webbrowser

LONG_VERSION = 'v%s' % VERSIONS['PyDAT']

class PyDAT(Tk):
	def __init__(self, guifile=None):
		Tk.__init__(self)
		self.title('PyDAT %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR, 'PyMS','Images','PyDAT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'PyMS','Images','PyDAT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyDAT', VERSIONS['PyDAT'])
		ga.track(GAScreen('PyDAT'))
		setup_trace(self, 'PyDAT')

		self.data_context = DataContext()

		self.stat_txt = None
		self.imagestbl = None
		self.sfxdatatbl = None
		self.portdatatbl = None
		self.mapdatatbl = None
		self.cmdicon = None
		self.iscriptbin = None
		self.units = None
		self.weapons = None
		self.flingy = None
		self.sprites = None
		self.images = None
		self.upgrades = None
		self.technology = None
		self.sounds = None
		self.portraits = None
		self.campaigns = None
		self.orders = None

		pal = Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.data_context.settings.settings.palettes.get(p, os.path.join(BASE_DIR, 'Palettes', '%s%spal' % (p,os.extsep))))
			except:
				continue
			self.data_context.palettes[p] = pal.palette
		self.dats = {}
		self.defaults = {}

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('openfolder', self.opendirectory, 'Open Directory (Ctrl+D)', NORMAL, 'Ctrl+D'),
			('import', self.iimport, 'Import from TXT (Ctrl+I)', NORMAL, 'Ctrl+I'),
			('openmpq', self.openmpq, 'Open MPQ (Ctrl+Alt+O)', NORMAL if SFMPQ_LOADED else DISABLED, 'Ctrl+Alt+O'),
			2,
			('save', self.save, 'Save (Ctrl+S)', NORMAL, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', NORMAL, 'Ctrl+Alt+A'),
			('export', self.export, 'Export to TXT (Ctrl+E)', NORMAL, 'Ctrl+E'),
			('savempq', self.savempq, 'Save MPQ (Ctrl+Alt+M)', NORMAL if SFMPQ_LOADED else DISABLED, 'Ctrl+Alt+M'),
			10,
			('asc3topyai', self.mpqtbl, 'Manage MPQ and TBL files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.dat editor (Windows Only)', NORMAL if WIN_REG_AVAILABLE else DISABLED, ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyDAT', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.hor_pane = PanedWindow(self, orient=HORIZONTAL)
		left = Frame(self.hor_pane)
		##listbox
		self.listframe = Frame(left, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, font=couriernew, width=45, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.listframe.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.changeid)
		self.listbox.bind('<ButtonRelease-3>', self.popup)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(side=TOP, fill=BOTH, padx=2, pady=2, expand=1)

		self.findhistory = []
		self.find = StringVar()
		self.jumpid = IntegerVar('', [0,227], allow_hex=True)

		search = Frame(left)
		tdd = TextDropDown(search, self.find, self.findhistory, 5)
		tdd.pack(side=LEFT, fill=X, expand=1)
		tdd.entry.bind('<Return>', self.findnext)
		Button(search, text='Find Next', command=self.findnext).pack(side=LEFT)
		right = Frame(search)
		entry = Entry(right, textvariable=self.jumpid, width=4)
		entry.pack(side=LEFT)
		entry.bind('<Return>', self.jump)
		Button(right, text='ID Jump', command=self.jump).pack(side=LEFT)
		right.pack(side=RIGHT)
		search.pack(fill=X, padx=2, pady=2)
		self.bind('<Control-f>', lambda e: tdd.focus_set(highlight=True))

		self.hor_pane.add(left, sticky=NSEW, minsize=300)

		listmenu = [
			('Copy Entry (Ctrl+Shift+C)', lambda t=0: self.copy(t), 0, 'Control-Shift-c'), # 0
			('Paste Entry (Ctrl+Shift+P)', lambda t=0: self.paste(t), 0, 'Control-Shift-p'), # 1
			None,
			('Copy Tab (Ctrl+Y)', lambda t=1: self.copy(t), 1, 'Control-y'), # 3
			('Paste Tab (Ctrl+B)', lambda t=1: self.paste(t), 1, 'Control-b'), # 4
			None,
			('Reload Entry (Ctrl+R)', self.reload, 0, 'Control-r'), #6
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u,b = m
				self.listmenu.add_command(label=l, command=c, underline=u)
				self.bind(b, c)
			else:
				self.listmenu.add_separator()

		self.status = StringVar()
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
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpq_export = self.data_context.settings.get('mpqexport',[])

		self.mpqhandler = MPQHandler(self.data_context.settings.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpqs) and self.mpqhandler.add_defaults():
			self.data_context.settings.settings.mpqs = self.mpqhandler.mpqs

		e = self.open_files()
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
		self.action_states()

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			stat_txt = TBL()
			imagestbl = TBL()
			sfxdatatbl = TBL()
			portdatatbl = TBL()
			mapdatatbl = TBL()
			cmdicon = CacheGRP()
			stat_txt.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('stat_txt', 'MPQ:rez\\stat_txt.tbl')))
			imagestbl.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('imagestbl', 'MPQ:arr\\images.tbl')))
			sfxdatatbl.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('sfxdatatbl', 'MPQ:arr\\sfxdata.tbl')))
			portdatatbl.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('portdatatbl', 'MPQ:arr\\portdata.tbl')))
			mapdatatbl.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('mapdatatbl', 'MPQ:arr\\mapdata.tbl')))
			cmdicon.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('cmdicons', 'MPQ:unit\\cmdbtns\\cmdicons.grp')))
		except PyMSError, e:
			err = e
		else:
			units = UnitsDAT()
			weapons = WeaponsDAT()
			flingy = FlingyDAT()
			sprites = SpritesDAT()
			images = ImagesDAT()
			upgrades = UpgradesDAT()
			technology = TechDAT()
			sounds = SoundsDAT()
			portraits = PortraitsDAT()
			campaigns = CampaignDAT()
			orders = OrdersDAT()
			defaults = [
				(units, UnitsDAT),
				(weapons, WeaponsDAT),
				(flingy, FlingyDAT),
				(sprites, SpritesDAT),
				(images, ImagesDAT),
				(upgrades, UpgradesDAT),
				(technology, TechDAT),
				(sounds, SoundsDAT),
				(portraits, PortraitsDAT),
				(campaigns, CampaignDAT),
				(orders, OrdersDAT),
			]
			defaultmpqs = MPQHandler()
			defaultmpqs.add_defaults()
			defaultmpqs.open_mpqs()
			for v,c in defaults:
				n = c.FILE_NAME
				try:
					v.load_file(defaultmpqs.get_file('MPQ:arr\\' + n, True))
				except:
					try:
						v.load_file(defaultmpqs.get_file('MPQ:arr\\' + n, False))
					except PyMSError, e:
						err = e
						break
			if not err:
				iscriptbin = IScriptBIN(weapons, flingy, images, sprites, sounds, stat_txt, imagestbl, sfxdatatbl)
				iscriptbin.load_file(self.mpqhandler.get_file(self.data_context.settings.settings.files.get('iscriptbin', 'MPQ:scripts\\iscript.bin')))
			defaultmpqs.close_mpqs()
		self.mpqhandler.close_mpqs()
		if not err:
			self.stat_txt = stat_txt
			self.imagestbl = imagestbl
			self.sfxdatatbl = sfxdatatbl
			self.portdatatbl = portdatatbl
			self.mapdatatbl = mapdatatbl
			self.cmdicon = cmdicon
			self.units = units
			self.weapons = weapons
			self.flingy = flingy
			self.sprites = sprites
			self.images = images
			self.upgrades = upgrades
			self.technology = technology
			self.sounds = sounds
			self.portraits = portraits
			self.campaigns = campaigns
			self.orders = orders
			self.iscriptbin = iscriptbin
			for v,c in defaults:
				n = c.FILE_NAME
				self.dats[n] = v
				self.defaults[n] = c()
				self.defaults[n].entries = ccopy(v.entries)
			for page in self.pages:
				page.files_updated()
			self.dattabs.active.activate()
		return err

	def grp(self, pal, path, draw_function=None, draw_info=None):
		if SFMPQ_LOADED and pal in self.data_context.palettes:
			p = os.path.join(BASE_DIR,'PyMS','MPQ',os.path.join(*path.split('\\')))
			if not path in self.data_context.grp_cache or not pal in self.data_context.grp_cache[path]:
				p = self.mpqhandler.get_file('MPQ:' + path)
				try:
					grp = CacheGRP()
					grp.load_file(p,restrict=1)
				except PyMSError:
					return None
				if not path in self.data_context.grp_cache:
					self.data_context.grp_cache[path] = {}
				self.data_context.grp_cache[path][pal] = frame_to_photo(self.data_context.palettes[pal], grp, 0, True, draw_function=draw_function, draw_info=draw_info)
			return self.data_context.grp_cache[path][pal]

	def unsaved(self):
		for page in self.pages:
			if page.unsaved():
				return True

	def action_states(self):
		edited = False
		if self.dattabs.active:
			edited = self.dattabs.active.edited
		self.editstatus['state'] = [DISABLED,NORMAL][edited]

	def load_data(self, id=None):
		self.dattabs.active.load_data(id)
	def save_data(self):
		self.dattabs.active.save_data()
		self.action_states()

	def changeid(self, key=None, i=None, focus_list=True):
		s = True
		if i == None:
			i = int(self.listbox.curselection()[0])
			s = False
		if i != self.dattabs.active.id:
			self.save_data()
			self.load_data(i)
			if s:
				self.listbox.select_clear(0,END)
				self.listbox.select_set(i)
				self.listbox.see(i)
			if focus_list:
				self.listframe.focus_set()

	def popup(self, e):
		self.dattabs.active.popup(e)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.changeid(i=a)

	def findnext(self, key=None):
		f = self.find.get()
		if not f in self.findhistory:
			self.findhistory.append(f)
		start = int(self.listbox.curselection()[0])
		cur = (start + 1) % self.listbox.size()
		while cur != start:
			if f.lower() in DATA_CACHE[self.dattabs.active.data][cur].lower():
				self.changeid(i=cur, focus_list=False)
				return
			cur = (cur+1) % self.listbox.size()
		askquestion(parent=self, title='Find', message="Can't find text.", type=OK)

	def jump(self, key=None):
		self.changeid(i=self.jumpid.get())

	def copy(self, t):
		self.dattabs.active.copy(t)

	def paste(self, t):
		self.dattabs.active.paste(t)

	def reload(self, key=None):
		self.dattabs.active.reload()

	def new(self, key=None):
		self.dattabs.active.new()

	def open(self, key=None):
		path = self.data_context.settings.lastpath.dat.select_file('open', self, 'Open DAT file', '*.dat', [('StarCraft DAT files','*.dat'),('All Files','*')])
		if not path:
			return
		try:
			filesize = os.path.getsize(path)
		except:
			ErrorDialog(self, PyMSError('Open',"Couldn't get file size for '%s'" % path))
		for page,_ in sorted(self.dattabs.pages.values(), key=lambda d: d[1]):
			if filesize == page.dat.filesize:
				page.open(path)
				self.dattabs.display(page.page_title)
				break
		else:
			ErrorDialog(self, PyMSError('Open',"Unrecognized DAT file '%s'" % path))

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
		showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (file, ', '.join(l)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(d)

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
		showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (dir, ', '.join(files)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(d)

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
		if SFMPQ_LOADED:
			self.save_data()
			SaveMPQDialog(self)

	def mpqtbl(self, key=None, err=None):
		data = [
			('TBL Settings',[
				('stat_txt.tbl', 'Contains Unit names', 'stat_txt', 'TBL'),
				('images.tbl', 'Contains GPR mpq file paths', 'imagestbl', 'TBL'),
				('sfxdata.tbl', 'Contains Sound mpq file paths', 'sfxdatatbl', 'TBL'),
				('portdata.tbl', 'Contains Portrait mpq file paths', 'portdatatbl', 'TBL'),
				('mapdata.tbl', 'Contains Campign map mpq file paths', 'mapdatatbl', 'TBL'),
			]),
			('Other Settings',[
				('cmdicons.grp', 'Contains icon images', 'cmdicons', 'CacheGRP'),
				('iscript.bin', 'Contains iscript entries for images.dat', 'iscriptbin', 'IScript'),
			])
		]
		DATSettingsDialog(self, data, (340,450), err, settings=self.data_context.settings)

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
