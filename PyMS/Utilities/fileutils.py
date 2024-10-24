
from __future__ import annotations

from .PyMSError import PyMSError

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

# TODO: Replace usage with IO
def load_file(file: str | BinaryIO, file_type: str = 'file', mode: str = 'rb') -> bytes:
	try:
		if isinstance(file, str):
			f = open(file, mode)
		else:
			f = file
		data = f.read()
	except Exception:
		name = ''
		if isinstance(file, str):
			name = " '%s'" % file
		raise PyMSError('Load',"Could not load %s%s" % (file_type, name), capture_exception=True)
	finally:
		try:
			f.close()
		except:
			pass
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
	from .UIKit import MessageBox
	import os
	if not is_subpath(file_path, Assets.base_dir):
		return True
	if not os.path.exists(file_path):
		return True
	return MessageBox.askyesno('Overwrite internal file?', "Are you sure you want to overwrite internal file '%s'? This could result in problems or negative experiences." % os.path.basename(file_path)) == MessageBox.YES
