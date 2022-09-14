
from .CompressionSetting import CompressionType, CompressionSetting
from .Locales import LOCALE_CHOICES, find_locale_index
from .CheckThread import CheckThread
from .LocaleDialog import LocaleDialog
from .UpdateFiles import UpdateFiles
from .FolderDialog import FolderDialog
from .GeneralSettings import GeneralSettings
from .CompressionSettings import CompressionSettings
from .ListfileSettings import ListfileSettings

from ..FileFormats.MPQ.SFmpq import *

from ..Utilities.DependencyError import DependencyError
from ..Utilities.utils import BASE_DIR, VERSIONS, WIN_REG_AVAILABLE, format_byte_size, register_registry, start_file
from ..Utilities.UIKit import *
from ..Utilities.Settings import SettingDict, Settings
from ..Utilities.analytics import ga, GAScreen
from ..Utilities.trace import setup_trace
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.TextDropDown import TextDropDown
from ..Utilities.Tooltip import Tooltip
from ..Utilities.ReportList import ReportList
from ..Utilities.StatusBar import StatusBar
from ..Utilities.UpdateDialog import UpdateDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.SettingsDialog import SettingsDialog
from ..Utilities.AboutDialog import AboutDialog
from ..Utilities.HelpDialog import HelpDialog

import sys, time, shutil
from thread import start_new_thread

if not SFMPQ_LOADED:
	e = DependencyError('PyMPQ', 'PyMS currently only has Windows and Mac support for MPQ files, thus this program is useless.\nIf you can help compile and test SFmpq for your operating system, then please Contact me!', ('Contact','file:///%s' % os.path.join(BASE_DIR, 'Docs', 'intro.html')))
	e.startup()
	sys.exit()

LONG_VERSION = 'v%s' % VERSIONS['PyMPQ']

class ColumnID:
	Filename = 0
	Size = 1
	Ratio = 2
	PackedSize = 3
	Locale = 4
	Attributes = 5

class PyMPQ(MainWindow):
	def __init__(self, guifile=None):
		self.settings = Settings('PyMPQ', '2')
		self.settings.set_defaults({
			'compression': str(CompressionType.Auto.setting()),
			'encrypt': False,
			'locale': 0
		})
		self.settings.sort.set_defaults({
			'column': 0,
			'ascending': True
		})
		self.settings.settings.set_defaults({
			'listfiles': [os.path.join(BASE_DIR,'PyMS','Data','Listfile.txt')]
		})
		self.settings.settings.autocompression.set_defaults({
			'Default': str(CompressionType.Standard.setting()),
			'.smk': str(CompressionType.NoCompression.setting()),
			'.mpq': str(CompressionType.NoCompression.setting()),
			'.wav': str(CompressionType.Audio.setting(level=1))
		})
		self.settings.settings.defaults.set_defaults({
			'maxfiles': 1024,
			'blocksize': 3
		})

		#Window
		MainWindow.__init__(self)
		self.title('PyMPQ %s' % LONG_VERSION)
		self.set_icon('PyMPQ')
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMPQ', VERSIONS['PyMPQ'])
		ga.track(GAScreen('PyMPQ'))
		setup_trace(self, 'PyMPQ')

		self.file = None
		self.all_files = []
		self.display_files = []
		self.totalsize = 0
		self.temp_folder = os.path.join(BASE_DIR,'PyMS','Temp',str(int(time.time())),'')
		self.thread = CheckThread(self, self.temp_folder)

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
		self.toolbar.add_button(Assets.get_image('register'), self.register, 'Set as default *.mpq editor (Windows Only)', enabled=WIN_REG_AVAILABLE)
		self.toolbar.add_button(Assets.get_image('help'), self.help, 'Help', Key.F1)
		self.toolbar.add_button(Assets.get_image('about'), self.about, 'About PyMPQ')
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('exit'), self.exit, 'Exit', Alt.F4)
		self.toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.regex = IntVar()
		self.regex.set(self.settings.get('regex', False))
		self.filter = StringVar()
		self.filter.set(['*','.+'][self.regex.get()])
		filter = Frame(self)
		Label(filter, text='Filter: ').pack(side=LEFT)
		self.textdrop = TextDropDown(filter, self.filter, self.settings.get('filters', []))
		self.textdrop.pack(side=LEFT, fill=X, expand=1)
		self.textdrop.entry.bind(Key.Return, self.dofilter)
		self.textdrop.default_background_color = self.textdrop.entry['bg']
		image = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','find.gif'))
		self.find_button = Button(filter, image=image, width=20, height=20, command=self.dofilter, state=DISABLED)
		self.find_button.image = image
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
		for level in range(0,CompressionType.Deflate.level_count()):
			compression = CompressionType.Deflate.setting(level)
			self.deflatemenu.add_radiobutton(label=compression.level_name(), underline=0, variable=self.compvar, value=str(compression), shortcut=Key.F9 if level == 0 else None, shortcut_widget=self)

		self.audiomenu = Menu(self.compmenu, tearoff=0)
		audio_compression = (
			(CompressionType.Audio.setting(level=0), Key.F6),
			(CompressionType.Audio.setting(level=1), Key.F7),
			(CompressionType.Audio.setting(level=2), Key.F8),
		)
		for compression,shortcut in audio_compression:
			self.audiomenu.add_radiobutton(label=compression.level_name(), underline=0, variable=self.compvar, value=str(compression), shortcut=shortcut, shortcut_widget=self)

		self.compmenu.add_radiobutton(label='Auto-Select', underline=0, variable=self.compvar, value=str(CompressionType.Auto.setting()), shortcut=Key.F4, shortcut_widget=self)
		self.compmenu.add_separator()
		self.compmenu.add_radiobutton(label='None', underline=0, variable=self.compvar, value=str(CompressionType.NoCompression.setting()), shortcut=Key.F2, shortcut_widget=self)
		self.compmenu.add_radiobutton(label='Standard', underline=0, variable=self.compvar, value=str(CompressionType.Standard.setting()), shortcut=Key.F3, shortcut_widget=self)
		self.compmenu.add_cascade(label='Deflate', menu=self.deflatemenu, underline=0)
		self.compmenu.add_cascade(label='Audio', menu=self.audiomenu, underline=0)
		
		for index,(locale_name,locale) in enumerate(LOCALE_CHOICES):
			command = None
			if locale != None:
				locale_name += ' [%d]' % locale
			else:
				command = self.choose_other_locale
			self.locale_menu.add_radiobutton(label=locale_name, variable=self.locale_menu_choice, value=index, command=command)

		self.setmenu.add_command(label='Settings Dialog', command=lambda: self.mansets(1), underline=0, shortcut=Ctrl.m, shortcut_widget=self)
		self.setmenu.add_separator()
		self.setmenu.add_cascade(label='Compression', menu=self.compmenu, underline=0)
		self.setmenu.add_checkbutton(label='Encrypt', underline=0, onvalue=1, offvalue=0, variable=self.encvar, shortcut=Key.F5, shortcut_widget=self)
		self.setmenu.add_cascade(label='Locale', menu=self.locale_menu, underline=0)

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Open', command=self.openfile, underline=0)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Extract', command=self.extract, underline=0)
		self.listmenu.add_command(label='Delete', command=self.remove, underline=0)
		self.listmenu.add_command(label='Rename', command=self.rename, underline=0)
		self.listmenu.add_command(label='Change Locale', command=self.changelocale, underline=0)
		
		self.listbox = ReportList(self, ['Name','Size','Ratio','Packed','Locale','Attributes',None], EXTENDED, self.select, self.do_rename, self.popup, self.openfile, min_widths=[50]*6)
		self.listbox.ascending_arrow = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','arrow.gif'))
		self.listbox.descending_arrow = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','arrowup.gif'))
		self.listbox.blank_arrow = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','arrowblank.gif'))
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
		statusbar = StatusBar(self)
		statusbar.add_label(self.status, width=25)
		statusbar.add_label(self.selected, width=30)
		statusbar.add_label(self.info, width=30)
		statusbar.add_label(self.locale_status, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		self.load_settings()

		if guifile:
			self.open(file=guifile)

		UpdateDialog.check_update(self, 'PyMPQ')

	def choose_other_locale(self):
		locale_dialog = LocaleDialog(self, title='Change locale', message='Type a custom locale or choose an existing locale')
		if locale_dialog.save:
			locale = locale_dialog.result.get()
			self.settings.locale = locale
			self.update_locale_status()
		else:
			locale_index = find_locale_index(self.settings.locale)
			_,locale = LOCALE_CHOICES[locale_index]
			self.after(1, lambda: self.locale_menu_choice.set(locale_index))

	def locale_changed(self, *_):
		locale_index = self.locale_menu_choice.get()
		_,locale = LOCALE_CHOICES[locale_index]
		if locale != None:
			self.settings.locale = locale
		self.update_locale_status()

	def update_locale_status(self):
		locale_index = find_locale_index(self.settings.locale)
		locale_name,_ = LOCALE_CHOICES[locale_index]
		self.locale_status.set('Locale: %s [%d]' % (locale_name, self.settings.locale))

	def load_settings(self):
		self.settings.windows.load_window_size('main', self, default_size=(700,500))
		self.settings.load_pane_sizes('list_sizes', self.listbox.panes, (317,74,45,67,52,64))
		self.compvar.set(self.settings.compression)
		self.encvar.set(self.settings.encrypt)
		self.locale_menu_choice.set(find_locale_index(self.settings.locale))

	def save_settings(self):
		self.settings.windows.save_window_size('main', self)
		self.settings.save_pane_sizes('list_sizes', self.listbox.panes)
		self.settings.compression = self.compvar.get()
		self.settings.encrypt = self.encvar.get()
		self.settings.save()

	def sort(self, column):
		if column == self.settings.sort.column:
			self.settings.sort.ascending = not self.settings.sort.ascending
		else:
			self.settings.sort.column = column
			self.settings.sort.ascending = True
		self.update_columns()
		self.update_list()

	def update_columns(self):
		for column,(button,_) in enumerate(self.listbox.columns):
			image = self.listbox.blank_arrow
			if column == self.settings.sort.column:
				if self.settings.sort.ascending:
					image = self.listbox.ascending_arrow
				else:
					image = self.listbox.descending_arrow
			button['image'] = image

	def is_mpq_open(self):
		return not not self.file

	def is_file_selected(self):
		return not not self.listbox.cur_selection()

	def select(self):
		if self.is_mpq_open():
			selected_indexes = self.listbox.cur_selection()
			total_size = 0
			for index in selected_indexes:
				total_size += self.display_files[index].fullSize
			self.selected.set('Selected %s files, %s' % (len(selected_indexes), format_byte_size(total_size)))
		else:
			self.selected.set('')
		self.action_states()

	def action_states(self):
		is_mpq_open = self.is_mpq_open()
		self.toolbar.tag_enabled('mpq_open', is_mpq_open)
		self.find_button['state'] = NORMAL if is_mpq_open else DISABLED
		self.toolbar.tag_enabled('file_selected', self.is_file_selected())

	def dofilter(self, e=None):
		if not self.is_mpq_open():
			return
		filter = self.filter.get()
		filters = self.settings.get('filters', [])
		if filter in filters:
			filters.remove(filter)
		filters.append(filter)
		if len(filters) > 10:
			del filters[0]
		self.update_list()

	def list_files(self, h=-1):
		close = False
		if h == -1:
			close = True
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Read MPQ (List Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		self.all_files = []
		self.totalsize = 0
		for e in SFileListFiles(h, str('\r\n'.join(self.settings.settings.get('listfiles', [])))):
			if e.fileExists:
				self.all_files.append(e)
				self.totalsize += e.fullSize
		if close:
			MpqCloseUpdatedArchive(h)

	def reset_entry_background_color(self):
		self.textdrop.entry['bg'] = self.textdrop.default_background_color
		self.resettimer = None

	def attributes_for_flags(self, flags):
		attributes = ''
		attributes += 'C' if (flags & (MAFA_COMPRESS | MAFA_COMPRESS2)) else '-'
		attributes += 'E' if (flags & MAFA_ENCRYPT) else '-'
		attributes += 'X' if (flags & MAFA_MODCRYPTKEY) else '-'
		return attributes

	def update_list(self):
		previously_selected = []
		if self.listbox.size():
			for i in self.listbox.cur_selection():
				previously_selected.append(self.display_files[i])
			self.listbox.delete(ALL)
		else:
			return
		if self.is_mpq_open() and self.all_files:
			self.display_files = self.all_files
			filter = self.filter.get()
			if not self.regex.get():
				if not filter.replace('*','').replace('?',''):
					filter = None
				else:
					filter = '^' + re.escape(filter).replace('\\?','.').replace('\\*','.+?') + '$'
			elif filter == '.+':
				filter = None
			if filter:
				try:
					filter = re.compile(filter)
				except:
					filter = None
					self.resettimer = self.after(1000, self.reset_entry_background_color)
					self.textdrop.entry['bg'] = '#FFB4B4'
			if filter:
				self.display_files = [file for file in self.display_files if filter.match(file.fileName)]
			def keysort(file):
				file_info = [file.fileName, file.fullSize, file.get_compression_ratio(), file.compressedSize, file.locale, file.flags]
				# We only need to re-arrange the sort info if we are sorting by something other than the first column
				if self.settings.sort.column:
					# Move sort column to front of info to sort
					file_info.insert(0, file_info[self.settings.sort.column])
					del file_info[self.settings.sort.column+1]
				return tuple(file_info)
			self.display_files.sort(key=keysort, reverse=not self.settings.sort.ascending)
			for file in self.display_files:#fileName,fullSize,compresssionRatio,compressedSize,locale,flags in file_info:
				i = (
					file.fileName,
					format_byte_size(file.fullSize),
					'%d%%' % int(file.get_compression_ratio()*100),
					format_byte_size(file.compressedSize),
					str(file.locale),
					self.attributes_for_flags(file.flags),
					''
				)
				self.listbox.insert(END, i)
				if file in previously_selected:
					self.listbox.select_set(END)
		self.action_states()

	def update_info(self, h=None):
		if self.is_mpq_open() or h:
			close = False
			if h == None:
				close = True
				h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Read MPQ (Update Info)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			files = SFileGetFileInfo(h,SFILE_INFO_NUM_FILES)
			self.info.set('Total %s/%s files, %s' % (len(self.all_files),files,format_byte_size(self.totalsize)))
			can_compact = files > len(self.all_files)
			self.toolbar.tag_enabled('can_compact', can_compact)
			if close:
				MpqCloseUpdatedArchive(h)
		else:
			self.info.set('')

	def do_rename(self, index, new_filename):
		file = self.display_files[index]
		success = False
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if not SFInvalidHandle(h) and MpqRenameAndSetFileLocale(h, file.fileName, new_filename, file.locale, file.locale):
			success = True
		MpqCloseUpdatedArchive(h)
		return success

	def mafa_settings(self, filename):
		compression = CompressionSetting.parse_value(self.compvar.get())
		if compression.type == CompressionType.Auto:
			extension = '.' + filename.split(os.extsep)[-1]
			if extension in self.settings.settings.autocompression:
				compression = CompressionSetting.parse_value(self.settings.settings.autocompression[extension])
			else:
				compression = CompressionSetting.parse_value(self.settings.autocompression.Default)
		flags = MAFA_REPLACE_EXISTING
		mafa_compression = compression.type.mafa_type()
		if mafa_compression != 0:
			flags |= MAFA_COMPRESS
		if self.settings.encrypt:
			flags |= MAFA_ENCRYPT
		return (flags, mafa_compression, compression.mafa_level())

	def popup(self, e, i):
		if not self.listbox.cur_selection():
			self.listbox.select_set(i)
		self.listmenu.post(*self.winfo_pointerxy())

	def changelocale(self):
		dialog = LocaleDialog(self)
		if dialog.save:
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Write MPQ (Change Locale)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			locale = dialog.result.get()
			for i in self.listbox.cur_selection():
				# TODO: Warn about files not updated
				if self.display_files[i].locale != locale and MpqSetFileLocale(h, self.display_files[i].fileName, self.display_files[i].locale, locale):
					self.display_files[i].locale = locale
			self.list_files(h)
			MpqCloseUpdatedArchive(h)
			self.update_list()

	def openfile(self, e=None):
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Open MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		try:
			for i in self.listbox.cur_selection():
				file = self.display_files[i]
				try:
					os.makedirs(os.path.join(self.temp_folder,os.path.dirname(file.fileName)))
				except (OSError, IOError) as e:
					if e.errno != 17:
						raise
				SFileSetLocale(file.locale)
				fh = SFileOpenFileEx(h, file.fileName)
				if fh:
					data,_ = SFileReadFile(fh)
					SFileCloseFile(fh)
					filepath = os.path.join(self.temp_folder,file.fileName)
					f = open(filepath, 'wb')
					f.write(data)
					f.close()
					start_file(filepath)
			if not self.thread.is_running():
				self.thread.start()
		except:
			raise
		finally:
			MpqCloseUpdatedArchive(h)

	def update_files(self, files):
		if len(files) == 1:
			if not MessageBox.askyesno(parent=self, title='File Edited', message='File "%s" has been modified since it was extracted.\n\nUpdate the archive with this file?' % files[0]):
				return
		else:
			u = UpdateFiles(self, files)
			if not u.files:
				return
			files = u.files
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Write MPQ (Update Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for filename in files:
			mafa_settings = self.mafa_settings(filename)
			MpqAddFileToArchiveEx(h, os.path.join(self.temp_folder,filename), filename, *mafa_settings)
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def new(self, key=None):
		file = self.settings.lastpath.mpq.select_save_file(self, title='Create new MPQ', filetypes=[('StarCraft MPQ','*.mpq'),('Embedded MPQ','*.exe'),('StarCraft Map','*.scm'),('BroodWar Map','*.scx')])
		if file:
			h = MpqOpenArchiveForUpdateEx(file, MOAU_CREATE_ALWAYS, self.settings.settings.defaults['maxfiles'], self.settings.settings.defaults['blocksize'])
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('New MPQ', "The MPQ could not be created/opened."))
				return
			MpqCloseUpdatedArchive(h)
			self.file = file
			self.all_files = []
			self.display_files = []
			self.totalsize = 0
			self.status.set('Editing new MPQ.')
			self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
			self.update_list()
			self.select()

	def open(self, key=None, file=None):
		if file == None:
			file = self.settings.lastpath.mpq.select_open_file(self, title='Open MPQ', filetypes=[('Any MPQ', '*.mpq;*.exe;*.scm;*.scx'),('StarCraft MPQ','*.mpq'),('Embedded MPQ','*.exe'),('StarCraft Map','*.scm'),('BroodWar Map','*.scx')])
			if not file:
				return
		h = MpqOpenArchiveForUpdateEx(file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			MessageBox.askquestion(parent=self, title='Open', message='There is no MPQ in "%s".' % file, type=MessageBox.OK)
			return
		self.file = file
		self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
		self.status.set('Load Successful!')
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def close(self, key=None):
		if not self.is_mpq_open():
			return
		self.file = None
		self.all_files = []
		self.display_files = []
		self.title('PyMPQ %s' % LONG_VERSION)
		self.status.set('Open or create an MPQ.')
		self.cleanup_temp()
		self.update_info()
		self.update_list()
		self.select()

	def add(self, key=None):
		if not self.is_mpq_open():
			return
		files = self.settings.lastpath.files.select_open_files(self, key='import', title='Add files...')
		if files:
			f = FolderDialog(self)
			if f.save:
				h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
				if SFInvalidHandle(h):
					ErrorDialog(self, PyMSError('Write MPQ (Add File)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
					return
				SFileSetLocale(self.settings.locale)
				for filepath in files:
					filename = os.path.basename(filepath)
					folder = self.settings['import'].get('add_folder', '')
					if folder:
						filename = folder + filename
					mafa_settings = self.mafa_settings(filename)
					MpqAddFileToArchiveEx(h, filepath, filename, *mafa_settings)
				self.list_files(h)
				self.update_info(h)
				MpqCloseUpdatedArchive(h)
				self.update_list()
				self.select()

	def adddir(self, key=None):
		if not self.is_mpq_open():
			return
		path = self.settings.lastpath.files.select_directory(self, key='import_dir', title='Add files from folder...')
		if not path:
			return
		path = os.path.join(path,'')
		fo = FolderDialog(self)
		if fo.save:
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Write MPQ (Add Folder)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			for root,_,filenames in os.walk(path):
				folder = self.settings['import'].get('add_folder', '')
				path_folder = root.replace(path,'')
				if path_folder:
					folder += '\\'.join(os.path.split(path_folder)) + '\\'
				for filename in filenames:
					mafa_settings = self.mafa_settings(filename)
					MpqAddFileToArchiveEx(h, os.path.join(root,filename), folder + filename, *mafa_settings)
			self.list_files(h)
			self.update_info(h)
			MpqCloseUpdatedArchive(h)
			self.update_list()
			self.select()

	def remove(self, key=None):
		if not self.is_file_selected():
			return
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Write MPQ (Remove Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for i in self.listbox.cur_selection():
			filename,_,_,_,locale,_,_ = self.listbox.get(i)
			MpqDeleteFileWithLocale(h, filename, int(locale))
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def rename(self, key=None):
		if not self.is_file_selected():
			return
		self.listbox.columns[ColumnID.Filename][1].edit()

	# def editlistfile(self, key=None):
		# if not self.is_mpq_open():
			# return
		# pass

	def extract(self, key=None):
		if not self.is_file_selected():
			return
		path = self.settings.lastpath.files.select_directory(self, key='export', title='Extract files...')
		if not path:
			return
		h = SFileOpenArchive(self.file)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Read MPQ (Extract Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for index in self.listbox.cur_selection():
			file = self.display_files[index]
			path_components = file.fileName.split('\\')
			try:
				os.makedirs(os.path.join(path,*path_components[:-1]))
			except (OSError, IOError) as e:
				if e.errno != 17:
					raise
			SFileSetLocale(file.locale)
			fh = SFileOpenFileEx(h, file.fileName)
			if fh:
				data,_ = SFileReadFile(fh)
				SFileCloseFile(fh)
				f = open(os.path.join(path,*path_components),'wb')
				f.write(data)
				f.close()
			else:
				ErrorDialog(self, PyMSError('Extract', "Couldn't load file '%s'" % file.fileName))
		SFileCloseArchive(h)

	def mansets(self, key=None):
		if key:
			SettingsDialog(self, [('General',GeneralSettings),('List Files',ListfileSettings),('Compression Auto-Selection',CompressionSettings)], (400,255), None, settings=self.settings)
		else:
			self.setmenu.post(*self.winfo_pointerxy())

	def compact(self, key=None):
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Compact MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		MpqCompactArchive(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)

	def register(self, e=None):
		try:
			register_registry('PyMPQ','','mpq',os.path.join(BASE_DIR, 'PyMPQ.pyw'),os.path.join(BASE_DIR,'PyMS','Images','PyMPQ.ico'))
		except PyMSError as e:
			ErrorDialog(self, e)

	def help(self, e=None):
		HelpDialog(self, self.settings, 'Help/Programs/PyMPQ.md')

	def about(self, key=None):
		AboutDialog(self, 'PyMPQ', LONG_VERSION)

	def cleanup_temp(self):
		self.thread.end()
		if os.path.exists(self.temp_folder):
			shutil.rmtree(self.temp_folder)

	def exit(self, e=None):
		self.cleanup_temp()
		self.save_settings()
		self.destroy()
