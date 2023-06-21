
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

class VF4Flag:
	walkable    = 0x0001
	mid_ground  = 0x0002
	high_ground = 0x0004
	blocks_sight = 0x0008
	ramp        = 0x0010

class VF4Megatile:
	def __init__(self) -> None:
		self.flags = [0] * 16

	def load_data(self, data: bytes) -> None:
		self.flags = list(int(v) for v in struct.unpack('<16H', data))

	def save_data(self) -> bytes:
		return struct.pack('<16H', *self.flags)

	def __eq__(self, other) -> bool:
		if not isinstance(other, VF4Megatile):
			return False
		return other.flags == self.flags

class VF4(object):
	MAX_ID = 65535

	def __init__(self): # type: () -> None
		self._megatile = [] # type: list[VF4Megatile]

	def megatile_count(self): # type: () -> int
		return len(self._megatile)

	def megatiles_remaining(self): # type: () -> int
		return (VF4.MAX_ID+1) - len(self._megatile)

	def get_megatile(self, id): # type: (int) -> VF4Megatile
		return self._megatile[id]

	def add_megatile(self, flags): # type: (VF4Megatile) -> int
		id = len(self._megatile)
		self._megatile.append(flags)
		return id

	def load_file(self, file): # type: (str | BinaryIO) -> None
		data = load_file(file, 'VF4')
		if data and len(data) % 32:
			raise PyMSError('Load',"'%s' is an invalid VF4 file" % file)
		all_megatile = [] # type: list[VF4Megatile]
		try:
			o = 0
			while o + 31 < len(data):
				flags = VF4Megatile()
				flags.load_data(data[o:o+32])
				all_megatile.append(flags)
				o += 32
		except:
			raise PyMSError('Load',"Unsupported VF4 file '%s', could possibly be corrupt" % file)
		self._megatile = all_megatile

	def save_file(self, file): # type: (str | BinaryIO) -> None
		data = b''
		for flags in self._megatile:
			data += flags.save_data()
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the VF4 to '%s'" % file)
		else:		
			file.write(data)
			file.close()
