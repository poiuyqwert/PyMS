
from .Config import PyGRAFTConfig
from .Delegates import MainDelegate
from .GraftData import UnitsGraftData, UpgradesGraftData, ResearchGraftData, TechGraftData, OrdersGraftData, ButtonsGraftData, AnyGraftData
from .Tabs import GraftTab, ReqGraftTab, ButtonCardsTab, ButtonSetsTab, StatInfoTab
from .SettingsUI.SettingsDialog import SettingsDialog

from ..FileFormats.Graft import FGP
from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag
from ..FileFormats.TBL import TBL
from ..FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT

from ..Utilities import registry
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.DataContext import DataContext
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.PyMSWarning import PyMSWarning
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.SponsorDialog import SponsorDialog
from ..Utilities.SettingsUI.BaseSettingsDialog import ErrorableSettingsDialogDelegate
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities import Assets
from ..Utilities import UIKit as UI

import os

from typing import cast

LONG_VERSION = 'v' + Assets.version('PyGRAFT')

class PyGRAFT(UI.MainWindow, MainDelegate, ErrorableSettingsDialogDelegate):
	def __init__(self, guifile: str | None = None) -> None:
		self.guifile = guifile
		UI.MainWindow.__init__(self)
		self.title(f'PyGRAFT {LONG_VERSION}')
		self.set_icon('PyGRAFT')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyGRAFT', Assets.version('PyGRAFT'))
		ga.track(GAScreen('PyGRAFT'))
		setup_trace('PyGRAFT', self)

		self.config_ = PyGRAFTConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)

		self.mpq_handler = MPQHandler(self.config_.settings.mpqs)
		self.data_context = DataContext()

		self.units_data = UnitsGraftData()
		self.upgrades_data = UpgradesGraftData()
		self.research_data = ResearchGraftData()
		self.tech_data = TechGraftData()
		self.orders_data = OrdersGraftData()
		self.buttons_data = ButtonsGraftData()
		for graft_data in self.all_graft_data():
			try:
				graft_data.new()
			except PyMSError:
				pass

		self.menu = UI.Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File')
		file_menu.add_command('New', self.new, UI.Ctrl.n)
		file_menu.add_command('Open...', self.open, UI.Ctrl.o)
		file_menu.add_command('Open Directory...', self.open_directory, UI.Ctrl.d)
		file_menu.add_command('Open MPQ...', self.open_mpq, UI.Ctrl.Alt.o, enabled=MPQ.supported(), underline='m')
		file_menu.add_separator()
		file_menu.add_command('Save', self.save, UI.Ctrl.s)
		file_menu.add_command('Save As...', self.saveas, UI.Ctrl.Alt.s, underline='As')
		file_menu.add_command('Save MPQ...', self.save_mpq, UI.Ctrl.Alt.m, enabled=MPQ.supported(), underline='a')
		file_menu.add_separator()
		file_menu.add_command('Import from TXT...', self.iimport, UI.Ctrl.i)
		file_menu.add_command('Export to TXT...', self.export, UI.Ctrl.e)
		file_menu.add_command('Import FireGraft Project...', self.import_fgp, UI.Shift.Ctrl.i, underline='f')
		file_menu.add_separator()
		file_menu.add_command('Check for Updates...', self.check_for_updates, underline='u')
		file_menu.add_separator()
		file_menu.add_command('Exit', self.exit, UI.Shortcut.Exit, underline='x')

		settings_menu = self.menu.add_cascade('Settings')
		settings_menu.add_command('Manage Settings...', self.settings, UI.Ctrl.m)
		settings_menu.add_command('Reload Data Files', self.reload_files, underline='r')
		settings_menu.add_separator()
		settings_menu.add_command('Set as Default *.graft Editor (Windows Only)', self.register_registry, enabled=registry.IS_AVAILABLE, underline='D')

		help_menu = self.menu.add_cascade('Help')
		help_menu.add_command('View Help', self.help, UI.Key.F1, underline='h')
		help_menu.add_separator()
		help_menu.add_command('Donate...', self.sponsor, underline='d')
		help_menu.add_command('About PyGRAFT', self.about, underline='a')

		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('openfolder'), self.open_directory, 'Open Directory', UI.Ctrl.d, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('openmpq'), self.open_mpq, 'Open MPQ', UI.Ctrl.Alt.o, enabled=MPQ.supported(), bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', UI.Ctrl.s, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', UI.Ctrl.Alt.s, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('savempq'), self.save_mpq, 'Save MPQ', UI.Ctrl.Alt.m, enabled=MPQ.supported(), bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import from TXT', UI.Ctrl.i, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export to TXT', UI.Ctrl.e, bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.settings, 'Manage Settings', UI.Ctrl.m, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('debug'), self.reload_files, 'Reload Data Files')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as Default *.graft Editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'View Help', UI.Key.F1, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyGRAFT')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_button(Assets.get_image('update'), self.check_for_updates, 'Check for Updates')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit, bind_shortcut=False)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		self.hor_pane = UI.PanedWindow(self, orient=UI.HORIZONTAL)
		left = UI.Frame(self.hor_pane)
		self.listbox = UI.ScrolledListbox(left, scroll_speed=2, font=UI.Font.fixed(), width=45, height=1)
		self.listbox.pack(side=UI.TOP, fill=UI.BOTH, padx=2, pady=2, expand=1)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), lambda *_: self.select_entry())
		self.hor_pane.add(left, sticky=UI.NSEW, minsize=300)

		self.notebook = UI.Notebook(self.hor_pane)
		self.tabs: list[GraftTab] = [
			ButtonSetsTab(self.notebook, self, self.buttons_data),
			ButtonCardsTab(self.notebook, self, self.buttons_data),
			StatInfoTab(self.notebook, self, self.buttons_data),
			ReqGraftTab(self.notebook, self, self.units_data),
			ReqGraftTab(self.notebook, self, self.upgrades_data),
			ReqGraftTab(self.notebook, self, self.research_data),
			ReqGraftTab(self.notebook, self, self.tech_data),
			ReqGraftTab(self.notebook, self, self.orders_data),
		]
		tab_titles = ('Button Sets', 'Button Cards', 'Unit Stat Info', 'Unit Training Reqs.', 'Upgrade Research Reqs.', 'Tech Research Reqs.', 'Tech Usage Reqs.', 'Order Reqs.')
		for tab, title in zip(self.tabs, tab_titles):
			self.notebook.add_tab(tab, title)
		self.notebook.bind(UI.WidgetEvent.Notebook.TabActivated(), lambda _: self.refresh())
		self.hor_pane.add(self.notebook.notebook, sticky=UI.NSEW)
		self.hor_pane.pack(fill=UI.BOTH, expand=1)

		self.status = UI.StringVar()
		self.entry_count = UI.StringVar()
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, weight=0.60)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.entry_count)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.config_.windows.main.load_size(self)
		self.config_.list_size.load_size(self.hor_pane)

		self.refresh()

	def initialize(self) -> None:
		e = self.open_files()
		if e:
			self.settings(err=e)
		if self.guifile:
			self.open(file_path=self.guifile)
		UpdateDialog.check_update(self, 'PyGRAFT')

	def all_graft_data(self) -> tuple[AnyGraftData, ...]:
		return (self.units_data, self.upgrades_data, self.research_data, self.tech_data, self.orders_data, self.buttons_data)

	def active_tab(self) -> GraftTab:
		return cast(GraftTab, self.notebook.active)

	def active_graft_data(self) -> AnyGraftData:
		return self.active_tab().get_graft_data()

	def refresh(self) -> None:
		tab = self.active_tab()
		tab.refresh()
		self.listbox.delete(0, UI.END)
		names = tab.entry_names()
		if names:
			self.listbox.insert(UI.END, *names)
			dimmed_foreground = self.listbox.listbox.cget('disabledforeground')
			for index in tab.dimmed_entries():
				self.listbox.itemconfig(index, foreground=dimmed_foreground)
			self.listbox.select_set(tab.selected)
			self.listbox.see(tab.selected)
		self.update_status_bar()

	def update_status_bar(self) -> None:
		graft_data = self.active_graft_data()
		self.status.set(graft_data.display_name)
		self.editstatus['state'] = UI.NORMAL if graft_data.edited else UI.DISABLED
		entry_count = self.listbox.size()
		self.entry_count.set(f'{entry_count} entr{"y" if entry_count == 1 else "ies"}')

	def select_entry(self) -> None:
		selection = self.listbox.curselection()
		if not selection:
			return
		index = int(selection[0])
		tab = self.active_tab()
		if index != tab.selected and not self.confirm_leave():
			# Stay on the entry being edited
			index = tab.selected
		elif index == tab.selected:
			return
		# Confirming can refresh the list (by applying changes), so (re)select the entry in the list
		self.listbox.select_clear(0, UI.END)
		self.listbox.select_set(index)
		self.listbox.see(index)
		if index != tab.selected:
			tab.select(index)

	def confirm_leave(self) -> bool:
		# Only the active tab can have unapplied changes, since leaving a tab asks to apply them
		return self.active_tab().confirm_leave()

	def confirm_apply_before_save(self) -> bool:
		return self.active_tab().confirm_apply_before_save()

	def open_files(self) -> PyMSError | None:
		self.mpq_handler.open_mpqs()
		err = None
		try:
			stat_txt = TBL()
			stat_txt.load(self.mpq_handler.load_file(self.config_.settings.files.stat_txt.file_path))
			# unitnames.tbl is optional (it's only in mods with expanded units), so it's only an error if it's found but can't be loaded
			unitnames: TBL | None = None
			if unitnames_file := self.mpq_handler.get_file(self.config_.settings.files.unitnames.file_path):
				unitnames = TBL()
				unitnames.load(unitnames_file)
			units_dat = UnitsDAT()
			units_dat.load(self.mpq_handler.load_file(self.config_.settings.files.dat.units.file_path))
			upgrades_dat = UpgradesDAT()
			upgrades_dat.load(self.mpq_handler.load_file(self.config_.settings.files.dat.upgrades.file_path))
			techdata_dat = TechDAT()
			techdata_dat.load(self.mpq_handler.load_file(self.config_.settings.files.dat.techdata.file_path))
			orders_dat = OrdersDAT()
			orders_dat.load(self.mpq_handler.load_file(self.config_.settings.files.dat.orders.file_path))
		except PyMSError as e:
			err = e
		else:
			self.data_context.set_stat_txt_tbl(stat_txt)
			self.data_context.set_unitnames_tbl(unitnames)
			self.data_context.set_units_dat(units_dat)
			self.data_context.set_upgrades_dat(upgrades_dat)
			self.data_context.set_techdata_dat(techdata_dat)
			self.data_context.set_orders_dat(orders_dat)
			self.refresh()
		finally:
			self.mpq_handler.close_mpqs()
		return err

	def reload_files(self) -> None:
		if not self.confirm_leave():
			return
		err = self.open_files()
		if err:
			ErrorDialog(self, err)

	def show_warnings(self, warnings: list[PyMSWarning]) -> None:
		if warnings:
			WarningDialog(self, warnings)

	# Saving

	def check_saved(self, graft_data: AnyGraftData | None = None) -> CheckSaved:
		# Check the given file, or every file when `None`
		for check_data in (graft_data,) if graft_data else self.all_graft_data():
			if not check_data.edited:
				continue
			save = UI.MessageBox.askyesnocancel(parent=self, title='Save Changes?', message=f"Save changes to '{check_data.display_name}'?", default=UI.MessageBox.YES)
			if save is None:
				return CheckSaved.cancelled
			if save and self.save_graft_data(check_data, check_data.file_path) == CheckSaved.cancelled:
				return CheckSaved.cancelled
		return CheckSaved.saved

	def save_graft_data(self, graft_data: AnyGraftData, file_path: str | None) -> CheckSaved:
		if not file_path:
			file_path = self.config_.last_path.graft.select_save(self, title=f'Save {graft_data.file_name} As', filename=graft_data.file_name)
			if not file_path:
				return CheckSaved.cancelled
		elif not check_allow_overwrite_internal_file(file_path):
			return CheckSaved.cancelled
		try:
			graft_data.save(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return CheckSaved.cancelled
		graft_data.file_path = file_path
		graft_data.edited = False
		self.update_status_bar()
		return CheckSaved.saved

	# File commands

	def new(self, _event: UI.Event | None = None) -> None:
		if not self.confirm_leave():
			return
		graft_data = self.active_graft_data()
		if self.check_saved(graft_data) == CheckSaved.cancelled:
			return
		try:
			graft_data.new()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.refresh()

	def graft_data_for_file_name(self, file_name: str) -> AnyGraftData | None:
		for graft_data in self.all_graft_data():
			if graft_data.file_name.lower() == file_name.lower():
				return graft_data
		return None

	def open(self, _event: UI.Event | None = None, file_path: str | None = None) -> None:
		if file_path is None:
			file_path = self.config_.last_path.graft.select_open(self)
			if not file_path:
				return
		if not self.confirm_leave():
			return
		# Files with a known name open into their tab, anything else into the active tab's file
		graft_data = self.graft_data_for_file_name(os.path.basename(file_path)) or self.active_graft_data()
		if self.check_saved(graft_data) == CheckSaved.cancelled:
			return
		try:
			warnings = graft_data.load(file_path)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if graft_data is not self.active_graft_data():
			for title, (tab, _) in self.notebook.pages.items():
				if cast(GraftTab, tab).get_graft_data() is graft_data:
					self.notebook.display(title)
					break
		self.refresh()
		self.show_warnings(warnings)

	def _open_all(self, source: str, read: dict[AnyGraftData, bytes | str]) -> None:
		if not read:
			ErrorDialog(self, PyMSError('Open', f'No Graft files found in {source}'))
			return
		if not self.confirm_leave():
			return
		if any(self.check_saved(graft_data) == CheckSaved.cancelled for graft_data in read):
			return
		warnings: list[PyMSWarning] = []
		loaded: list[str] = []
		failed: list[str] = []
		for graft_data, any_input in read.items():
			try:
				warnings.extend(graft_data.load(any_input))
			except PyMSError as e:
				failed.append(f'{graft_data.file_name}: {e.error}')
			else:
				loaded.append(graft_data.file_name)
		self.refresh()
		message = ''
		if loaded:
			message += f'Graft files opened:\n\t{", ".join(loaded)}'
		if failed:
			if message:
				message += '\n\n'
			message += 'Graft files that could not be opened:\n\t' + '\n\t'.join(failed)
		UI.MessageBox.showinfo(parent=self, title='Graft Files Found', message=message)
		self.show_warnings(warnings)

	def open_directory(self, _event: UI.Event | None = None) -> None:
		path = self.config_.last_path.dir.select_open(self)
		if not path:
			return
		read: dict[AnyGraftData, bytes | str] = {}
		for graft_data in self.all_graft_data():
			file_path = os.path.join(path, graft_data.file_name)
			if os.path.exists(file_path):
				read[graft_data] = file_path
		self._open_all(f'directory "{path}"', read)

	def open_mpq(self, _event: UI.Event | None = None) -> None:
		if not MPQ.supported():
			return
		path = self.config_.last_path.mpq.select_open(self)
		if not path:
			return
		read: dict[AnyGraftData, bytes | str] = {}
		try:
			mpq = MPQ.of(path)
			with mpq.open():
				for graft_data in self.all_graft_data():
					try:
						read[graft_data] = mpq.read_file(graft_data.mpq_path)
					except Exception:
						continue
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self._open_all(f'MPQ "{path}"', read)

	def save(self, _event: UI.Event | None = None) -> None:
		if not self.confirm_apply_before_save():
			return
		graft_data = self.active_graft_data()
		self.save_graft_data(graft_data, graft_data.file_path)

	def saveas(self, _event: UI.Event | None = None) -> None:
		if not self.confirm_apply_before_save():
			return
		self.save_graft_data(self.active_graft_data(), None)

	def save_mpq(self, _event: UI.Event | None = None) -> None:
		if not MPQ.supported():
			return
		if not self.confirm_apply_before_save():
			return
		path = self.config_.last_path.mpq.select_save(self)
		if not path:
			return
		not_saved: list[str] = []
		try:
			mpq = MPQ.of(path)
			with mpq.open_or_create():
				for graft_data in self.all_graft_data():
					try:
						mpq.add_data(graft_data.save_bytes(), graft_data.mpq_path, compression=MPQCompressionFlag.pkware)
					except Exception as e:
						not_saved.append(f'{graft_data.file_name}: {e}')
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if not_saved:
			details = '\n'.join(not_saved)
			UI.MessageBox.showwarning(parent=self, title='Save problems', message=f'The following files could not be saved to the MPQ:\n\n{details}')

	def iimport(self, _event: UI.Event | None = None) -> None:
		path = self.config_.last_path.txt.select_open(self)
		if not path:
			return
		if not self.confirm_leave():
			return
		try:
			self.active_graft_data().import_text(path, self.data_context)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.refresh()

	def export(self, _event: UI.Event | None = None) -> None:
		if not self.confirm_apply_before_save():
			return
		graft_data = self.active_graft_data()
		path = self.config_.last_path.txt.select_save(self, filename=os.path.splitext(graft_data.file_name)[0])
		if not path:
			return
		try:
			graft_data.export_text(path, self.data_context)
		except PyMSError as e:
			ErrorDialog(self, e)

	def import_fgp(self, _event: UI.Event | None = None) -> None:
		path = self.config_.last_path.fgp.select_open(self)
		if not path:
			return
		if not self.confirm_leave():
			return
		fgp = FGP()
		try:
			warnings = fgp.load(path)
			for graft_data in self.all_graft_data():
				warnings.extend(graft_data.import_fgp(fgp))
		except PyMSError as e:
			ErrorDialog(self, e)
			self.refresh()
			return
		self.refresh()
		self.show_warnings(warnings)

	# Other commands

	def settings(self, _event: UI.Event | None = None, err: PyMSError | None = None) -> None:
		SettingsDialog(self, config=self.config_, delegate=self, err=err, mpq_handler=self.mpq_handler)

	def register_registry(self, _event: UI.Event | None = None) -> None:
		try:
			registry.register('PyGRAFT', 'graft', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, _event: UI.Event | None = None) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyGRAFT.md')

	def about(self, _event: UI.Event | None = None) -> None:
		AboutDialog(self, 'PyGRAFT', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def check_for_updates(self) -> None:
		UpdateDialog(self, 'PyGRAFT')

	def exit(self, _event: UI.Event | None = None) -> None:
		# Applied changes then count as unsaved changes of their file
		if not self.confirm_leave():
			return
		if self.check_saved() == CheckSaved.cancelled:
			return
		self.config_.windows.main.save_size(self)
		self.config_.list_size.save_size(self.hor_pane)
		self.config_.save()
		self.destroy()
