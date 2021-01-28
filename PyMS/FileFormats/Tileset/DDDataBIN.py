
from ...Utilities.utils import isstr
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

class DDDataBIN:
	def __init__(self):
		self.doodads = [[0]*256 for _ in range(512)]

	def load_file(self, file):
		data = load_file(file, 'dddata.dat')
		if len(data) != 262144:
			raise PyMSError('Load',"'%s' is an invalid dddata.bin file" % file)
		doodads = []
		try:
			o = 0
			while o + 511 < len(data):
				doodads.append(list(struct.unpack('<256H', data[o:o+512])))
				o += 512
		except:
			raise PyMSError('Load',"Unsupported dddata.dat file '%s', could possibly be corrupt" % file)
		self.doodads = doodads

	def save_file(self, file):
		data = ''
		for d in self.doodads:
			data += struct.pack('<256H', *d)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the dddata.dat to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()
