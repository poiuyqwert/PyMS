
from ...Utilities.utils import isstr
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

class VX4:
	MAX_ID = 65535
	def __init__(self, expanded=False):
		self.graphics = []
		self.lookup = {}
		self.expanded = expanded

	def graphics_remaining(self):
		return (VX4.MAX_ID+1) - len(self.graphics)

	def find_tile(self, tile):
		tile = tuple(tuple(r) for r in tile)
		tile_hash = hash(tile)
		if tile_hash in self.lookup:
			return self.lookup[tile_hash]
		return None

	def add_tile(self, tile):
		correct_size = (len(tile) == 16)
		if correct_size:
			for r in tile:
				if len(r) != 2:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Add Tile', 'Incorrect tile size')
		id = len(self.graphics)
		self.graphics.append(tuple(tuple(r) for r in tile))
		tile_hash = hash(self.graphics[id])
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)
	def set_tile(self, id, tile):
		correct_size = (len(tile) == 16)
		if correct_size:
			for r in tile:
				if len(r) != 2:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Set Tile', 'Incorrect tile size')
		old_hash = hash(self.graphics[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.graphics[id] = tuple(tuple(r) for r in tile)
		tile_hash = hash(self.graphics[id])
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)

	# expanded = True, False, or None (None = .vx4ex file extension detection)
	def load_file(self, file, expanded=None):
		if expanded == None and isstr(file):
			expanded = (file[-6:].lower() == '.vx4ex')
		data = load_file(file, 'VX4')
		struct_size = (64 if expanded else 32)
		file_type = 'Expanded VX4 file' if expanded else 'VX4 file'
		if data and len(data) % struct_size:
			raise PyMSError('Load',"'%s' is an invalid %s" % (file, file_type))
		graphics = []
		lookup = {}
		try:
			ref_size_max = 0xFFFFFFFE if expanded else 0xFFFE
			struct_frmt = '<16L' if expanded else '<16H'
			for id in range(len(data) / struct_size):
				graphics.append(tuple(((d & ref_size_max)/2,d & 1) for d in struct.unpack(struct_frmt, data[id*struct_size:(id+1)*struct_size])))
				tile_hash = hash(graphics[-1])
				if not tile_hash in lookup:
					lookup[tile_hash] = []
				lookup[tile_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported %s '%s', could possibly be corrupt" % (file_type, file))
		self.graphics = graphics
		self.lookup = lookup
		self.expanded = expanded

	def save_file(self, file):
		data = ''
		struct_frmt = '<16L' if self.expanded else '<16H'
		for d in self.graphics:
			data += struct.pack(struct_frmt, *[g*2 + h for g,h in d])
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VX4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()
