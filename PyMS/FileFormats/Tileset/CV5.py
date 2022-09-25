
from ...Utilities.utils import isstr
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

class CV5:
	MAX_ID = 4095
	def __init__(self):
		self.groups = []

	def groups_remaining(self):
		return (CV5.MAX_ID+1) - len(self.groups)

	def load_file(self, file):
		data = load_file(file, 'CV5')
		if data and len(data) % 52:
			raise PyMSError('Load',"'%s' is an invalid CV5 file" % file)
		groups = []
		try:
			o = 0
			while o + 51 < len(data):
				d = list(struct.unpack('<HBB24H', data[o:o+52]))
				groups.append([d[0],(d[1] & 240) >> 4,d[1] & 15,(d[2] & 240) >> 4,d[2] & 15] + d[3:11] + [d[11:]])
				o += 52
		except:
			raise PyMSError('Load',"Unsupported CV5 file '%s', could possibly be corrupt" % file)
		self.groups = groups
		# n = len(groups[0])-1
		# info = [{} for _ in xrange(n)]
		# for gid in xrange(1024):
		# 	group = groups[gid]
		# 	for i in xrange(n):
		# 		v = group[i]
		# 		if not v in info[i]:
		# 			info[i][v] = []
		# 		info[i][v].append(gid)
		# names = ['index','buildable','flags','buildable2','groundheight','edgeleft','edgeup','edgeright','edgedown','unknown9','hasup','unknown11','hasdown']
		# for name,data in zip(names,info):
		# 	print(name)
		# 	for k in sorted(data.keys()):
		# 		print('\t%s' % k)
		# 		print('\t\t%s' % data[k])

	def save_file(self, file):
		data = ''
		for d in self.groups:
			data += struct.pack('<HBB24H', *[d[0],(d[1] << 4) + d[2],(d[3] << 4) + d[4]] + d[5:13] + d[13])
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the CV5 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()
