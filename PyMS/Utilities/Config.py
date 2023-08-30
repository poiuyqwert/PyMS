
from __future__ import annotations

from .UIKit import FileDialog, parse_resizable, FileType, AnyWindow, Geometry, GeometryAdjust, Size, PanedWindow, HORIZONTAL, Misc
from . import Assets
from .MPQHandler import MPQHandler

from numbers import Number
import os, json
from enum import Enum

from typing import Any, Sequence, TypeAlias, Protocol, runtime_checkable, Generic, TypeVar, Callable

JSONValue: TypeAlias = 'int | float | str | bool | None | JSONObject | JSONArray'
JSONObject = dict[str, JSONValue]
JSONArray = Sequence[JSONValue]

def migrate_nest(data: dict, keypath: tuple[str, ...]) -> dict:
	'''Ensure there are nested `dict` objects in all parts of the keypath'''
	for key in keypath:
		sub_data = data.get(key)
		if not isinstance(sub_data, dict):
			sub_data = {}
			data[key] = sub_data
		data = sub_data
	return data

def migrate_field(data: dict, from_keypath: tuple[str, ...], to_keypath: tuple[str, ...]) -> None:
	value: Any | None = None
	obj: Any = data
	for key in from_keypath:
		if not isinstance(obj, dict):
			return
		if not key in obj:
			return
		value = obj[key]
	if len(to_keypath) > 1:
		data = migrate_nest(data, to_keypath[:-1])
	data[to_keypath[-1]] = value

def migrate_fields(data: dict, keypaths: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]):
	for from_keypath,to_keypath in keypaths:
		migrate_field(data, from_keypath, to_keypath)

@runtime_checkable
class ConfigObject(Protocol):
	def encode(self) -> JSONValue:
		...

	def decode(self, data: JSONValue) -> None:
		...

	def save_state(self) -> None:
		...

	def reset_state(self) -> None:
		...

class Group(ConfigObject):
	def encode(self) -> JSONValue:
		import inspect
		data = {}
		for attr, _ in inspect.getmembers(self, lambda member: not inspect.ismethod(member) and not inspect.isclass(member)):
			if attr.startswith('_'):
				continue
			value = getattr(self, attr)
			if not isinstance(value, ConfigObject):
				continue
			key = attr.rstrip('_')
			data[key] = value.encode()
		return data

	def decode(self, data: JSONValue) -> None:
		if not isinstance(data, dict):
			return
		for attr, attr_data in list(data.items()):
			if not isinstance(attr, str) or attr.startswith('_'):
				continue
			if not hasattr(self, attr):
				attr = attr + '_'
				if not hasattr(self, attr):
					continue
			object = getattr(self, attr)
			if not isinstance(object, ConfigObject):
				continue
			object.decode(attr_data)

	def save_state(self) -> None:
		import inspect
		for attr, _ in inspect.getmembers(self, lambda member: not inspect.ismethod(member) and not inspect.isclass(member)):
			if attr.startswith('_'):
				continue
			value = getattr(self, attr)
			if not isinstance(value, ConfigObject):
				continue
			value.save_state()

	def reset_state(self) -> None:
		import inspect
		for attr, _ in inspect.getmembers(self, lambda member: not inspect.ismethod(member) and not inspect.isclass(member)):
			if attr.startswith('_'):
				continue
			value = getattr(self, attr)
			if not isinstance(value, ConfigObject):
				continue
			value.reset_state()

class Config(Group):
	_name: str
	_version: int
	_migrations: dict[int, Callable[[dict], None]]

	def __init__(self) -> None:
		Group.__init__(self)
		if self._name is None or self._version is None:
			raise NotImplementedError('`_name` and/or `_version` are not set for `%s`' % self.__class__.__name__)
		self.load()

	def load(self) -> None:
		data: JSONObject | None = None
		try:
			with open(Assets.settings_file_path(self._name), 'r') as f:
				raw_data = json.load(f)
			if isinstance(raw_data, dict):
				data = dict(raw_data)
			if data:
				version = data.get('version')
				try:
					version = int(version) # type: ignore[arg-type]
				except:
					version = None
				if version is None or (version != self._version and self._migrations is None):
					data = None
				elif version is not None and version != self._version and self._migrations is not None:
					for migration_version in range(version, self._version):
						migration = self._migrations.get(migration_version)
						if migration is not None:
							migration(data)
				if data is not None:
					del data['version']
		except:
			data = None
		if data:
			self.decode(data)

	def save(self) -> None:
		try:
			data = self.encode()
			assert isinstance(data, dict)
			data['version'] = self._version
			with open(Assets.settings_file_path(self._name), 'w') as f:
				json.dump(data, f, sort_keys=True, indent=4)
		except:
			pass

class String(ConfigObject):
	def __init__(self, default: str | None = None) -> None:
		self.value = default
		self._saved_state = self.value

	def encode(self) -> JSONValue:
		return self.value

	def decode(self, value: JSONValue) -> None:
		if not isinstance(value, str):
			return
		self.value = value

	def save_state(self) -> None:
		self._saved_state = self.value

	def reset_state(self) -> None:
		self.value = self._saved_state

class Int(ConfigObject):
	def __init__(self, default: int | None = None, limits: tuple[int, int] | None = None) -> None:
		self.value = default
		self._saved_state = self.value
		self.limits = limits

	def encode(self) -> JSONValue:
		return self.value

	def decode(self, value: JSONValue) -> None:
		if not isinstance(value, Number):
			return
		self.value = int(value)
		if self.limits is not None:
			self.value = min(self.limits[1], max(self.limits[0], self.value))

	def save_state(self) -> None:
		self._saved_state = self.value

	def reset_state(self) -> None:
		self.value = self._saved_state

class Float(ConfigObject):
	def __init__(self, default: float | None = None, limits: tuple[float, float] | None = None) -> None:
		self.value = default
		self._saved_state = self.value
		self.limits = limits

	def encode(self) -> JSONValue:
		return self.value

	def decode(self, value: JSONValue) -> None:
		if not isinstance(value, Number):
			return
		self.value = float(value)
		if self.limits is not None:
			self.value = min(self.limits[1], max(self.limits[0], self.value))

	def save_state(self) -> None:
		self._saved_state = self.value

	def reset_state(self) -> None:
		self.value = self._saved_state

class Boolean(ConfigObject):
	def __init__(self, default: bool | None = None) -> None:
		self.value = default
		self._saved_state = self.value

	def encode(self) -> JSONValue:
		return self.value

	def decode(self, value: JSONValue) -> None:
		if not isinstance(value, Number):
			return
		self.value = bool(value)

	def save_state(self) -> None:
		self._saved_state = self.value

	def reset_state(self) -> None:
		self.value = self._saved_state

class WindowGeometry(ConfigObject):
	def __init__(self, default_size: Size | None = None, default_centered: bool = True) -> None:
		self._geometry: str | None = None
		self._saved_state: str | None = self._geometry
		self._default_size = default_size
		self._default_centered = default_centered

	def save(self, window: AnyWindow, closing: bool = True) -> None:
		resizable_w,resizable_h = parse_resizable(window.resizable())
		geometry = Geometry.of(window)
		if resizable_w or resizable_h:
			if geometry.maximized:
				window.wm_state('normal')
				window.update_idletasks()
				geometry = Geometry.of(window)
				geometry.maximized = True
			self._geometry = geometry.text
		else:
			self._geometry = GeometryAdjust(pos=geometry.pos).text

	def load(self, window: AnyWindow) -> None:
		if self._geometry and (geometry_adjust := GeometryAdjust.parse(self._geometry)):
			# if position:
			# 	geometry_adjust.pos = position
			resizable_w,resizable_h = parse_resizable(window.resizable())
			can_maximize = (resizable_w and resizable_h)
			if (resizable_w or resizable_h) and (geometry := geometry_adjust.geometry):
				cur_geometry = Geometry.of(window)
				min_size = Size.of(window.minsize())
				# max_w,max_h = window.maxsize()
				screen_size = Size(window.winfo_screenwidth(), window.winfo_screenheight())
				geometry.clamp(size=screen_size, min_size=min_size)
				if not resizable_w:
					geometry.size.width = cur_geometry.size.width
				if not resizable_h:
					geometry.size.height = cur_geometry.size.height
				window.geometry(geometry.text)
			else:
				if geometry_adjust.size is not None:
					geometry_adjust.size = None
				window.geometry(geometry_adjust.text)
			window.update_idletasks()
			if geometry_adjust.maximized and can_maximize:
				try:
					window.wm_state('zoomed')
				except:
					pass
		else:
			window.update_idletasks()
			geometry = Geometry.of(window)
			geometry_adjust = GeometryAdjust()
			if self._default_size:
				geometry.size = self._default_size
				geometry_adjust.size = self._default_size
			if self._default_centered:
				screen_size = Size(window.winfo_screenwidth(), window.winfo_screenheight())
				geometry_adjust.pos = screen_size.center - geometry.size // 2
			window.geometry(geometry_adjust.text)

	def encode(self) -> JSONValue:
		return self._geometry

	def decode(self, geometry: JSONValue) -> None:
		if not isinstance(geometry, str) or Geometry.parse(geometry) is None:
			return
		self._geometry = geometry

	def save_state(self) -> None:
		self._saved_state = self._geometry

	def reset_state(self) -> None:
		self._geometry = self._saved_state

class PaneSizes(ConfigObject):
	def __init__(self, defaults: list[int] = [], pane_index: int | None = None) -> None:
		self._sizes: list[int] = defaults
		self._pane_index = pane_index
		self._saved_state: list[int] = list(self._sizes)

	def save(self, paned_window: PanedWindow) -> None:
		paned_window.update()
		axis_index = 0 if paned_window.cget('orient') == HORIZONTAL else 1
		if self._pane_index is not None:
			pane_indexes = [self._pane_index]
		else:
			pane_indexes = list(range(len(paned_window.panes())-1))
		sizes: list[int] = []
		offset = 0
		for pane_index in pane_indexes:
			coord = paned_window.sash_coord(pane_index)[axis_index]
			sizes.append(coord - offset)
			offset = coord
		self._sizes = sizes

	def load(self, paned_window: PanedWindow) -> None:
		if not self._sizes:
			return
		paned_window.update()
		axis_index = 0 if paned_window.cget('orient') == HORIZONTAL else 1
		if self._pane_index is not None:
			pane_indexes = [self._pane_index]
		else:
			pane_indexes = list(range(len(paned_window.panes())-1))
		offset = 0
		for pane_index,size in zip(pane_indexes, self._sizes):
			coords = [0, 0]
			offset += size
			coords[axis_index] = offset
			paned_window.sash_place(pane_index, *coords)

	def encode(self) -> JSONValue:
		return self._sizes

	def decode(self, data: JSONValue) -> None:
		if not isinstance(data, list):
			return
		sizes: list[int] = []
		for size in data:
			if not isinstance(size, int):
				return
			sizes.append(size)
		self._sizes = sizes

class File(ConfigObject):
	def __init__(self, default: str, name: str, filetypes: list[FileType], initial_filename: str | None = None) -> None:
		self.file_path = default
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._initial_filename = initial_filename or os.path.basename(self.file_path)
		self._saved_state = self.file_path

	def select_file(self, parent: Misc, name: str | None = None, filetypes: list[FileType] | None = None) -> str | None:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		initial_dir: str | None = None # TODO: Initial dir
		path = FileDialog.askopenfilename(
			parent=window,
			title=f'Select {name or self._name}',
			initialdir=initial_dir or Assets.base_dir,
			filetypes=filetypes or self._filetypes,
			defaultextension=self._default_extension,
			initialfile=self._initial_filename
		)
		setattr(window, '_pyms__window_blocking', False)
		# if path:
		# 	self.file_path = path
		return path

	def select_mpq(self, parent: Misc, mpq_handler: MPQHandler, history_config: List, window_geometry_config: WindowGeometry, name: str | None = None, filetype: FileType | None = None) -> str | None:
		from .MPQSelect import MPQSelect
		mpq_select = MPQSelect(parent, mpq_handler, name or self._name, filetype or self._filetypes[0],history_config, window_geometry_config, action=MPQSelect.Action.select)
		return mpq_select.file

	def encode(self) -> JSONValue:
		return self.file_path

	def decode(self, file_path: JSONValue) -> None:
		if not isinstance(file_path, str):
			return
		if not file_path.startswith('MPQ:') and not os.path.exists(file_path):
			return
		self.file_path = file_path

	def save_state(self) -> None:
		self._saved_state = self.file_path

	def reset_state(self) -> None:
		self.file_path = self._saved_state

class FileOpType(Enum):
	open_save = 0
	import_export = 1

	def title(self, name: str, save: bool) -> str:
		op_name: str
		match self:
			case FileOpType.open_save:
				op_name = 'Save' if save else 'Open'
			case FileOpType.import_export:
				op_name = 'Export' if save else 'Import'
		return f'{op_name} {name}'

	@property
	def save_key(self) -> str:
		match self:
			case FileOpType.open_save:
				return 'save'
			case FileOpType.import_export:
				return 'export'

	@property
	def open_key(self) -> str:
		match self:
			case FileOpType.open_save:
				return 'open'
			case FileOpType.import_export:
				return 'import'

class SelectFile(ConfigObject):
	def __init__(self, name: str, filetypes: list[FileType], op_type: FileOpType = FileOpType.open_save, initial_filename: str | None = None) -> None:
		self._open_directory = Assets.base_dir
		self._saved_state_open = self._open_directory
		self._save_directory = Assets.base_dir
		self._saved_state_save = self._save_directory
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._op_type = op_type
		self._initial_filename = initial_filename

	def _select_file(self, parent: Misc, save: bool, title: str | None, filetypes: list[FileType] | None) -> str | None:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		path: str | None
		if save:
			path = FileDialog.asksaveasfilename(
				parent=window,
				title=title or self._op_type.title(self._name, save),
				initialdir=self._save_directory if save else self._open_directory,
				filetypes=filetypes or self._filetypes,
				defaultextension=self._default_extension,
				initialfile=self._initial_filename
			)
		else:
			path = FileDialog.askopenfilename(
				parent=window,
				title=title or self._op_type.title(self._name, save),
				initialdir=self._save_directory if save else self._open_directory,
				filetypes=filetypes or self._filetypes,
				defaultextension=self._default_extension,
				initialfile=self._initial_filename
			)
		from .fileutils import check_allow_overwrite_internal_file
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

	def select_open(self, parent: Misc, title: str | None = None, filetypes: list[FileType] | None = None) -> str | None:
		return self._select_file(parent, False, title, filetypes)

	def select_save(self, parent: Misc, title: str | None = None, filetypes: list[FileType] | None = None) -> str | None:
		return self._select_file(parent, True, title, filetypes)

	def encode(self) -> JSONValue:
		return {
			self._op_type.open_key: self._open_directory,
			self._op_type.save_key: self._save_directory
		}

	def decode(self, data: JSONValue) -> None:
		if not isinstance(data, dict):
			return
		open_directory = data.get(self._op_type.open_key)
		if isinstance(open_directory, str) and os.path.exists(open_directory):
			self._open_directory = open_directory
		save_directory = data.get(self._op_type.save_key)
		if isinstance(save_directory, str) and os.path.exists(save_directory):
			self._save_directory = save_directory

	def save_state(self) -> None:
		self._saved_state_open = self._open_directory
		self._saved_state_save = self._save_directory

	def reset_state(self) -> None:
		self._open_directory = self._saved_state_open
		self._save_directory = self._saved_state_save

class SelectFiles(ConfigObject):
	def __init__(self, title: str, filetypes: list[FileType]) -> None:
		self._directory = Assets.base_dir
		self._saved_state = self._directory
		self._title = title
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)

	def select_open(self, parent: Misc, filetypes: list[FileType] | None = None) -> list[str]:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		paths: list[str] | str = FileDialog.askopenfilename(
			parent=window,
			multiple=True,
			title=self._title,
			initialdir=self._directory,
			filetypes=filetypes or self._filetypes,
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

	def encode(self) -> JSONValue:
		return self._directory

	def decode(self, directory: JSONValue) -> None:
		if not isinstance(directory, str) or not os.path.exists(directory):
			return
		self._directory = directory

	def save_state(self) -> None:
		self._saved_state = self._directory

	def reset_state(self) -> None:
		self._directory = self._saved_state

class SelectDirectory(ConfigObject):
	def __init__(self, title: str = 'Select Folder', default: str | None = None) -> None:
		self.path = default
		self._saved_state = self.path
		self._title = title

	def select_open(self, parent: Misc) -> str | None:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		path = FileDialog.askdirectory(parent=window, title=self._title, initialdir=self.path or Assets.base_dir)
		setattr(window, '_pyms__window_blocking', False)
		if path:
			self.path = path
		return path

	def encode(self) -> JSONValue:
		return self.path

	def decode(self, directory: JSONValue) -> None:
		if not isinstance(directory, str) or not os.path.exists(directory):
			return
		self.path = directory

	def save_state(self) -> None:
		self._saved_state = self.path

	def reset_state(self) -> None:
		self.path = self._saved_state

class Warning(ConfigObject):
	def __init__(self, message: str, title: str = 'Warning!', remember_version: int = 1) -> None:
		self._seen_version = 0
		self._saved_state = self._seen_version
		self._message = message
		self._title = title
		self._remember_version = remember_version

	def present(self, parent: Misc) -> None:
		if self._remember_version <= self._seen_version:
			return
		from .WarnDialog import WarnDialog
		dialog = WarnDialog(parent, self._message, self._title, show_dont_warn=True)
		if dialog.dont_warn.get():
			self._seen_version = self._remember_version

	def encode(self) -> JSONValue:
		return self._seen_version

	def decode(self, seen_version: JSONValue) -> None:
		if not isinstance(seen_version, int):
			return
		self._seen_version = seen_version

	def save_state(self) -> None:
		self._saved_state = self._seen_version

	def reset_state(self) -> None:
		self._seen_version = self._saved_state

V = TypeVar('V', int, float, str, bool, dict)
class Dictionary(ConfigObject, Generic[V]):
	def __init__(self, value_type: type[V], defaults: dict[str, V] = {}) -> None:
		self.value_type: type[V] = value_type
		self.data: dict[str, V] = defaults
		self._saved_state: dict[str, V] = self.data

	def encode(self) -> JSONValue:
		return dict(self.data)

	def decode(self, data: JSONValue) -> None:
		if not isinstance(data, dict):
			return
		for key,value in data.items():
			if not isinstance(key, str) or not isinstance(value, self.value_type):
				continue
			self.data[key] = value

	def save_state(self) -> None:
		self._saved_state = dict(self.data)

	def reset_state(self) -> None:
		self.data = dict(self._saved_state)

class List(ConfigObject, Generic[V]):
	def __init__(self, value_type: type[V], defaults: list[V] = []) -> None:
		self.value_type: type[V] = value_type
		self.data: list[V] = defaults
		self._saved_state: list[V] = self.data

	def encode(self) -> JSONValue:
		return self.data

	def decode(self, data: JSONValue) -> None:
		if not isinstance(data, list):
			return
		self.data = []
		for value in data:
			if not isinstance(value, self.value_type):
				continue
			self.data.append(value)

	def save_state(self) -> None:
		self._saved_state = list(self.data)

	def reset_state(self) -> None:
		self.data = list(self._saved_state)
