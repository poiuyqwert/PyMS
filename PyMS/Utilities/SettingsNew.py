
from .UIKit import FileDialog, RE_GEOMETRY, parse_geometry, build_geometry, parse_resizable, FileType, WindowExtensions
from . import Assets
from .WarnDialog import WarnDialog
from .fileutils import check_allow_overwrite_internal_file

from numbers import Number
import os, json

from typing import Any, Sequence, TypeAlias

JSONValue: TypeAlias = int | float | str | bool | None | 'JSONObject' | 'JSONArray'
JSONObject = dict[str, JSONValue]
JSONArray = Sequence[JSONValue]

class SettingObject(object):
	def encode(self): # type: () -> JSONValue
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, data): # type: (JSONValue) -> None
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class Group(SettingObject):
	def encode(self): # type: () -> JSONValue
		import inspect
		data = {}
		for attr, value in inspect.getmembers(self, lambda member: not inspect.ismethod(member)):
			if attr.startswith('_') or not isinstance(value, SettingObject):
				continue
			data[attr] = value.encode()
		return data

	def decode(self, data): # type: (JSONValue) -> None
		if not isinstance(data, dict):
			return
		for attr, attr_data in list(data.items()):
			if not isinstance(attr, str) or not attr.startswith('_') or not hasattr(self, attr):
				continue
			object = getattr(self, attr)
			if not isinstance(object, SettingObject):
				continue
			object.decode(attr_data)

class Settings(Group):
	_name: str
	_version: int

	def __init__(self): # type: () -> None
		Group.__init__(self)
		if self._name is None or self._version is None:
			raise NotImplementedError('`_name` and/or `_version` are not set for `%s`' % self.__class__.__name__)
		self.load()

	def load(self): # type: () -> None
		data = None
		try:
			with open(Assets.settings_file_path(self._name), 'r') as f:
				data = json.load(f)
			if data:
				version = data.get('version')
				if version != self._version: # TODO: Migrations?
					data = None
				else:
					del data['version']
		except:
			data = None
		if data:
			self.decode(data)

	def save(self): # type: () -> None
		try:
			data = self.encode()
			assert isinstance(data, dict)
			data['version'] = self._version
			with open(Assets.settings_file_path(self._name), 'w') as f:
				json.dump(data, f, sort_keys=True, indent=4)
		except:
			pass

class String(SettingObject):
	def __init__(self, default=None): # type: (str | None) -> None
		self.value = default

	def encode(self): # type: () -> JSONValue
		return self.value

	def decode(self, value): # type: (JSONValue) -> None
		if not isinstance(value, str):
			return
		self.value = value

class Int(SettingObject):
	def __init__(self, default=None): # type: (int | None) -> None
		self.value = default

	def encode(self): # type: () -> JSONValue
		return self.value

	def decode(self, value): # type: (JSONValue) -> None
		if not isinstance(value, Number):
			return
		self.value = int(value)

class Float(SettingObject):
	def __init__(self, default=None):  # type: (float | None) -> None
		self.value = default

	def encode(self): # type: () -> JSONValue
		return self.value

	def decode(self, value): # type: (JSONValue) -> None
		if not isinstance(value, Number):
			return
		self.value = float(value)

class Boolean(SettingObject):
	def __init__(self, default=None): # type: (bool | None) -> None
		self.value = default

	def encode(self): # type: () -> JSONValue
		return self.value

	def decode(self, value): # type: (JSONValue) -> None
		if not isinstance(value, Number):
			return
		self.value = bool(value)

class WindowGeometry(SettingObject):
	def __init__(self, default_size=None, default_centered=True): # type: (tuple[int, int] | None, bool) -> None
		self._geometry = None # type: str | None
		self._default_size = default_size
		self._default_centered = default_centered

	def save(self, window, closing=True): # type: (WindowExtensions, bool) -> None
		resizable_w,resizable_h = parse_resizable(window.resizable())
		w,h,x,y,_ = parse_geometry(window.winfo_geometry())
		if resizable_w or resizable_h:
			maximized = False
			if window.is_maximized():
				maximized = True
				window.wm_state('normal')
				window.update_idletasks()
				w,h,x,y,_ = parse_geometry(window.winfo_geometry())
				if not closing:
					window.wm_state('zoomed')
					window.update_idletasks()
			self._geometry = build_geometry(pos=(x,y), size=(w,h), maximized=maximized)
		else:
			self._geometry = build_geometry(pos=(x,y))

	def load(self, window): # type: (WindowExtensions) -> None
		if self._geometry:
			w,h,x,y,fullscreen = parse_geometry(self._geometry)
			# if position:
			# 	x,y = position
			resizable_w,resizable_h = parse_resizable(window.resizable())
			can_fullscreen = (resizable_w and resizable_h)
			if (resizable_w or resizable_h) and w is not None and h is not None:
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
				window.geometry(build_geometry(pos=(x,y), size=(w,h)))
			else:
				window.geometry(build_geometry(pos=(x,y)))
			window.update_idletasks()
			if fullscreen and can_fullscreen:
				try:
					window.wm_state('zoomed')
				except:
					pass
		else:
			window.update_idletasks()
			w,h,x,y,_ = parse_geometry(window.winfo_geometry())
			if self._default_size:
				size = self._default_size
			else:
				size = (w,h)
			pos: tuple[int, int] | None = None
			if self._default_centered:
				window.update_idletasks()
				screen_w = window.winfo_screenwidth()
				screen_h = window.winfo_screenheight()
				pos = ((screen_w - w) // 2, (screen_h - h) // 2)
			window.geometry(build_geometry(pos=pos, size=size))

	def encode(self): # type: () -> JSONValue
		return self._geometry

	def decode(self, geometry): # type: (JSONValue) -> None
		if not isinstance(geometry, str) or not RE_GEOMETRY.match(geometry):
			return
		self._geometry = geometry

# TODO: This simply replicates the existing Settings use case, but should this be more complicated like `SelectFile`?
class File(SettingObject):
	def __init__(self, default=None): # type: (str | None) -> None
		self._file_path = default

	def encode(self): # type: () -> JSONValue
		return self._file_path

	def decode(self, file_path): # type: (JSONValue) -> None
		if not isinstance(file_path, str):
			return
		if not file_path.startswith('MPQ:') and not os.path.exists(file_path):
			return
		self._file_path = file_path

class SelectFile(SettingObject):
	def __init__(self, name, filetypes, initial_filename=None): # type: (str, list[FileType], str | None) -> None
		self._open_directory = Assets.base_dir
		self._save_directory = Assets.base_dir
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._initial_filename = initial_filename

	def _select_file(self, window, save): # type: (WindowExtensions, bool) -> (str | None)
		setattr(window, '_pyms__window_blocking', True)
		path: str | None
		if save:
			path = FileDialog.asksaveasfilename(
				parent=window,
				title='%s %s' % ('Save' if save else 'Open', self._name),
				initialdir=self._save_directory if save else self._open_directory,
				filetypes=self._filetypes,
				defaultextension=self._default_extension,
				initialfile=self._initial_filename
			)
		else:
			path = FileDialog.askopenfilename(
				parent=window,
				title='%s %s' % ('Save' if save else 'Open', self._name),
				initialdir=self._save_directory if save else self._open_directory,
				filetypes=self._filetypes,
				defaultextension=self._default_extension,
				initialfile=self._initial_filename
			)
		if save and path and not check_allow_overwrite_internal_file(path):
			path = None
		setattr(window, '_pyms__window_blocking', False)
		if path:
			directory = os.path.dirname(path)
			if save:
				self._save_directory = directory
			else:
				self._open_directory = directory
		return path

	def select_open(self, window): # type: (WindowExtensions) -> (str | None)
		return self._select_file(window, False)

	def select_save(self, window): # type: (WindowExtensions) -> (str | None)
		return self._select_file(window, True)

	def encode(self): # type: () -> JSONValue
		return {
			'open': self._open_directory,
			'save': self._save_directory
		}

	def decode(self, data): # type: (JSONValue) -> None
		if not isinstance(data, dict):
			return
		open_directory = data.get('open')
		if isinstance(open_directory, str) and os.path.exists(open_directory):
			self._open_directory = open_directory
		save_directory = data.get('save')
		if isinstance(save_directory, str) and os.path.exists(save_directory):
			self._save_directory = save_directory

class SelectFiles(SettingObject):
	def __init__(self, title, filetypes): # type: (str, list[FileType]) -> None
		self._directory = Assets.base_dir
		self._title = title
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)

	def select_open(self, window): # type: (WindowExtensions) -> list[str]
		setattr(window, '_pyms__window_blocking', True)
		paths: list[str] | str = FileDialog.askopenfilename(
			parent=window,
			multiple=True,
			title=self._title,
			initialdir=self._directory,
			filetypes=self._filetypes,
			defaultextension=self._default_extension
		) # type: ignore[call-arg]
		setattr(window, '_pyms__window_blocking', False)
		if isinstance(paths, str):
			if paths:
				paths = [paths]
			else:
				paths = []
		if paths:
			self._directory = os.path.dirname(paths[0])
		return paths

	def encode(self): # type: () -> JSONValue
		return self._directory

	def decode(self, directory): # type: (JSONValue) -> None
		if not isinstance(directory, str) or not os.path.exists(directory):
			return
		self._directory = directory

class SelectDirectory(SettingObject):
	def __init__(self, title='Select Folder'): # type: (str) -> None
		self._directory = Assets.base_dir
		self._title = title

	def select_open(self, window): # type: (WindowExtensions) -> (str | None)
		setattr(window, '_pyms__window_blocking', True)
		path = FileDialog.askdirectory(parent=window, title=self._title, initialdir=self._directory)
		setattr(window, '_pyms__window_blocking', False)
		if path:
			self._directory = path
		return path

	def encode(self): # type: () -> JSONValue
		return self._directory

	def decode(self, directory): # type: (JSONValue) -> None
		if not isinstance(directory, str) or not os.path.exists(directory):
			return
		self._directory = directory

class Warning(SettingObject):
	def __init__(self, message, title='Warning!', remember_version=1): # type: (str, str, int) -> None
		self._seen_version = 0
		self._message = message
		self._title = title
		self._remember_version = remember_version

	def present(self, window): # type: (WindowExtensions) -> None
		if self._remember_version <= self._seen_version:
			return
		dialog = WarnDialog(window, self._message, self._title, show_dont_warn=True)
		if dialog.dont_warn.get():
			self._seen_version = self._remember_version

	def encode(self): # type: () -> JSONValue
		return self._seen_version

	def decode(self, seen_version): # type: (JSONValue) -> None
		if not isinstance(seen_version, int):
			return
		self._seen_version = seen_version
