
from .CompressionSetting import CompressionOption, CompressionSetting
from .Locales import LOCALE_CHOICES, find_locale_index
from .CheckThread import CheckThread
from .LocaleDialog import LocaleDialog
from .UpdateFiles import UpdateFiles
from .FolderDialog import FolderDialog
from .SettingsUI.SettingsDialog import SettingsDialog
from .Config import PyMPQConfig

from ..FileFormats.MPQ.MPQ import MPQ, MPQLibrary, MPQFileEntry

from ..Utilities.DependencyError import DependencyError
from ..Utilities.utils import WIN_REG_AVAILABLE, format_byte_size, register_registry, start_file
from ..Utilities.UIKit import *
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities import Assets
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog

import sys, time, shutil, os, re

if not MPQ.supported():
	e = DependencyError('PyMPQ', 'PyMS currently only has Windows and Mac support for MPQ files, thus this program is useless.\nIf you can help compile and test StormLib and/or SFmpq for your operating system, then please Contact me!', (('Contact','file:///%s' % Assets.readme_file_path),))
	e.startup()
	sys.exit()

LONG_VERSION = 'v%s' % Assets.version('PyMPQ')

class ColumnID:
	Filename = 0
	Size = 1
	Ratio = 2
	PackedSize = 3
	Locale = 4
	Attributes = 5

class PyMPQ(MainWindow):
	def __init__(self, guifile=None): # type: (str | None) -> None
		#Window
		MainWindow.__init__(self)
		self.title('PyMPQ %s' % LONG_VERSION)
		self.set_icon('PyMPQ')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMPQ', Assets.version('PyMPQ'))
		ga.track(GAScreen('PyMPQ'))
		setup_trace('PyMPQ', self)
		
		self.config_ = PyMPQConfig()
		Theme.load_theme(self.config_.theme.value, self)

		self.mpq = None # type: MPQ | None
		self.all_files = [] # type: list[MPQFileEntry]
		self.display_files = [] # type: list[MPQFileEntry]
		self.totalsize = 0
		self.temp_folder = os.path.join(Assets.internal_temp_dir, str(int(time.time())))
		def update_files(files): # type: (list[str]) -> None
			self.after(1, self.update_files, files)
		self.thread = CheckThread(update_files, self.temp_folder)
		self.resettimer = None # type: str | None

		#Toolbar
		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('new'), self.new, 'New', Ctrl.n)
		self.toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('close'), self.close, 'Close', Ctrl.w)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add Files', Ctrl.i, enabled=False, tags='mpq_open')
		self.toolbar.add_button(Assets.get_image('openfolder'), self.adddir, 'Add Directory', Ctrl.d, enabled=False, tags='mpq_open')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Delete Files', Key.Delete, enabled=False, tags='file_selected')
		self.toolbar.add_button(Assets.get_image('export'), self.extract, 'Extract Files', Ctrl.e, enabled=False, tags='file_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('edit'), self.rename, 'Rename File', Ctrl.r, enabled=False, tags='file_selected')
		self.toolbar.add_button(Assets.get_image('debug'), self.compact, 'Compact Archive', Ctrl.p, enabled=False, tags='can_compact')
		# self.toolbar.add_button(Assets.get_image('insert'), self.editlistfile, 'Edit Internal Listfile', Ctrl.l, enabled=False, tags='mpq_open')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.mansets, 'Manage Settings', Ctrl.m)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('register'), self.register_registry, 'Set as default *.mpq editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyMPQ')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Shortcut.Exit)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.regex = IntVar()
		self.regex.set(self.config_.filter.regex.value)
		self.filter = StringVar()
		self.filter.set(['*','.+'][self.regex.get()])
		filter = Frame(self)
		Label(filter, text='Filter: ').pack(side=LEFT)
		self.textdrop = TextDropDown(filter, self.filter, self.config_.filter.history.data)
		self.textdrop.pack(side=LEFT, fill=X, expand=1)
		self.textdrop.entry.bind(Key.Return(), self.dofilter)
		self.default_background_color = self.textdrop.entry['bg']
		self.find_button = Button(filter, image=Assets.get_image('find'), width=20, height=20, command=self.dofilter, state=DISABLED)
		Tooltip(self.find_button, 'List Matches')
		self.find_button.pack(side=LEFT, padx=2)
		Radiobutton(filter, text='Regex', variable=self.regex, value=1).pack(side=RIGHT)
		Radiobutton(filter, text='Wildcard', variable=self.regex, value=0).pack(side=RIGHT)
		filter.pack(side=TOP, fill=X)

		self.encvar = IntVar()
		self.compvar = StringVar()

		self.locale_menu_choice = IntVar()
		self.locale_menu_choice.trace('w', self.locale_changed)

		self.setmenu = Menu(self, tearoff=0)
		self.compmenu = Menu(self.setmenu, tearoff=0)
		self.locale_menu = Menu(self.setmenu, tearoff=0)
		
		self.deflatemenu = Menu(self.compmenu, tearoff=0)
		for level in range(0,CompressionOption.Deflate.level_count()):
			compression = CompressionOption.Deflate.setting(level)
			self.deflatemenu.add_radiobutton(label=compression.level_name(), underline=0, variable=self.compvar, value=str(compression), shortcut=Key.F9 if level == 0 else None, shortcut_widget=self) # type: ignore

		self.audiomenu = Menu(self.compmenu, tearoff=0)
		audio_compression = (
			(CompressionOption.Audio.setting(level=0), Key.F6),
			(CompressionOption.Audio.setting(level=1), Key.F7),
			(CompressionOption.Audio.setting(level=2), Key.F8),
		)
		for compression,shortcut in audio_compression:
			self.audiomenu.add_radiobutton(label=compression.level_name(), underline=0, variable=self.compvar, value=str(compression), shortcut=shortcut, shortcut_widget=self) # type: ignore

		self.compmenu.add_radiobutton(label='Auto-Select', underline=0, variable=self.compvar, value=str(CompressionOption.Auto.setting()), shortcut=Key.F4, shortcut_widget=self) # type: ignore
		self.compmenu.add_separator()
		self.compmenu.add_radiobutton(label='None', underline=0, variable=self.compvar, value=str(CompressionOption.NoCompression.setting()), shortcut=Key.F2, shortcut_widget=self) # type: ignore
		self.compmenu.add_radiobutton(label='Standard', underline=0, variable=self.compvar, value=str(CompressionOption.Standard.setting()), shortcut=Key.F3, shortcut_widget=self) # type: ignore
		self.compmenu.add_cascade(label='Deflate', menu=self.deflatemenu, underline=0)
		self.compmenu.add_cascade(label='Audio', menu=self.audiomenu, underline=0)
		
		for index,(locale_name,locale) in enumerate(LOCALE_CHOICES):
			command = lambda: None
			if locale is not None:
				locale_name += ' [%d]' % locale
			else:
				command = self.choose_other_locale
			self.locale_menu.add_radiobutton(label=locale_name, variable=self.locale_menu_choice, value=index, command=command)

		self.setmenu.add_command(label='Settings Dialog', command=lambda: self.mansets(1), underline=0, shortcut=Ctrl.m, shortcut_widget=self) # type: ignore
		self.setmenu.add_separator()
		self.setmenu.add_cascade(label='Compression', menu=self.compmenu, underline=0)
		self.setmenu.add_checkbutton(label='Encrypt', underline=0, onvalue=1, offvalue=0, variable=self.encvar, shortcut=Key.F5, shortcut_widget=self) # type: ignore
		self.setmenu.add_cascade(label='Locale', menu=self.locale_menu, underline=0)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Open', command=self.openfile, underline=0)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Extract', command=self.extract, underline=0)
		self.listmenu.add_command(label='Delete', command=self.remove, underline=0)
		self.listmenu.add_command(label='Rename', command=self.rename, underline=0)
		self.listmenu.add_command(label='Change Locale', command=self.changelocale, underline=0)
		
		self.listbox = ReportList(self, ['Name','Size','Ratio','Packed','Locale','Attributes',None], EXTENDED, self.select, self.do_rename, self.popup, self.openfile, min_widths=[50]*6)
		self.listbox_ascending_arrow = Assets.get_image('arrow.gif')
		self.listbox_descending_arrow = Assets.get_image('arrowup.gif')
		self.listbox_blank_arrow = Assets.get_image('arrowblank.gif')
		for column,(button,_) in enumerate(self.listbox.columns):
			if column <= ColumnID.Attributes:
				button['command'] = lambda c=column: self.sort(c)
			button['compound'] = LEFT
		attributes_column_button,_ = self.listbox.columns[ColumnID.Attributes]
		Tooltip(attributes_column_button, 'Attributes:\n C = Compressed\n E = Encrypted\n X = Adjust CryptKey')
		self.update_columns()
		self.update_list()
		self.listbox.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.status.set('Open or create an MPQ.')
		self.selected = StringVar()
		self.info = StringVar()
		self.locale_status = StringVar()
		self.library_status = StringVar()
		self.library_status.set(MPQLibrary.display_name(MPQ.default_library()))
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=25)
		statusbar.add_label(self.selected, width=30)
		statusbar.add_label(self.info, width=30)
		statusbar.add_label(self.locale_status, weight=1)
		statusbar.add_label(self.library_status, width=10)
		statusbar.pack(side=BOTTOM, fill=X)

		self.load_settings()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyMPQ')

	def choose_other_locale(self): # type: () -> None
		locale_dialog = LocaleDialog(self, title='Change locale', message='Type a custom locale or choose an existing locale')
		if locale_dialog.save:
			locale = locale_dialog.result.get()
			self.config_.locale.value = locale
			self.update_locale_status()
		else:
			locale_index = find_locale_index(self.config_.locale.value)
			# _,locale = LOCALE_CHOICES[locale_index]
			self.after(1, lambda: self.locale_menu_choice.set(locale_index))

	def locale_changed(self, *_): # type: (Any) -> None
		locale_index = self.locale_menu_choice.get()
		_name,locale = LOCALE_CHOICES[locale_index]
		if locale is not None:
			self.config_.locale.value = locale
		self.update_locale_status()

	def update_locale_status(self): # type: () -> None
		locale_index = find_locale_index(self.config_.locale.value)
		locale_name,_ = LOCALE_CHOICES[locale_index]
		self.locale_status.set('Locale: %s [%d]' % (locale_name, self.config_.locale.value))

	def load_settings(self): # type: () -> None
		self.config_.windows.main.load_size(self)
		self.config_.list_sizes.load_size(self.listbox.panes)
		self.compvar.set(self.config_.compression.value)
		self.encvar.set(self.config_.encrypt.value)
		self.locale_menu_choice.set(find_locale_index(self.config_.locale.value))

	def save_settings(self): # type: () -> None
		self.config_.windows.main.save_size(self)
		self.config_.list_sizes.save_size(self.listbox.panes)
		self.config_.compression.value = self.compvar.get()
		self.config_.encrypt.value = self.encvar.get()
		self.config_.save()

	def sort(self, column): # type: (int) -> None
		if column == self.config_.sort.column.value:
			self.config_.sort.ascending.value = not self.config_.sort.ascending.value
		else:
			self.config_.sort.column.value = column
			self.config_.sort.ascending.value = True
		self.update_columns()
		self.update_list()

	def update_columns(self): # type: () -> None
		for column,(button,_) in enumerate(self.listbox.columns):
			image = self.listbox_blank_arrow
			if column == self.config_.sort.column.value:
				if self.config_.sort.ascending.value:
					image = self.listbox_ascending_arrow
				else:
					image = self.listbox_descending_arrow
			button['image'] = image

	def is_mpq_chosen(self): # type: () -> bool
		return not not self.mpq

	def is_file_selected(self): # type: () -> bool
		return not not self.listbox.cur_selection()

	def select(self): # type: () -> None
		if self.is_mpq_chosen():
			selected_indexes = self.listbox.cur_selection()
			total_size = 0
			for index in selected_indexes:
				total_size += self.display_files[index].full_size or 0
			self.selected.set('Selected %s files, %s' % (len(selected_indexes), format_byte_size(total_size)))
		else:
			self.selected.set('')
		self.action_states()

	def action_states(self): # type: () -> None
		is_mpq_chosen = self.is_mpq_chosen()
		self.toolbar.tag_enabled('mpq_open', is_mpq_chosen)
		self.find_button['state'] = NORMAL if is_mpq_chosen else DISABLED
		self.toolbar.tag_enabled('file_selected', self.is_file_selected())

	def dofilter(self, e=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		filter = self.filter.get()
		filters = self.config_.filter.history.data
		if filter in filters:
			filters.remove(filter)
		filters.append(filter)
		if len(filters) > 10:
			del filters[0]
		self.update_list()

	def open_mpq(self, read_only=True): # type: (bool) -> MPQ._WithContextManager
		assert self.mpq is not None
		try:
			return self.mpq.open(read_only)
		except:
			raise PyMSError('MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ.")

	def list_files(self): # type: () -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		file_entries = [] # type: list[MPQFileEntry]
		try:
			with self.open_mpq():
				file_entries = self.mpq.list_files()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.all_files = []
		self.totalsize = 0
		for file_entry in file_entries:
			self.all_files.append(file_entry)
			self.totalsize += file_entry.full_size or 0

	def reset_entry_background_color(self): # type: () -> None
		self.textdrop.entry['bg'] = self.default_background_color
		self.resettimer = None

	def attributes_for_file_entry(self, file_entry): # type: (MPQFileEntry) -> str
		attributes = ''
		attributes += 'C' if file_entry.compressed else '-'
		attributes += 'E' if file_entry.encrypted else '-'
		attributes += 'X' if file_entry.mod_crypt_key else '-'
		return attributes

	def update_list(self): # type: () -> None
		previously_selected = []
		if self.listbox.size():
			for i in self.listbox.cur_selection():
				previously_selected.append(self.display_files[i])
			self.listbox.delete(ALL)
		# else:
		# 	return
		if self.is_mpq_chosen() and self.all_files:
			self.display_files = self.all_files
			filter_str = self.filter.get()
			if not self.regex.get():
				if not filter_str.replace('*','').replace('?',''):
					filter_str = ''
				else:
					filter_str = '^' + re.escape(filter_str).replace('\\?','.').replace('\\*','.+?') + '$'
			elif filter_str == '.+':
				filter_str = ''
			filter = None # type: re.Pattern | None
			if filter_str:
				try:
					filter = re.compile(filter_str)
				except Exception as error:
					filter = None
					self.resettimer = self.after(1000, self.reset_entry_background_color)
					self.textdrop.entry['bg'] = '#FFB4B4'
			if filter:
				self.display_files = [file_entry for file_entry in self.display_files if filter.match(file_entry.file_name.decode('utf-8'))]
			def keysort(file_entry): # type: (MPQFileEntry) -> tuple
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
					'%d%%' % int(file_entry.get_compression_ratio()*100),
					format_byte_size(file_entry.compressed_size or 0),
					str(file_entry.locale),
					self.attributes_for_file_entry(file_entry),
					''
				]
				self.listbox.insert(END, info)
				if file_entry in previously_selected:
					self.listbox.select_set(END)
		self.action_states()

	def update_info(self): # type: () -> None
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
		self.info.set('Total %s/%s files, %s' % (len(self.all_files), block_count, format_byte_size(self.totalsize)))
		can_compact = block_count > len(self.all_files)
		self.toolbar.tag_enabled('can_compact', can_compact)

	def do_rename(self, index, new_filename): # type: (int, str) -> bool
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

	def compression_settings(self, filename): # type: (str) -> tuple[int, int]
		compression = CompressionSetting.parse_value(self.compvar.get())
		if compression.type == CompressionOption.Auto:
			extension = '.' + filename.split(os.extsep)[-1]
			if extension in self.config_.settings.autocompression.data:
				compression = CompressionSetting.parse_value(self.config_.settings.autocompression.data[extension])
			else:
				compression = CompressionSetting.parse_value(self.config_.settings.autocompression.data['Default'])
		mpq_compression_flags = compression.type.compression_type()
		return (mpq_compression_flags, compression.compression_level())

	def popup(self, e, i): # type: (Event, int) -> None
		if not self.listbox.cur_selection():
			self.listbox.select_set(i)
		self.listmenu.post(*self.winfo_pointerxy())

	def changelocale(self): # type: () -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		dialog = LocaleDialog(self)
		if dialog.save:
			new_locale = dialog.result.get()
			try:
				with self.open_mpq(read_only=False):
					for i in self.listbox.cur_selection():
						file_entry = self.display_files[i]
						if file_entry.locale == new_locale:
							continue
						try:
							self.mpq.change_file_locale(file_entry.file_name, file_entry.locale, new_locale)
							file_entry.locale = new_locale
						except:
							# TODO: Warn about files not updated
							pass
					self.mpq.flush()
					self.list_files()
			except PyMSError as e:
				ErrorDialog(self, e)
				return
			self.update_list()

	def openfile(self, e=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		try:
			with self.open_mpq(read_only=False):
				for i in self.listbox.cur_selection():
					file_entry = self.display_files[i]
					try:
						os.makedirs(os.path.join(self.temp_folder,os.path.dirname(file_entry.file_name.decode('utf-8'))))
					except (OSError, IOError) as e:
						if e.errno != 17:
							raise
					data = self.mpq.read_file(file_entry.file_name, file_entry.locale)
					file_path = os.path.join(self.temp_folder,file_entry.file_name.decode('utf-8'))
					with open(file_path, 'wb') as f:
						f.write(data)
					start_file(file_path)
				if not self.thread.is_running():
					self.thread.start()
		except PyMSError as e:
			ErrorDialog(self, e)
			return

	def update_files(self, files): # type: (list[str]) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		if len(files) == 1:
			if not MessageBox.askyesno(parent=self, title='File Edited', message='File "%s" has been modified since it was extracted.\n\nUpdate the archive with this file?' % files[0]):
				return
		else:
			u = UpdateFiles(self, files)
			if not u.files:
				return
			files = u.files
		try:
			with self.open_mpq(read_only=False):
				for file_name in files:
					compression,compression_level = self.compression_settings(file_name)
					self.mpq.add_file(os.path.join(self.temp_folder,file_name), file_name, compression=compression, compression_level=compression_level)
				self.mpq.flush()
				self.list_files()
				self.update_info()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.update_list()
		self.select()

	def _update_listfiles(self): # type: () -> None
		if not self.mpq:
			return
		for listfile_path in self.config_.settings.listfiles.data:
			self.mpq.add_listfile(listfile_path)

	def new(self, key=None): # type: (Event | None) -> None
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
		self._update_listfiles()
		self.all_files = []
		self.display_files = []
		self.totalsize = 0
		self.status.set('Editing new MPQ.')
		self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
		self.update_list()
		self.select()

	def open(self, key=None, file=None): # type: (Event | None, str | None) -> None
		if file is None:
			file = self.config_.last_path.mpq.select_open(self)
			if not file:
				return
		mpq = MPQ.of(file)
		try:
			mpq.open()
		except PyMSError:
			ErrorDialog(self, PyMSError('MPQ', "The file is not an MPQ, or the MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		self.close()
		self.mpq = mpq
		self._update_listfiles()
		self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
		self.status.set('Load Successful!')
		self.list_files()
		self.update_info()
		self.mpq.close()
		self.update_list()
		self.select()

	def close(self, key=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		self.mpq.close()
		self.mpq = None
		self.all_files = []
		self.display_files = []
		self.listbox.delete(ALL)
		self.title('PyMPQ %s' % LONG_VERSION)
		self.status.set('Open or create an MPQ.')
		self.cleanup_temp()
		self.update_info()
		# self.update_list()
		self.select()

	def add(self, key=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		files = self.config_.last_path.add.files.select_open(self)
		if not files:
			return
		f = FolderDialog(self, self.config_.import_.files_prefix)
		if not f.save:
			return
		with self.open_mpq(read_only=False):
			for filepath in files:
				filename = os.path.basename(filepath)
				folder = self.config_.import_.files_prefix.value
				compression,compression_level = self.compression_settings(filename)
				self.mpq.add_file(filepath, folder + filename, self.config_.locale.value, compression=compression, compression_level=compression_level)
			self.mpq.flush()
			self.list_files()
			self.update_info()
		self.update_list()
		self.select()

	def adddir(self, key=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		path = self.config_.last_path.add.folder.select_open(self)
		if not path:
			return
		path = os.path.join(path,'')
		fo = FolderDialog(self, self.config_.import_.folder_prefix)
		if not fo.save:
			return
		with self.open_mpq(read_only=False):
			for root,_,filenames in os.walk(path):
				folder = self.config_.import_.folder_prefix.value
				path_folder = root.replace(path,'')
				if path_folder:
					folder += '\\'.join(os.path.split(path_folder)) + '\\'
				for filename in filenames:
					compression,compression_level = self.compression_settings(filename)
					self.mpq.add_file(os.path.join(root,filename), folder + filename, self.config_.locale.value, compression=compression, compression_level=compression_level)
			self.mpq.flush()
			self.list_files()
			self.update_info()
		self.update_list()
		self.select()

	def remove(self, key=None): # type: (Event | None) -> None
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

	def rename(self, key=None): # type: (Event | None) -> None
		if not self.is_file_selected():
			return
		listbox = self.listbox.columns[ColumnID.Filename][1]
		if not isinstance(listbox, EditableReportSubList):
			return
		listbox.edit()

	# def editlistfile(self, key=None):
		# if not self.is_mpq_chosen():
			# return
		# pass

	def extract(self, key=None): # type: (Event | None) -> None
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
				try:
					os.makedirs(os.path.join(path,*path_components[:-1]))
				except (OSError, IOError) as e:
					if e.errno != 17:
						raise
				try:
					data = self.mpq.read_file(file_entry.file_name, file_entry.locale)
				except:
					ErrorDialog(self, PyMSError('Extract', "Couldn't read file '%s' from MPQ" % file_entry.file_name.decode('utf-8')))
				with open(os.path.join(path,*path_components),'wb') as f:
					f.write(data)

	def mansets(self, key=None): # type: (Event | None) -> None
		if key:
			SettingsDialog(self, self.config_)
			self._update_listfiles()
		else:
			self.setmenu.post(*self.winfo_pointerxy())

	def compact(self, key=None): # type: (Event | None) -> None
		if not self.is_mpq_chosen():
			return
		assert self.mpq is not None
		with self.open_mpq(read_only=False):
			self.mpq.compact()
		self.update_info()

	def register_registry(self, e=None): # type: (Event | None) -> None
		try:
			register_registry('PyMPQ', 'mpq', '')
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None): # type: (Event | None) -> None
		HelpDialog(self, self.config_.windows.help, 'Help/Programs/PyMPQ.md')

	def about(self, key=None): # type: (Event | None) -> None
		AboutDialog(self, 'PyMPQ', LONG_VERSION)

	def cleanup_temp(self): # type: () -> None
		self.thread.end()
		if os.path.exists(self.temp_folder):
			shutil.rmtree(self.temp_folder)

	def exit(self, e=None): # type: (Event | None) -> None
		self.cleanup_temp()
		self.save_settings()
		self.destroy()
