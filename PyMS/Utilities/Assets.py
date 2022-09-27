
from .UIKit import PhotoImage as _PhotoImage
from .UIKit import PILImage as _PILImage
from .UIKit import ImageTk as _ImageTk

import os as _os
import sys as _sys

if hasattr(_sys, 'frozen'):
	base_dir = _os.path.dirname(_sys.executable)
else:
	base_dir = _os.path.dirname(_os.path.dirname(_os.path.dirname(__file__)))

## Internals
internals_dir = _os.path.join(base_dir, 'PyMS')

## Versions
versions_file_path = _os.path.join(internals_dir, 'versions.json')

_VERSIONS = None
def version(program_name): # type: (str) -> str
	global _VERSIONS
	if _VERSIONS == None:
		import json
		with open(versions_file_path, 'r') as f:
			_VERSIONS = json.load(f)
	return _VERSIONS[program_name]

## Readme
readme_file_path = _os.path.join(base_dir, 'README.md')

## Images
images_dir = _os.path.join(internals_dir, 'Images')

def image_path(filename): # type: (str) -> str
	return _os.path.join(images_dir, filename)

_IMAGE_CACHE = {}
def get_image(filename, cache=True): # type: (str, bool) -> (_PhotoImage | None)
	if not _os.extsep in filename:
		filename += _os.extsep + 'gif'
	global _IMAGE_CACHE
	if filename in _IMAGE_CACHE:
		return _IMAGE_CACHE[filename]
	path = image_path(filename)
	if not _os.path.exists(path):
		return None
	try:
		image = _PhotoImage(file=path)
	except:
		return None
	if cache:
		_IMAGE_CACHE[filename] = image
	return image

def clear_image_cache():
	global _IMAGE_CACHE
	_IMAGE_CACHE.clear()

## MPQ
mpq_dir = _os.path.join(internals_dir, 'MPQ')

def mpq_file_path(*path_components): # type: (*str) -> str
	return _os.path.join(mpq_dir, *path_components)

def mpq_file_name(*path_components): # type: (*str) -> str
	return '\\'.join(path_components)

def mpq_file_ref(*path_components): # type: (*str) -> str
	return 'MPQ:' + mpq_file_name(*path_components)

def mpq_file_path_to_file_name(file_path): # type: (str) -> str
	if not file_path.startswith(mpq_dir):
		return file_path
	path_components = _os.path.split(_os.path.relpath(file_path, mpq_dir))
	return mpq_file_name(*path_components)

def mpq_file_path_to_ref(file_path): # type: (str) -> str
	if not file_path.startswith(mpq_dir):
		return file_path
	path_components = _os.path.split(_os.path.relpath(file_path, mpq_dir))
	return mpq_file_ref(*path_components)

def mpq_ref_to_file_path(file_ref): # type: (str) -> str
	if not file_ref.startswith('MPQ:'):
		return file_ref
	path_components = file_ref[4:].split('\\')
	return mpq_file_path(*path_components)

def mpq_ref_to_file_name(file_ref): # type: (str) -> str
	if not file_ref.startswith('MPQ:'):
		return file_ref
	return file_ref[4:]

## Docs
docs_dir = _os.path.join(base_dir, 'Docs')

def doc_path(filename): # type: (str) -> str
	return _os.path.join(docs_dir, filename)

## Data
data_dir = _os.path.join(internals_dir, 'Data')

def data_file_path(filename): # type: (str) -> str
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

_DATA_CACHE = {}
def data_cache(filename): # type: (str) -> list[str]
	global _DATA_CACHE
	if not filename in _DATA_CACHE:
		with open(data_file_path('%s.txt' % filename), 'r') as f:
			_DATA_CACHE[filename] = [l.rstrip() for l in f.readlines()]
	return _DATA_CACHE[filename]

## Palettes
palettes_dir = _os.path.join(base_dir, 'Palettes')

def palette_file_path(filename): # type: (str) -> str
	return _os.path.join(palettes_dir, filename)

## Settings
settings_dir = _os.path.join(base_dir, 'Settings')

def settings_file_path(name): # type: (str) -> str
	return _os.path.join(settings_dir, '%s%stxt' % (name, _os.extsep))

## Logs
logs_dir = _os.path.join(internals_dir, 'Logs')

def log_file_path(filename): # type: (str) -> str
	return _os.path.join(logs_dir, filename)

## Internal Temp
internal_temp_dir = _os.path.join(internals_dir, 'Temp')

def internal_temp_file(filename):
	return _os.path.join(internal_temp_dir, filename)

## Help
help_dir = _os.path.join(base_dir, 'Help')

class HelpFolder(object):
	def __init__(self, name): # type: (str) -> HelpFolder
		self.name = name
		self.parent = None # type: (HelpFolder | None)
		self.folders = [] # type: list[HelpFolder]
		self.files = [] # type: list[HelpFile]

	def add_folder(self, folder): # type: (HelpFolder) -> None
		self.folders.append(folder)
		folder.parent = self

	def add_file(self, file): # type: (HelpFile) -> None
		self.files.append(file)

	def index(self, path): # type: (str) -> (str | None)
		path_components = path.split('#')[0].split('/')
		if path_components[0] == '':
			path_components.pop(0)
		if path_components.pop(0) != 'Help':
			return None
		if path_components[-1].endswith('.md'):
			path_components[-1] = _os.path.splitext(path_components[-1])[0]
		return self._index(path_components)

	def _index(self, path_components): # type: (list[str]) -> (str | None)
		if len(path_components) == 1:
			for index, file in enumerate(self.files):
				if path_components[0] == file.name:
					return str(index)
		else:
			for index, folder in enumerate(self.folders):
				if path_components[0] == folder.name:
					sub_index = folder._index(path_components[1:])
					if sub_index == None:
						return None
					return '%d.%s' % (index + len(self.files), sub_index)
		return None

	def get_file(self, index): # type: (str) -> (HelpFile | None)
		return self._get_file(list(int(i) for i in index.split('.')))

	def _get_file(self, index_components): # type: (list[int]) -> (HelpFile | None)
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
	def __init__(self, path, folder): # type: (str, HelpFolder) -> HelpFile
		self.path = '/'.join(_os.path.split(path))
		self.name = _os.path.splitext(path.split('/')[-1])[0]
		self.folder = folder

_HELP_TREE = None
def help_tree(force_update=False): # type: (bool) -> (HelpFolder)
	global _HELP_TREE 
	if _HELP_TREE != None and force_update == False:
		return _HELP_TREE
	root = None
	parents = {} # type: dict[str, HelpFolder]
	for path, _, filenames in _os.walk(help_dir):
		folder = HelpFolder(_os.path.split(path)[-1])
		parents[path] = folder
		if root == None:
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
	_HELP_TREE = root
	return root

def help_file_path(path): # type: (str) -> (str | None)
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

_HELP_IMAGE_CACHE = {}
def help_image(path): # type: (str) -> (_PhotoImage | None)
	path_components = path.split('/')
	if path_components[0] == '':
		path_components.pop(0)
	if path_components[0] == 'Help':
		path_components.pop(0)
	full_path = _os.path.join(help_dir, *path_components)
	if not _os.path.exists(full_path):
		return None
	global _HELP_IMAGE_CACHE
	if full_path in _HELP_IMAGE_CACHE:
		return _HELP_IMAGE_CACHE[full_path]
	try:
		image = _PhotoImage(file=full_path)
	except:
		try:
			pil_image = _PILImage.open(full_path)
			image = _ImageTk.PhotoImage(pil_image)
		except:
			return None
	_HELP_IMAGE_CACHE[full_path] = image
	return image

def clear_help_image_cache():
	global _HELP_IMAGE_CACHE
	_HELP_IMAGE_CACHE.clear()
