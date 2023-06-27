
from .TRGCodeText import TRGCodeText
from .FindReplaceDialog import FindReplaceDialog
from .CodeColors import CodeColors

from ..FileFormats import TRG
from ..FileFormats import TBL
from ..FileFormats import AIBIN

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Settings import Settings
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved

from typing import cast, BinaryIO

# def customs(trg):
	# trg.dynamic_actions[1] = ['MySetLocationTo',[TRG.new_location,TRG.new_x1,TRG.new_y1,TRG.new_x2,TRG.new_y2,TRG.new_flags,TRG.new_properties]]
	# trg.dynamic_actions[2] = ['MySetLocationFromDeaths',[TRG.new_location,TRG.action_tunit]]
	# trg.dynamic_actions[3] = ['MyRemoveUnit',[TRG.action_player,TRG.action_tunit,TRG.action_location]]
	# trg.dynamic_actions[255] = ['StickUnit',[]]
# TRG.REGISTER.append(customs)

LONG_VERSION = 'v%s' % Assets.version('PyTRG')

class PyTRG(MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		self.settings = Settings('PyTRG', '1')
		self.settings.settings.files.set_defaults({
			'stat_txt':'MPQ:rez\\stat_txt.tbl',
			'aiscript':'MPQ:scripts\\aiscript.bin',
		})

		#Window
		MainWindow.__init__(self)
		self.set_icon('PyTRG')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTRG', Assets.version('PyTRG'))
		ga.track(GAScreen('PyTRG'))
		setup_trace('PyTRG', self)
		Theme.load_theme(self.settings.get('theme'), self)

		self.trg: TRG.TRG | None = None
		self.file: str | None = None
		self.edited = False
		self.tbl: TBL.TBL
		self.aibin: AIBIN.AIBIN
		# self.findhistory = []
		# self.replacehistory = []
		self.findwindow: FindReplaceDialog | None = None

		self.update_title()

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import TRG', Ctrl.i)
		self.toolbar.add_gap()
		def save():
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas():
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savegottrg'), self.savegottrg, 'Save *.got Compatable *.trg', Ctrl.g, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export TRG', Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', Ctrl.t, enabled=False, tags='file_open')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', Ctrl.Alt.c)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.tblbin, 'Manage stat_txt.tbl and aiscript.bin files', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.trg editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTRG')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.completing = False
		self.complete = [None, 0]
		self.autocomptext = list(TRG.keywords) + ['Trigger','Conditions','Actions']
		self.autocompfuncs: list[str] = []
		self.autocompfuncs.extend(name for name in TRG.TRG.conditions[TRG.NORMAL_TRIGGERS] if name)
		self.autocompfuncs.extend(name for name in TRG.TRG.conditions[TRG.MISSION_BRIEFING] if name)
		self.autocompfuncs.extend(name for name in TRG.TRG.actions[TRG.NORMAL_TRIGGERS] if name)
		self.autocompfuncs.extend(name for name in TRG.TRG.actions[TRG.MISSION_BRIEFING] if name)
		self.autocompfuncs.extend(name for name in TRG.TRG.new_actions if name)
		self.autocompfuncs.sort()

		# Text editor
		self.text = TRGCodeText(self, self.edit, highlights=self.settings.get('highlights'), state=DISABLED)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		#Statusbar
		self.status = StringVar()
		self.status.set('Load or create a TRG.')
		self.codestatus = StringVar()
		self.codestatus.set('Line: 1  Column: 0  Selected: 0')
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=0.4)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.codestatus)
		statusbar.pack(side=BOTTOM, fill=X)

		self.settings.windows.load_window_size('main', self)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpq_paths()
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyTRG')

		if e:
			self.tblbin(err=e)

	def open_files(self) -> (PyMSError | None):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tbl = TBL.TBL()
			aibin = AIBIN.AIBIN()
			tbl.load_file(cast(BinaryIO, self.mpqhandler.get_file(self.settings.settings.files['stat_txt'])))
			aibin.load_file(cast(BinaryIO, self.mpqhandler.get_file(self.settings.settings.files['aiscript'])))
		except PyMSError as e:
			err = e
		else:
			self.tbl = tbl
			self.aibin = aibin
		self.mpqhandler.close_mpqs()
		return err

	def check_saved(self) -> CheckSaved:
		if not self.trg or not self.edited:
			return CheckSaved.saved
		file = self.file
		if not file:
			file = 'Unnamed.trg'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.file:
			return self.save()
		else:
			return self.saveas()

	def is_file_open(self) -> bool:
		return not not self.trg

	def action_states(self) -> None:
		self.toolbar.tag_enabled('file_open', self.is_file_open())
		self.text['state'] = NORMAL if self.is_file_open() else DISABLED

	def statusupdate(self) -> None:
		if not self.completing:
			self.text.taboverride = None
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.codestatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edit(self) -> None:
		if not self.completing:
			self.text.taboverride = None
			self.complete = [None, 0]
		self.mark_edited()

	def update_title(self) -> None:
		file_path = self.file
		if not file_path and self.is_file_open():
			file_path = 'Untitled.trg'
		if not file_path:
			self.title('PyTRG %s' % LONG_VERSION)
		else:
			self.title('PyTRG %s (%s)' % (LONG_VERSION, file_path))

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.text.re = None
		self.trg = TRG.TRG(self.tbl,self.aibin)
		self.file = None
		self.status.set('Editing new TRG.')
		self.update_title()
		self.action_states()
		self.text.delete('1.0', END)
		self.mark_edited(False)

	def open(self, file: str | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		if file is None:
			file = self.settings.lastpath.trg.select_open_file(self, title='Open TRG', filetypes=[FileType.trg()])
			if not file:
				return
		trg = TRG.TRG()
		try:
			trg.load_file(file)
			data = trg.decompile_data()
		except PyMSError as e:
			try:
				trg.load_file(file, True)
				data = trg.decompile_data()
			except PyMSError as e:
				ErrorDialog(self, e)
				return
		self.text.re = None
		self.trg = trg
		self.update_title()
		self.file = file
		self.status.set('Load Successful!')
		self.action_states()
		self.text.delete('1.0', END)
		self.text.insert('1.0', data.rstrip('\n'))
		self.text.edit_reset()
		self.text.see('1.0')
		self.mark_edited(False)

	def iimport(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		file = self.settings.lastpath.txt.select_open_file(self, key='import', title='Import TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			text = open(file,'r').read()
		except:
			ErrorDialog(self, PyMSError('Import','Could not open file "%s"' % file))
			return
		self.text.re = None
		self.trg = TRG.TRG()
		self.file = file
		self.update_title()
		self.status.set('Import Successful!')
		self.action_states()
		self.text.delete('1.0', END)
		self.text.insert('1.0', text.rstrip('\n'))
		self.text.edit_reset()
		self.mark_edited(False)

	def save(self) -> CheckSaved:
		return self.saveas(file_path=self.file)

	def saveas(self, file_path: str | None = None) -> CheckSaved:
		if not self.trg:
			return CheckSaved.saved
		if not file_path:
			file_path = self.settings.lastpath.trg.select_save_file(self, title='Save TRG As', filetypes=[FileType.trg()])
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			self.trg.interpret(self.text)
			self.trg.compile(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.status.set('Save Successful!')
		self.mark_edited(False)
		self.file = file_path
		self.update_title()
		return CheckSaved.saved

	def savegottrg(self) -> None:
		if not self.trg:
			return
		file = self.settings.lastpath.trg.select_save_file(self, title='Save *.got Compatable *.trg As', filetypes=[FileType.trg()])
		if not file:
			return
		try:
			text = self.text.get('1.0', END)
			self.trg.interpret(text)
			self.trg.compile(file, True)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.status.set('*.got Compatable *.trg Saved Successfully!')

	def export(self) -> None:
		file = self.settings.lastpath.txt.select_save_file(self, key='export', title='Export TXT', filetypes=[FileType.txt()])
		if not file:
			return
		try:
			f = open(file,'w')
			f.write(self.text.get('1.0',END))
			f.close()
			self.status.set('Export Successful!')
		except PyMSError as e:
			ErrorDialog(self, e)

	def test(self) -> None:
		i = TRG.TRG()
		try:
			text = self.text.get('1.0', END)
			warnings = i.interpret(text)
		except PyMSError as e:
			if e.line is not None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line is not None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line is not None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			MessageBox.showinfo(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.')

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.trg = None
		self.file = None
		self.update_title()
		self.status.set('Load or create a TRG.')
		self.text.delete('1.0', END)
		self.mark_edited(False)
		self.action_states()

	def find(self) -> None:
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind(Key.F3(), self.findwindow.findnext)
		else:
			self.findwindow.make_active() # type: ignore[attr-defined]
			self.findwindow.findentry.focus_set(highlight=True)

	def colors(self) -> None:
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.highlights = c.cont

	def tblbin(self, err: PyMSError | None = None) -> None:
		data = [
			('File Settings',[
				('stat_txt.tbl', 'Contains Unit and AI Script names', 'stat_txt', 'TBL'),
				('aiscript.bin', "Contains AI ID's and references to names in stat_txt.tbl", 'aiscript', 'AIBIN'),
			]),
			('Theme',)
		]
		SettingsDialog(self, data, (550,380), err, mpqhandler=self.mpqhandler)

	def register_registry(self) -> None:
		try:
			register_registry('PyTRG', 'trg', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.settings, 'Help/Programs/PyTRG.md')

	def about(self) -> None:
		AboutDialog(self, 'PyTRG', LONG_VERSION, [('FaRTy1billion','For creating TrigPlug and giving me the specs!')])

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.settings.windows.save_window_size('main', self)
		self.settings['highlights'] = self.text.highlights
		self.settings.save()
		self.destroy()

	def autocomplete(self) -> bool:
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' (,):'
		def docomplete(s, e, v, t):
			ss = '%s+%sc' % (s,len(t))
			se = '%s+%sc' % (s,len(v))
			self.text.delete(s, ss)
			self.text.insert(s, v)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] is None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] is not None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart' % INSERT),self.text.index('%s -1c wordend' % INSERT)
			t,f = self.text.get(s,e),0
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz{':
			ac = list(self.autocomptext)
			m = re.match('\\A\\s*[a-z\\{]+\\Z',t)
			if not m:
				ac.extend(self.autocompfuncs)
			for id,ai in self.aibin.ais.items():
				if not id in ac:
					ac.append(id)
				cs = TBL.decompile_string(self.tbl.strings[ai[1]][:-1], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for ns in self.tbl.strings[:228]:
				cs = ns.split('\x00')
				if cs[1] != '*':
					cs = TBL.decompile_string('\x00'.join(cs[:2]), '\x0A\x28\x29\x2C')
				else:
					cs = TBL.decompile_string(cs[0], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('ConstDef', head)
				if not item:
					break
				var = '{%s}' % self.text.get(*item)
				if not var in ac:
					ac.append(var)
				head = item[1]
			ac.sort()
			if m:
				ac = self.autocompfuncs + ac
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,):'
				elif self.complete[0] is not None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r
		return False

	def completed(self) -> None:
		self.completing = False

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)
