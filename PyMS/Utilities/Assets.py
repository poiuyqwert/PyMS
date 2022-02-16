
from UIKit import PhotoImage as _PhotoImage

import os as _os
import sys as _sys

if hasattr(_sys, 'frozen'):
	base_dir = _os.path.dirname(unicode(_sys.executable, _sys.getfilesystemencoding()))
else:
	base_dir = _os.path.dirname(_os.path.dirname(_os.path.dirname(unicode(__file__, _sys.getfilesystemencoding()))))

## Images
images_dir = _os.path.join(base_dir, 'PyMS', 'Images')

def image_path(filename): # type: (str) -> str
	return _os.path.join(images_dir, filename)

_IMAGE_CACHE = {}
def get_image(filename, cache=True): # type: (str, bool) -> _PhotoImage
	if not _os.extsep in filename:
		filename += _os.extsep + 'gif'
	global _IMAGE_CACHE
	if filename in _IMAGE_CACHE:
		return _IMAGE_CACHE[filename]
	path = image_path(filename)
	if not _os.path.exists(path):
		return None
	image = _PhotoImage(file=path)
	if cache:
		_IMAGE_CACHE[filename] = image
	return image

def clear_image_cache():
	global _IMAGE_CACHE
	_IMAGE_CACHE.clear()

## MPQ
mpq_dir = _os.path.join(base_dir, 'PyMS', 'MPQ')

def mpq_file_path(*path_components): # type: (*str) -> str
	return _os.path.join(mpq_dir, *path_components)

def mpq_file_ref(*path_components): # type: (*str) -> str
	return 'MPQ:' + '\\'.join(path_components)

def mpq_file_to_ref(file_path): # type: (str) -> str
	if not file_path.startswith(mpq_dir):
		return file_path
	path_components = _os.path.split(_os.path.relpath(file_path, mpq_dir))
	return mpq_file_ref(*path_components)

def mpq_ref_to_file(file_ref): # type: (str) -> str
	if not file_ref.startswith('MPQ:'):
		return file_ref
	path_components = file_ref[4:].split('\\')
	return mpq_file_path(*path_components)

## Docs
docs_dir = _os.path.join(base_dir, 'Docs')

def doc_path(filename): # type: (str) -> str
	return _os.path.join(docs_dir, filename)

## Data
data_dir = _os.path.join(base_dir, 'PyMS', 'Data')

def data_file_path(filename): # type: (str) -> str
	return _os.path.join(data_dir, filename)

## Palettes
palettes_dir = _os.path.join(base_dir, 'Palettes')

def palette_file_path(filename): # type: (str) -> str
	return _os.path.join(palettes_dir, filename)

## Settings
settings_dir = _os.path.join(base_dir, 'Settings')

def settings_file_path(name): # type: (str) -> str
	return _os.path.join(settings_dir, '%s%stxt' % (name, _os.extsep))

## Logs
logs_dir = _os.path.join(base_dir, 'PyMS', 'Logs')

def log_file_path(filename): # type: (str) -> str
	return _os.path.join(logs_dir, filename)
