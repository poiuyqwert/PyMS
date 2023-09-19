
from .Config import PyTRGConfig
from .Delegates import MainDelegate
from .TRGCodeText import TRGCodeText
from .FindReplaceDialog import FindReplaceDialog
from .CodeColors import CodeColors
from .SettingsUI.SettingsDialog import SettingsDialog

from ..FileFormats.TRG import TRG, Conditions, Actions, BriefingActions, UnitProperties, Parameters
from ..FileFormats import TBL
from ..FileFormats.AIBIN import AIBIN

from ..Utilities.utils import WIN_REG_AVAILABLE, register_registry
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities import IO

from dataclasses import dataclass
import re

LONG_VERSION = 'v%s' % Assets.version('PyTRG')

@dataclass
class Completing:
	initial_text: str
	initial_start: str
	initial_end: str
	options: list[str]
	option_index: int
	current_end: str
	current_text: str

	def next_option(self) -> str:
		self.option_index += 1
		if self.option_index == len(self.options):
			self.option_index = 0
		return self.options[self.option_index]

class PyTRG(MainWindow, MainDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		MainWindow.__init__(self)
		self.guifile = guifile

		self.set_icon('PyTRG')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyTRG', Assets.version('PyTRG'))
		ga.track(GAScreen('PyTRG'))
		setup_trace('PyTRG', self)

		self.config_ = PyTRGConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.trg: TRG.TRG | None = None
		self.file: str | None = None
		self.edited = False
		self.tbl: TBL.TBL
		self.aibin: AIBIN.AIBIN
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
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage stat_txt.tbl and aiscript.bin files', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.trg editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyTRG')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.complete: Completing | None = None
		keywords: dict[str, None] = dict.fromkeys(('Trigger', 'BriefingTrigger', 'Conditions', 'Actions', 'String', 'UnitProperties'))
		functions: dict[str, None] = {}
		for condition in Conditions.definitions_registry:
			functions[condition.name] = None
			for cparameter in condition.parameters:
				if isinstance(cparameter, Parameters.HasKeywords):
					for keyword in cparameter.keywords():
						keywords[keyword] = None
		for action in Actions.definitions_registry + BriefingActions.definitions_registry:
			functions[action.name] = None
			for aparameter in action.parameters:
				if isinstance(aparameter, Parameters.HasKeywords):
					for keyword in aparameter.keywords():
						keywords[keyword] = None
		for property in UnitProperties.properties_definitions:
			functions[property.name] = None
		self.autocomptext = list(keywords.keys())
		self.autocompfuncs: list[str] = list(functions.keys())
		self.autocompfuncs.sort()

		# Text editor
		self.text = TRGCodeText(self, self, self.autocomptext, self.edit, highlights=self.config_.highlights.data, state=DISABLED)
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

		self.config_.windows.main.load(self)

		self.mpqhandler = MPQHandler(self.config_.mpqs)

	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.settings(err=e)
		if self.guifile:
			self.open(file=self.guifile)
		UpdateDialog.check_update(self, 'PyTRG')

	def open_files(self) -> (PyMSError | None):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tbl = TBL.TBL()
			aibin = AIBIN.AIBIN()
			tbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.stat_txt.file_path))
			aibin.load(self.mpqhandler.load_file(self.config_.settings.files.aiscript.file_path))
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
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.codestatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edit(self) -> None:
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
			file = self.config_.last_path.trg.select_open(self)
			if not file:
				return
		trg = TRG.TRG()
		try:
			trg.load(file)
			data = IO.output_to_text(lambda f: trg.decompile(f))
		except PyMSError as e:
			try:
				trg.load(file, TRG.Format.got)
				data = IO.output_to_text(lambda f: trg.decompile(f))
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
		file = self.config_.last_path.txt.select_open(self)
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
			file_path = self.config_.last_path.trg.select_save(self)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			text = self.text.get('1.0', END)
			self.trg.compile(text) # TODO: Warnings
			self.trg.save(file_path)
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
		file = self.config_.last_path.trg.select_save(self, title='Save GOT Compatable TRG')
		if not file:
			return
		try:
			text = self.text.get('1.0', END)
			self.trg.compile(text) # TODO: Warnings
			self.trg.save(file, TRG.Format.got)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.status.set('GOT Compatable TRG Saved Successfully!')

	def export(self) -> None:
		file = self.config_.last_path.txt.select_save(self)
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
			warnings = i.compile(text)
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
			self.findwindow = FindReplaceDialog(self, self.text, self.config_.windows.find_replace)
			self.bind(Key.F3(), self.findwindow.findnext)
		else:
			self.findwindow.make_active() # type: ignore[attr-defined]
			self.findwindow.findentry.focus_set(highlight=True)

	def colors(self) -> None:
		c = CodeColors(self, self.text, self.config_.windows.colors)
		if c.cont:
			self.text.setup(c.cont)
			self.highlights = c.cont

	def settings(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, self.config_, self, err, self.mpqhandler)

	def register_registry(self) -> None:
		try:
			register_registry('PyTRG', 'trg', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyTRG.md')

	def about(self) -> None:
		AboutDialog(self, 'PyTRG', LONG_VERSION, [('FaRTy1billion','For creating TrigPlug and giving me the specs!')])

	def exit(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save(self)
		self.config_.highlights.data = dict(self.text.highlights)
		self.config_.save()
		self.destroy()

	def autocomplete(self) -> bool:
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.text.taboverride = ' (,):'
		def docomplete() -> None:
			if not self.complete:
				return
			complete_text = self.complete.next_option()
			current_end = '%s+%sc' % (self.complete.initial_start, len(self.complete.initial_text))
			complete_end = '%s+%sc' % (self.complete.initial_start, len(complete_text))
			self.text.delete(self.complete.initial_start, current_end)
			self.text.insert(self.complete.initial_start, complete_text)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', self.complete.initial_end, complete_end)
		start = self.text.index('%s -1c wordstart' % INSERT)
		end = self.text.index('%s -1c wordend' % INSERT)
		text = self.text.get(start, end)
		if self.complete is not None:
			if self.complete.initial_start != start or self.complete.initial_end != end or self.complete.initial_text != text:
				self.complete = None
			else:
				docomplete()
				return True
		if text and text[0].lower() in 'abcdefghijklmnopqrstuvwxyz{':
			ac = list(self.autocomptext)
			m = re.match(r'\A\s*[a-z\{]+\Z', text)
			if not m:
				ac.extend(self.autocompfuncs)
			for id,header in self.aibin.script_headers.items():
				if not id in ac:
					ac.append(id)
				cs = TBL.decompile_string(self.tbl.strings[header.string_id][:-1], '\x0A\x28\x29\x2C')
				if not cs in ac:
					ac.append(cs)
			for ns in self.tbl.strings[:228]:
				components = ns.split('\x00')
				if components[1] != '*':
					name = TBL.decompile_string('\x00'.join(components[:2]), '\x0A\x28\x29\x2C')
				else:
					name = TBL.decompile_string(components[0], '\x0A\x28\x29\x2C')
				if not name in ac:
					ac.append(name)
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
				if v and v.lower().startswith(text.lower()):
					matches.append(v)
			if matches:
				self.complete = Completing(text, start, end, [text] + matches, 0, end, text)
				docomplete()
				r = True
			return r
		return False

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		MainWindow.destroy(self)

	# MainDelegate
	def get_trg(self) -> TRG.TRG:
		assert self.trg is not None
		return self.trg
