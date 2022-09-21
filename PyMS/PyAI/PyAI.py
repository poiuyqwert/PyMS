
from .ListboxTooltip import ListboxTooltip
from .EditScriptDialog import EditScriptDialog
from .FindDialog import FindDialog
from .ContinueImportDialog import ContinueImportDialog
from .ImportListDialog import ImportListDialog
from .CodeEditDialog import CodeEditDialog
from .FlagEditor import FlagEditor
from .ExternalDefDialog import ExternalDefDialog
from .StringEditor import StringEditor

from ..FileFormats import AIBIN
from ..FileFormats import TBL
from ..FileFormats import DAT
from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag

from ..Utilities.utils import register_registry, WIN_REG_AVAILABLE
from ..Utilities.UIKit import *
from ..Utilities.Settings import Settings
from ..Utilities import Assets
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.StatusBar import StatusBar
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.FileType import FileType

import os, shutil
from collections import OrderedDict

LONG_VERSION = 'v%s' % Assets.version('PyAI')

class PyAI(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyAI', '1')
		self.settings.set_defaults({
			'stat_txt': Assets.mpq_file_path('rez', 'stat_txt.tbl'),
		})
		self.settings.settings.files.set_defaults({
			'unitsdat': 'MPQ:arr\\units.dat',
			'upgradesdat': 'MPQ:arr\\upgrades.dat',
			'techdatadat': 'MPQ:arr\\techdata.dat',
		})

		MainWindow.__init__(self)
		self.title('No files loaded')
		self.set_icon('PyAI')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyAI', Assets.version('PyAI'))
		ga.track(GAScreen('PyAI'))
		setup_trace('PyAI', self)

		self.aiscript = None
		self.bwscript = None
		self.stat_txt = self.settings['stat_txt']
		self.tbl = TBL.TBL()
		try:
			self.tbl.load_file(self.stat_txt)
		except:
			self.stat_txt = None
			self.tbl = None
		self.tbledited = False
		self.unitsdat = None
		self.upgradesdat = None
		self.techdat = None
		self.ai = None
		self.strings = {}
		self.edited = False
		self.undos = []
		self.redos = []
		self.imports = []
		self.extdefs = []
		for t,l in [('imports',self.imports),('extdefs',self.extdefs)]:
			if t in self.settings:
				for f in self.settings.get(t):
					if os.path.exists(f):
						l.append(f)
		self.highlights = self.settings.get('highlights', None)
		self.findhistory = []
		self.replacehistory = []

		self.sort = StringVar()
		self.sort.set('order')
		self.sort.trace('w', lambda *_: self.resort())
		self.reference = IntVar()
		self.reference.set(self.settings.get('reference', 0))

		# Note: Toolbar will bind the shortcuts below
		# TODO: Check for items not bound by `Toolbar`
		self.menu = Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File')
		file_menu.add_command('New', self.new, Ctrl.n, bind_shortcut=False)
		file_menu.add_command('Open', self.open, Ctrl.o, bind_shortcut=False)
		file_menu.add_command('Open Default Scripts', self.open_default, Ctrl.d, bind_shortcut=False)
		file_menu.add_command('Open MPQ', self.open_mpq, Ctrl.Alt.o, enabled=MPQ.supported(), bind_shortcut=False, underline='m')
		file_menu.add_command('Save', self.save, Ctrl.s, enabled=False, tags='file_open', bind_shortcut=False)
		file_menu.add_command('Save As...', self.saveas, Ctrl.Alt.a, enabled=False, tags='file_open', bind_shortcut=False, underline='As')
		file_menu.add_command('Save MPQ', self.savempq, Ctrl.Alt.m, enabled=MPQ.supported(), tags=('file_open','mpq_available'), bind_shortcut=False, underline='a')
		file_menu.add_command('Close', self.close, Ctrl.w, enabled=False, tags='file_open', bind_shortcut=False, underline='c')
		file_menu.add_separator()
		file_menu.add_command('Set as default *.bin editor (Windows Only)', self.register, enabled=WIN_REG_AVAILABLE, underline='t')
		file_menu.add_separator()
		file_menu.add_command('Exit', self.exit, Shortcut.Exit, underline='e')

		edit_menu = self.menu.add_cascade('Edit')
		edit_menu.add_command('Undo', self.undo, Ctrl.z, enabled=False, tags='can_undo', bind_shortcut=False, underline='u')
		edit_menu.add_command('Redo', self.redo, Ctrl.y, enabled=False, tags='can_redo', bind_shortcut=False, underline='r')
		edit_menu.add_separator()
		edit_menu.add_command('Select All', self.select_all, Ctrl.a, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Add Blank Script', self.add, Key.Insert, enabled=False, tags='file_open', bind_shortcut=False, underline='b')
		edit_menu.add_command('Remove Scripts', self.remove, Key.Delete, enabled=False, tags='scripts_selected', bind_shortcut=False, underline='v')
		edit_menu.add_command('Find Scripts', self.find, Ctrl.f, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_separator()
		edit_menu.add_command('Export Scripts', self.export, Ctrl.Alt.e, enabled=False, tags='scripts_selected', bind_shortcut=False)
		edit_menu.add_command('Import Scripts', self.iimport, Ctrl.Alt.i, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Import a List of Files', self.listimport, Ctrl.l, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_checkbutton('Print Reference when Decompiling', self.reference, underline='p')
		edit_menu.add_separator()
		edit_menu.add_command('Edit AI Script', self.codeedit, Ctrl.e, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Edit AI ID, String, and Extra Info.', self.edit, Ctrl.i, enabled=False, tags='scripts_selected', bind_shortcut=False, underline='ID')
		edit_menu.add_command('Edit Flags', self.editflags, Ctrl.g, enabled=False, tags='scripts_selected', bind_shortcut=False)
		edit_menu.add_separator()
		edit_menu.add_command('Manage External Definition Files', self.extdef, Ctrl.x, bind_shortcut=False)
		edit_menu.add_command('Manage TBL File', self.managetbl, Ctrl.t, bind_shortcut=False)
		edit_menu.add_command('Manage MPQ and DAT Settings', self.managedat, Ctrl.u, bind_shortcut=False, underline='m')

		view_menu = self.menu.add_cascade('View')
		view_menu.add_radiobutton('File Order', self.sort, 'order', underline='Order')
		view_menu.add_radiobutton('Sort by ID', self.sort, 'idsort', underline='ID')
		view_menu.add_radiobutton('Sort by BroodWar', self.sort, 'bwsort', underline='BroodWar')
		view_menu.add_radiobutton('Sort by Flags', self.sort, 'flagsort', underline='Flags')
		view_menu.add_radiobutton('Sort by Strings', self.sort, 'stringsort', underline='Strings')

		help_menu = self.menu.add_cascade('Help')
		help_menu.add_command('View Help', self.help, Key.F1, bind_shortcut=False, underline='h')
		help_menu.add_separator()
		help_menu.add_command('About PyAI', self.about, underline='a')

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default Scripts', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('openmpq'), self.open_mpq, 'Open MPQ', Ctrl.Alt.o, enabled=MPQ.supported())
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savempq'), self.savempq, 'Save MPQ', Ctrl.Alt.m, enabled=False, tags=('file_open','mpq_available'))
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('undo'), self.undo, 'Undo', Ctrl.z, enabled=False, tags='can_undo')
		self.toolbar.add_button(Assets.get_image('redo'), self.redo, 'Redo', Ctrl.y, enabled=False, tags='can_redo')
		self.toolbar.add_section()
		self.toolbar.add_radiobutton(Assets.get_image('order'), self.sort, 'order', 'File Order')
		self.toolbar.add_radiobutton(Assets.get_image('idsort'), self.sort, 'idsort', 'Sort by ID')
		self.toolbar.add_radiobutton(Assets.get_image('bwsort'), self.sort, 'bwsort', 'Sory by BroodWar')
		self.toolbar.add_radiobutton(Assets.get_image('flagsort'), self.sort, 'flagsort', 'Sort by Flags')
		self.toolbar.add_radiobutton(Assets.get_image('stringsort'), self.sort, 'stringsort', 'Sort by String')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyAI')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		
		self.toolbar.add_row()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add Blank Script', Key.Insert, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Scripts', Key.Delete, enabled=False, tags='scripts_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Scripts', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Scripts', Ctrl.Alt.e, enabled=False, tags='scripts_selected')
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Scripts', Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('listimport'), self.listimport, 'Import a List of Files', Ctrl.l, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_checkbutton(Assets.get_image('reference'), self.reference, 'Print Reference when Decompiling')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('codeedit'), self.codeedit, 'Edit AI Script', Ctrl.e, enabled=False, tags='scripts_selected')
		self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit AI ID, String, and Extra Info.', Ctrl.i, enabled=False, tags='scripts_selected')
		self.toolbar.add_button(Assets.get_image('flags'), self.editflags, 'Edit Flags', Ctrl.g, enabled=False, tags='scripts_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('extdef'), self.extdef, 'Manage External Definition Files', Ctrl.x)
		self.toolbar.add_button(Assets.get_image('tbl'), self.managetbl, 'Manage TBL file', Ctrl.t)
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.managedat, 'Manage MPQ and DAT Settings', Ctrl.u)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('openset'), self.openset, 'Open TBL and DAT Settings')
		self.toolbar.add_button(Assets.get_image('saveset'), self.saveset, 'Save TBL and DAT Settings')
		self.toolbar.pack(side=TOP, fill=X)

		self.menu.tag_enabled('mpq_available', MPQ.supported())
		self.toolbar.tag_enabled('mpq_available', MPQ.supported())

		self.listbox = ScrolledListbox(self, selectmode=EXTENDED, font=Font.fixed(), activestyle=DOTBOX, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
		self.listbox.pack(fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.get_entry = self.get_entry
		self.listbox.bind(ButtonRelease.Click_Right, self.popup)
		self.listbox.bind(Double.Click_Left, self.codeedit)

		# TODO: Cleanup
		listmenu = [
			('Add Blank Script (Insert)', self.add, 4), # 0
			('Remove Scripts (Delete)', self.remove, 0), # 1
			None,
			('Export Scripts (Ctrl+Alt+E)', self.export, 0), # 3
			('Import Scripts (Ctrl+Alt+I)', self.iimport, 0), # 4
			None,
			('Edit AI Script (Ctrl+E)', self.codeedit, 5), #6
			('Edit Script ID, String, and AI Info (Ctrl+I)', self.edit, 8), # 7
			('Edit Flags (Ctrl+G)', self.editflags, 8), # 8
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u = m
				self.listmenu.add_command(label=l, command=c, underline=u)
			else:
				self.listmenu.add_separator()

		self.status = StringVar()
		self.status.set('Load your files or create new ones.')
		self.scriptstatus = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.scriptstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(aiscript_path=guifile)

		UpdateDialog.check_update(self, 'PyAI')

		if e:
			self.managedat(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			unitsdat = DAT.UnitsDAT()
			upgradesdat = DAT.UpgradesDAT()
			techdat = DAT.TechDAT()
			unitsdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.unitsdat))
			upgradesdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.upgradesdat))
			techdat.load_file(self.mpqhandler.get_file(self.settings.settings.files.techdatadat))
			if not self.tbl:
				file = self.settings.lastpath.tbl.select_open_file(self, title='Open a stat_txt.tbl first', filetypes=[FileType.tbl()])
				tbl = TBL.TBL()
				tbl.load_file(file)
				self.stat_txt = file
				self.tbl = tbl
		except PyMSError as e:
			err = e
		else:
			self.unitsdat = unitsdat
			self.upgradesdat = upgradesdat
			self.techdat = techdat
			if self.ai:
				self.ai.unitsdat = unitsdat
				self.ai.upgradesdat = upgradesdat
				self.ai.techdat = techdat
		self.mpqhandler.close_mpqs()
		return err

	# Misc. functions
	def title(self, text=None):
		MainWindow.title(self,'PyAI %s (%s)' % (LONG_VERSION, text))

	def get_entry(self, index):
		match = re.match(r'(....)\s{5}(\s\s|BW)\s{5}([01]{3})\s{5}(.+)', self.listbox.get(index))
		id = match.group(1)
		return (id, match.group(2) == 'BW', match.group(3), self.ai.ais[id][1], match.group(4))

	def entry_text(self, id, bw, flags, string):
		if isinstance(string, int):
			string = TBL.decompile_string(self.ai.tbl.strings[string])
		if len(string) > 50:
			string = string[:47] + '...'
		aiinfo = ''
		if id in self.ai.aiinfo:
			aiinfo = self.ai.aiinfo[id][0]
		return '%s     %s     %s     %s%s%s' % (id, ['  ','BW'][bw], flags, string, ' ' * (55-len(string)), aiinfo)

	def set_entry(self, index, id, bw, flags, string):
		if index != END:
			self.listbox.delete(index)
		self.listbox.insert(index, self.entry_text(id, bw, flags, string))

	def resort(self):
		{'order':self.order,'idsort':self.idsort,'bwsort':self.bwsort,'flagsort':self.flagsort,'stringsort':self.stringsort}[self.sort.get()]()

	def add_undo(self, type, data):
		max = self.settings.get('undohistory', 10)
		if not max:
			return
		if self.redos:
			self.redos = []
			self.toolbar.tag_enabled('can_redo', False)
			self.menu.tag_enabled('can_redo', False)
		if not self.undos:
			self.toolbar.tag_enabled('can_undo', True)
			self.menu.tag_enabled('can_undo', True)
		self.undos.append((type, data))
		if len(self.undos) > max:
			del self.undos[0]

	def is_file_open(self):
		return not not self.ai

	def has_scripts_selected(self):
		return not not self.listbox.curselection()

	def action_states(self):
		is_file_open = self.is_file_open()
		has_scripts_selected = self.has_scripts_selected()

		self.toolbar.tag_enabled('file_open', is_file_open)
		self.menu.tag_enabled('file_open', is_file_open)

		self.toolbar.tag_enabled('scripts_selected', has_scripts_selected)
		self.menu.tag_enabled('scripts_selected', has_scripts_selected)

	def unsaved(self):
		if self.tbledited:
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % self.stat_txt, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				self.tbl.compile(self.stat_txt)
				self.tbledited = False
		if self.ai and self.edited:
			aiscript = self.aiscript
			if not aiscript:
				aiscript = 'aiscript.bin'
			bwscript = self.bwscript
			if not bwscript:
				bwscript = 'bwscript.bin'
			save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s' and '%s'?" % (aiscript, bwscript), default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return True
				if self.aiscript:
					self.save()
				else:
					return self.saveas()

	def edittbl(self, edited=None):
		if edited == None:
			return self.tbledited
		self.tbledited = edited

	def stattxt(self, file=None):
		if file == None:
			return self.stat_txt
		self.stat_txt = file

	# TODO: Update
	def popup(self, e):
		if self.ai:
			if not self.listbox.curselection():
				s = DISABLED
			else:
				s = NORMAL
			for i in [1,3,7,8]:
				self.listmenu.entryconfig(i, state=s)
			self.listmenu.post(e.x_root, e.y_root)

	# Acitions
	def new(self, key=None):
		if not self.unsaved():
			self.ai = AIBIN.AIBIN(False, self.unitsdat, self.upgradesdat, self.techdat, self.tbl)
			self.ai.bwscript = AIBIN.BWBIN(self.unitsdat, self.upgradesdat, self.techdat, self.tbl)
			self.ai.bwscript.tbl = self.tbl
			self.strings = {}
			self.aiscript = None
			self.bwscript = None
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			self.title('aiscript.bin, bwscript.bin')
			self.status.set('Editing new file!')
			self.listbox.delete(0, END)
			self.action_states()
			self.scriptstatus.set('aiscript.bin: 0 (0 B)     bwscript.bin: 0 (0 B)')

	def open(self, key=None, aiscript_data=None, aiscript_path=None, bwscript_data=None, bwscript_path=None): # type: (None, bytes, str, bytes, str) -> None
		if not self.unsaved():
			if not aiscript_path:
				aiscript_path = self.settings.lastpath.bin.select_open_file(self, title='Open aiscript.bin', filetypes=[FileType.bin_ai()])
				if not aiscript_path:
					return
				if not bwscript_path:
					bwscript_path = self.settings.lastpath.bin.select_open_file(self, title='Open bwscript.bin (Cancel to only open aiscript.bin)', filetypes=[FileType.bin_ai()])
			warnings = []
			try:
				ai = AIBIN.AIBIN(bwscript_data if bwscript_data else bwscript_path, self.unitsdat, self.upgradesdat, self.techdat, self.tbl, bwscript_is_data=not not bwscript_data)
				warnings.extend(ai.warnings)
				if aiscript_data:
					warnings.extend(ai.load_data(aiscript_data))
				else:
					warnings.extend(ai.load_file(aiscript_path, True))
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.ai = ai
			self.strings = {}
			for id,ai in self.ai.ais.iteritems():
				if not ai[1] in self.strings:
					self.strings[ai[1]] = []
				self.strings[ai[1]].append(id)
			self.aiscript = aiscript_path
			self.bwscript = bwscript_path
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			if not bwscript_path:
				bwscript_path = 'bwscript.bin'
			self.title('%s, %s' % (aiscript_path,bwscript_path))
			self.status.set('Load Successful!')
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
			if warnings:
				WarningDialog(self, warnings)

	def open_default(self, key=None):
		self.open(key, aiscript_path=Assets.mpq_file_path('Scripts','aiscript.bin'), bwscript_path=Assets.mpq_file_path('Scripts','bwscript.bin'))

	def open_mpq(self):
		file = self.settings.lastpath.mpq.select_open_file(self, title='Open MPQ', filetypes=[FileType.mpq(),FileType.exe_mpq()])
		if not file:
			return
		mpq = MPQ.of(file)
		try:
			mpq_ctx = mpq.open()
		except:
			ErrorDialog(self, PyMSError('Open','Could not open MPQ "%s"' % file))
			return
		with mpq_ctx:
			ai = mpq.read_file('scripts\\aiscript.bin')
			bw = None
			try:
				bw = mpq.read_file('scripts\\bwscript.bin')
			except:
				pass
		self.open(aiscript_data=ai, aiscript_path='scripts\\aiscript.bin', bwscript_data=bw, bwscript_path='scripts\\bwscript.bin')

	def save(self, key=None, ai=None, bw=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if ai == None:
			ai = self.aiscript
		if bw == None and self.ai.bwscript.ais:
			bw = self.bwscript
		if ai == None:
			self.saveas()
			return
		if self.tbledited:
			file = self.settings.lastpath.tbl.select_save_file(self, title="Save stat_txt.tbl (Cancel doesn't stop bin saving)", filetypes=[FileType.tbl()])
			if file:
				self.stat_txt = file
				try:
					self.tbl.compile(file)
				except PyMSError as e:
					ErrorDialog(self, e)
					return
				self.tbledited = False
		try:
			self.ai.compile(ai, bw)
			self.aiscript = ai
			if bw != None:
				self.bwscript = bw
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.status.set('Save Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		aiscript = self.settings.lastpath.bin.select_save_file(self, title='Save aiscript.bin As', filetypes=[FileType.bin_ai()])
		if not aiscript:
			return True
		bwscript = None
		if self.ai.bwscript.ais:
			bwscript = self.settings.lastpath.bin.select_save_file(self, title='Save bwscript.bin As (Cancel to save aiscript.bin only)', filetypes=[FileType.bin_ai()])
		if self.save(ai=aiscript, bw=bwscript):
			self.tbledited = False
			self.title('%s, %s' % (self.aiscript,self.bwscript))

	def savempq(self, key=None):
		file = self.settings.lastpath.mpq.select_save_file(self, title='Save MPQ to...', filetypes=[FileType.mpq(),FileType.exe_mpq()])
		if file:
			if file.endswith('%sexe' % os.extsep) and not os.path.exists(file):
				try:
					shutil.copy(Assets.data_file_path('SEMPQ.exe'), file)
				except:
					ErrorDialog(self, PyMSError('Saving','Could not create SEMPQ "%s".' % file))
					return
			not_saved = []
			try:
				ai,_ = self.ai.compile_data()
				bw,_ = self.ai.bwscript.compile_data()
				mpq = MPQ.of(file)
				with mpq.open_or_create():
					try:
						mpq.add_data(ai, 'scripts\\aiscript.bin', compression=MPQCompressionFlag.pkware)
					except:
						not_saved.append('scripts\\aiscript.bin')
					try:
						mpq.add_data(bw, 'scripts\\bwscript.bin', compression=MPQCompressionFlag.pkware)
					except:
						not_saved.append('scripts\\bwscript.bin')
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			if not_saved:
				MessageBox.askquestion(parent=self, title='Save problems', message='%s could not be saved to the MPQ.' % ' and '.join(not_saved), type=MessageBox.OK)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.ai = None
			self.strings = {}
			self.aiscript = None
			self.bwscript = None
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.undos = []
			self.redos = []
			self.title('No files loaded')
			self.status.set('Load your files or create new ones.')
			self.listbox.delete(0, END)
			self.action_states()
			self.scriptstatus.set('')

	def register(self, e=None):
		try:
			register_registry('PyAI', 'bin', 'AI')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyAI.md')

	def about(self):
		thanks = [
			('bajadulce',"Testing, support, and hosting! I can't thank you enough!"),
			('ashara','Lots of help with beta testing and ideas'),
			('MamiyaOtaru','Found lots of bugs, most importantly ones on Mac and Linux.'),
			('Heinerman','File specs and command information'),
			('modmaster50','Lots of ideas, testing, and support, thanks a lot!')
		]
		AboutDialog(self, 'PyAI', LONG_VERSION, thanks)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings.windows.save_window_size('main', self)
			self.settings.stat_txt = self.stat_txt
			self.settings.highlights = self.highlights
			self.settings.reference = self.reference.get()
			self.settings.imports = self.imports
			self.settings.extdefs = self.extdefs
			self.settings.save()
			self.destroy()

	# TODO: Cleanup sorts
	def order(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			for id,ai in self.ai.ais.iteritems():
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)
	def idsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = list(self.ai.ais.keys())
			ais.sort()
			for id in ais:
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
					self.listbox.see(END)
			if not sel:
				self.listbox.select_set(0)
	def bwsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.iteritems():
				ais.append('%s %s' % (ai[0], id))
			ais.sort()
			for a in ais:
				id = a.split(' ',1)[1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)
	def flagsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.iteritems():
				ais.append('%s %s' % (AIBIN.convflags(ai[2]), id))
			ais.sort()
			ais.reverse()
			for a in ais:
				id = a.split(' ',1)[1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)
	def stringsort(self, key=None):
		if self.ai:
			sel = []
			if self.listbox.size():
				for index in self.listbox.curselection():
					try:
						sel.append(self.get_entry(index)[0])
					except:
						pass
				self.listbox.delete(0, END)
			ais = []
			for id,ai in self.ai.ais.iteritems():
				ais.append('%s\x00%s' % (TBL.decompile_string(self.ai.tbl.strings[ai[1]]), id))
			ais.sort()
			for a in ais:
				id = a.split('\x00')[-1]
				ai = self.ai.ais[id]
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
				if sel and id in sel:
					self.listbox.select_set(END)
			if not sel:
				self.listbox.select_set(0)

	def undo(self, key=None):
		if key and self.buttons['undo']['state'] != NORMAL:
			return
		max = self.settings.get('redohistory', 10)
		undo = self.undos.pop()
		if max:
			if not self.redos:
				self.toolbar.tag_enabled('can_redo', True)
				self.menu.tag_enabled('can_redo', True)
			self.redos.append(undo)
			if len(self.redos) > max:
				del self.redos[0]
		if not self.undos:
			self.toolbar.tag_enabled('can_undo', False)
			self.menu.tag_enabled('can_undo', False)
			self.edited = False
			self.editstatus['state'] = DISABLED
		if undo[0] == 'remove':
			start = self.listbox.size()
			for id,ai,bw,info,s in undo[1]:
				self.ai.ais[id] = ai
				if bw:
					self.ai.bwscript.ais[id] = ai
					self.ai.bwscript.aisizes[id] = s
				else:
					self.ai.aisizes[id] = s
				if info:
					self.ai.aiinfo[id] = info
				if not ai[1] in self.strings:
					self.strings[ai[1]] = []
				if id not in self.strings[ai[1]]:
					self.strings[ai[1]].append(id)
				self.set_entry(END, id, not ai[0], AIBIN.convflags(ai[2]), ai[1])
			self.listbox.select_clear(0, END)
			self.listbox.select_set(start, END)
			self.listbox.see(start)
			self.action_states()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif undo[0] == 'add':
			id = undo[1][0]
			del self.ai.ais[id]
			del self.ai.aisizes[id]
			if id in self.ai.aiinfo:
				del self.ai.aiinfo[id]
			self.strings[undo[1][1][1]].remove(id)
			if not self.strings[undo[1][1][1]]:
				del self.strings[undo[1][1][1]]
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif undo[0] == 'edit':
			oldid,id,oldflags,_,oldstrid,_,oldaiinfo,aiinfo = undo[1]
			if oldid != id:
				self.ai.ais[oldid] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[oldid] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[oldid] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = oldid
			self.ai.ais[id][1] = oldstrid
			self.ai.ais[id][2] = oldflags
			if oldaiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',OrderedDict(),[]]
				self.ai.aiinfo[id][0] = oldaiinfo
			self.resort()
		elif undo[0] == 'flags':
			self.ai.ais[undo[1][0]][2] = undo[1][1]
			self.resort()

	def redo(self, key=None):
		if key and self.buttons['redo']['state'] != NORMAL:
			return
		self.edited = True
		self.editstatus['state'] = NORMAL
		max = self.settings.get('undohistory', 10)
		redo = self.redos.pop()
		if max:
			if not self.undos:
				self.toolbar.tag_enabled('can_undo', True)
				self.menu.tag_enabled('can_undo', True)
			self.undos.append(redo)
			if len(self.undos) > max:
				del self.undos[0]
		if not self.redos:
			self.toolbar.tag_enabled('can_redo', False)
			self.menu.tag_enabled('can_redo', False)
		if redo[0] == 'remove':
			for id,ai,bw,_,s in redo[1]:
				del self.ai.ais[id]
				if bw:
					del self.ai.bwscript.ais[id]
					del self.ai.bwscript.aisizes[id]
				else:
					del self.ai.aisizes[id]
				if id in self.ai.aiinfo:
					del self.ai.aiinfo[id]
				self.strings[ai[1]].remove(id)
				if not self.strings[ai[1]]:
					del self.strings[ai[1]]
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif redo[0] == 'add':
			id = redo[1][0]
			ai = redo[1][1]
			self.ai.ais[id] = ai
			self.ai.aisizes[id] = 1
			if redo[1][2]:
				self.ai.aiinfo = [redo[1][2],OrderedDict(),[]]
			if not ai[1] in self.strings:
				self.strings[ai[1]] = []
			if id not in self.strings[ai[1]]:
				self.strings[ai[1]].append(id)
			self.resort()
			self.action_states()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
		elif redo[0] == 'edit':
			id,oldid,_,oldflags,_,oldstrid,aiinfo,oldaiinfo = redo[1]
			if oldid != id:
				self.ai.ais[oldid] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[oldid] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[oldid] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = oldid
			self.ai.ais[id][1] = oldstrid
			self.ai.ais[id][2] = oldflags
			if oldaiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',OrderedDict(),[]]
				self.ai.aiinfo[id][0] = oldaiinfo
			self.resort()
		elif redo[0] == 'flags':
			self.ai.ais[redo[1][0]][2] = redo[1][2]
			self.resort()

	def select_all(self, key=None):
		self.listbox.select_set(0, END)

	def add(self, key=None):
		if key and self.buttons['add']['state'] != NORMAL:
			return
		s = 2+sum(self.ai.aisizes.values())
		if s > 65535:
			ErrorDialog(self, PyMSError('Adding',"There is not enough room in your aiscript.bin to add a new script"))
			return
		e = EditScriptDialog(self, title='Adding New AI Script')
		id = e.id.get()
		if id:
			ai = [1,int(e.string.get()),e.flags,[[36]],[]]
			self.ai.ais[id] = ai
			self.ai.aisizes[id] = 1
			if e.aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',OrderedDict(),[]]
				self.ai.aiinfo[id][0] = e.aiinfo
			if not ai[1] in self.strings:
				self.strings[ai[1]] = []
			if id not in self.strings[ai[1]]:
				self.strings[ai[1]].append(id)
			self.set_entry(END, id, False, '000', ai[1])
			self.listbox.select_clear(0, END)
			self.listbox.select_set(END)
			self.resort()
			self.listbox.see(self.listbox.curselection()[0])
			self.action_states()
			self.edited = True
			self.editstatus['state'] = NORMAL
			self.add_undo('add', [id, ai, e.aiinfo])
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
				self.scriptstatus.set(s)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		indexs = self.listbox.curselection()
		ids = []
		cantremove = {}
		for index in indexs:
			external = []
			e = self.get_entry(index)
			if e[0] in self.ai.externaljumps[e[1]][0]:
				for d in self.ai.externaljumps[e[1]][0][e[0]].iteritems():
					for id in d[1]:
						if not id in external:
							external.append(id)
			if external:
				cantremove[e[0]] = external
			else:
				ids.append(index)
		if cantremove:
			more = len(cantremove) != len(indexs)
			t = '\n'.join(['\t%s referenced by: %s' % (id,', '.join(refs)) for id,refs in cantremove.iteritems()])
			# TODO: Figure out how this `cont` is supposed to be used
			cont = MessageBox.askquestion(parent=self, title='Removing', message="These scripts can not be removed because they are referenced by other scripts:\n%s%s" % (t,['','\n\nContinue removing the other scripts?'][more]), default=[None,MessageBox.YES][more], type=[MessageBox.OK,MessageBox.YESNOCANCEL][more])
		undo = []
		n = 0
		for index in ids:
			index = int(index) - n
			item = self.get_entry(index)
			id = item[0]
			ai = self.ai.ais[id]
			del self.ai.ais[id]
			bw = None
			if item[1]:
				bw = self.ai.bwscript.ais[id]
				del self.ai.bwscript.ais[id]
				s = self.ai.bwscript.aisizes[id]
				del self.ai.bwscript.aisizes[id]
			else:
				s = self.ai.aisizes[id]
				del self.ai.aisizes[id]
			if item[0] in self.ai.aiinfo:
				del self.ai.aiinfo[id]
			self.strings[ai[1]].remove(id)
			if not self.strings[ai[1]]:
				del self.strings[ai[1]]
			undo.append((item[0], ai, bw, self.ai.aiinfo.get(item[0]), s))
			self.listbox.delete(index)
			n += 1
		if self.listbox.size():
			if indexs[0] != '0':
				self.listbox.select_set(int(indexs[0])-1)
			else:
				self.listbox.select_set(0)
		self.action_states()
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.add_undo('remove', undo)
		s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
		if self.ai.bwscript:
			s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
		self.scriptstatus.set(s)

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		FindDialog(self)

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		export = self.settings.lastpath.ai_txt.select_save_file(self, key='export', title='Export To', filetypes=[FileType.txt()])
		if export:
			indexs = self.listbox.curselection()
			external = []
			ids = []
			for index in indexs:
				e = self.get_entry(index)
				ids.append(e[0])
				if ids[-1] in self.ai.externaljumps[e[1]][1]:
					for id in self.ai.externaljumps[e[1]][1][ids[-1]]:
						if not id in external:
							external.append(id)
			if external:
				for i in ids:
					if i in external:
						external.remove(i)
				if external:
					ids.extend(external)
			try:
				warnings = self.ai.decompile(export, self.extdefs, self.reference.get(), 1, ids)
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			if warnings:
				WarningDialog(self, warnings)
			if external:
				MessageBox.askquestion(parent=self, title='External References', message='One or more of the scripts you are exporting references an external block, so the scripts that are referenced have been exported as well:\n    %s' % '\n    '.join(external), type=MessageBox.OK)

	def iimport(self, key=None, iimport=None, c=True, parent=None):
		if key and self.buttons['import']['state'] != NORMAL:
			return
		if parent == None:
			parent = self
		if not iimport:
			iimport = self.settings.latpath.ai_txt.select_open_file(self, key='import', title='Import From', filetypes=[FileType.txt()])
		if iimport:
			i = AIBIN.AIBIN(False, self.unitsdat, self.upgradesdat, self.techdat, self.stat_txt)
			i.bwscript = AIBIN.BWBIN(self.unitsdat, self.upgradesdat, self.techdat, self.stat_txt)
			try:
				warnings = i.interpret(iimport, self.extdefs)
				for id in i.ais.keys():
					if id in self.ai.externaljumps[0]:
						for _,l in self.ai.externaljumps[0]:
							for cid in l:
								if not cid in i.ais:
									raise PyMSError('Interpreting',"You can't edit scripts (%s) that are referenced externally with out editing the scripts with the external references (%s) at the same time." % (id,cid))
			except PyMSError as e:
				ErrorDialog(parent, e)
				return -1
			cont = c
			if warnings:
				w = WarningDialog(parent, warnings, True)
				cont = w.cont
			if cont:
				for id,ai in i.ais.iteritems():
					if id in self.ai.ais and (cont == True or cont != 2):
						x = ContinueImportDialog(parent, id)
						cont = x.cont
						if not cont:
							continue
						elif cont == 3:
							break
					self.ai.ais[id] = ai
					if not ai[0]:
						self.ai.bwscript.ais[id] = i.bwscript.ais[id]
					for a,b in ((0,0),(0,1),(1,0),(1,1)):
						if id in i.externaljumps[a][b]:
							self.ai.externaljumps[a][b][id] = i.externaljumps[a][b][id]
						elif id in self.ai.externaljumps[a][b]:
							del self.ai.externaljumps[a][b][id]
					if id in i.aiinfo:
						self.ai.aiinfo[id] = i.aiinfo[id]
					elif id in self.ai.aiinfo:
						del self.ai.aiinfo[id]
					if id in i.bwscript.aiinfo:
						self.ai.bwscript.aiinfo[id] = i.bwscript.aiinfo[id]
					elif id in self.ai.bwscript.aiinfo:
						del self.ai.bwscript.aiinfo[id]
					if not ai[1] in self.strings:
						self.strings[ai[1]] = []
					if id not in self.strings[ai[1]]:
						self.strings[ai[1]].append(id)
					self.resort()
			s = 'aiscript.bin: %s (%s B) ' % (len(self.ai.ais),sum(self.ai.aisizes.values()))
			if self.ai.bwscript:
				s += '     bwscript.bin: %s (%s B)' % (len(self.ai.bwscript.ais),sum(self.ai.bwscript.aisizes.values()))
			self.scriptstatus.set(s)
			self.action_states()
			self.edited = True
			self.editstatus['state'] = NORMAL
			return cont

	def listimport(self, key=None):
		if key and self.buttons['listimport']['state'] != NORMAL:
			return
		ImportListDialog(self)

	def codeedit(self, key=None):
		if key and self.buttons['codeedit']['state'] != NORMAL:
			return
		indexs = self.listbox.curselection()
		external = []
		ids = []
		for index in indexs:
			e = self.get_entry(index)
			ids.append(e[0])
			if ids[-1] in self.ai.externaljumps[e[1]][1]:
				for id in self.ai.externaljumps[e[1]][1][ids[-1]]:
					if not id in external:
						external.append(id)
		if external:
			for i in external:
				if not i in ids:
					ids.append(i)
		CodeEditDialog(self, self.settings, ids)

	def edit(self, key=None):
		if key and self.buttons['edit']['state'] != NORMAL:
			return
		id = self.get_entry(self.listbox.curselection()[0])[0]
		aiinfo = ''
		if id in self.ai.aiinfo:
			aiinfo = self.ai.aiinfo[id][0]
		e = EditScriptDialog(self, id, self.ai.ais[id][2], self.ai.ais[id][1], aiinfo, initial=id)
		if e.id.get():
			undo = (id,e.id.get(),self.ai.ais[id][2],e.flags,self.ai.ais[id][1],int(e.string.get()),aiinfo,e.aiinfo)
			if e.id.get() != id:
				self.ai.ais[e.id.get()] = self.ai.ais[id]
				if not self.ai.ais[id][0]:
					self.ai.bwscript.ais[e.id.get()] = self.ai.bwscript.ais[id]
					del self.ai.bwscript.ais[id]
				del self.ai.ais[id]
				if id in self.ai.aiinfo:
					self.ai.aiinfo[e.id.get()] = self.ai.aiinfo[id]
					del self.ai.aiinfo[id]
				id = e.id.get()
			self.ai.ais[id][1] = int(e.string.get())
			self.ai.ais[id][2] = e.flags
			if e.aiinfo != aiinfo:
				if not id in self.ai.aiinfo:
					self.ai.aiinfo[id] = ['',OrderedDict(),[]]
				self.ai.aiinfo[id][0] = e.aiinfo
			self.add_undo('edit', undo)
			self.resort()

	def editflags(self, key=None):
		if key and self.buttons['flags']['state'] != NORMAL:
			return
		id = self.get_entry(self.listbox.curselection()[0])[0]
		f = FlagEditor(self, self.ai.ais[id][2])
		if f.flags != None:
			self.add_undo('flags', [id,self.ai.ais[id][2],f.flags])
			self.ai.ais[id][2] = f.flags
			self.resort()
			self.edited = True
			self.editstatus['state'] = NORMAL

	def extdef(self, key=None):
		if key and self.buttons['extdef']['state'] != NORMAL:
			return
		ExternalDefDialog(self, self.settings)

	def managetbl(self, key=None):
		i = 0
		if self.listbox.size():
			i = self.get_entry(self.listbox.curselection()[0])[3]
		StringEditor(self, index=i)

	def managedat(self, key=None, err=None):
		data = [
			('DAT  Settings',[
				('units.dat', 'Used to check if a unit is a Building or has Air/Ground attacks', 'unitsdat', 'UnitsDAT'),
				('upgrades.dat', 'Used to specify upgrade string entries in stat_txt.tbl', 'upgradesdat', 'UpgradesDAT'),
				('techdata.dat', 'Used to specify technology string entries in stat_txt.tbl', 'techdatadat', 'TechDAT')
			])
		]
		SettingsDialog(self, data, (340,295), err, mpqhandler=self.mpqhandler)

	def openset(self, key=None):
		file = self.settings.lastpath.set_txt.select_open_file(self, title='Load Settings', filetypes=[FileType.txt()])
		if file:
			try:
				files = open(file,'r').readlines()
			except:
				MessageBox.showerror('Invalid File',"Could not open '%s'." % file)
			sets = [
				TBL.TBL(),
				DAT.UnitsDAT(),
				DAT.UpgradesDAT(),
				DAT.TechDAT(),
			]
			for n,s in enumerate(sets):
				try:
					s.load_file(files[n] % {'path': Assets.base_dir})
				except PyMSError as e:
					ErrorDialog(self, e)
					return
			self.tbl = sets[0]
			self.stat_txt = files[0]
			self.unitsdat = sets[1]
			self.upgradesdat = sets[2]
			self.techdat = sets[3]

	def saveset(self, key=None):
		file = self.settings.lastpath.set_txt.select_save_file(self, title='Save Settings', filetypes=[FileType.txt()])
		if file:
			try:
				set = open(file,'w')
			except:
				MessageBox.showerror('Invalid File',"Could not save to '%s'." % file)
			set.write(('%s\n%s\n%s\n%s' % (self.stat_txt, self.settings.settings.filees.self.unitsdat, self.settings.settings.filees.self.upgradesdat, self.settings.settings.filees.self.techdat)).replace(Assets.base_dir, '%(path)s'))
			set.close()
