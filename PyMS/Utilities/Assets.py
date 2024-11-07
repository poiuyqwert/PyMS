
from __future__ import annotations

import os as _os
import sys as _sys

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from .UIKit import PhotoImage
	from .UIKit import Image
	from .UIKit import ImageTk

if hasattr(_sys, 'frozen'):
	base_dir = _os.path.dirname(_sys.executable)
else:
	base_dir = _os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))

## Internals
internals_dir = _os.path.join(base_dir, 'PyMS')

## Versions
versions_file_path = _os.path.join(internals_dir, 'versions.json')

_VERSIONS: dict[str, str] = {}
def version(program_name: str) -> str:
	global _VERSIONS
	if not _VERSIONS:
		import json
		with open(versions_file_path, 'r') as f:
			_VERSIONS = json.load(f)
	return _VERSIONS[program_name]

## Readme
readme_file_path = _os.path.join(base_dir, 'README.md')

## Images
images_dir = _os.path.join(internals_dir, 'Images')

def image_path(filename: str) -> str:
	return _os.path.join(images_dir, filename)

_IMAGE_CACHE: dict[str, Image] = {}
def get_image(filename: str, cache: bool = True) -> Image:
	from .UIKit import PhotoImage
	if not _os.extsep in filename:
		filename += _os.extsep + 'gif'
	if filename in _IMAGE_CACHE:
		return _IMAGE_CACHE[filename]
	path = image_path(filename)
	try:
		image = PhotoImage(file=path)
	except:
		image = PhotoImage()
	if cache:
		_IMAGE_CACHE[filename] = image
	return image

def clear_image_cache():
	_IMAGE_CACHE.clear()

## MPQ
mpq_dir = _os.path.join(internals_dir, 'MPQ')

def mpq_file_path(*path_components: str) -> str:
	return _os.path.join(mpq_dir, *path_components)

def mpq_file_name(*path_components: str) -> str:
	return '\\'.join(path_components)

def mpq_file_ref(*path_components: str) -> str:
	return 'MPQ:' + mpq_file_name(*path_components)

def mpq_file_path_to_file_name(file_path: str) -> str:
	if not file_path.startswith(mpq_dir):
		return file_path
	path_components = _os.path.normpath(_os.path.relpath(file_path, mpq_dir)).split(_os.path.sep)
	return mpq_file_name(*path_components)

def mpq_file_path_to_ref(file_path: str) -> str:
	if not file_path.startswith(mpq_dir):
		return file_path
	path_components = _os.path.normpath(_os.path.relpath(file_path, mpq_dir)).split(_os.path.sep)
	return mpq_file_ref(*path_components)

def mpq_ref_to_file_path(file_ref: str) -> str:
	if not file_ref.startswith('MPQ:'):
		return file_ref
	path_components = file_ref[4:].split('\\')
	return mpq_file_path(*path_components)

def mpq_ref_to_file_name(file_ref: str) -> str:
	if not file_ref.startswith('MPQ:'):
		return file_ref
	return file_ref[4:]

## Data
data_dir = _os.path.join(internals_dir, 'Data')

def data_file_path(filename: str) -> str:
	return _os.path.join(data_dir, filename)

class DataReference:
	SelCircleSize   = 'SelCircleSize' # Selection Circle Sizes
	Rightclick      = 'Rightclick' # Right Click Actions
	Flingy          = 'Flingy' # Flingy Entries
	Behaviours      = 'Behaviours' # Behaviours
	DamTypes        = 'DamTypes' # Damage Types
	Mapdata         = 'Mapdata' # Campaign Names
	Units           = 'Units' # Default Units
	Remapping       = 'Remapping' # Remapping
	DrawList        = 'DrawList' # Draw Types
	FlingyControl   = 'FlingyControl' # Flingy Controlers
	Sprites         = 'Sprites' # Default Sprites
	Animations      = 'Animations' # IScript Animations
	Orders          = 'Orders' # Default Orders
	IscriptIDList   = 'IscriptIDList' # IScript ID's
	Portdata        = 'Portdata' # Default Campaign
	Weapons         = 'Weapons' # Default Weapons
	UnitSize        = 'UnitSize' # Unit Sizes
	Techdata        = 'Techdata' # Default Technologies
	ElevationLevels = 'ElevationLevels' # Elevation Levels
	Images          = 'Images' # Default Images
	Upgrades        = 'Upgrades' # Default Upgrades
	Explosions      = 'Explosions' # Explosion Types
	Races           = 'Races' # Races
	Icons           = 'Icons' # Icons
	Sfxdata         = 'Sfxdata' # Sound Effects
	ShieldSize      = 'ShieldSize' # Shield Sizes

_DATA_CACHE: dict[str, list[str]] = {}
def data_cache(filename: str) -> list[str]:
	if not filename in _DATA_CACHE:
		with open(data_file_path('%s.txt' % filename), 'r') as f:
			_DATA_CACHE[filename] = [l.rstrip() for l in f.readlines()]
	return _DATA_CACHE[filename]

## Palettes
palettes_dir = _os.path.join(base_dir, 'Palettes')

def palette_file_path(filename: str) -> str:
	return _os.path.join(palettes_dir, filename)

## Settings
settings_dir = _os.path.join(base_dir, 'Settings')

def settings_file_path(name: str) -> str:
	return _os.path.join(settings_dir, '%s%stxt' % (name, _os.extsep))

## Logs
logs_dir = _os.path.join(internals_dir, 'Logs')

def log_file_path(filename: str) -> str:
	return _os.path.join(logs_dir, filename)

## Internal Temp
internal_temp_dir = _os.path.join(internals_dir, 'Temp')

def internal_temp_file(filename):
	return _os.path.join(internal_temp_dir, filename)

## Help
help_dir = _os.path.join(base_dir, 'Help')

class HelpFolder(object):
	def __init__(self, name: str) -> None:
		self.name = name
		self.parent: (HelpFolder | None) = None
		self.folders: list[HelpFolder] = []
		self.files: list[HelpFile] = []

	def add_folder(self, folder: HelpFolder) -> None:
		self.folders.append(folder)
		folder.parent = self

	def add_file(self, file: HelpFile) -> None:
		self.files.append(file)

	def index(self, path: str) -> str | None:
		path_components = path.split('#')[0].split('/')
		if path_components[0] == '':
			path_components.pop(0)
		if path_components.pop(0) != 'Help':
			return None
		if path_components[-1].endswith('.md'):
			path_components[-1] = _os.path.splitext(path_components[-1])[0]
		return self._index(path_components)

	def _index(self, path_components: list[str]) -> (str | None):
		if len(path_components) == 1:
			for index, file in enumerate(self.files):
				if path_components[0] == file.name:
					return str(index)
		else:
			for index, folder in enumerate(self.folders):
				if path_components[0] == folder.name:
					sub_index = folder._index(path_components[1:])
					if sub_index is None:
						return None
					return '%d.%s' % (index + len(self.files), sub_index)
		return None

	def get_file(self, index: str) -> HelpFile | None:
		return self._get_file(list(int(i) for i in index.split('.')))

	def _get_file(self, index_components: list[int]) -> (HelpFile | None):
		if len(index_components) == 1:
			if index_components[0] >= len(self.files):
				return None
			return self.files[index_components[0]]
		else:
			index_components[0] -= len(self.files)
			if index_components[0] >= len(self.folders):
				return None
			return self.folders[index_components[0]]._get_file(index_components[1:])

	def __repr__(self):
		result = self.name
		for file in self.files:
			result += '\n - ' + file.name
		for folder in self.folders:
			result += '\n > ' + repr(folder).replace('\n', '\n  ')
		return result
class HelpFile(object):
	def __init__(self, path: str, folder: HelpFolder) -> None:
		self.path = '/'.join(_os.path.split(path))
		self.name = _os.path.splitext(path.split('/')[-1])[0]
		self.folder = folder

_HELP_TREE: HelpFolder | None = None
def help_tree( force_update: bool = False) -> HelpFolder:
	global _HELP_TREE 
	if _HELP_TREE is not None and force_update == False:
		return _HELP_TREE
	root = None
	parents: dict[str, HelpFolder] = {}
	for path, _, filenames in _os.walk(help_dir):
		folder = HelpFolder(_os.path.split(path)[-1])
		parents[path] = folder
		if root is None:
			root = folder
		else:
			parent_path,_ = _os.path.split(path)
			parents[parent_path].add_folder(folder)
		for filename in filenames:
			if filename.startswith('.'):
				continue
			_, ext = _os.path.splitext(filename)
			if ext != _os.extsep + 'md':
				continue
			folder.add_file(HelpFile(_os.path.relpath(_os.path.join(path, filename), help_dir), folder))
	assert root is not None
	_HELP_TREE = root
	return root

def help_file_path(path: str) -> str | None:
	if not _os.extsep in path:
		path += _os.extsep + 'md'
	path_components = path.split('/')
	if path_components[0] == '':
		path_components.pop(0)
	if path_components[0] == 'Help':
		path_components.pop(0)
	full_path = _os.path.join(help_dir, *path_components)
	if not _os.path.exists(full_path):
		return None
	return full_path

_HELP_IMAGE_CACHE: dict[str, Image] = {}
def help_image(path: str) -> Image | None:
	from .UIKit import PhotoImage as _PhotoImage
	from .UIKit import PILImage as _PILImage
	from .UIKit import ImageTk as _ImageTk
	path_components = path.split('/')
	if path_components[0] == '':
		path_components.pop(0)
	if path_components[0] == 'Help':
		path_components.pop(0)
	full_path = _os.path.join(help_dir, *path_components)
	if not _os.path.exists(full_path):
		return None
	if full_path in _HELP_IMAGE_CACHE:
		return _HELP_IMAGE_CACHE[full_path]
	image: Image
	try:
		image = _PhotoImage(file=full_path)
	except:
		try:
			pil_image = _PILImage.open(full_path)
			image = cast(Image, _ImageTk.PhotoImage(pil_image))
		except:
			return None
	_HELP_IMAGE_CACHE[full_path] = image
	return image

def clear_help_image_cache():
	_HELP_IMAGE_CACHE.clear()

## Themes

themes_dir = _os.path.join(base_dir, 'PyMS', 'Themes')

def theme_file_path(name: str) -> str:
	return _os.path.join(themes_dir, '%s.txt' % name)

_THEME_LIST: list[str] | None = None
def theme_list() -> list[str]:
	global _THEME_LIST
	if not _THEME_LIST:
		_THEME_LIST = []
		for filename in _os.listdir(themes_dir):
			if not filename.endswith('.txt'):
				continue
			_THEME_LIST.append(filename[:-4])
		_THEME_LIST.sort()
	return _THEME_LIST
