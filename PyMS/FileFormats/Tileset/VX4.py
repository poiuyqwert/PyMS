
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

class VX4Minitile(object):
	def __init__(self, image_id: int = 0, flipped: bool = False) -> None:
		self.image_id = image_id
		self.flipped = flipped

	def load_data(self, data: bytes) -> None:
		if len(data) == 2:
			format = '<H'
		else:
			format = '<L'
		value = int(struct.unpack(format, data)[0])
		self.flipped = bool(value & 1)
		self.image_id = value >> 1

	def save_data(self, expanded: bool) -> bytes:
		if expanded:
			format = '<L'
		else:
			format = '<H'
		return struct.pack(format, int(self.flipped) | (self.image_id << 1))

	def __hash__(self) -> int:
		return hash((self.image_id, self.flipped))

class VX4Megatile(object):
	def __init__(self, minitiles: list[VX4Minitile] | None = None) -> None:
		if minitiles is None:
			self.minitiles = list(VX4Minitile() for _ in range(16))
		else:
			self.minitiles = minitiles

	def load_data(self, data: bytes) -> None:
		size = len(data) // 16
		o = 0
		for n in range(16):
			self.minitiles[n].load_data(data[o:o+size])
			o += size

	def save_data(self, expanded: bool) -> bytes:
		data = b''
		for minitile in self.minitiles:
			data += minitile.save_data(expanded)
		return data

	def __hash__(self) -> int:
		return hash(tuple(self.minitiles))

class VX4(object):
	MAX_ID = 65535

	def __init__(self, expanded: bool = False) -> None:
		self._megatiles: list[VX4Megatile] = []
		self._lookup: dict[int, list[int]] = {}
		self._expanded = expanded

	def is_expanded(self) -> bool:
		return self._expanded

	def expand(self) -> None:
		self._expanded = True

	def megatile_count(self) -> int:
		return len(self._megatiles)

	def megatiles_remaining(self) -> int:
		return (VX4.MAX_ID+1) - len(self._megatiles)

	def find_megatile_ids(self, megatile: VX4Megatile) -> list[int]:
		return self._lookup.get(hash(megatile), [])

	def get_megatile(self, id: int) -> VX4Megatile:
		return self._megatiles[id]

	def add_megatile(self, megatile: VX4Megatile) -> None:
		id = len(self._megatiles)
		self._megatiles.append(megatile)
		megatile_hash = hash(megatile)
		if not megatile_hash in self._lookup:
			self._lookup[megatile_hash] = []
		self._lookup[megatile_hash].append(id)

	def set_megatile(self, id: int, megatile: VX4Megatile) -> None:
		old_hash = hash(self._megatiles[id])
		self._lookup[old_hash].remove(id)
		if len(self._lookup[old_hash]) == 0:
			del self._lookup[old_hash]
		self._megatiles[id] = megatile
		megatile_hash = hash(megatile)
		if not megatile_hash in self._lookup:
			self._lookup[megatile_hash] = []
		self._lookup[megatile_hash].append(id)

	# expanded = True, False, or None (None = .vx4ex file extension detection)
	def load_file(self, file: str | BinaryIO, expanded: bool | None = None) -> None:
		if expanded is None and isinstance(file, str):
			expanded = (file[-6:].lower() == '.vx4ex')
		data = load_file(file, 'VX4')
		if expanded is None:
			expanded = (len(data) // 32 >= VX4.MAX_ID)
		struct_size = (64 if expanded else 32)
		file_type = 'Expanded VX4 file' if expanded else 'VX4 file'
		if data and len(data) % struct_size:
			raise PyMSError('Load',"'%s' is an invalid %s" % (file, file_type))
		megatiles: list[VX4Megatile] = []
		lookup: dict[int, list[int]] = {}
		try:
			o = 0
			for id in range(len(data) // struct_size):
				megatile = VX4Megatile()
				megatile.load_data(data[o:o+struct_size])
				o += struct_size
				megatiles.append(megatile)
				megatile_hash = hash(megatile)
				if not megatile_hash in lookup:
					lookup[megatile_hash] = []
				lookup[megatile_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported %s '%s', could possibly be corrupt" % (file_type, file))
		self._megatiles = megatiles
		self._lookup = lookup
		self._expanded = expanded

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for megatile in self._megatiles:
			data += megatile.save_data(self._expanded)
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
