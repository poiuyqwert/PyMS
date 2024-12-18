
from __future__ import annotations

from .UIKit import FileDialog, parse_resizable, FileType, AnyWindow, Geometry, GeometryAdjust, Size, PanedWindow, HORIZONTAL, Misc, Font

from . import Assets
from .MPQHandler import MPQHandler
from . import JSON

from numbers import Number
import os, json, re, enum
from dataclasses import dataclass
from copy import deepcopy

from typing import Any, Protocol, runtime_checkable, Generic, TypeVar, Callable, Generator, overload, Literal, cast

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
	def encode(self) -> JSON.Value:
		...

	def decode(self, data: JSON.Value) -> None:
		...

	def reset(self) -> None:
		...

	def store_state(self) -> None:
		...

	def restore_state(self) -> None:
		...

class Group(ConfigObject):
	@staticmethod
	def _fields(group: Group) -> Generator[tuple[str, ConfigObject], None, None]:
		import inspect
		for attr, _ in inspect.getmembers(group, lambda member: not inspect.ismethod(member) and not inspect.isclass(member)):
			if attr.startswith('_'):
				continue
			value = getattr(group, attr)
			if not isinstance(value, ConfigObject):
				continue
			yield (attr.rstrip('_'), value)

	def encode(self) -> JSON.Value:
		data = {}
		for key, value in Group._fields(self):
			data[key] = value.encode()
		return data

	def decode(self, data: JSON.Value) -> None:
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

	def reset(self) -> None:
		for _, value in Group._fields(self):
			value.reset()

	def store_state(self) -> None:
		for _, value in Group._fields(self):
			value.store_state()

	def restore_state(self) -> None:
		for _, value in Group._fields(self):
			value.restore_state()

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
		data: JSON.Object | None = None
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
			from . import trace
			if tracer := trace.get_tracer():
				tracer.trace_error()
			data = None
		if data:
			self.decode(data)

	def save(self) -> None:
		import os
		try:
			data = self.encode()
			assert isinstance(data, dict)
			data['version'] = self._version
			with open(Assets.settings_file_path(self._name), 'w') as f:
				json.dump(data, f, sort_keys=True, indent=4)
		except:
			from . import trace
			if tracer := trace.get_tracer():
				tracer.trace_error()

class String(ConfigObject):
	def __init__(self, *, default: str | None = None) -> None:
		self._default = default
		self.value = self._default
		self._saved_state = self.value

	def encode(self) -> JSON.Value:
		return self.value

	def decode(self, value: JSON.Value) -> None:
		if not isinstance(value, str):
			return
		self.value = value

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

class Int(ConfigObject):
	def __init__(self, *, default: int, limits: tuple[int, int] | None = None) -> None:
		self._default = default
		self.value = self._default
		self._saved_state = self.value
		self.limits = limits

	def encode(self) -> JSON.Value:
		return self.value

	def decode(self, value: JSON.Value) -> None:
		if not isinstance(value, Number):
			return
		self.value = int(value)
		if self.limits is not None:
			self.value = min(self.limits[1], max(self.limits[0], self.value))

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

class Float(ConfigObject):
	def __init__(self, *, default: float, limits: tuple[float, float] | None = None) -> None:
		self._default = default
		self.value = self._default
		self._saved_state = self.value
		self.limits = limits

	def encode(self) -> JSON.Value:
		return self.value

	def decode(self, value: JSON.Value) -> None:
		if not isinstance(value, Number):
			return
		self.value = float(value)
		if self.limits is not None:
			self.value = min(self.limits[1], max(self.limits[0], self.value))

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

class Boolean(ConfigObject):
	def __init__(self, *, default: bool) -> None:
		self._default = default
		self.value = self._default
		self._saved_state = self.value

	def encode(self) -> JSON.Value:
		return self.value

	def decode(self, value: JSON.Value) -> None:
		if not isinstance(value, Number):
			return
		self.value = bool(value)

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

class WindowGeometry(ConfigObject):
	def __init__(self, *, default_size: Size | None = None, default_centered: bool = True) -> None:
		self._geometry: str | None = None
		self._saved_state: str | None = self._geometry
		self._default_size = default_size
		self._default_centered = default_centered

	def save_size(self, window: AnyWindow, closing: bool = True) -> None:
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

	def load_size(self, window: AnyWindow) -> None:
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

	def encode(self) -> JSON.Value:
		return self._geometry

	def decode(self, geometry: JSON.Value) -> None:
		if not isinstance(geometry, str) or Geometry.parse(geometry) is None:
			return
		self._geometry = geometry

	def reset(self) -> None:
		self._geometry = None

	def store_state(self) -> None:
		self._saved_state = self._geometry

	def restore_state(self) -> None:
		self._geometry = self._saved_state

class PaneSizes(ConfigObject):
	def __init__(self, *, defaults: list[int] = [], pane_index: int | None = None) -> None:
		self._defaults = defaults
		self._sizes: list[int] = self._defaults
		self._pane_index = pane_index
		self._saved_state: list[int] = list(self._sizes)

	def save_size(self, paned_window: PanedWindow) -> None:
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

	def load_size(self, paned_window: PanedWindow) -> None:
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

	def encode(self) -> JSON.Value:
		return self._sizes

	def decode(self, data: JSON.Value) -> None:
		if not isinstance(data, list):
			return
		sizes: list[int] = []
		for size in data:
			if not isinstance(size, int):
				return
			sizes.append(size)
		self._sizes = sizes

	def reset(self) -> None:
		self._sizes = self._defaults

	def store_state(self) -> None:
		self._saved_state = self._sizes

	def restore_state(self) -> None:
		self._sizes = self._saved_state

class File(ConfigObject):
	def __init__(self, *, default: str, name: str, filetypes: list[FileType], initial_filename: str | None = None) -> None:
		self._default = default
		self.file_path = self._default
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._initial_filename = initial_filename or os.path.basename(self.file_path)
		self._saved_state = self.file_path

	def select_file(self, parent: Misc, name: str | None = None, filetypes: list[FileType] | None = None) -> str | None:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		initial_dir: str | None = None
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

	def encode(self) -> JSON.Value:
		return self.file_path

	def decode(self, file_path: JSON.Value) -> None:
		if not isinstance(file_path, str):
			return
		if not file_path.startswith('MPQ:') and not os.path.exists(file_path):
			return
		self.file_path = file_path

	def reset(self) -> None:
		self.file_path = self._default

	def store_state(self) -> None:
		self._saved_state = self.file_path

	def restore_state(self) -> None:
		self.file_path = self._saved_state

class FileOpType(enum.Enum):
	open_save = 0
	import_export = 1

	def title(self, name: str, save: bool, multiple: bool = False) -> str:
		op_name: str
		match self:
			case FileOpType.open_save:
				op_name = 'Save' if save else 'Open'
			case FileOpType.import_export:
				op_name = 'Export' if save else 'Import'
		plural = ('s' if name[-1].islower() else "'s") if multiple else ''
		return f'{op_name} {name}{plural}'

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
	def __init__(self, *, name: str, filetypes: list[FileType], op_type: FileOpType = FileOpType.open_save, initial_filename: str | None = None) -> None:
		self._open_directory = Assets.base_dir
		self._saved_state_open = self._open_directory
		self._save_directory = Assets.base_dir
		self._saved_state_save = self._save_directory
		self._name = name
		self._filetypes = FileType.include_all_files(filetypes)
		self._default_extension = FileType.default_extension(filetypes)
		self._op_type = op_type
		self._initial_filename = initial_filename

	@overload
	def _select_file(self, parent: Misc, save: bool, title: str | None, filetypes: list[FileType] | None, multiple: Literal[False] = False) -> str | None: ...
	@overload
	def _select_file(self, parent: Misc, save: bool, title: str | None, filetypes: list[FileType] | None, multiple: Literal[True]) -> list[str] | None: ...
	def _select_file(self, parent: Misc, save: bool, title: str | None, filetypes: list[FileType] | None, multiple: bool = False, filename: str | None = None) -> str | list[str] | None:
		window = parent.winfo_toplevel()
		setattr(window, '_pyms__window_blocking', True)
		path: str | list[str] | None
		if save:
			path = FileDialog.asksaveasfilename(
				parent=window,
				title=title or self._op_type.title(self._name, True),
				initialdir=self._save_directory if save else self._open_directory,
				filetypes=filetypes or self._filetypes,
				defaultextension=self._default_extension,
				initialfile=filename or self._initial_filename
			)
		else:
			if multiple:
				paths = FileDialog.askopenfilenames(
					parent=window,
					title=title or self._op_type.title(self._name, False, multiple),
					initialdir=self._save_directory if save else self._open_directory,
					filetypes=filetypes or self._filetypes,
					defaultextension=self._default_extension
				)
				if isinstance(paths, tuple):
					path = list(paths)
			else:
				path = FileDialog.askopenfilename(
					parent=window,
					title=title or self._op_type.title(self._name, False, multiple),
					initialdir=self._save_directory if save else self._open_directory,
					filetypes=filetypes or self._filetypes,
					defaultextension=self._default_extension
				)
		if not path:
			path = None
		from .fileutils import check_allow_overwrite_internal_file
		if save and path is not None:
			if isinstance(path, (list, tuple)):
				path = list(p for p in path if check_allow_overwrite_internal_file(p))
				if not path:
					path = None
			elif not check_allow_overwrite_internal_file(path):
				path = None
		setattr(window, '_pyms__window_blocking', False)
		if path is not None:
			if isinstance(path, (list, tuple)):
				directory = os.path.dirname(path[0])
			else:
				directory = os.path.dirname(path)
			if save:
				self._save_directory = directory
			else:
				self._open_directory = directory
		return path

	def select_open(self, parent: Misc, title: str | None = None, filetypes: list[FileType] | None = None) -> str | None:
		return self._select_file(parent, False, title, filetypes)

	def select_open_multiple(self, parent: Misc, title: str | None = None, filetypes: list[FileType] | None = None) -> list[str] | None:
		return self._select_file(parent, False, title, filetypes, True)

	def select_save(self, parent: Misc, title: str | None = None, filetypes: list[FileType] | None = None, filename: str | None = None) -> str | None:
		return self._select_file(parent, True, title, filetypes)

	def encode(self) -> JSON.Value:
		return {
			self._op_type.open_key: self._open_directory,
			self._op_type.save_key: self._save_directory
		}

	def decode(self, data: JSON.Value) -> None:
		if not isinstance(data, dict):
			return
		open_directory = data.get(self._op_type.open_key)
		if isinstance(open_directory, str) and os.path.exists(open_directory):
			self._open_directory = open_directory
		save_directory = data.get(self._op_type.save_key)
		if isinstance(save_directory, str) and os.path.exists(save_directory):
			self._save_directory = save_directory

	def reset(self) -> None:
		self._open_directory = Assets.base_dir
		self._save_directory = Assets.base_dir

	def store_state(self) -> None:
		self._saved_state_open = self._open_directory
		self._saved_state_save = self._save_directory

	def restore_state(self) -> None:
		self._open_directory = self._saved_state_open
		self._save_directory = self._saved_state_save

# class SelectFiles(ConfigObject):
# 	def __init__(self, *, title: str, filetypes: list[FileType]) -> None:
# 		self.directory = Assets.base_dir
# 		self._saved_state = self.directory
# 		self._title = title
# 		self._filetypes = FileType.include_all_files(filetypes)
# 		self._default_extension = FileType.default_extension(filetypes)

# 	def select_open(self, parent: Misc, filetypes: list[FileType] | None = None) -> list[str]:
# 		window = parent.winfo_toplevel()
# 		setattr(window, '_pyms__window_blocking', True)
# 		paths: list[str] | str = FileDialog.askopenfilename(
# 			parent=window,
# 			multiple=True,
# 			title=self._title,
# 			initialdir=self.directory,
# 			filetypes=filetypes or self._filetypes,
# 			defaultextension=self._default_extension
# 		) # type: ignore[call-arg]
# 		setattr(window, '_pyms__window_blocking', False)
# 		if isinstance(paths, str):
# 			if paths:
# 				paths = [paths]
# 			else:
# 				paths = []
# 		if paths:
# 			self.directory = os.path.dirname(paths[0])
# 		return paths

# 	def encode(self) -> JSON.Value:
# 		return self.directory

# 	def decode(self, directory: JSON.Value) -> None:
# 		if not isinstance(directory, str) or not os.path.exists(directory):
# 			return
# 		self.directory = directory

# 	def reset(self) -> None:
# 		self.directory = Assets.base_dir

# 	def store_state(self) -> None:
# 		self._saved_state = self.directory

# 	def restore_state(self) -> None:
# 		self.directory = self._saved_state

class SelectDirectory(ConfigObject):
	def __init__(self, *, title: str = 'Select Folder') -> None:
		self.path = Assets.base_dir
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

	def encode(self) -> JSON.Value:
		return self.path

	def decode(self, directory: JSON.Value) -> None:
		if not isinstance(directory, str) or not os.path.exists(directory):
			return
		self.path = directory

	def reset(self) -> None:
		self.path = Assets.base_dir

	def store_state(self) -> None:
		self._saved_state = self.path

	def restore_state(self) -> None:
		self.path = self._saved_state

class Warning(ConfigObject):
	def __init__(self, *, message: str, title: str = 'Warning!', remember_version: int = 1) -> None:
		self._seen_version = 0
		self._saved_state = self._seen_version
		self._message = message
		self._title = title
		self._remember_version = remember_version

	def present(self, parent: Misc, message: str | None = None, title: str | None = None) -> None:
		if self._remember_version <= self._seen_version:
			return
		from .WarnDialog import WarnDialog
		dialog = WarnDialog(parent, message or self._message, title or self._title, show_dont_warn=True)
		if dialog.dont_warn.get():
			self._seen_version = self._remember_version

	def encode(self) -> JSON.Value:
		return self._seen_version

	def decode(self, seen_version: JSON.Value) -> None:
		if not isinstance(seen_version, int):
			return
		self._seen_version = seen_version

	def reset(self) -> None:
		self._seen_version = 0

	def store_state(self) -> None:
		self._saved_state = self._seen_version

	def restore_state(self) -> None:
		self._seen_version = self._saved_state

V = TypeVar('V', int, float, str, bool, dict)
class Dictionary(ConfigObject, Generic[V]):
	def __init__(self, *, value_type: type[V], defaults: dict[str, V] = {}) -> None:
		self.value_type: type[V] = value_type
		self._defaults: dict[str, V] = dict(defaults)
		self.data: dict[str, V] = dict(self._defaults)
		self._saved_state: dict[str, V] = self.data

	def encode(self) -> JSON.Value:
		return dict(self.data)

	def decode(self, data: JSON.Value) -> None:
		if not isinstance(data, dict):
			return
		for key,value in data.items():
			if not isinstance(key, str) or not isinstance(value, self.value_type):
				continue
			self.data[key] = value

	def reset(self) -> None:
		self.data = dict(self._defaults)

	def store_state(self) -> None:
		self._saved_state = dict(self.data)

	def restore_state(self) -> None:
		self.data = dict(self._saved_state)

class List(ConfigObject, Generic[V]):
	def __init__(self, *, value_type: type[V], defaults: list[V] = []) -> None:
		self.value_type: type[V] = value_type
		self._defaults: list[V] = list(defaults)
		self.data: list[V] = list(self._defaults)
		self._saved_state: list[V] = self.data

	def encode(self) -> JSON.Value:
		return self.data

	def decode(self, data: JSON.Value) -> None:
		if not isinstance(data, list):
			return
		self.data = []
		for value in data:
			if not isinstance(value, self.value_type):
				continue
			self.data.append(value)

	def reset(self) -> None:
		self.data = list(self._defaults)

	def store_state(self) -> None:
		self._saved_state = list(self.data)

	def restore_state(self) -> None:
		self.data = list(self._saved_state)


O = TypeVar('O', bound=JSON.Codable)
class JSONList(ConfigObject, Generic[O]):
	def __init__(self, *, value_type: type[O], defaults: list[O] = []) -> None:
		self.value_type: type[O] = value_type
		self._defaults: list[O] = list(defaults)
		self.data: list[O] = list(self._defaults)
		self._saved_state: list[O] = self.data

	def encode(self) -> JSON.Value:
		data: list[dict] = []
		for obj in self.data:
			try:
				data.append(obj.to_json())
			except:
				continue
		return data

	def decode(self, data: JSON.Value) -> None:
		if not isinstance(data, list):
			return
		self.data = []
		for value in data:
			if not isinstance(value, dict):
				continue
			try:
				self.data.append(self.value_type.from_json(value))
			except:
				continue

	def reset(self) -> None:
		self.data = deepcopy(self._defaults)

	def store_state(self) -> None:
		self._saved_state = deepcopy(self.data)

	def restore_state(self) -> None:
		self.data = deepcopy(self._saved_state)

E = TypeVar('E', bound=enum.Enum)
class Enum(ConfigObject, Generic[E]):
	def __init__(self, *, enum_type: type[E], default: E) -> None:
		self._enum_type = enum_type
		self._default = default
		self.value = self._default
		self._saved_state = self.value

	def encode(self) -> JSON.Value:
		return self.value.value

	def decode(self, data: JSON.Value) -> None:
		try:
			value = self._enum_type(data)
		except:
			return
		self.value = value

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

class Color(ConfigObject):
	RE_MATCH = re.compile(r'#?[a-zA-Z0-9]{6}')

	def __init__(self, *, default: str) -> None:
		self._default = default
		self.value = self._default
		self._saved_state = self.value

	def encode(self) -> JSON.Value:
		return self.value

	def decode(self, value: JSON.Value) -> None:
		if not isinstance(value, str):
			return
		if not Color.RE_MATCH.match(value):
			return
		self.value = value

	def reset(self) -> None:
		self.value = self._default

	def store_state(self) -> None:
		self._saved_state = self.value

	def restore_state(self) -> None:
		self.value = self._saved_state

@dataclass
class Style:
	foreground: str | None = None
	background: str | None = None
	bold: bool = False

	@property
	def configuration(self) -> dict[str, Any]:
		configuration: dict[str, Any] = {}
		if self.foreground is not None:
			configuration['foreground'] = self.foreground
		if self.background is not None:
			configuration['background'] = self.background
		if self.bold:
			configuration['font'] = Font.fixed().bolded()
		return configuration

	def copy(self) -> Style:
		return Style(
			foreground=self.foreground,
			background=self.background,
			bold=self.bold
		)

class HighlightStyle(ConfigObject):
	def __init__(self, default: Style) -> None:
		self._default = default
		self.style = self._default.copy()
		self._saved_state = self.style.copy()

	def encode(self) -> JSON.Value:
		return {
			'foreground': self.style.foreground,
			'background': self.style.background,
			'bold': self.style.bold
		}

	def decode(self, value: JSON.Value) -> None:
		from .UIKit.Font import Font
		if not isinstance(value, dict):
			return
		foreground = value.get('foreground')
		if not isinstance(foreground, str) or not Color.RE_MATCH.match(foreground):
			foreground = None
		background = value.get('background')
		if not isinstance(background, str) or not Color.RE_MATCH.match(background):
			background = None
		bold = value.get('bold')
		if not isinstance(bold, bool):
			bold = False
		self.style = Style(
			foreground=foreground,
			background=background,
			bold=bold
		)

	def reset(self) -> None:
		self.style = self._default.copy()

	def store_state(self) -> None:
		self._saved_state = self.style.copy()

	def restore_state(self) -> None:
		self.style = self._saved_state.copy()
