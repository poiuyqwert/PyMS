
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

class VX4Minitile(object):
	def __init__(self):
		self.flipped = False
		self.image_id = 0

	def load_data(self, data): # type: (bytes) -> None
		if len(data) == 2:
			format = '<H'
		else:
			format = '<L'
		value = int(struct.unpack(format, data)[0])
		self.flipped = bool(value & 1)
		self.image_id = value >> 1

	def save_data(self, expanded): # type: (bool) -> bytes
		if expanded:
			format = '<L'
		else:
			format = '<H'
		return struct.pack(format, int(self.flipped) | (self.image_id << 1))

	def __hash__(self) -> int:
		return hash((self.flipped, self.image_id))

class VX4Megatile(object):
	def __init__(self): # type: () -> None
		self.minitiles = [] # type: list[VX4Minitile]

	def load_data(self, data): # type: (bytes) -> None
		size = int(len(data) / 16)
		o = 0
		for _ in range(16):
			minitile = VX4Minitile()
			minitile.load_data(data[o:o+size])
			o += size

	def save_data(self, expanded): # type: (bool) -> bytes
		data = b''
		for minitile in self.minitiles:
			data += minitile.save_data(expanded)
		return data

	def __hash__(self) -> int:
		return hash(tuple(self.minitiles))

class VX4(object):
	MAX_ID = 65535

	def __init__(self, expanded=False): # type: (bool) -> None
		self.megatiles = [] # type: list[VX4Megatile]
		self.lookup = {} # type: dict[int, list[int]]
		self.expanded = expanded

	def graphics_remaining(self): # type: () -> int
		return (VX4.MAX_ID+1) - len(self.megatiles)

	# def find_tile(self, tile):
	# 	tile = tuple(tuple(r) for r in tile)
	# 	tile_hash = hash(tile)
	# 	if tile_hash in self.lookup:
	# 		return self.lookup[tile_hash]
	# 	return None

	def add_tile(self, tile): # type: (VX4Megatile) -> None
		id = len(self.megatiles)
		self.megatiles.append(tile)
		tile_hash = hash(tile)
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)

	def set_tile(self, id, tile): # type: (int, VX4Megatile) -> None
		old_hash = hash(self.megatiles[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.megatiles[id] = tile
		tile_hash = hash(tile)
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)

	# expanded = True, False, or None (None = .vx4ex file extension detection)
	def load_file(self, file, expanded=None): # type: (str | BinaryIO, bool | None) -> None
		if expanded is None and isinstance(file, str):
			expanded = (file[-6:].lower() == '.vx4ex')
		data = load_file(file, 'VX4')
		if expanded is None:
			expanded = (len(data) / 32 >= VX4.MAX_ID)
		struct_size = (64 if expanded else 32)
		file_type = 'Expanded VX4 file' if expanded else 'VX4 file'
		if data and len(data) % struct_size:
			raise PyMSError('Load',"'%s' is an invalid %s" % (file, file_type))
		megatiles = [] # type: list[VX4Megatile]
		lookup = {} # type: dict[int, list[int]]
		try:
			o = 0
			for id in range(int(len(data) / struct_size)):
				megatile = VX4Megatile()
				megatile.load_data(data[o:o+struct_size])
				o += struct_size
				self.megatiles.append(megatile)
				tile_hash = hash(megatile)
				if not tile_hash in lookup:
					lookup[tile_hash] = []
				lookup[tile_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported %s '%s', could possibly be corrupt" % (file_type, file))
		self.megatiles = megatiles
		self.lookup = lookup
		self.expanded = expanded

	def save_file(self, file): # type: (str | BinaryIO) -> None
		data = b''
		for megatile in self.megatiles:
			data += megatile.save_data(self.expanded)
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the VX4 to '%s'" % file)
		else:
			file.write(data)
			file.close()
