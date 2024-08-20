
from .Config import PyAIConfig
from .ListboxTooltip import ListboxTooltip
from .EditScriptDialog import EditScriptDialog
from .FindDialog import FindDialog
from .ImportListDialog import ImportListDialog
from .CodeEditDialog import CodeEditDialog
from .FlagEditor import FlagEditor
from .ExternalDefDialog import ExternalDefDialog
from .SettingsUI.SettingsDialog import SettingsDialog
# from .StringEditor import StringEditor
from .Sort import SortBy
from .Delegates import MainDelegate, ActionDelegate, TooltipDelegate
from . import Actions

from ..FileFormats.AIBIN import AIBIN
from ..FileFormats.AIBIN.AICodeHandlers import AISerializeContext, AIDefinitionsHandler, AIParseContext, AILexer
from ..FileFormats.AIBIN.DataContext import DataContext
from ..FileFormats import TBL
from ..FileFormats import DAT
from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag

from ..Utilities.utils import register_registry, WIN_REG_AVAILABLE, binary
from ..Utilities.UIKit import *
from ..Utilities import Assets
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
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
from ..Utilities.ActionManager import ActionManager
from ..Utilities.CodeHandlers.SerializeContext import Formatters
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate

import os

LONG_VERSION = 'v%s' % Assets.version('PyAI')

class PyAI(MainWindow, MainDelegate, ActionDelegate, TooltipDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile
		self.aiscript: str | None = None
		self.bwscript: str | None = None

		MainWindow.__init__(self)
		self.update_title()
		self.set_icon('PyAI')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyAI', Assets.version('PyAI'))
		ga.track(GAScreen('PyAI'))
		setup_trace('PyAI', self)

		self.config_ = PyAIConfig()
		Theme.load_theme(self.config_.theme.value, self)

		# self.stat_txt: str | None = self.config_.stat_txt.file_path
		# self.tbl: TBL.TBL | None = TBL.TBL()
		# try:
		# 	self.tbl.load_file(self.stat_txt)
		# except:
		# 	self.stat_txt = None
		# 	self.tbl = None
		# self.tbledited = False
		self.tbl: TBL.TBL | None = None
		self.unitsdat: DAT.UnitsDAT | None = None
		self.upgradesdat: DAT.UpgradesDAT | None = None
		self.techdat: DAT.TechDAT | None = None
		self.ai: AIBIN.AIBIN | None = None

		self.strings: dict[int, list[str]] = {}
		self.script_list: list[AIBIN.AIScriptHeader] = []
		self.edited = False
	
		self.action_manager = ActionManager()
		self.action_manager.state_updated += self.action_states
		self.imports = list(file_path for file_path in self.config_.imports.data if os.path.exists(file_path))
		self.highlights = self.config_.highlights.data
		self.findhistory: list[str] = []
		self.replacehistory: list[str] = []

		self.sort = StringVar()
		self.sort.set(self.config_.sort.value.value)
		self.sort.trace('w', lambda *_: self.refresh_listbox())
		self.reference = BooleanVar()
		self.reference.set(self.config_.reference.value)

		# Note: Toolbar will bind the shortcuts below
		# TODO: Check for items not bound by `Toolbar`
		self.menu = Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File') # type: ignore[func-returns-value, arg-type]
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

		edit_menu = self.menu.add_cascade('Edit') # type: ignore[func-returns-value, arg-type]
		edit_menu.add_command('Undo', self.action_manager.undo, Ctrl.z, enabled=False, tags='can_undo', bind_shortcut=False, underline='u')
		edit_menu.add_command('Redo', self.action_manager.redo, Ctrl.y, enabled=False, tags='can_redo', bind_shortcut=False, underline='r')
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
		# edit_menu.add_command('Manage TBL File', self.managetbl, Ctrl.t, bind_shortcut=False)
		edit_menu.add_command('Manage Settings', self.settings, Ctrl.u, bind_shortcut=False, underline='m')

		view_menu = self.menu.add_cascade('View') # type: ignore[func-returns-value, arg-type]
		view_menu.add_radiobutton('File Order', self.sort, SortBy.file_order.value, underline='Order')
		view_menu.add_radiobutton('Sort by ID', self.sort, SortBy.id.value, underline='ID')
		view_menu.add_radiobutton('Sort by BroodWar', self.sort, SortBy.bw.value, underline='BroodWar')
		view_menu.add_radiobutton('Sort by Flags', self.sort, SortBy.flags.value, underline='Flags')
		view_menu.add_radiobutton('Sort by Strings', self.sort, SortBy.string.value, underline='Strings')

		help_menu = self.menu.add_cascade('Help') # type: ignore[func-returns-value, arg-type]
		help_menu.add_command('View Help', self.help, Key.F1, bind_shortcut=False, underline='h')
		help_menu.add_separator()
		help_menu.add_command('About PyAI', self.about, underline='a')

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default Scripts', Ctrl.d)
		self.toolbar.add_button(Assets.get_image('openmpq'), self.open_mpq, 'Open MPQ', Ctrl.Alt.o, enabled=MPQ.supported())
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', Ctrl.s, enabled=False, tags='file_open')
		def saveas() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savempq'), self.savempq, 'Save MPQ', Ctrl.Alt.m, enabled=False, tags=('file_open','mpq_available'))
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('undo'), self.action_manager.undo, 'Undo', Ctrl.z, enabled=False, tags='can_undo')
		self.toolbar.add_button(Assets.get_image('redo'), self.action_manager.redo, 'Redo', Ctrl.y, enabled=False, tags='can_redo')
		self.toolbar.add_section()
		self.toolbar.add_radiobutton(Assets.get_image('order'), self.sort, 'order', 'File Order')
		self.toolbar.add_radiobutton(Assets.get_image('idsort'), self.sort, 'idsort', 'Sort by ID')
		self.toolbar.add_radiobutton(Assets.get_image('bwsort'), self.sort, 'bwsort', 'Sory by BroodWar')
		self.toolbar.add_radiobutton(Assets.get_image('flagsort'), self.sort, 'flagsort', 'Sort by Flags')
		self.toolbar.add_radiobutton(Assets.get_image('stringsort'), self.sort, 'stringsort', 'Sort by String')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.bin editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
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
		# self.toolbar.add_button(Assets.get_image('tbl'), self.managetbl, 'Manage TBL file', Ctrl.t)
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage Settings', Ctrl.u)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('openset'), self.openset, 'Open TBL and DAT Settings')
		self.toolbar.add_button(Assets.get_image('saveset'), self.saveset, 'Save TBL and DAT Settings')
		self.toolbar.pack(side=TOP, fill=X)

		self.menu.tag_enabled('mpq_available', MPQ.supported()) # type: ignore[attr-defined]
		self.toolbar.tag_enabled('mpq_available', MPQ.supported()) # type: ignore[attr-defined]

		self.listbox = ScrolledListbox(self, selectmode=EXTENDED, font=Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(WidgetEvent.Listbox.Select(), lambda _: self.action_states())
		self.listbox.bind(ButtonRelease.Click_Right(), self.popup)
		self.listbox.bind(Double.Click_Left(), self.codeedit)
		ListboxTooltip(self.listbox, self)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command('Add Blank Script', self.add, Key.Insert, underline='b') # type: ignore
		self.listmenu.add_command('Remove Scripts', self.remove, Key.Delete, tags='scripts_selected', underline='r') # type: ignore
		self.listmenu.add_separator()
		self.listmenu.add_command('Export Scripts', self.export, Ctrl.Alt.e, tags='scripts_selected') # type: ignore
		self.listmenu.add_command('Import Scripts', self.iimport, Ctrl.Alt.i) # type: ignore
		self.listmenu.add_separator()
		self.listmenu.add_command('Edit AI Script', self.codeedit, Ctrl.e, tags='scripts_selected', underline='a') # type: ignore
		self.listmenu.add_command('Edit Script ID and String', self.edit, Ctrl.i, tags='scripts_selected', underline='s') # type: ignore
		self.listmenu.add_command('Edit Flags', self.editflags, Ctrl.g, tags='scripts_selected', underline='f') # type: ignore

		self.status = StringVar()
		self.status.set('Load your files or create new ones.')
		self.scriptstatus = StringVar()
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.scriptstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.config_.windows.main.load_size(self)

		self.mpqhandler = MPQHandler(self.config_.mpqs)

	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.settings(err=e)
		if self.guifile:
			self.open(aiscript=(None, self.guifile))
		UpdateDialog.check_update(self, 'PyAI')

	def open_files(self) -> PyMSError | None:
		self.mpqhandler.open_mpqs()
		err = None
		try:
			unitsdat = DAT.UnitsDAT()
			upgradesdat = DAT.UpgradesDAT()
			techdat = DAT.TechDAT()
			unitsdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.units.file_path))
			upgradesdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.upgrades.file_path))
			techdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.techdata.file_path))
			tbl = TBL.TBL()
			tbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.stat_txt.file_path))
			# if not self.tbl:
			# 	file = self.config_.last_path.tbl.select_open(self)
			# 	# TODO: We need stat_txt but if it fails to load we present settings but you don't manage it in settings?
			# 	if not file:
			# 		raise PyMSError('Load', 'You must load a stat_txt.tbl file')
			# 	tbl = TBL.TBL()
			# 	tbl.load_file(file)
			# 	self.stat_txt = file
			# 	self.tbl = tbl
		except PyMSError as e:
			err = e
		else:
			self.unitsdat = unitsdat
			self.upgradesdat = upgradesdat
			self.techdat = techdat
			self.tbl = tbl
			# TODO: DAT usage?
			# if self.ai:
			# 	self.ai.unitsdat = unitsdat
			# 	self.ai.upgradesdat = upgradesdat
			# 	self.ai.techdat = techdat
		self.mpqhandler.close_mpqs()
		return err

	# Misc. functions
	def update_title(self) -> None:
		details = 'No Files Loaded'
		if self.aiscript:
			details = f' ({self.aiscript})'
			if self.bwscript:
				details += f' ({self.bwscript})'
		self.title(f'PyAI {LONG_VERSION}{details}')

	def entry_text(self, header: AIBIN.AIScriptHeader) -> str:
		string = f'String {header.string_id}'
		if self.tbl:
			string = TBL.decompile_string(self.tbl.strings[header.string_id])
		if len(string) > 50:
			string = string[:47] + '...'
		return f'{header.id}     {"BW" if header.is_in_bw else "  "}     {binary(header.flags, 3)}     {string}'

	def get_sortby(self) -> SortBy:
		return SortBy(self.sort.get())

	def get_selected_headers(self) -> list[AIBIN.AIScriptHeader]:
		selected = []
		for index in self.listbox.curselection():
			try:
				selected.append(self.script_list[index])
			except:
				pass
		return selected

	def refresh_listbox(self) -> None:
		yview = self.listbox.yview()
		was_selected = self.get_selected_headers()
		self.listbox.delete(0, END)
		if not self.ai:
			return
		self.script_list = self.get_sortby().sort(self.ai.list_scripts(), self.tbl)
		for header in self.script_list:
			self.listbox.insert(END, self.entry_text(header))
			if header in was_selected:
				self.listbox.select_set(END)
		self.listbox.yview_moveto(yview[0])

	# def add_undo(self, type: str, data: Any) -> None:
	# 	max = self.config_.max_undos.value
	# 	if not max:
	# 		return
	# 	if self.redos:
	# 		self.redos = []
	# 		self.toolbar.tag_enabled('can_redo', False)
	# 		self.menu.tag_enabled('can_redo', False) # type: ignore[attr-defined]
	# 	if not self.undos:
	# 		self.toolbar.tag_enabled('can_undo', True)
	# 		self.menu.tag_enabled('can_undo', True) # type: ignore[attr-defined]
	# 	self.undos.append((type, data))
	# 	if len(self.undos) > max:
	# 		del self.undos[0]

	def is_file_open(self) -> bool:
		return not not self.ai

	def has_scripts_selected(self) -> bool:
		return not not self.listbox.curselection()

	def action_states(self) -> None:
		is_file_open = self.is_file_open()
		has_scripts_selected = self.has_scripts_selected()

		self.toolbar.tag_enabled('file_open', is_file_open)
		self.menu.tag_enabled('file_open', is_file_open) # type: ignore[attr-defined]

		self.toolbar.tag_enabled('scripts_selected', has_scripts_selected)
		self.menu.tag_enabled('scripts_selected', has_scripts_selected) # type: ignore[attr-defined]

		self.toolbar.tag_enabled('can_undo', self.action_manager.can_undo())
		self.menu.tag_enabled('can_undo', self.action_manager.can_undo()) # type: ignore[attr-defined]

		self.toolbar.tag_enabled('can_redo', self.action_manager.can_redo())
		self.menu.tag_enabled('can_redo', self.action_manager.can_redo()) # type: ignore[attr-defined]

	def check_saved(self) -> CheckSaved:
		# if self.tbledited:
		# 	save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % self.stat_txt, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		# 	if save != MessageBox.NO:
		# 		if save == MessageBox.CANCEL:
		# 			return CheckSaved.cancelled
		# 		self.tbl.compile(self.stat_txt)
		# 		self.tbledited = False
		if not self.ai or not self.edited:
			return CheckSaved.saved
		aiscript = self.aiscript
		if not aiscript:
			aiscript = 'aiscript.bin'
		bwscript = self.bwscript
		if not bwscript:
			bwscript = 'bwscript.bin'
		save = MessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s' and '%s'?" % (aiscript, bwscript), default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
		if save == MessageBox.NO:
			return CheckSaved.saved
		if save == MessageBox.CANCEL:
			return CheckSaved.cancelled
		if self.aiscript:
			return self.save()
		else:
			return self.saveas()

	# def is_tbl_edited(self) -> bool:
	# 	return self.tbledited

	# def mark_tbl_edited(self, edited: bool = True) -> None:
	# 	self.tbledited = edited

	# def get_stat_txt_path(self) -> str:
	# 	return self.stat_txt

	# def set_stat_txt_path(self, file_path: str) -> None:
	# 	self.stat_txt = file_path

	def popup(self, event: Event) -> None:
		if not self.ai:
			return
		self.listmenu.tag_enabled('scripts_selected', not not self.listbox.curselection()) # type: ignore[attr-defined]
		self.listmenu.post(event.x_root, event.y_root)

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = NORMAL if edited else DISABLED

	def update_script_status(self) -> None:
		if self.ai is None:
			self.scriptstatus.set('')
			return
		# TODO: Calculate sizes
		s = f'aiscript.bin: {len(self.ai._script_headers)} (? B)'
		if self.ai.bw_bin:
			s += f'     bwscript.bin: {len(self.ai.bw_bin._script_headers)} (? B)'
		self.scriptstatus.set(s)

	# Acitions
	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		bwscript = AIBIN.BWBIN()
		self.ai = AIBIN.AIBIN(bwscript)
		self.strings = {}
		self.aiscript = None
		self.bwscript = None
		self.mark_edited(False)
		self.title('aiscript.bin, bwscript.bin')
		self.status.set('Editing new file!')
		self.listbox.delete(0, END)
		self.action_states()
		self.update_script_status()

	def open(self, aiscript: tuple[IO.AnyInputBytes | None, str] | None = None, bwscript: tuple[IO.AnyInputBytes | None, str] | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		aiscript_file: IO.AnyInputBytes | None = None
		aiscript_path: str | None = None
		if aiscript:
			aiscript_file,aiscript_path = aiscript
		else:
			aiscript_path = self.config_.last_path.bin.select_open(self, title='Open aiscript.bin')
			if aiscript_path is None:
				return
		bwscript_file: IO.AnyInputBytes | None = None
		bwscript_path: str | None = None
		if bwscript:
			bwscript_file,bwscript_path = bwscript
		if not bwscript:
			bwscript_path = self.config_.last_path.bin.select_open(self, title='Open bwscript.bin (Cancel to only open aiscript.bin)')
		# warnings = []
		try:
			bw: AIBIN.BWBIN | None = None
			if bwscript_file is not None:
				bw = AIBIN.BWBIN()
				bw.load(bwscript_file)
			elif bwscript_path is not None:
				bw = AIBIN.BWBIN()
				bw.load(bwscript_path)
			ai = AIBIN.AIBIN(bw)
			ai.load(aiscript_file or aiscript_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.ai = ai
		self.strings = {}
		for id,header in self.ai._script_headers.items():
			if not header.string_id in self.strings:
				self.strings[header.string_id] = []
			self.strings[header.string_id].append(id)
		self.aiscript = aiscript_path
		self.bwscript = bwscript_path
		self.mark_edited(False)
		if not bwscript_path:
			bwscript_path = 'bwscript.bin'
		self.title('%s, %s' % (aiscript_path,bwscript_path))
		self.status.set('Load Successful!')
		self.refresh_listbox()
		self.action_states()
		self.update_script_status()
		# if warnings:
		# 	WarningDialog(self, warnings)

	def open_default(self) -> None:
		self.open(aiscript=(None, Assets.mpq_file_path('Scripts','aiscript.bin')), bwscript=(None, Assets.mpq_file_path('Scripts','bwscript.bin')))

	def open_mpq(self) -> None:
		file = self.config_.last_path.mpq.select_open(self)
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
		self.open(aiscript=(ai, 'scripts\\aiscript.bin'), bwscript=(bw, 'scripts\\bwscript.bin'))

	def save(self) -> CheckSaved:
		return self.saveas(ai_path=self.aiscript, bw_path=self.bwscript)

	def saveas(self, ai_path: str | None = None, bw_path: str | None = None) -> CheckSaved:
		if not self.ai:
			return CheckSaved.saved
		if not ai_path:
			ai_path = self.config_.last_path.bin.select_save(self, title='Save aiscript.bin')
			if not ai_path:
				return CheckSaved.cancelled
		if not check_allow_overwrite_internal_file(ai_path):
			return CheckSaved.cancelled
		if self.ai.bw_bin and self.ai.bw_bin._script_headers and not bw_path:
			bw_path = self.config_.last_path.bin.select_save(self, title='Save bwscript.bin (Cancel to save aiscript.bin only)')
		if bw_path and not check_allow_overwrite_internal_file(bw_path):
			return CheckSaved.cancelled
		# if self.tbl and self.tbledited:
		# 	tbl_path = self.config_.last_path.tbl.select_save(self, title="Save stat_txt.tbl (Cancel doesn't stop bin saving)")
		# 	if tbl_path:
		# 		if not check_allow_overwrite_internal_file(tbl_path):
		# 			return CheckSaved.cancelled
		# 		try:
		# 			self.tbl.compile(tbl_path)
		# 		except PyMSError as e:
		# 			ErrorDialog(self, e)
		# 			return CheckSaved.cancelled
		# 		self.stat_txt = tbl_path
		# 		self.tbledited = False
		try:
			self.ai.save(ai_path)
			if self.ai.bw_bin and bw_path:
				self.ai.bw_bin.save(bw_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		self.aiscript = ai_path
		if bw_path is not None:
			self.bwscript = bw_path
		self.mark_edited(False)
		self.status.set('Save Successful!')
		self.update_title()
		return CheckSaved.saved

	def savempq(self) -> None:
		if not self.ai:
			return
		file = self.config_.last_path.mpq.select_save(self)
		if not file:
			return
		not_saved = []
		try:
			ai_bin = self.ai
			ai = IO.output_to_bytes(lambda f: ai_bin.save(f))
			bw: bytes | None = None
			if self.ai.bw_bin:
				bw_bin = self.ai.bw_bin
				bw = IO.output_to_bytes(lambda f: bw_bin.save(f))
			mpq = MPQ.of(file)
			with mpq.open_or_create():
				try:
					mpq.add_data(ai, 'scripts\\aiscript.bin', compression=MPQCompressionFlag.pkware)
				except:
					not_saved.append('scripts\\aiscript.bin')
				if bw:
					try:
						mpq.add_data(bw, 'scripts\\bwscript.bin', compression=MPQCompressionFlag.pkware)
					except:
						not_saved.append('scripts\\bwscript.bin')
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not_saved:
			MessageBox.askquestion(parent=self, title='Save problems', message='%s could not be saved to the MPQ.' % ' and '.join(not_saved), type=MessageBox.OK)

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.ai = None
		self.strings = {}
		self.aiscript = None
		self.bwscript = None
		self.mark_edited(False)
		self.action_manager.clear()
		self.update_title()
		self.status.set('Load your files or create new ones.')
		self.listbox.delete(0, END)
		self.action_states()
		self.update_script_status()

	def register_registry(self, e=None) -> None:
		try:
			register_registry('PyAI', 'bin', 'AI')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyAI.md')

	def about(self) -> None:
		thanks = [
			('bajadulce',"Testing, support, and hosting! I can't thank you enough!"),
			('ashara','Lots of help with beta testing and ideas'),
			('MamiyaOtaru','Found lots of bugs, most importantly ones on Mac and Linux.'),
			('Heinerman','File specs and command information'),
			('modmaster50','Lots of ideas, testing, and support, thanks a lot!')
		]
		AboutDialog(self, 'PyAI', LONG_VERSION, thanks)

	def exit(self, e=None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		# self.config_.stat_txt.file_path = self.stat_txt
		self.config_.highlights.data = self.highlights
		self.config_.reference.value = self.reference.get()
		self.config_.imports.data = self.imports
		self.config_.save()
		self.destroy()

	def select_all(self):
		self.listbox.select_set(0, END)

	def add(self) -> None:
		if not self.ai:
			return
		s = 2 + self.ai.calculate_size()
		if s > 65535:
			ErrorDialog(self, PyMSError('Adding',"There is not enough room in your aiscript.bin to add a new script"))
			return
		e = EditScriptDialog(self, title='Adding New AI Script')
		id = e.id.get()
		if not id:
			return
		header = AIBIN.AIScriptHeader()
		header.id = id
		header.string_id = int(e.string.get())
		header.flags = e.flags
		action = Actions.AddScriptAction(self, header, None)
		self.action_manager.add_action(action)

	def remove(self) -> None:
		if not self.ai:
			return
		scripts = []
		for header in self.get_selected_headers():
			entry_point = self.ai.get_entry_point(header.id)
			if not entry_point:
				continue
			scripts.append((header, entry_point))
		action = Actions.RemoveScriptsAction(self, scripts)
		self.action_manager.add_action(action)

	def find(self) -> None:
		FindDialog(self)

	def export(self) -> None:
		if not self.ai:
			return
		headers = self.get_selected_headers()
		if not headers:
			return
		export_path = self.config_.last_path.txt.ai.select_save(self)
		if not export_path:
			return
		script_ids = list(header.id for header in headers)
		try:
			serialize_context = self.get_serialize_context()
			self.ai.decompile(export_path, serialize_context, script_ids)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		# if external:
		# 	MessageBox.askquestion(parent=self, title='External References', message='One or more of the scripts you are exporting references an external block, so the scripts that are referenced have been exported as well:\n    %s' % '\n    '.join(external), type=MessageBox.OK)

	def iimport(self, iimport_path: str | None = None, c: bool = True, parent: Misc | None = None) -> None:
		if not self.ai:
			return
		if parent is None:
			parent = self
		if not iimport_path:
			iimport_path = self.config_.last_path.txt.ai.select_open(self)
		if not iimport_path:
			return
		parse_context = self.get_parse_context(iimport_path)
		self.ai.compile(parse_context)
		if parse_context.warnings:
			WarningDialog(parent, parse_context.warnings, True)
		self.update_script_status()
		self.refresh_listbox()
		self.mark_edited()

	def listimport(self) -> None:
		ImportListDialog(self)

	def codeedit(self, event: Event | None = None) -> None:
		headers = self.get_selected_headers()
		CodeEditDialog(self, self, self.config_, list(header.id for header in headers))

	def edit(self):
		headers = self.get_selected_headers()
		if not headers:
			return
		header = headers[0]
		entry_point = self.ai.get_entry_point(header.id)
		if not entry_point:
			return
		e = EditScriptDialog(self, header.id, header.flags, header.string_id, initial=header.id)
		if not e.id.get():
			return
		action = Actions.EditScriptAction(self, header, entry_point, e.id.get(), e.flags, int(e.string.get()))
		self.action_manager.add_action(action)

	def editflags(self):
		headers = self.get_selected_headers()
		if not headers:
			return
		header = headers[0]
		f = FlagEditor(self, header.flags)
		if f.flags is None:
			return
		action = Actions.EditFlagsAction(self, header, f.flags)
		self.action_manager.add_action(action)

	def extdef(self) -> None:
		ExternalDefDialog(self, self.config_)

	# def managetbl(self) -> None:
	# 	headers = self.get_selected_headers()
	# 	if not headers:
	# 		return
	# 	StringEditor(self, index=headers[0].id)

	def settings(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, self.config_, self, err, self.mpqhandler)

	def openset(self) -> None:
		file = self.config_.last_path.txt.settings.select_open(self)
		if not file:
			return
		try:
			files = open(file,'r').readlines()
		except:
			MessageBox.showerror('Invalid File',"Could not open '%s'." % file)

		tbl = TBL.TBL()
		try:
			tbl.load_file(files[0] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.tbl = tbl
		
		unitsdat = DAT.UnitsDAT()
		try:
			unitsdat.load_file(files[1] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.unitsdat = unitsdat
		
		upgradesdat = DAT.UpgradesDAT()
		try:
			upgradesdat.load_file(files[2] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.upgradesdat = upgradesdat

		techdat = DAT.TechDAT()
		try:
			techdat.load_file(files[3] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.techdat = techdat

	def saveset(self) -> None:
		file = self.config_.last_path.txt.settings.select_save(self)
		if file:
			try:
				set = open(file,'w')
			except:
				MessageBox.showerror('Invalid File',"Could not save to '%s'." % file)
			set.write(('%s\n%s\n%s\n%s' % (
					self.config_.settings.files.stat_txt.file_path,
					self.config_.settings.files.dat.units.file_path,
					self.config_.settings.files.dat.upgrades,
					self.config_.settings.files.dat.techdata
				)).replace(Assets.base_dir, '%(path)s'))
			set.close()

	# ActionsDelegate
	def get_ai_bin(self) -> AIBIN.AIBIN:
		assert self.ai is not None
		return self.ai

	def refresh_scripts(self, select_script_ids: list[str] | None = None) -> None:
		self.refresh_listbox()
		if select_script_ids is not None:
			self.listbox.select_clear(0, END)
			for index,header in enumerate(self.script_list):
				if not header.id in select_script_ids:
					continue
				self.listbox.select_set(index)

	# Main Delegate
	def get_highlights(self) -> Any:
		return self.highlights

	def set_highlights(self, highlights: Any) -> None:
		self.highlights = highlights

	def get_tbl(self) -> TBL.TBL:
		assert self.tbl is not None
		return self.tbl

	def get_upgrades_dat(self) -> DAT.UpgradesDAT:
		assert self.upgradesdat is not None
		return self.upgradesdat

	def get_tech_dat(self) -> DAT.TechDAT:
		assert self.techdat is not None
		return self.techdat

	def save_code(self, code: str, parent: AnyWindow) -> bool:
		if not self.ai:
			return False
		parse_context = self.get_parse_context(code)
		try:
			self.ai.compile(parse_context)
		except PyMSError as e:
			ErrorDialog(parent, e)
			return False
		if parse_context.warnings:
			WarningDialog(parent, parse_context.warnings, True)
		self.update_script_status()
		self.refresh_listbox()
		self.mark_edited()
		return True

	def get_export_references(self) -> bool:
		return self.reference.get()

	def _get_data_context(self) -> DataContext:
		return DataContext(
			stattxt_tbl = self.tbl,
			unitnames_tbl = None,
			units_dat = self.unitsdat,
			upgrades_dat = self.upgradesdat,
			techdata_dat = self.techdat
		)

	def _get_definitions_handler(self) -> AIDefinitionsHandler:
		# TODO: Load definitions files
		defs = AIDefinitionsHandler()
		for extdef in self.config_.extdefs.data:
			defs.parse(extdef)
		return defs

	def _get_formatters(self) -> Formatters:
		return Formatters()

	def get_serialize_context(self) -> AISerializeContext:
		definitions = self._get_definitions_handler()
		formatters = self._get_formatters()
		data_context = self._get_data_context()
		return AISerializeContext(definitions, formatters, data_context)

	def get_parse_context(self, input: IO.AnyInputText) -> AIParseContext:
		definitions = self._get_definitions_handler()
		data_context = self._get_data_context()
		with IO.InputText(input) as f:
			code = f.read()
		lexer = AILexer(code)
		return AIParseContext(lexer, definitions, data_context)

	# Tooltip Delegate
	def get_list_entry(self, index: int) -> AIBIN.AIScriptHeader:
		return self.script_list[index]
