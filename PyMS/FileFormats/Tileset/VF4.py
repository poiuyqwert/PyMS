
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
	blocks_view = 0x0008
	ramp        = 0x0010
	
class VF4(object):
	MAX_ID = 65535

	def __init__(self): # type: () -> None
		self._flags = [] # type: list[list[int]]

	def flag_count(self): # type: () -> int
		return len(self._flags)

	def flags_remaining(self): # type: () -> int
		return (VF4.MAX_ID+1) - len(self._flags)

	def get_flags(self, id): # type: (int) -> list[int]
		return self._flags[id]

	def add_flags(self, flags): # type: (list[int]) -> int
		if len(flags) != 16:
			raise PyMSError('Add Flags', 'Invalid minitile flags (expected list of size 16, got %d)' % len(flags))
		id = len(self._flags)
		self._flags.append(flags)
		return id

	def load_file(self, file): # type: (str | BinaryIO) -> None
		data = load_file(file, 'VF4')
		if data and len(data) % 32:
			raise PyMSError('Load',"'%s' is an invalid VF$ file" % file)
		flags = [] # type: list[list[int]]
		try:
			o = 0
			while o + 31 < len(data):
				flags.append(list(int(v) for v in struct.unpack('<16H', data[o:o+32])))
				o += 32
		except:
			raise PyMSError('Load',"Unsupported VF4 file '%s', could possibly be corrupt" % file)
		self._flags = flags

	def save_file(self, file): # type: (str | BinaryIO) -> None
		data = b''
		for d in self._flags:
			data += struct.pack('<16H', *d)
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
