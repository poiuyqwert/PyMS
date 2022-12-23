
from .utils import isstr
from .UIKit import FileDialog, RE_GEOMETRY, parse_geometry, parse_resizable, HORIZONTAL
from .UIKit.Widgets import Toplevel, PanedWindow
from .UIKit.Components import MainWindow
from .UIKit.FileType import FileType
from . import Assets
from .WarnDialog import WarnDialog
from .fileutils import check_allow_overwrite_internal_file

from numbers import Number
import os, json

class SettingObject(object):
	def encode(self):
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, data):
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class Group(SettingObject):
	def encode(self):
		import inspect
		data = {}
		for attr, value in inspect.getmembers(self, lambda member: not inspect.ismethod(member)):
			if attr.startswith('_') or not isinstance(value, SettingObject):
				continue
			data[attr] = value.encode()
		return data

	def decode(self, data):
		if not isinstance(data, dict):
			return
		for attr, attr_data in data.items():
			if not isstr(attr) or attr.startswith('_') or not hasattr(self, attr):
				continue
			object = getattr(self, attr)
			if not isinstance(object, SettingObject):
				continue
			object.decode(attr_data)

class SettingsFile(Group):
	_name = None # type: str
	_version = None # type: int
	_migrations = [] # type: list[Callable[Any, Any | None]]

	def __init__(self): # type: () -> SettingsFile
		Group.__init__(self)
		if self._name == None or self._version == None:
			raise NotImplementedError('`_name` and/or `_version` are not set for `%s`' % self.__class__.__name__)
		self.load()

	def load(self):
		data = None
		try:
			with open(Assets.settings_file_path(self._name), 'r') as f:
				data = json.load(f)
			if data:
				version = data.get('version', 1)
				if 'version' in data:
					del data['version']
				try:
					version = int(version)
				except:
					version = None
				if version == None or version > self._version:
					data = None
				elif version < self._version:
					for old_version in range(version, self._version):
						try:
							data = self.migrate_from(old_version, data)
						except:
							data = None
						if data == None:
							break
		except:
			data = None
		if data:
			self.decode(data)

	def save(self):
		try:
			data = self.encode()
			data['version'] = self._version
			with open(Assets.settings_file_path(self._name + '_new'), 'w') as f:
				json.dump(data, f, sort_keys=True, indent=4)
		except:
			pass

	def migrate_from(self, old_version, data): # type: (int, Any) -> Any
		"""If the settings file being loaded is an old version, the `migrate_from` method will be called for each version prior to the current version.
		By default this will use `self._migrations` to do the migrations."""
		if not self._migrations:
			return None
		index = old_version - 1
		if index >= len(self._migrations):
			return None
		return self._migrations[index](data)

class String(SettingObject):
	def __init__(self, default=None, optional=False): # type: (str, bool) -> String
		self._default = default
		self._optional = optional
		self.value = default

	def encode(self):
		return self.value

	def decode(self, value):
		if not isstr(value):
			value = None
		if value == None and not self._optional:
			value = self._default
		self.value = value

class StringList(SettingObject):
	def __init__(self): # type: (list[str]) -> StringList
		self.value = []

	def encode(self):
		return self.value

	def decode(self, value):
		if not isinstance(value, list):
			value = []
		else:
			value = list(string for string in value if isstr(string))
		self.value = value

class Int(SettingObject):
	def __init__(self, default=None, optional=False): # type: (int, bool) -> Int
		self._default = default
		self._optional = optional
		self.value = default

	def encode(self):
		return self.value

	def decode(self, value):
		if not isinstance(value, Number):
			value = None
		else:
			value = int(value)
		if value == None and not self._optional:
			value = self._default
		self.value = value

class Float(SettingObject):
	def __init__(self, default=None, optional=False):  # type: (float, bool) -> Float
		self._default = default
		self._optional = optional
		self.value = default

	def encode(self):
		return self.value

	def decode(self, value):
		if not isinstance(value, Number):
			value = None
		else:
			value = float(value)
		if value == None and not self._optional:
			value = self._default
		self.value = value

class Boolean(SettingObject):
	def __init__(self, default=None, optional=False): # type: (bool, bool) -> Boolean
		self._default = default
		self._optional = optional
		self.value = default

	def encode(self):
		return self.value

	def decode(self, value):
		if not isinstance(value, Number):
			value = None
		else:
			value = bool(value)
		if value == None and not self._optional:
			value = self._default
		self.value = value

class Enum(SettingObject):
	def __init__(self, options, default_option): # type: (list[str | int], str | int) -> Enum
		self._options = options
		self._default_option = default_option
		self.value = default_option

	def encode(self):
		return self.value

	def decode(self, value):
		if not value in self._options:
			value = self._default_option
		self.value = value

class WindowGeometry(SettingObject):
	def __init__(self, default_size=None, default_centered=True): # type: (tuple[int,int] | None, bool) -> WindowGeometry
		self._geometry = None
		self._default_size = default_size
		self._default_centered = default_centered

	def save(self, window, closing=True): # type: (Toplevel | MainWindow, bool) -> None
		resizable_w,resizable_h = parse_resizable(window.resizable())
		w,h,x,y,_ = parse_geometry(window.winfo_geometry())
		if resizable_w or resizable_h:
			z = ''
			if window.is_maximized():
				z = '^'
				window.wm_state('normal')
				window.update_idletasks()
				w,h,x,y,_ = parse_geometry(window.winfo_geometry())
				if not closing:
					window.wm_state('zoomed')
					window.update_idletasks()
			self._geometry = '%sx%s+%d+%d%s' % (w,h,x,y,z)
		else:
			self._geometry = '+%d+%d' % (x,y)

	def load(self, window): # type: (Toplevel | MainWindow) -> None
		if self._geometry:
			w,h,x,y,fullscreen = parse_geometry(self._geometry)
			# if position:
			# 	x,y = position
			resizable_w,resizable_h = parse_resizable(window.resizable())
			can_fullscreen = (resizable_w and resizable_h)
			if (resizable_w or resizable_h) and w != None and h != None:
				cur_w,cur_h,_,_,_ = parse_geometry(window.winfo_geometry())
				min_w,min_h = window.minsize()
				# max_w,max_h = window.maxsize()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				if resizable_w:
					if x+w > screen_w:
						x = screen_w-w
					if x < 0:
						x = 0
					w = max(min_w,min(screen_w,w))
				else:
					w = cur_w
				if resizable_h:
					if y+h > screen_h:
						y = screen_h-h
					if y < 0:
						y = 0
					h = max(min_h,min(screen_h,h))
				else:
					h = cur_h
				window.geometry('%dx%d+%d+%d' % (w,h, x,y))
			else:
				window.geometry('+%d+%d' % (x,y))
			window.update_idletasks()
			if fullscreen and can_fullscreen:
				try:
					window.wm_state('zoomed')
				except:
					pass
		else:
			window.update_idletasks()
			w,h,x,y,_ = parse_geometry(window.winfo_geometry())
			geometry = ''
			if self._default_size:
				w,h = self._default_size
				geometry = '%dx%d' % self._default_size
			else:
				geometry = '%dx%d' % (w,h)
			# if position:
			# 	geometry += '+%d+%d' % position
			if self._default_centered:
				window.update_idletasks()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				geometry += '+%d+%d' % ((screen_w-w)/2,(screen_h-h)/2)
			window.geometry(geometry)

	def encode(self):
		return self._geometry

	def decode(self, geometry):
		if not isstr(geometry) or not RE_GEOMETRY.match(geometry):
			return
		self._geometry = geometry

class PaneSizes(SettingObject):
	def __init__(self, default_sizes=None): # type: (list[int] | int | None) -> PaneSizes
		self._default_sizes = default_sizes
		self._sizes = []

	def save(self, pane): # type: (PanedWindow) -> None
		axis = 0 if pane.cget('orient') == HORIZONTAL else 1
		self._sizes = []
		prev_coord = 0
		for index in range(len(pane.panes())-1):
			coord = pane.sash_coord(index)[axis]
			self._sizes.append(coord - prev_coord)
			prev_coord = coord

	def load(self, pane): # type: (PanedWindow) -> None
		axis = 0 if pane.cget('orient') == HORIZONTAL else 1
		coords = [0,0]
		for index in range(len(pane.panes())-1):
			size = 0
			if index < len(self._sizes):
				size = self._sizes[index]
			elif isinstance(self._default_sizes, list) and index < len(self._default_sizes):
				size = self._default_sizes[index]
			elif isinstance(self._default_sizes, int):
				size = self._default_sizes
			else:
				return
			coords[axis] += size
			pane.sash_place(index, *size)

	def encode(self):
		if self._sizes and len(self._sizes) == 1:
			return self._sizes[0]
		return self._sizes

	def decode(self, sizes):
		if isinstance(sizes, list):
			self._sizes = sizes
		elif isinstance(sizes, Number):
			self._sizes = [int(sizes)]
		else:
			self._sizes = []

# TODO: This simply replicates the existing Settings use case, but should this be more complicated like `SelectFile`?
class File(SettingObject):
	def __init__(self, default=None): # type: (str) -> File
		self.path = default

	def encode(self):
		return self.path

	def decode(self, file_path):
		if not isstr(file_path):
			return
		if not file_path.startswith('MPQ:') and not os.path.exists(file_path):
			return
		self.path = file_path

class SelectFile(SettingObject):
	def __init__(self, name, filetypes, initial_filename=None): # type: (str, list[FileType], str) -> SelectFile
		self._open_directory = Assets.base_dir
		self._save_directory = Assets.base_dir
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._initial_filename = initial_filename

	def _select_file(self, window, name, save): # type: (Toplevel | MainWindow, str | None, bool) -> None
		dialog = FileDialog.asksaveasfilename if save else FileDialog.askopenfilename
		window._pyms__window_blocking = True
		kwargs = {}
		if self._initial_filename:
			kwargs['initialfile'] = self._initial_filename
		path = dialog(
			parent=window,
			title='%s %s' % ('Save' if save else 'Open', name or self._name),
			initialdir=self._save_directory if save else self._open_directory,
			filetypes=self._filetypes,
			defaultextension=self._default_extension,
			**kwargs
		)
		if save and path and not check_allow_overwrite_internal_file(path):
			path = None
		window._pyms__window_blocking = False
		if path:
			directory = os.path.dirname(path)
			if save:
				self._save_directory = directory
			else:
				self._open_directory = directory
		return path

	def select_open(self, window, name=None): # type: (Toplevel | MainWindow, str | None) -> None
		self._select_file(window, name, False)

	def select_save(self, window, name=None): # type: (Toplevel | MainWindow, str | None) -> None
		self._select_file(window, name, True)

	def encode(self):
		return {
			'open': self._open_directory,
			'save': self._save_directory
		}

	def decode(self, data):
		if not isinstance(data, dict):
			return
		open_directory = data.get('open')
		if isstr(open_directory) and os.path.isdir(open_directory):
			self._open_directory = open_directory
		save_directory = data.get('save')
		if isstr(save_directory) and os.path.isdir(save_directory):
			self._save_directory = save_directory

class SelectFiles(SettingObject):
	def __init__(self, title, filetypes): # type: (str, list[FileType]) -> SelectFiles
		self._directory = Assets.base_dir
		self._title = title
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)

	def select_open(self, window, title=None): # type: (Toplevel | MainWindow, str | None) -> None
		window._pyms__window_blocking = True
		paths = FileDialog.askopenfilename(
			parent=window,
			multiple=True,
			title=title or self._title,
			initialdir=self._directory,
			filetypes=self._filetypes,
			defaultextension=self._default_extension
		)
		window._pyms__window_blocking = False
		if isstr(paths):
			if paths:
				paths = [paths]
			else:
				paths = []
		if paths:
			self._directory = os.path.dirname(paths[0])
		return paths

	def encode(self):
		return self._directory

	def decode(self, directory):
		if not isstr(directory) or not os.path.isdir(directory):
			return
		self._directory = directory

class SelectDirectory(SettingObject):
	def __init__(self, title='Select Folder'): # type: (str) -> SelectDirectory
		self._directory = Assets.base_dir
		self._title = title

	def select_open(self, window, title=None): # type: (Toplevel | MainWindow, str | None) -> None
		window._pyms__window_blocking = True
		path = FileDialog.askdirectory(parent=window, title=title or self._title, initialdir=self._directory)
		window._pyms__window_blocking = False
		if path:
			self._directory = path
		return path

	def encode(self):
		return self._directory

	def decode(self, directory):
		if not isstr(directory) or not os.path.isdir(directory):
			return
		self._directory = directory

class Warning(SettingObject):
	def __init__(self, message, title='Warning!', remember_version=1): # type: (str, str, int) -> Warning
		self._seen_version = 0
		self._message = message
		self._title = title
		self._remember_version = remember_version

	def present(self, window, message=None, title=None): # type: (Toplevel | MainWindow, str | None, str | None) -> None
		if self._remember_version <= self._seen_version:
			return
		dialog = WarnDialog(window, message or self._message, title or self._title, show_dont_warn=True)
		if dialog.dont_warn.get():
			self._seen_version = self._remember_version

	def encode(self):
		return self._seen_version

	def decode(self, seen_version):
		if not isinstance(seen_version, int):
			return
		self._seen_version = seen_version
