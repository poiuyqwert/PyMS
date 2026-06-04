
from .Config import PyAIConfig
from .ListboxTooltip import ListboxTooltip
from .EditScriptDialog import EditScriptDialog
from .FindScriptDialog import FindScriptDialog
from .ImportListDialog import ImportListDialog
from .CodeEditDialog import CodeEditDialog
from .FlagEditor import FlagEditor
from .ExternalDefDialog import ExternalDefDialog
from .SettingsUI.SettingsDialog import SettingsDialog
# from .StringEditor import StringEditor
from .DecompilingFormatDialog import DecompilingFormatDialog
from .Sort import SortBy
from .Delegates import MainDelegate, ActionDelegate, TooltipDelegate
from . import Actions
from .AddedPluginsDialog import AddedPluginsDialog
from .FixIssuesUI.FixIssuesDialog import FixIssuesDialog

from ..FileFormats.AIBIN import AIBIN
from ..FileFormats.AIBIN.CodeHandlers import AISerializeContext, AIParseContext, AIParseSettings, AILexer, AIDefsSourceCodeHandler, DataContext
from ..FileFormats import TBL
from ..FileFormats import DAT
from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag

from ..Utilities.utils import binary
from ..Utilities import registry
from ..Utilities import UIKit as UI
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
from ..Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate
from ..Utilities.SponsorDialog import SponsorDialog

import io, os

from typing import IO as BuiltinIO

LONG_VERSION = 'v' + Assets.version('PyAI')

class PyAI(UI.MainWindow, MainDelegate, ActionDelegate, TooltipDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile
		self.aiscript: str | None = None
		self.bwscript: str | None = None

		UI.MainWindow.__init__(self)
		self.update_title()
		self.set_icon('PyAI')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyAI', Assets.version('PyAI'))
		ga.track(GAScreen('PyAI'))
		setup_trace('PyAI', self)

		self.config_ = PyAIConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)

		self.data_context = DataContext()
		self.ai: AIBIN.AIBIN | None = None

		self.script_list: list[AIBIN.AIScript] = []
		self.edited = False

		self.action_manager = ActionManager()
		self.action_manager.state_updated += self.action_states
		self.findhistory: list[str] = []
		self.replacehistory: list[str] = []

		self.sort = UI.StringVar()
		self.sort.set(self.config_.sort.value.value)
		self.sort.trace_add('write', lambda *_: self.refresh_listbox())
		# self.reference = BooleanVar()
		# self.reference.set(self.config_.reference.value)

		# Note: Toolbar will bind the shortcuts below
		# TODO: Check for items not bound by `Toolbar`
		self.menu = UI.Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File') # type: ignore[func-returns-value, arg-type]
		file_menu.add_command('New', self.new, UI.Ctrl.n, bind_shortcut=False)
		file_menu.add_command('Open', self.open, UI.Ctrl.o, bind_shortcut=False)
		file_menu.add_command('Open Default Scripts', self.open_default, UI.Ctrl.d, bind_shortcut=False)
		file_menu.add_command('Open MPQ', self.open_mpq, UI.Ctrl.Alt.o, enabled=MPQ.supported(), bind_shortcut=False, underline='m')
		def do_save() -> None:
			self.save()
		file_menu.add_command('Save', do_save, UI.Ctrl.s, enabled=False, tags='file_open', bind_shortcut=False)
		def do_saveas() -> None:
			self.saveas()
		file_menu.add_command('Save As...', do_saveas, UI.Ctrl.Alt.a, enabled=False, tags='file_open', bind_shortcut=False, underline='As')
		file_menu.add_command('Save MPQ', self.savempq, UI.Ctrl.Alt.m, enabled=MPQ.supported(), tags=('file_open','mpq_available'), bind_shortcut=False, underline='a')
		file_menu.add_command('Close', self.close, UI.Ctrl.w, enabled=False, tags='file_open', bind_shortcut=False, underline='c')
		file_menu.add_separator()
		file_menu.add_command('Set as default *.bin editor (Windows Only)', self.register_registry, enabled=registry.IS_AVAILABLE, underline='t')
		file_menu.add_separator()
		file_menu.add_command('Exit', self.exit, UI.Shortcut.Exit, underline='e')

		edit_menu = self.menu.add_cascade('Edit') # type: ignore[func-returns-value, arg-type]
		edit_menu.add_command('Undo', self.action_manager.undo, UI.Ctrl.z, enabled=False, tags='can_undo', bind_shortcut=False, underline='u')
		edit_menu.add_command('Redo', self.action_manager.redo, UI.Ctrl.y, enabled=False, tags='can_redo', bind_shortcut=False, underline='r')
		edit_menu.add_separator()
		edit_menu.add_command('Select All', self.select_all, UI.Ctrl.a, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Add Blank Script', self.add, UI.Key.Insert, enabled=False, tags='file_open', bind_shortcut=False, underline='b')
		edit_menu.add_command('Remove Scripts', self.remove, UI.Key.Delete, enabled=False, tags='scripts_selected', bind_shortcut=False, underline='v')
		edit_menu.add_command('Find Scripts', self.find, UI.Ctrl.f, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_separator()
		edit_menu.add_command('Export Scripts', self.export, UI.Ctrl.Alt.e, enabled=False, tags='scripts_selected', bind_shortcut=False)
		edit_menu.add_command('Import Scripts', self.iimport, UI.Ctrl.Alt.i, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Import a List of Files', self.listimport, UI.Ctrl.l, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_separator()
		# edit_menu.add_checkbutton('Print Reference when Decompiling', self.reference, underline='p')
		edit_menu.add_command('Decompiling Format', self.decompiling_format)
		edit_menu.add_separator()
		edit_menu.add_command('Edit AI Script', self.codeedit, UI.Ctrl.e, enabled=False, tags='file_open', bind_shortcut=False)
		edit_menu.add_command('Edit AI ID, String, and Extra Info.', self.edit, UI.Ctrl.i, enabled=False, tags='scripts_selected', bind_shortcut=False, underline='ID')
		edit_menu.add_command('Edit Flags', self.editflags, UI.Ctrl.g, enabled=False, tags='scripts_selected', bind_shortcut=False)
		edit_menu.add_separator()
		edit_menu.add_command('Manage External Definition Files', self.extdef, UI.Ctrl.x, bind_shortcut=False)
		# edit_menu.add_command('Manage TBL File', self.managetbl, Ctrl.t, bind_shortcut=False)
		edit_menu.add_command('Manage Settings', self.settings, UI.Ctrl.u, bind_shortcut=False, underline='m')

		view_menu = self.menu.add_cascade('View') # type: ignore[func-returns-value, arg-type]
		view_menu.add_radiobutton('File Order', self.sort, SortBy.file_order.value, underline='Order')
		view_menu.add_radiobutton('Sort by ID', self.sort, SortBy.id.value, underline='ID')
		view_menu.add_radiobutton('Sort by BroodWar', self.sort, SortBy.bw.value, underline='BroodWar')
		view_menu.add_radiobutton('Sort by Flags', self.sort, SortBy.flags.value, underline='Flags')
		view_menu.add_radiobutton('Sort by Strings', self.sort, SortBy.string.value, underline='Strings')

		help_menu = self.menu.add_cascade('Help') # type: ignore[func-returns-value, arg-type]
		help_menu.add_command('View Help', self.help, UI.Key.F1, bind_shortcut=False, underline='h')
		help_menu.add_separator()
		help_menu.add_command('About PyAI', self.about, underline='a')

		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o)
		self.toolbar.add_button(Assets.get_image('opendefault'), self.open_default, 'Open Default Scripts', UI.Ctrl.d)
		self.toolbar.add_button(Assets.get_image('openmpq'), self.open_mpq, 'Open MPQ', UI.Ctrl.Alt.o, enabled=MPQ.supported())
		def save() -> None:
			self.save()
		self.toolbar.add_button(Assets.get_image('save'), save, 'Save', UI.Ctrl.s, enabled=False, tags='file_open')
		def saveas() -> None:
			self.saveas()
		self.toolbar.add_button(Assets.get_image('saveas'), saveas, 'Save As', UI.Ctrl.Alt.a, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('savempq'), self.savempq, 'Save MPQ', UI.Ctrl.Alt.m, enabled=False, tags=('file_open','mpq_available'))
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('undo'), self.action_manager.undo, 'Undo', UI.Ctrl.z, enabled=False, tags='can_undo')
		self.toolbar.add_button(Assets.get_image('redo'), self.action_manager.redo, 'Redo', UI.Ctrl.y, enabled=False, tags='can_redo')
		self.toolbar.add_section()
		self.toolbar.add_radiobutton(Assets.get_image('order'), self.sort, 'order', 'File Order')
		self.toolbar.add_radiobutton(Assets.get_image('idsort'), self.sort, 'idsort', 'Sort by ID')
		self.toolbar.add_radiobutton(Assets.get_image('bwsort'), self.sort, 'bwsort', 'Sort by BroodWar')
		self.toolbar.add_radiobutton(Assets.get_image('flagsort'), self.sort, 'flagsort', 'Sort by Flags')
		self.toolbar.add_radiobutton(Assets.get_image('stringsort'), self.sort, 'stringsort', 'Sort by String')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.bin editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', UI.Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyAI')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit)

		self.toolbar.add_row()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add Blank Script', UI.Key.Insert, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Scripts', UI.Key.Delete, enabled=False, tags='scripts_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find Scripts', UI.Ctrl.f, enabled=False, tags='file_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Scripts', UI.Ctrl.Alt.e, enabled=False, tags='scripts_selected')
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Scripts', UI.Ctrl.Alt.i, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('listimport'), self.listimport, 'Import a List of Files', UI.Ctrl.l, enabled=False, tags='file_open')
		self.toolbar.add_section()
		# self.toolbar.add_checkbutton(Assets.get_image('reference'), self.reference, 'Print Reference when Decompiling')
		self.toolbar.add_button(Assets.get_image('debug'), self.decompiling_format, 'Decompiling Format')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('codeedit'), self.codeedit, 'Edit AI Script', UI.Ctrl.e, enabled=False, tags='file_open')
		self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit AI ID, String, and Extra Info.', UI.Ctrl.i, enabled=False, tags='scripts_selected')
		self.toolbar.add_button(Assets.get_image('flags'), self.editflags, 'Edit Flags', UI.Ctrl.g, enabled=False, tags='scripts_selected')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('extdef'), self.extdef, 'Manage External Definition Files', UI.Ctrl.x)
		# self.toolbar.add_button(Assets.get_image('tbl'), self.managetbl, 'Manage TBL file', Ctrl.t)
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage Settings', UI.Ctrl.u)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('openset'), self.openset, 'Open TBL and DAT Settings')
		self.toolbar.add_button(Assets.get_image('saveset'), self.saveset, 'Save TBL and DAT Settings')
		self.toolbar.pack(side=UI.TOP, fill=UI.X)

		self.menu.tag_enabled('mpq_available', MPQ.supported()) # type: ignore[attr-defined]
		self.toolbar.tag_enabled('mpq_available', MPQ.supported()) # type: ignore[attr-defined]

		self.listbox = UI.ScrolledListbox(self, selectmode=UI.EXTENDED, font=UI.Font.fixed(), width=1, height=1)
		self.listbox.pack(fill=UI.BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), lambda _: self.action_states())
		self.listbox.bind(UI.ButtonRelease.Click_Right(), self.popup)
		self.listbox.bind(UI.Double.Click_Left(), self.codeedit)
		ListboxTooltip(self.listbox, delegate=self)

		self.listmenu = UI.Menu(self, tearoff=0)
		self.listmenu.add_command('Add Blank Script', self.add, UI.Key.Insert, underline='b') # type: ignore
		self.listmenu.add_command('Remove Scripts', self.remove, UI.Key.Delete, tags='scripts_selected', underline='r') # type: ignore
		self.listmenu.add_separator()
		self.listmenu.add_command('Export Scripts', self.export, UI.Ctrl.Alt.e, tags='scripts_selected') # type: ignore
		self.listmenu.add_command('Import Scripts', self.iimport, UI.Ctrl.Alt.i) # type: ignore
		self.listmenu.add_separator()
		self.listmenu.add_command('Edit AI Script', self.codeedit, UI.Ctrl.e, tags='scripts_selected', underline='a') # type: ignore
		self.listmenu.add_command('Edit Script ID and String', self.edit, UI.Ctrl.i, tags='scripts_selected', underline='s') # type: ignore
		self.listmenu.add_command('Edit Flags', self.editflags, UI.Ctrl.g, tags='scripts_selected', underline='f') # type: ignore

		self.status = UI.StringVar()
		self.status.set('Load your files or create new ones.')
		self.scriptstatus = UI.StringVar()
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.scriptstatus, weight=1)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

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
			# TODO: Files are not "required"?
			unitsdat = DAT.UnitsDAT()
			upgradesdat = DAT.UpgradesDAT()
			techdat = DAT.TechDAT()
			unitsdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.units.file_path))
			upgradesdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.upgrades.file_path))
			techdat.load_file(self.mpqhandler.load_file(self.config_.settings.files.dat.techdata.file_path))
			tbl = TBL.TBL()
			tbl.load_file(self.mpqhandler.load_file(self.config_.settings.files.stat_txt.file_path))
		except PyMSError as e:
			err = e
		else:
			self.data_context.set_stattxt_tbl(tbl)
			self.data_context.set_units_dat(unitsdat)
			self.data_context.set_upgrades_dat(upgradesdat)
			self.data_context.set_techdata_dat(techdat)
		self.mpqhandler.close_mpqs()
		return err

	# Misc. functions
	def update_title(self) -> None:
		if self.aiscript:
			details = f'{self.aiscript}'
			if self.bwscript:
				details += f', {self.bwscript}'
		else:
			details = 'No Files Loaded'
		self.title(f'PyAI {LONG_VERSION} ({details})')

	def entry_text(self, script: AIBIN.AIScript) -> str:
		string = f'String {script.string_id}'
		if (tbl_string := self.data_context.stattxt_string(script.string_id)):
			string = tbl_string
		if len(string) > 50:
			string = string[:47] + '...'
		return f'{script.id}     {"BW" if script.in_bwscript else "  "}     {binary(script.flags, 3)}     {string}'

	def get_sortby(self) -> SortBy:
		return SortBy(self.sort.get())

	def get_selected_scripts(self) -> list[AIBIN.AIScript]:
		selected: list[AIBIN.AIScript] = []
		for index in self.listbox.curselection():
			selected.append(self.script_list[index])
		return selected

	def refresh_listbox(self) -> None:
		yview = self.listbox.yview()
		was_selected = self.get_selected_scripts()
		self.listbox.delete(0, UI.END)
		if not self.ai:
			return
		self.script_list = self.get_sortby().sort(self.ai.list_scripts(), self.data_context.stattxt_tbl)
		for header in self.script_list:
			self.listbox.insert(UI.END, self.entry_text(header))
			if header in was_selected:
				self.listbox.select_set(UI.END)
		self.listbox.yview_moveto(yview[0])

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
		if not self.ai or not self.edited:
			return CheckSaved.saved
		aiscript = self.aiscript
		if not aiscript:
			aiscript = 'aiscript.bin'
		bwscript = self.bwscript
		if not bwscript:
			bwscript = 'bwscript.bin'
		save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{aiscript}' and '{bwscript}'?", default=UI.MessageBox.YES)
		if save is None:
			return CheckSaved.cancelled
		if not save:
			return CheckSaved.saved
		if self.aiscript:
			return self.save()
		return self.saveas()

	def popup(self, event: UI.Event) -> None:
		if not self.ai:
			return
		self.listmenu.tag_enabled('scripts_selected', not not self.listbox.curselection()) # type: ignore[attr-defined]
		self.listmenu.post(event.x_root, event.y_root)

	def mark_edited(self, edited: bool = True) -> None:
		self.edited = edited
		self.editstatus['state'] = UI.NORMAL if edited else UI.DISABLED

	def update_script_status(self) -> None:
		if self.ai is None:
			self.scriptstatus.set('')
			return
		ai_count,bw_count = self.ai.count_scripts()
		ai_size,bw_size = self.ai.calculate_sizes()
		s = f'aiscript.bin: {ai_count} ({ai_size} B)     bwscript.bin: {bw_count} ({bw_size} B)'
		if self.ai.active_plugins:
			active_plugins = ', '.join(sorted(self.ai.active_plugins))
			s = f'Plugins Required: {active_plugins}     {s}'
		self.scriptstatus.set(s)

	# Acitions
	def new(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.ai = AIBIN.AIBIN()
		self.aiscript = 'aiscript.bin'
		self.bwscript = 'bwscript.bin'
		self.mark_edited(False)
		self.update_title()
		self.status.set('Editing new file!')
		self.listbox.delete(0, UI.END)
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
		try:
			ai = AIBIN.AIBIN()
			issues = ai.load(aiscript_file or aiscript_path, bwscript_file or bwscript_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		edited = False
		if issues:
			if FixIssuesDialog(self, aibin=ai, issues=issues, delegate=self, config=self.config_).cancelled:
				return
			edited = True
		if ai.active_plugins:
			active_plugins = ', '.join(sorted(ai.active_plugins))
			self.config_.dont_warn.plugins.present(self, message=f'These files use features that require these plugins: {active_plugins}')
		self.ai = ai
		self.aiscript = aiscript_path
		self.bwscript = bwscript_path
		self.mark_edited(edited)
		self.update_title()
		self.status.set('Load Successful!')
		self.refresh_listbox()
		self.action_states()
		self.update_script_status()

	def open_default(self) -> None:
		self.open(aiscript=(None, Assets.mpq_file_path('Scripts','aiscript.bin')), bwscript=(None, Assets.mpq_file_path('Scripts','bwscript.bin')))

	def open_mpq(self) -> None:
		file = self.config_.last_path.mpq.select_open(self)
		if not file:
			return
		mpq = MPQ.of(file)
		try:
			mpq_ctx = mpq.open()
		except Exception:
			ErrorDialog(self, PyMSError('Open', f'Could not open MPQ "{file}"'))
			return
		with mpq_ctx:
			ai = mpq.read_file('scripts\\aiscript.bin')
			bw = None
			try:
				bw = mpq.read_file('scripts\\bwscript.bin')
			except Exception:
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
		if self.ai.has_bwscripts() and not bw_path:
			bw_path = self.config_.last_path.bin.select_save(self, title='Save bwscript.bin (Cancel to save aiscript.bin only)')
		if bw_path and not check_allow_overwrite_internal_file(bw_path):
			return CheckSaved.cancelled
		try:
			self.ai.save(ai_path, bw_path)
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
			ai_bytes = io.BytesIO()
			bw_bytes: io.BytesIO | None = None
			if self.ai.has_bwscripts():
				bw_bytes = io.BytesIO()
			ai_bin.save(ai_bytes, bw_bytes)
			mpq = MPQ.of(file)
			with mpq.open_or_create():
				try:
					mpq.add_data(ai_bytes.getvalue(), 'scripts\\aiscript.bin', compression=MPQCompressionFlag.pkware)
				except Exception:
					not_saved.append('scripts\\aiscript.bin')
				if bw_bytes:
					try:
						mpq.add_data(bw_bytes.getvalue(), 'scripts\\bwscript.bin', compression=MPQCompressionFlag.pkware)
					except Exception:
						not_saved.append('scripts\\bwscript.bin')
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not_saved:
			UI.MessageBox.showinfo(parent=self, title='Save problems', message=f'{" and ".join(not_saved)} could not be saved to the MPQ.')

	def close(self) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.ai = None
		self.aiscript = None
		self.bwscript = None
		self.mark_edited(False)
		self.action_manager.clear()
		self.update_title()
		self.status.set('Load your files or create new ones.')
		self.listbox.delete(0, UI.END)
		self.action_states()
		self.update_script_status()

	def register_registry(self, _event: UI.Event | None = None) -> None:
		try:
			registry.register('PyAI', 'bin', 'AI')
		except PyMSError as err:
			ErrorDialog(self, err)

	def help(self, _event: UI.Event | None = None) -> None:
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

	def sponsor(self) -> None:
		SponsorDialog(self)

	def exit(self, _event: UI.Event | None = None) -> None:
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		# self.config_.reference.value = self.reference.get()
		self.config_.save()
		self.destroy()

	def select_all(self) -> None:
		self.listbox.select_set(0, UI.END)

	def add(self) -> None:
		if not self.ai:
			return
		# TODO: Fix size calcs
		s = 2 + self.ai.calculate_sizes()[0]
		# TODO: Expand file?
		if s > 65535:
			ErrorDialog(self, PyMSError('Adding', "There is not enough room in your aiscript.bin to add a new script"))
			return
		dialog = EditScriptDialog(self, delegate=self, config=self.config_.windows.script_edit, title='Adding New AI Script')
		script_id = dialog.script_id.get()
		if not script_id:
			return
		string_text = dialog.string.get().strip()
		if not string_text:
			string_id = 0
		else:
			try:
				string_id = int(string_text)
			except ValueError:
				ErrorDialog(self, PyMSError('Adding', f"Invalid string ID '{string_text}' (must be a number)"))
				return
		# TODO: In bwscript?
		script = AIBIN.AIScript(script_id, dialog.flags, string_id, AIBIN.AIScript.blank_entry_point(), False)
		action = Actions.AddScriptAction(self, script, None)
		self.action_manager.add_action(action)

	def remove(self) -> None:
		if not self.ai:
			return
		action = Actions.RemoveScriptsAction(self, self.get_selected_scripts())
		self.action_manager.add_action(action)

	def find(self) -> None:
		FindScriptDialog(self, self.config_.windows.find.script, self)

	def export(self) -> None:
		if not self.ai:
			return
		headers = self.get_selected_scripts()
		if not headers:
			return
		export_path = self.config_.last_path.txt.ai.select_save(self)
		if not export_path:
			return
		script_ids = list(header.id for header in headers)
		try:
			with IO.OutputTextFile(export_path) as output:
				serialize_context = self.get_serialize_context(output)
				self.ai.decompile(serialize_context, script_ids)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if serialize_context.strategy.external_headers:
			UI.MessageBox.showinfo(parent=self, title='External References', message='One or more of the scripts you are exporting references an external block, so the scripts that are referenced have been exported as well:\n    %s' % '\n    '.join(script.get_name() for script in serialize_context.strategy.external_headers))

	def iimport(self, import_paths: list[str] | None = None,  parent: UI.AnyWindow | None = None) -> None:
		if not self.ai:
			return
		if parent is None:
			parent = self
		if not import_paths:
			import_path = self.config_.last_path.txt.ai.select_open(self)
			if not import_path:
				return
			import_paths = [import_path]
		for import_path in import_paths:
			if not self.save_code(import_path, parent):
				return

	def listimport(self) -> None:
		ImportListDialog(self, self, self.config_)

	def codeedit(self, _event: UI.Event | None = None) -> None:
		headers = self.get_selected_scripts()
		CodeEditDialog(self, self, self.config_, list(header.id for header in headers))

	def edit(self) -> None:
		scripts = self.get_selected_scripts()
		if not scripts:
			return
		script = scripts[0]
		dialog = EditScriptDialog(self, delegate=self, config=self.config_.windows.script_edit, script_id=script.id, flags=script.flags, string_index=script.string_id, initial=script.id)
		if not dialog.script_id.get():
			return
		action = Actions.EditScriptAction(self, script, new_id=dialog.script_id.get(), new_flags=dialog.flags, new_string_id=int(dialog.string.get()))
		self.action_manager.add_action(action)

	def editflags(self) -> None:
		headers = self.get_selected_scripts()
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

	def decompiling_format(self) -> None:
		DecompilingFormatDialog(self, self.config_.code.decomp_format)

	# def managetbl(self) -> None:
	# 	headers = self.get_selected_scripts()
	# 	if not headers:
	# 		return
	# 	StringEditor(self, index=headers[0].id)

	def settings(self, err: PyMSError | None = None) -> None:
		SettingsDialog(self, config=self.config_, delegate=self, err=err, mpq_handler=self.mpqhandler)

	def openset(self) -> None:
		file = self.config_.last_path.txt.settings.select_open(self)
		if not file:
			return
		try:
			with open(file, 'r', encoding='utf-8') as settings:
				files = settings.read().splitlines()
		except Exception:
			UI.MessageBox.showerror('Invalid File', f"Could not open '{file}'.")
			return

		if len(files) < 4:
			UI.MessageBox.showerror('Invalid File', f"'{file}' is not a valid settings file.")
			return

		tbl = TBL.TBL()
		try:
			tbl.load_file(files[0] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return

		unitsdat = DAT.UnitsDAT()
		try:
			unitsdat.load_file(files[1] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return

		upgradesdat = DAT.UpgradesDAT()
		try:
			upgradesdat.load_file(files[2] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return

		techdat = DAT.TechDAT()
		try:
			techdat.load_file(files[3] % {'path': Assets.base_dir})
		except PyMSError as e:
			ErrorDialog(self, e)
			return

		self.data_context.set_stattxt_tbl(tbl)
		self.data_context.set_units_dat(unitsdat)
		self.data_context.set_upgrades_dat(upgradesdat)
		self.data_context.set_techdata_dat(techdat)

	def saveset(self) -> None:
		file = self.config_.last_path.txt.settings.select_save(self)
		if file:
			try:
				with open(file, 'w', encoding='utf-8') as settings:
					settings.write('\n'.join((
						self.config_.settings.files.stat_txt.file_path or '',
						self.config_.settings.files.dat.units.file_path or '',
						self.config_.settings.files.dat.upgrades.file_path or '',
						self.config_.settings.files.dat.techdata.file_path or '',
					)).replace(Assets.base_dir, '%(path)s'))
			except Exception:
				UI.MessageBox.showerror('Invalid File', f"Could not save to '{file}'.")

	# ActionsDelegate
	def get_ai_bin(self) -> AIBIN.AIBIN:
		assert self.ai is not None
		return self.ai

	def refresh_scripts(self, select_script_ids: list[str] | None = None) -> None:
		self.refresh_listbox()
		if select_script_ids is not None:
			self.listbox.select_clear(0, UI.END)
			for index,header in enumerate(self.script_list):
				if not header.id in select_script_ids:
					continue
				self.listbox.select_set(index)

	# Main Delegate
	def get_data_context(self) -> DataContext:
		return self.data_context

	def save_code(self, code_or_path: str, parent: UI.AnyWindow) -> bool:
		if not self.ai:
			return False
		parse_context = self.get_parse_context(code_or_path)
		try:
			scripts = AIBIN.AIBIN.compile(parse_context)
			new_ai_size, new_bw_size = self.ai.can_add_scripts(scripts)
			if new_ai_size is not None:
				ai_size, _ = self.ai.calculate_sizes()
				if self.ai.expanded:
					raise PyMSError('Parse', f"There is not enough room in your aiscript.bin to compile these changes. The current file is {ai_size}B out of the max {self.ai.max_size()}B, these changes would make the file {new_ai_size}B.")
				else:
					if UI.MessageBox.askyesno(parent=self, title='Expand', message="There is not enough room in your aiscript.bin to compile these changes, would you like to expand your aiscript.bin? If you don't know what this is you should google 'AISE Plugin' before saying Yes") == UI.NO:
						return False
					self.ai.expand()
			if new_bw_size is not None and new_bw_size > self.ai.max_size(): # Check against max_size again for the case where the file just got expanded above because of aiscript.bin
				_, bw_size = self.ai.calculate_sizes()
				if self.ai.expanded:
					raise PyMSError('Parse', f"There is not enough room in your bwscript.bin to compile these changes. The current file is {bw_size}B out of the max {self.ai.max_size()}B, these changes would make the file {new_bw_size}B.")
				else:
					if UI.MessageBox.askyesno(parent=self, title='Expand', message="There is not enough room in your bwscript.bin to compile these changes, would you like to expand your bwscript.bin? If you don't know what this is you should google 'AISE Plugin' before saying Yes") == UI.NO:
						return False
					self.ai.expand()
		except PyMSError as e:
			ErrorDialog(parent, e)
			return False
		new_active_plugins = parse_context.language_context.active_plugins()
		if new_active_plugins:
			added_plugins = new_active_plugins.difference(self.ai.active_plugins)
			if added_plugins and not AddedPluginsDialog(parent, parse_context.language_context, added_plugins).add:
				return False
		if parse_context.warnings:
			WarningDialog(parent, parse_context.warnings, True)
		self.ai.active_plugins.update(new_active_plugins)
		self.ai.add_scripts(scripts)
		self.update_script_status()
		self.refresh_listbox()
		self.mark_edited()
		return True

	# def get_export_references(self) -> bool:
	# 	return self.reference.get()

	def _get_definitions_handler(self, parse_settings: AIParseSettings | None = None) -> DefinitionsHandler:
		defs = DefinitionsHandler()
		handler = AIDefsSourceCodeHandler()
		if parse_settings is None:
			parse_settings = AIParseSettings()
		for extdef in self.config_.extdefs.data:
			if not os.path.isfile(extdef):
				raise PyMSError('External Definitions', f"External definitions file not found: '{extdef}'. Remove or update the entry in the External Defs dialog.")
			with IO.InputText(extdef) as f:
				code = f.read()
			lexer = AILexer(code)
			parse_context = AIParseContext(lexer, parse_settings, defs, self.data_context)
			handler.parse(parse_context)
			parse_context.finalize()
		return defs

	def get_formatters(self) -> Formatters:
		return Formatters(
			block = self.config_.code.decomp_format.block.value.formatter,
			command = self.config_.code.decomp_format.command.value.formatter,
			comment = self.config_.code.decomp_format.comment.value.formatter,
		)

	def get_serialize_context(self, output: BuiltinIO[str]) -> AISerializeContext:
		definitions = self._get_definitions_handler()
		formatters = self.get_formatters()
		return AISerializeContext(output, definitions, formatters, self.data_context)

	def get_parse_context(self, any_input: IO.AnyInputText) -> AIParseContext:
		parse_settings = AIParseSettings()
		definitions = self._get_definitions_handler(parse_settings)
		with IO.InputText(any_input) as input_text:
			code = input_text.read()
		lexer = AILexer(code)
		return AIParseContext(lexer, parse_settings, definitions, self.data_context)

	def select_scripts(self, ids: list[str], keep_existing: bool = False) -> None:
		if not keep_existing:
			self.listbox.select_clear(0, UI.END)
		for index,script in enumerate(self.script_list):
			if script.id in ids:
				self.listbox.select_set(index)

	def get_find_history(self) -> list[str]:
		return self.findhistory

	def get_replace_history(self) -> list[str]:
		return self.replacehistory

	# Tooltip Delegate
	def get_list_entry(self, index: int) -> AIBIN.AIScript:
		return self.script_list[index]
