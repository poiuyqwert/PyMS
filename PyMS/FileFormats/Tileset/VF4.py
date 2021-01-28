
from ...Utilities.utils import isstr
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

class VF4:
	MAX_ID = 65535
	def __init__(self):
		self.flags = []

	def flags_remaining(self):
		return (VF4.MAX_ID+1) - len(self.flags)

	def load_file(self, file):
		data = load_file(file, 'VF4')
		if data and len(data) % 32:
			raise PyMSError('Load',"'%s' is an invalid VF$ file" % file)
		flags = []
		try:
			o = 0
			while o + 31 < len(data):
				flags.append(list(struct.unpack('<16H', data[o:o+32])))
				o += 32
		except:
			raise PyMSError('Load',"Unsupported VF4 file '%s', could possibly be corrupt" % file)
		self.flags = flags

	def save_file(self, file):
		data = ''
		for d in self.flags:
			data += struct.pack('<16H', *d)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VF4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()
