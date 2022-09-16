
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