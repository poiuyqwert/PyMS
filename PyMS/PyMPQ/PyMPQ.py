
from .CompressionSetting import CompressionOption, CompressionSetting
from .Locales import LOCALE_CHOICES, find_locale_index
from .CheckThread import CheckThread
from .LocaleDialog import LocaleDialog
from .UpdateFiles import UpdateFiles
from .FolderDialog import FolderDialog
from .SettingsUI.SettingsDialog import SettingsDialog
from .Config import PyMPQConfig

from ..FileFormats.MPQ.MPQ import MPQ, MPQLibrary, MPQFileEntry, MPQFileFlag

from ..Utilities.DependencyError import DependencyError
from ..Utilities.utils import format_byte_size, start_file
from ..Utilities import registry
from ..Utilities import UIKit as UI
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.fileutils import check_allow_overwrite_internal_file
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog
from ..Utilities.SponsorDialog import SponsorDialog

import sys, time, shutil, os, re

from typing import Any

if not MPQ.supported():
	dep_err_dialog = DependencyError('PyMPQ', 'PyMS currently only has Windows and Mac support for MPQ files, thus this program is useless.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me!')
	dep_err_dialog.startup()
	sys.exit()

LONG_VERSION = 'v' + Assets.version('PyMPQ')

class ColumnID:
	Filename = 0
	Size = 1
	Ratio = 2
	PackedSize = 3
	Locale = 4
	Attributes = 5

class PyMPQ(UI.MainWindow):
	def __init__(self, guifile: str | None = None) -> None:
		#Window
		UI.MainWindow.__init__(self)
		self.set_icon('PyMPQ')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMPQ', Assets.version('PyMPQ'))
		ga.track(GAScreen('PyMPQ'))
		setup_trace('PyMPQ', self)

		self.config_ = PyMPQConfig()
		UI.Theme.load_theme(self.config_.theme.value, self)

		self.mpq: MPQ | None = None
		self.mpq_path: str | None = None
		self.all_files: list[MPQFileEntry] = []
		self.display_files: list[MPQFileEntry] = []
		self.totalsize = 0
		self.temp_folder = os.path.join(Assets.internal_temp_dir, str(int(time.time())))
		def update_files(files: list[str]) -> None:
			self.after_managed(1, self.update_files, files)
		self.thread = CheckThread(update_files, self.temp_folder)
		self.resettimer: str | None = None

		self.update_title()

		self.encvar = UI.BooleanVar()
		self.compvar = UI.StringVar()

		self.locale_menu_choice = UI.IntVar()
		self.locale_menu_choice.trace_add('write', self.locale_changed)

		#Menubar
		self.menu = UI.Menu(self)
		self.config(menu=self.menu)

		file_menu = self.menu.add_cascade('File', underline=0)
		file_menu.add_command('New...', self.new, UI.Ctrl.n, underline='n')
		file_menu.add_command('Open...', self.open, UI.Ctrl.o, underline='o')
		file_menu.add_separator()
		file_menu.add_command('Close', self.close, UI.Ctrl.w, underline='c')
		file_menu.add_separator()
		file_menu.add_command('Exit', self.exit, UI.Shortcut.Exit, underline='x')

		files_menu = self.menu.add_cascade('Files', underline=1)
		files_menu.add_command('Add Files...', self.add, UI.Ctrl.i, enabled=False, tags='mpq_open', underline='a')
		files_menu.add_command('Add Directory...', self.adddir, UI.Ctrl.d, enabled=False, tags='mpq_open', underline='d')
		files_menu.add_command('Delete Files', self.remove, UI.Key.Delete, enabled=False, tags='file_selected', underline='l')
		files_menu.add_separator()
		files_menu.add_command('Open File', self.openfile, enabled=False, tags='file_selected', underline='o')
		files_menu.add_command('Rename File', self.rename, UI.Ctrl.r, enabled=False, tags='file_selected', underline='r')
		files_menu.add_command('Change Locale...', self.changelocale, enabled=False, tags='file_selected', underline='g')
		files_menu.add_separator()
		files_menu.add_command('Extract Files...', self.extract, UI.Ctrl.e, enabled=False, tags='file_selected', underline='e')
		files_menu.add_separator()
		files_menu.add_command('Compact Archive', self.compact, UI.Ctrl.p, enabled=False, tags='can_compact', underline='p')

		settings_menu = self.menu.add_cascade('Settings', underline=0)
		settings_menu.add_command('Manage Settings...', self.mansets, UI.Ctrl.m, underline='m')
		compression_menu = settings_menu.add_cascade('Compression', underline=0)
		compression_menu.add_radiobutton('Auto-Select', self.compvar, str(CompressionOption.Auto.setting()), UI.Key.F4, underline=0)
		compression_menu.add_separator()
		compression_menu.add_radiobutton('None', self.compvar, str(CompressionOption.NoCompression.setting()), UI.Key.F2, underline=0)
		compression_menu.add_radiobutton('Standard', self.compvar, str(CompressionOption.Standard.setting()), UI.Key.F3, underline=0)
		deflate_menu = compression_menu.add_cascade('Deflate', underline=0)
		for level in range(0,CompressionOption.Deflate.level_count()):
			compression = CompressionOption.Deflate.setting(level)
			deflate_menu.add_radiobutton(compression.level_name(), self.compvar, str(compression), UI.Key.F9 if level == 0 else None, underline=0)
		audio_menu = compression_menu.add_cascade('Audio', underline=0)
		audio_compression = (
			(CompressionOption.Audio.setting(level=0), UI.Key.F6),
			(CompressionOption.Audio.setting(level=1), UI.Key.F7),
			(CompressionOption.Audio.setting(level=2), UI.Key.F8),
		)
		for compression,shortcut in audio_compression:
			audio_menu.add_radiobutton(compression.level_name(), self.compvar, str(compression), shortcut, underline=0)
		settings_menu.add_checkbutton('Encrypt', self.encvar, onvalue=1, offvalue=0, shortcut=UI.Key.F5, underline=0)
		locale_menu = settings_menu.add_cascade('Locale', underline=0)
		for index,(locale_name,locale) in enumerate(LOCALE_CHOICES):
			command = lambda: None # pylint: disable=unnecessary-lambda-assignment
			if locale is not None:
				locale_name += f' [{locale}]'
			else:
				locale_name += '...'
				command = self.choose_other_locale
			locale_menu.add_radiobutton(locale_name, self.locale_menu_choice, index, command=command)
		settings_menu.add_separator()
		settings_menu.add_command('Set as Default *.mpq Editor (Windows Only)', self.register_registry, enabled=registry.IS_AVAILABLE, underline='t')

		help_menu = self.menu.add_cascade('Help', underline=0)
		help_menu.add_command('View Help', self.help, UI.Key.F1, underline='h')
		help_menu.add_separator()
		help_menu.add_command('Donate...', self.sponsor, underline='d')
		help_menu.add_command('About PyMPQ', self.about, underline='a')

		#Toolbar
		self.toolbar = UI.Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', UI.Ctrl.n, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', UI.Ctrl.o, bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', UI.Ctrl.w, bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add Files', UI.Ctrl.i, enabled=False, tags='mpq_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('openfolder'), self.adddir, 'Add Directory', UI.Ctrl.d, enabled=False, tags='mpq_open', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Delete Files', UI.Key.Delete, enabled=False, tags='file_selected', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('export'), self.extract, 'Extract Files', UI.Ctrl.e, enabled=False, tags='file_selected', bind_shortcut=False)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('edit'), self.rename, 'Rename File', UI.Ctrl.r, enabled=False, tags='file_selected', bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('debug'), self.compact, 'Compact Archive', UI.Ctrl.p, enabled=False, tags='can_compact', bind_shortcut=False)
		# self.toolbar.add_button(Assets.get_image('insert'), self.editlistfile, 'Edit Internal Listfile', Ctrl.l, enabled=False, tags='mpq_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mansets, 'Manage Settings', UI.Ctrl.m, bind_shortcut=False)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as Default *.mpq Editor (Windows Only)', enabled=registry.IS_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'View Help', UI.Key.F1, bind_shortcut=False)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyMPQ')
		self.toolbar.add_button(Assets.get_image('money'), self.sponsor, 'Donate')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', UI.Shortcut.Exit, bind_shortcut=False)
		self.toolbar.pack(side=UI.TOP, padx=1, pady=1, fill=UI.X)

		self.regex = UI.IntVar()
		self.regex.set(self.config_.filter.regex.value)
		self.filter = UI.StringVar()
		self.filter.set(['*','.+'][self.regex.get()])
		filter_frame = UI.Frame(self)
		UI.Label(filter_frame, text='Filter: ').pack(side=UI.LEFT)
		self.filter_history = UI.InputHistory(config=self.config_.filter.history)
		self.textdrop = UI.TextDropDown(filter_frame, self.filter, self.filter_history)
		self.textdrop.pack(side=UI.LEFT, fill=UI.X, expand=1)
		self.textdrop.entry.bind(UI.Key.Return(), self.dofilter)
		self.default_background_color = self.textdrop.entry['bg']
		self.find_button = UI.Button(filter_frame, image=Assets.get_image('find'), width=20, height=20, command=self.dofilter, state=UI.DISABLED)
		UI.Tooltip(self.find_button, 'List Matches')
		self.find_button.pack(side=UI.LEFT, padx=2)
		UI.Radiobutton(filter_frame, text='Regex', variable=self.regex, value=1).pack(side=UI.RIGHT)
		UI.Radiobutton(filter_frame, text='Wildcard', variable=self.regex, value=0).pack(side=UI.RIGHT)
		filter_frame.pack(side=UI.TOP, fill=UI.X)

		self.listmenu = UI.Menu(self, tearoff=0)
		self.listmenu.add_command('Open File', self.openfile, underline='o')
		self.listmenu.add_separator()
		self.listmenu.add_command('Extract Files...', self.extract, UI.Ctrl.e, bind_shortcut=False, underline='e')
		self.listmenu.add_command('Delete Files', self.remove, UI.Key.Delete, bind_shortcut=False, underline='d')
		self.listmenu.add_command('Rename File', self.rename, UI.Ctrl.r, bind_shortcut=False, underline='r')
		self.listmenu.add_command('Change Locale...', self.changelocale, underline='c')

		self.listbox = UI.ReportList(self, ['Name','Size','Ratio','Packed','Locale','Attributes',None], UI.EXTENDED, scmd=self.select, rcmd=self.do_rename, pcmd=self.popup, dcmd=self.openfile, min_widths=[50]*6)
		self.listbox_ascending_arrow = Assets.get_image('arrow.gif')
		self.listbox_descending_arrow = Assets.get_image('arrowup.gif')
		self.listbox_blank_arrow = Assets.get_image('arrowblank.gif')
		for column,(button,_) in enumerate(self.listbox.columns):
			if column <= ColumnID.Attributes:
				button['command'] = lambda c=column: self.sort(c)
			button['compound'] = UI.LEFT
		attributes_column_button,_ = self.listbox.columns[ColumnID.Attributes]
		UI.Tooltip(attributes_column_button, 'Attributes:\n C = Compressed\n E = Encrypted\n X = Adjust CryptKey')
		self.update_columns()
		self.update_list()
		self.listbox.pack(fill=UI.BOTH, expand=1)

		#Statusbar
		self.status = UI.StringVar()
		self.status.set('Open or create an MPQ.')
		self.selected = UI.StringVar()
		self.info = UI.StringVar()
		self.locale_status = UI.StringVar()
		self.library_status = UI.StringVar()
		self.library_status.set(MPQLibrary.display_name(MPQ.default_library()))
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.status, width=25)
		statusbar.add_label(self.selected, width=30)
		statusbar.add_label(self.info, width=30)
		statusbar.add_label(self.locale_status, weight=1)
		statusbar.add_label(self.library_status, width=10)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.load_settings()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyMPQ')

	def update_title(self) -> None:
		if self.mpq_path:
			details = f' ({self.mpq_path})'
		else:
			details = ''
		self.title(f'PyMPQ {LONG_VERSION}{details}')

	def choose_other_locale(self) -> None:
		locale_dialog = LocaleDialog(self, title='Change locale', message='Type a custom locale or choose an existing locale')
		if locale_dialog.save:
			locale = locale_dialog.result.get()
			self.config_.locale.value = locale
			self.update_locale_status()
		else:
			locale_index = find_locale_index(self.config_.locale.value)
			# _,locale = LOCALE_CHOICES[locale_index]
			self.after_managed(1, lambda: self.locale_menu_choice.set(locale_index))

	def locale_changed(self, *_: Any) -> None:
		locale_index = self.locale_menu_choice.get()
		_name,locale = LOCALE_CHOICES[locale_index]
		if locale is not None:
			self.config_.locale.value = locale
		self.update_locale_status()

	def update_locale_status(self) -> None:
		locale_index = find_locale_index(self.config_.locale.value)
		locale_name,_ = LOCALE_CHOICES[locale_index]
		self.locale_status.set(f'Locale: {locale_name} [{self.config_.locale.value}]')

	def load_settings(self) -> None:
		self.config_.windows.main.load_size(self)
		self.config_.list_sizes.load_size(self.listbox.panes)
		assert self.config_.compression.value is not None
		self.compvar.set(self.config_.compression.value)
		self.encvar.set(self.config_.encrypt.value)
		self.locale_menu_choice.set(find_locale_index(self.config_.locale.value))

	def save_settings(self) -> None:
		self.config_.windows.main.save_size(self)
		self.config_.list_sizes.save_size(self.listbox.panes)
		self.config_.compression.value = self.compvar.get()
		self.config_.encrypt.value = self.encvar.get()
		self.config_.save()

	def sort(self, column: int) -> None:
		if column == self.config_.sort.column.value:
			self.config_.sort.ascending.value = not self.config_.sort.ascending.value
		else:
			self.config_.sort.column.value = column
			self.config_.sort.ascending.value = True
		self.update_columns()
		self.update_list()

	def update_columns(self) -> None:
		for column,(button,_) in enumerate(self.listbox.columns):
			image = self.listbox_blank_arrow
			if column == self.config_.sort.column.value:
				if self.config_.sort.ascending.value:
					image = self.listbox_ascending_arrow
				else:
					image = self.listbox_descending_arrow
			button['image'] = image

	def is_mpq_chosen(self) -> bool:
		return self.mpq is not None

	def is_file_selected(self) -> bool:
		return bool(self.listbox.cur_selection())

	def select(self) -> None:
		if self.is_mpq_chosen():
			selected_indexes = self.listbox.cur_selection()
			total_size = 0
			for index in selected_indexes:
				total_size += self.display_files[index].full_size or 0
			self.selected.set(f'Selected {len(selected_indexes)} files, {format_byte_size(total_size)}')
		else:
			self.selected.set('')
		self.action_states()

	def action_states(self) -> None:
		is_mpq_chosen = self.is_mpq_chosen()
		self.toolbar.tag_enabled('mpq_open', is_mpq_chosen)
		self.menu.tag_enabled('mpq_open', is_mpq_chosen)
		self.find_button['state'] = UI.NORMAL if is_mpq_chosen else UI.DISABLED
		is_file_selected = self.is_file_selected()
		self.toolbar.tag_enabled('file_selected', is_file_selected)
		self.menu.tag_enabled('file_selected', is_file_selected)

	def dofilter(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		self.filter_history.record(self.filter.get())
		self.update_list()

	def open_mpq(self, read_only: bool = True) -> MPQ._WithContextManager:
		assert self.mpq is not None
		try:
			return self.mpq.open(read_only)
		except Exception as exc:
			raise PyMSError('MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ.") from exc

	def list_files(self) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		file_entries: list[MPQFileEntry] = []
		try:
			with self.open_mpq():
				file_entries = self.mpq.list_files()
		except PyMSError as err:
			ErrorDialog(self, err)
			return
		self.all_files = []
		self.totalsize = 0
		for file_entry in file_entries:
			self.all_files.append(file_entry)
			self.totalsize += file_entry.full_size or 0

	def reset_entry_background_color(self) -> None:
		self.textdrop.entry['bg'] = self.default_background_color
		self.resettimer = None

	def attributes_for_file_entry(self, file_entry: MPQFileEntry) -> str:
		attributes = ''
		attributes += 'C' if file_entry.compressed else '-'
		attributes += 'E' if file_entry.encrypted else '-'
		attributes += 'X' if file_entry.mod_crypt_key else '-'
		return attributes

	def update_list(self) -> None:
		previously_selected = []
		if self.listbox.size():
			for i in self.listbox.cur_selection():
				previously_selected.append(self.display_files[i])
			self.listbox.delete(UI.ALL)
		# else:
		# 	return
		if self.is_mpq_chosen() and self.all_files:
			self.display_files = list(self.all_files)
			filter_str = self.filter.get()
			if not self.regex.get():
				if not filter_str.replace('*','').replace('?',''):
					filter_str = ''
				else:
					filter_str = '^' + re.escape(filter_str).replace('\\?','.').replace('\\*','.+?') + '$'
			elif filter_str == '.+':
				filter_str = ''
			filter_pattern: re.Pattern | None = None
			if filter_str:
				try:
					filter_pattern = re.compile(filter_str)
				except Exception:
					filter_pattern = None
					self.resettimer = self.after_managed(1000, self.reset_entry_background_color)
					self.textdrop.entry['bg'] = '#FFB4B4'
			if filter_pattern:
				self.display_files = [file_entry for file_entry in self.display_files if filter_pattern.match(file_entry.file_name.decode('utf-8'))]
			def keysort(file_entry: MPQFileEntry) -> tuple:
				file_info = [file_entry.file_name, file_entry.full_size, file_entry.get_compression_ratio(), file_entry.compressed_size, file_entry.locale, self.attributes_for_file_entry(file_entry)]
				# We only need to re-arrange the sort info if we are sorting by something other than the first column
				if self.config_.sort.column.value:
					# Move sort column to front of info to sort
					file_info.insert(0, file_info[self.config_.sort.column.value])
					del file_info[self.config_.sort.column.value+1]
				return tuple(file_info)
			self.display_files.sort(key=keysort, reverse=not self.config_.sort.ascending.value)
			for file_entry in self.display_files:
				info = [
					file_entry.file_name.decode('utf-8'),
					format_byte_size(file_entry.full_size or 0),
					f'{int(file_entry.get_compression_ratio()*100)}%',
					format_byte_size(file_entry.compressed_size or 0),
					str(file_entry.locale),
					self.attributes_for_file_entry(file_entry),
					''
				]
				self.listbox.insert(UI.END, info)
				if file_entry in previously_selected:
					self.listbox.select_set(UI.END)
		self.action_states()

	def update_info(self) -> None:
		if not self.is_mpq_chosen():
			self.info.set('')
			return
		assert self.mpq is not None
		try:
			with self.open_mpq():
				block_count = self.mpq.used_block_count()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.info.set(f'Total {len(self.all_files)}/{block_count} files, {format_byte_size(self.totalsize)}')
		can_compact = block_count > len(self.all_files)
		self.toolbar.tag_enabled('can_compact', can_compact)
		self.menu.tag_enabled('can_compact', can_compact)

	def do_rename(self, index: int, new_filename: str) -> bool:
		if not self.is_mpq_chosen():
			return False
		assert self.mpq is not None
		file_entry = self.display_files[index]
		try:
			with self.open_mpq(read_only=False):
				self.mpq.rename_file(file_entry.file_name, new_filename)
		except PyMSError as e:
			ErrorDialog(self, e)
			return False
		return True

	def add_file_to_mpq(self, file_path: str, mpq_file_name: str) -> None:
		assert self.mpq is not None
		compression,compression_level = self.compression_settings(file_path)
		flags = MPQFileFlag.encrypted if self.encvar.get() else MPQFileFlag.none
		self.mpq.add_file(file_path, mpq_file_name, self.config_.locale.value, flags=flags, compression=compression, compression_level=compression_level)

	def compression_settings(self, filename: str) -> tuple[int, int]:
		compression = CompressionSetting.parse_value(self.compvar.get())
		if compression.type == CompressionOption.Auto:
			_,extension = os.path.splitext(filename)
			if extension and extension in self.config_.settings.autocompression.data:
				compression = CompressionSetting.parse_value(self.config_.settings.autocompression.data[extension])
			else:
				compression = CompressionSetting.parse_value(self.config_.settings.autocompression.data.get('Default', str(CompressionOption.Standard.setting())))
		mpq_compression_flags = compression.type.compression_type()
		return (mpq_compression_flags, compression.compression_level())

	def popup(self, _event: UI.Event, _i: str) -> None:
		# if not self.listbox.cur_selection():
		# 	self.listbox.select_set(i)
		self.listmenu.post(*self.winfo_pointerxy())

	def changelocale(self) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		dialog = LocaleDialog(self)
		if dialog.save:
			new_locale = dialog.result.get()
			failed_files: list[str] = []
			try:
				with self.open_mpq(read_only=False):
					for i in self.listbox.cur_selection():
						file_entry = self.display_files[i]
						if file_entry.locale == new_locale:
							continue
						try:
							self.mpq.change_file_locale(file_entry.file_name, file_entry.locale, new_locale)
							file_entry.locale = new_locale
						except Exception:
							failed_files.append(file_entry.file_name.decode('utf-8'))
					self.mpq.flush()
					self.list_files()
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.update_list()
			if failed_files:
				ErrorDialog(self, PyMSError('MPQ', "Couldn't change the locale of the following files:\n" + '\n'.join(failed_files)))

	def openfile(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		try:
			with self.open_mpq(read_only=False):
				for i in self.listbox.cur_selection():
					file_entry = self.display_files[i]
					path_components = file_entry.file_name.decode('utf-8').split('\\')
					try:
						os.makedirs(os.path.join(self.temp_folder,*path_components[:-1]))
					except (OSError, IOError) as e:
						if e.errno != 17:
							raise
					data = self.mpq.read_file(file_entry.file_name, file_entry.locale)
					file_path = os.path.join(self.temp_folder,*path_components)
					with open(file_path, 'wb') as f:
						f.write(data)
					start_file(file_path)
				if not self.thread.is_running():
					self.thread.start()
		except PyMSError as e:
			ErrorDialog(self, e)
			return

	def update_files(self, files: list[str]) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		files = [file_name.lstrip(os.sep) for file_name in files]
		if len(files) == 1:
			if not UI.MessageBox.askyesno(parent=self, title='File Edited', message=f'File "{files[0]}" has been modified since it was extracted.\n\nUpdate the archive with this file?'):
				return
		else:
			u = UpdateFiles(self, files)
			if not u.files:
				return
			files = u.files
		try:
			with self.open_mpq(read_only=False):
				for file_name in files:
					self.add_file_to_mpq(os.path.join(self.temp_folder,file_name), file_name.replace(os.sep, '\\'))
				self.mpq.flush()
				self.list_files()
				self.update_info()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.update_list()
		self.select()

	def _update_listfiles(self) -> None:
		if not self.mpq:
			return
		for listfile_path in self.config_.settings.listfiles.data:
			self.mpq.add_listfile(listfile_path)

	def new(self, _event: UI.Event | None = None) -> None:
		file = self.config_.last_path.mpq.select_save(self)
		if not file:
			return
		mpq = MPQ.of(file)
		try:
			mpq.create(self.config_.settings.defaults.maxfiles.value, self.config_.settings.defaults.blocksize.value, stay_open=False)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.close()
		self.mpq = mpq
		self.mpq_path = file
		self._update_listfiles()
		self.all_files = []
		self.display_files = []
		self.totalsize = 0
		self.status.set('Editing new MPQ.')
		self.update_title()
		self.update_list()
		self.select()

	def open(self, _event: UI.Event | None = None, file: str | None = None) -> None:
		if file is None:
			file = self.config_.last_path.mpq.select_open(self)
			if not file:
				return
		mpq = MPQ.of(file)
		try:
			open_context = mpq.open()
		except Exception as e:
			ErrorDialog(self, PyMSError('MPQ', "The file is not an MPQ, or the MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ.", cause=e))
			return
		self.close()
		self.mpq = mpq
		self.mpq_path = file
		self._update_listfiles()
		self.update_title()
		self.status.set('Load Successful!')
		with open_context:
			self.list_files()
			self.update_info()
		self.update_list()
		self.select()

	def close(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		self.mpq.close()
		self.mpq = None
		self.mpq_path = None
		self.all_files = []
		self.display_files = []
		self.listbox.delete(UI.ALL)
		self.update_title()
		self.status.set('Open or create an MPQ.')
		self.cleanup_temp()
		self.update_info()
		# self.update_list()
		self.select()

	def add(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		files = self.config_.last_path.import_.files.select_open_multiple(self)
		if not files:
			return
		f = FolderDialog(self, self.config_.import_.files_prefix)
		if not f.save:
			return
		try:
			with self.open_mpq(read_only=False):
				for filepath in files:
					filename = os.path.basename(filepath)
					folder = self.config_.import_.files_prefix.value or ''
					self.add_file_to_mpq(filepath, folder + filename)
				self.mpq.flush()
				self.list_files()
				self.update_info()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.update_list()
		self.select()

	def adddir(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		path = self.config_.last_path.import_.folder.select_open(self)
		if not path:
			return
		path = os.path.join(path,'')
		fo = FolderDialog(self, self.config_.import_.folder_prefix)
		if not fo.save:
			return
		try:
			with self.open_mpq(read_only=False):
				for root,_,filenames in os.walk(path):
					folder = self.config_.import_.folder_prefix.value or ''
					path_folder = root.replace(path,'')
					if path_folder:
						folder += '\\'.join(os.path.split(path_folder)) + '\\'
					for filename in filenames:
						self.add_file_to_mpq(os.path.join(root,filename), folder + filename)
				self.mpq.flush()
				self.list_files()
				self.update_info()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.update_list()
		self.select()

	def remove(self, _event: UI.Event | None = None) -> None:
		if not self.is_file_selected():
			return
		assert self.mpq is not None
		with self.open_mpq(read_only=False):
			for i in self.listbox.cur_selection():
				file_entry = self.display_files[i]
				self.mpq.delete_file(file_entry.file_name, file_entry.locale)
			self.mpq.flush()
			self.list_files()
			self.update_info()
		self.update_list()
		self.select()

	def rename(self, _event: UI.Event | None = None) -> None:
		if not self.is_file_selected():
			return
		listbox = self.listbox.columns[ColumnID.Filename][1]
		if not isinstance(listbox, UI.EditableReportSubList):
			return
		listbox.edit()

	# def editlistfile(self, key=None):
		# if not self.is_mpq_chosen():
			# return
		# pass

	def extract(self, _event: UI.Event | None = None) -> None:
		if not self.is_file_selected():
			return
		assert self.mpq is not None
		path = self.config_.last_path.export.select_open(self)
		if not path:
			return
		with self.open_mpq():
			for index in self.listbox.cur_selection():
				file_entry = self.display_files[index]
				path_components = file_entry.file_name.decode('utf-8').split('\\')
				output_path = os.path.join(path,*path_components)
				if not check_allow_overwrite_internal_file(output_path):
					continue
				try:
					os.makedirs(os.path.join(path,*path_components[:-1]))
				except (OSError, IOError) as e:
					if e.errno != 17:
						raise
				try:
					data = self.mpq.read_file(file_entry.file_name, file_entry.locale)
				except Exception:
					ErrorDialog(self, PyMSError('Extract', f"Couldn't read file '{file_entry.file_name.decode('utf-8')}' from MPQ"))
					continue
				with open(output_path,'wb') as f:
					f.write(data)

	def mansets(self, _event: UI.Event | None = None) -> None:
		SettingsDialog(self, self.config_)
		self._update_listfiles()

	def compact(self, _event: UI.Event | None = None) -> None:
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		with self.open_mpq(read_only=False):
			self.mpq.compact()
		self.update_info()

	def register_registry(self, _event: UI.Event | None = None) -> None:
		try:
			registry.register('PyMPQ', 'mpq', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, _event: UI.Event | None = None) -> None:
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyMPQ.md')

	def about(self, _event: UI.Event | None = None) -> None:
		AboutDialog(self, 'PyMPQ', LONG_VERSION)

	def sponsor(self) -> None:
		SponsorDialog(self)

	def cleanup_temp(self) -> None:
		self.thread.end()
		if os.path.exists(self.temp_folder):
			shutil.rmtree(self.temp_folder)

	def exit(self, _event: UI.Event | None = None) -> None:
		self.cleanup_temp()
		self.save_settings()
		self.destroy()
