
from .utils import isstr
from .PyMSError import PyMSError

class BadFile:
	def __init__(self, file):
		self.file = file

	def __str__(self):
		return self.file

	def __nonzero__(self):
		return False

class SFile:
	def __init__(self, text='', file='<Internal SFile>'):
		self.text = text
		self.file = file

	def write(self, text):
		self.text += text

	def read(self):
		return self.text

	def close(self):
		pass

	def __str__(self):
		return self.file

def load_file(file, file_type='file', mode='rb'):
	try:
		if isstr(file):
			f = open(file,mode)
		else:
			f = file
		data = f.read()
	except:
		name = ''
		if isstr(file):
			name = " '%s'" % file
		elif isinstance(file, BadFile):
			name = " '%s'" % file.file
		raise PyMSError('Load',"Could not load %s%s" % (file_type, name), capture_exception=True)
	finally:
		try:
			f.close()
		except:
			pass
	return data

# Check if `path` is a sub-path of `root`
def is_subpath(path, root_path): # type: (str, str) -> bool
	import os
	path = os.path.realpath(path)
	root_path = os.path.realpath(root_path)
	if not root_path.endswith(os.sep):
		root_path += os.sep
	return path.startswith(root_path) # Python3: os.path.commonpath

# If `file_path` is an existing file in an internal folder, check if the user actually wants to overwrite it
def check_allow_overwrite_internal_file(file_path): # type: (str) -> bool
	from . import Assets
	from .UIKit import MessageBox
	import os
	if not is_subpath(file_path, Assets.base_dir):
		return True
	if not os.path.exists(file_path):
		return True
	return MessageBox.askyesno('Overwrite internal file?', "Are you sure you want to overwrite internal file '%s'? This could result in problems or negative experiences." % os.path.basename(file_path)) == MessageBox.YES
