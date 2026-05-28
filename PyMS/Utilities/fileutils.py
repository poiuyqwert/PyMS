
from __future__ import annotations

from .PyMSError import PyMSError

from typing import BinaryIO

# TODO: Replace usage with IO
def load_file(file: str | BinaryIO, file_type: str = 'file') -> bytes:
	try:
		if isinstance(file, str):
			with open(file, 'rb') as f:
				data = f.read()
		else:
			data = file.read()
	except Exception as exc:
		name = ''
		if isinstance(file, str):
			name = f" '{file}'"
		raise PyMSError('Load', f"Could not load {file_type}{name}") from exc
	return data

# Check if `path` is a sub-path of `root`
def is_subpath(path: str, root_path: str) -> bool:
	import os
	path = os.path.realpath(path)
	root_path = os.path.realpath(root_path)
	if not root_path.endswith(os.sep):
		root_path += os.sep
	return path.startswith(root_path) # Python3: os.path.commonpath

# If `file_path` is an existing file in an internal folder, check if the user actually wants to overwrite it
def check_allow_overwrite_internal_file(file_path: str) -> bool:
	from . import Assets
	from .UIKit import MessageBox  # pylint: disable=cyclic-import
	import os
	if not is_subpath(file_path, Assets.base_dir):
		return True
	if not os.path.exists(file_path):
		return True
	return MessageBox.askyesno('Overwrite internal file?', f"Are you sure you want to overwrite internal file '{os.path.basename(file_path)}'? This could result in problems or negative experiences.") == MessageBox.YES
