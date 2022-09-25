
from .utils import create_temp_file
from .PyMSError import PyMSError

import os, codecs

class AtomicWriter:
	def __init__(self, path, mode="w+b", createmode=None, encoding=None):
		self.real_file = path
		self.handle = None
		self.temp_file = None
		
		if os.path.isfile(path):
			temp_file = create_temp_file(path, createmode=createmode)
			if encoding:
				self.handle = codecs.open(temp_file, mode, encoding)
			else:
				self.handle = open(temp_file, mode)
			self.temp_file = temp_file
		else:
			self.handle = open(path, mode)

		self.write = self.handle.write
		self.fileno = self.handle.fileno

	def close(self):
		if self.handle and not self.handle.closed:
			self.handle.flush()
			os.fsync(self.handle.fileno())
			self.handle.close()
		if self.temp_file:
			bak_file = None
			if os.path.isfile(self.real_file):
				directory, filename = os.path.split(self.real_file)
				bak_name = '.%s~' % filename
				while os.path.isfile(os.path.join(directory,bak_name)):
					bak_name += '~'
				bak_file = os.path.join(directory, bak_name)
				try:
					os.rename(self.real_file, bak_file)
				except:
					bak_file = None
					pass
			try:
				os.rename(self.temp_file, self.real_file)
			except:
				if bak_file:
					try:
						os.rename(bak_file, self.real_file)
					except:
						pass
				raise PyMSError('Save', "File already exists and cannot be modified")
			finally:
				if bak_file:
					try:
						os.remove(bak_file)
					except:
						pass

	def discard(self):
		if self.handle and not self.handle.closed:
			self.handle.close()
		if self.temp_file:
			try:
				os.remove(self.temp_file)
			except:
				pass

	def __del__(self):
		self.discard()
