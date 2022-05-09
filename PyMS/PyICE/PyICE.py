
from ImportListDialog import ImportListDialog
from FindDialog import FindDialog
from CodeEditDialog import CodeEditDialog

from ..FileFormats import IScriptBIN
from ..FileFormats import TBL
from ..FileFormats import DAT

from ..Utilities.utils import BASE_DIR, VERSIONS, WIN_REG_AVAILABLE, couriernew, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Settings import Settings
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.StatusBar import StatusBar
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.DataCache import DATA_CACHE
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog

import os, webbrowser
from copy import deepcopy
from collections import OrderedDict

LONG_VERSION = 'v%s' % VERSIONS['PyICE']

class ColumnID:
	IScripts = 0
	Images = 1
	Sprites = 2
	Flingys = 3
	Units = 4

class PyICE(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyICE', '1')
		self.settings.set_defaults({
			'findhistory':[],
		})
		self.settings.settings.files.set_defaults({
			'stat_txt':'MPQ:rez\\stat_txt.tbl',
			'unitnamestbl':'MPQ:rez\\unitnames.tbl',
			'imagestbl':'MPQ:arr\\images.tbl',
			'sfxdatatbl':'MPQ:arr\\sfxdata.tbl',
			'unitsdat':'MPQ:arr\\units.dat',
			'weaponsdat':'MPQ:arr\\weapons.dat',
			'flingydat':'MPQ:arr\\flingy.dat',
			'spritesdat':'MPQ:arr\\sprites.dat',
			'imagesdat':'MPQ:arr\\images.dat',
			'sfxdatadat':'MPQ:arr\\sfxdata.dat'
		})

		#Window
		MainWindow.__init__(self)
		self.title('PyICE %s (No files loaded)' % LONG_VERSION)
		self.set_icon('PyICE')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyICE', VERSIONS['PyICE'])
		ga.track(GAScreen('PyICE'))
		setup_trace(self, 'PyICE')

		self.file = None
		self.ibin = None
		self.edited = False
		self.tbl = None
		self.imagestbl = None
		self.sfxdatatbl = None
		self.unitsdat = None
		self.weaponsdat = None
		self.flingydat = None
		self.spritesdat = None
		self.imagesdat = None
		self.soundsdat = None

		self.highlights = self.settings.get('highlights', None)
		self.findhistory = []
		self.replacehistory = []
		self.imports = []

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n),
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default Scripts', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Entries', Ctrl.Alt.e, enabled=False, tags='entries_selected')
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Entries', Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('listimport'), self.listimport, 'Import a List of Files', Ctrl.l, enabled=False, tags='entries_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Entries', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('codeedit'), self.codeedit, 'Edit IScript entries', Ctrl.e, enabled=False, tags='entries_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.tblbin, 'Manage TBL and DAT files', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE),
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyICE'),
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Alt.F4)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		#listbox,etc.
		listframes = Frame(self)
		def listbox_colum(name):
			f = Frame(listframes)
			Label(f, text=name + ':', anchor=W).pack(fill=X)
			listbox = ScrolledListbox(f, activestyle=DOTBOX, selectmode=MULTIPLE, font=couriernew, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
			listbox.bind('<<ListboxSelect>>', lambda _,l=listbox: self.listbox_selection_changed(l))
			listbox.pack(fill=BOTH, expand=1)
			Button(f, text='Unselect All', command=lambda l=listbox: self.unselect(l)).pack(fill=X)
			f.pack(side=LEFT, fill=BOTH, padx=2, expand=1)
			return listbox
		self.iscriptlist = listbox_colum('IScript Entries')
		self.imageslist = listbox_colum('Images')
		self.spriteslist = listbox_colum('Sprites')
		self.flingylist = listbox_colum("Flingy's")
		self.unitlist = listbox_colum('Units')
		listframes.pack(fill=BOTH, pady=2, expand=1)

		self.bind(Ctrl.a, lambda *e: self.select_all())

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a BIN.')
		self.selectstatus = StringVar()
		self.selectstatus.set("IScript ID's Selected: None")
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','save.gif')))
		statusbar.add_label(self.selectstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings.settings or not len(self.settings.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()
		if e:
			self.tblbin(err=e)

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyICE')

	def select_all(self):
		self.iscriptlist.select_set(0, END)
		self.action_states()

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tbl = TBL.TBL()
			imagestbl = TBL.TBL()
			sfxdatatbl = TBL.TBL()
			unitsdat = DAT.UnitsDAT()
			weaponsdat = DAT.WeaponsDAT()
			flingydat = DAT.FlingyDAT()
			spritesdat = DAT.SpritesDAT()
			imagesdat = DAT.ImagesDAT()
			soundsdat = DAT.SoundsDAT()
			tbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.stat_txt))
			imagestbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.imagestbl))
			sfxdatatbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.sfxdatatbl))
			unitsdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.unitsdat))
			weaponsdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.weaponsdat))
			flingydat.load_file(self.mpqhandler.get_file(self.settings.settings.files.flingydat))
			spritesdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.spritesdat))
			imagesdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.imagesdat))
			soundsdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.sfxdatadat))
		except PyMSError as e:
			err = e
		else:
			self.tbl = tbl
			self.imagestbl = imagestbl
			self.sfxdatatbl = sfxdatatbl
			self.unitsdat = unitsdat
			self.weaponsdat = weaponsdat
			self.flingydat = flingydat
			self.spritesdat = spritesdat
			self.imagesdat = imagesdat
			self.soundsdat = soundsdat
			try:
				unitnamestbl = TBL.TBL()
				unitnamestbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.unitnamestbl))
			except:
				self.unitnamestbl = None
			else:
				self.unitnamestbl = unitnamestbl
			self.update_dat_lists()
		self.mpqhandler.close_mpqs()
		return err

	def get_image_names(self):
		return tuple(DAT.DATEntryName.image(entry_id, data_names=DATA_CACHE['Images.txt']) for entry_id in range(self.imagesdat.entry_count()))

	def get_sprite_names(self):
		return tuple(DAT.DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Sprites.txt']) for entry_id in range(self.spritesdat.entry_count()))

	def get_flingy_names(self):
		return tuple(DAT.DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Flingy.txt']) for entry_id in range(self.flingydat.entry_count()))

	def get_unit_names(self):
		return tuple(DAT.DATEntryName.unit(entry_id, stat_txt=self.tbl, unitnamestbl=self.unitnamestbl, data_names_usage=DAT.DataNamesUsage.ignore) for entry_id in range(self.unitsdat.entry_count()))

	def update_dat_lists(self):
		updates = (
			(self.get_image_names(), ColumnID.Images, self.imageslist),
			(self.get_sprite_names(), ColumnID.Sprites, self.spriteslist),
			(self.get_flingy_names(), ColumnID.Flingys, self.flingylist),
			(self.get_unit_names(), ColumnID.Units, self.unitlist)
		)
		for names, column, listbox in updates:
			listbox.delete(0,END)
			for index,name in enumerate(names):
				listbox.insert(END, '%03s %s [%s]' % (index, name, self.iscript_id_from_selection_index(index, column)))
		self.action_states()

	def update_iscrips_list(self):
		self.iscriptlist.delete(0,END)
		for iscript_id in self.ibin.headers.keys():
			if iscript_id in self.ibin.extrainfo:
				name = self.ibin.extrainfo[iscript_id]
			elif iscript_id < len(DATA_CACHE['IscriptIDList.txt']):
				name = DATA_CACHE['IscriptIDList.txt'][iscript_id]
			else:
				name = 'Unnamed Custom Entry'
			self.iscriptlist.insert(END, '%03s %s' % (iscript_id, name))

	def iscript_id_from_selection_index(self, index, column):
		index = int(index)
		if column == ColumnID.IScripts:
			return self.ibin.headers.keys()[index]
		if column >= ColumnID.Units:
			index = self.unitsdat.get_entry(index).graphics
		if column >= ColumnID.Flingys:
			index = self.flingydat.get_entry(index).sprite
		if column >= ColumnID.Sprites:
			index = self.spritesdat.get_entry(index).image
		return self.imagesdat.get_entry(index).iscript_id

	def selected_iscript_ids(self):
		iscript_ids = []
		lists = (
			(ColumnID.IScripts, self.iscriptlist),
			(ColumnID.Units, self.unitlist),
			(ColumnID.Flingys, self.flingylist),
			(ColumnID.Sprites, self.spriteslist),
			(ColumnID.Images, self.imageslist)
		)
		for column,listbox in lists:
			selected_indexes = listbox.curselection()
			for index in selected_indexes:
				iscript_id = self.iscript_id_from_selection_index(index, column)
				if not iscript_id in iscript_ids:
					iscript_ids.append(iscript_id)
		return sorted(iscript_ids)

	def unselect(self, listbox):
		listbox.select_clear(0, END)
		self.listbox_selection_changed()

	def listbox_selection_changed(self, listbox=None):
		iscript_ids = self.selected_iscript_ids()
		if iscript_ids:
			self.selectstatus.set("IScript ID's Selected: %s" % ', '.join([str(i) for i in iscript_ids]))
		else:
			self.selectstatus.set("IScript ID's Selected: None")
		self.action_states()
		if listbox:
			listbox.focus_set()

	def is_file_open(self):
		return not not self.ibin

	def action_states(self):
		is_file_open = self.is_file_open()
		for listbox in [self.imageslist,self.spriteslist,self.flingylist,self.unitlist]:
			listbox.listbox['state'] = NORMAL if is_file_open else DISABLED
		self.toolbar.tag_enabled('file_open', is_file_open)

		entries_selected = not not self.selected_iscript_ids()
		self.toolbar.tag_enabled('entries_selected', entries_selected)

	def unsaved(self):
		if self.is_file_open() and self.edited:
			iscript = self.file
			if not iscript:
				iscript = 'iscript.bin'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % iscript, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					return self.saveas()

	def create_iscriptbin(self):
		return IScriptBIN.IScriptBIN(
				weaponsdat=self.weaponsdat,
				flingydat=self.flingydat,
				imagesdat=self.imagesdat,
				spritesdat=self.spritesdat,
				soundsdat=self.soundsdat,
				stat_txt=self.tbl,
				imagestbl=self.imagestbl,
				sfxdatatbl=self.sfxdatatbl
			)

	def new(self, key=None):
		if not self.unsaved():
			self.iscriptlist.delete(0,END)
			self.ibin = self.create_iscriptbin()
			self.file = None
			self.status.set('Editing new BIN.')
			self.title('PyICE %s (Unnamed.bin)' % LONG_VERSION)
			self.action_states()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.settings.lastpath.bin.select_open_files(self, title='Open BIN', filetypes=[('IScripts','*.bin')])
				if not file:
					return
			ibin = self.create_iscriptbin()
			try:
				ibin.load_file(file)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.ibin = ibin
			self.update_iscrips_list()
			self.title('PyICE %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.action_states()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def open_default(self, key=None):
		self.open(key, os.path.join(BASE_DIR, 'PyMS', 'MPQ', 'scripts','iscript.bin'))

	def save(self, key=None):
		if not self.is_file_open():
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.ibin.compile(self.file)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.status.set('Save Successful!')
		self.edited = False
		self.editstatus['state'] = DISABLED

	def saveas(self, key=None):
		if not self.is_file_open():
			return
		file = self.settings.lastpath.bin.select_save_file(self, title='Save BIN As', filetypes=[('IScripts','*.bin')])
		if not file:
			return True
		self.file = file
		self.save()

	# TODO: Cleanup
	def iimport(self, key=None, file=None, parent=None):
		if not self.is_file_open():
			return
		if not file:
			file = self.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[('Text Files','*.txt')])
		if not file:
			return
		if parent == None:
			parent = self
		ibin = self.create_iscriptbin()
		try:
			if self.ibin.code:
				s = self.ibin.code.keys()[-1] + 10
			else:
				s = 0
			w = ibin.interpret(file, s)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if w:
			w = WarningDialog(self, w, True)
			if not w.cont:
				return
		for id in ibin.headers.keys():
			if id in self.ibin.headers:
				for o in self.ibin.headers[id][2]:
					if o != None and o in self.ibin.offsets:
						self.ibin.remove_code(o,id)
			self.ibin.headers[id] = ibin.headers[id]
		for o,i in ibin.offsets.iteritems():
			if o in self.ibin.offsets:
				self.ibin.offsets[o].extend(i)
			else:
				self.ibin.offsets[o] = i
		c = deepcopy(self.ibin.code)
		for o,cmd in ibin.code.iteritems():
			c[o] = cmd
		k = c.keys()
		k.sort()
		self.ibin.code = OrderedDict(sorted(c.iteritems(), key=lambda item: item[0]))
		self.ibin.extrainfo.update(ibin.extrainfo)
		self.update_iscrips_list()
		self.status.set('Import Successful!')
		self.action_states()
		self.edited = True
		self.editstatus['state'] = NORMAL

	def export(self, key=None):
		selected_iscript_ids = self.selected_iscript_ids()
		if not selected_iscript_ids:
			return
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[('Text Files','*.txt')])
		if not file:
			return True
		try:
			self.ibin.decompile(file, ids=selected_iscript_ids)
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def listimport(self, key=None):
		if not self.is_file_open():
			return
		ImportListDialog(self, self.settings)

	def close(self, key=None):
		if not self.is_file_open():
			return
		if not self.unsaved():
			self.iscriptlist.delete(0,END)
			self.ibin = None
			self.title('PyICE %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a BIN.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.listbox_selection_changed()

	def find(self, key=None):
		if not self.is_file_open():
			return
		FindDialog(self)

	def codeedit(self, key=None):
		selected_iscript_ids = self.selected_iscript_ids()
		if not selected_iscript_ids:
			return
		CodeEditDialog(self, self.settings, selected_iscript_ids)

	def tblbin(self, key=None, err=None):
		data = [
			('TBL Settings',[
				('stat_txt.tbl', 'Contains Unit names', 'stat_txt', 'TBL'),
				('unitnames.tbl', 'Contains Unit names for expanded dat files', 'unitnamestbl', 'TBL'),
				('images.tbl', 'Contains GPR mpq file paths', 'imagestbl', 'TBL'),
				('sfxdata.tbl', 'Contains Sound mpq file paths', 'sfxdatatbl', 'TBL'),
			]),
			('DAT Settings',[
				('units.dat', 'Contains link to flingy.dat entries', 'unitsdat', 'UnitsDAT'),
				('weapons.dat', 'Contains stat_txt.tbl string entry for weapon names', 'weaponsdat', 'WeaponsDAT'),
				('flingy.dat', 'Contains link to sprite.dat entries', 'flingydat', 'FlingyDAT'),
				('sprites.dat', 'Contains link to images.dat entries', 'spritesdat', 'SpritesDAT'),
				('images.dat', 'Contains link to IScript entries and images.tbl string indexs', 'imagesdat', 'ImagesDAT'),
				('sfxdata.dat', 'Contains sfxdata.tbl string entries for mpq file paths', 'sfxdatadat', 'SoundsDAT'),
			])
		]
		SettingsDialog(self, data, (340,495), err, settings=self.settings, mpqhandler=self.mpqhandler)

	def register(self, e=None):
		try:
			register_registry('PyICE','','bin',os.path.join(BASE_DIR, 'PyICE.pyw'),os.path.join(BASE_DIR, 'PyMS', 'Images','PyICE.ico'))
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open(os.path.join(BASE_DIR, 'Docs', 'PyICE.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyICE', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.highlights = self.highlights
			self.settings.save()
			self.destroy()
