
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

class DDDataBIN(object):
	def __init__(self) -> None:
		self._doodads = [[0]*256 for _ in range(512)]

	def doodad_count(self) -> int:
		return len(self._doodads)
	
	def get_doodad(self, id: int) -> list[int]:
		return self._doodads[id]

	def add_doodad(self, doodad: list[int]) -> int:
		if len(doodad) != 256:
			raise PyMSError('Add Doodad', 'Incorrect doodad placeability (expected list of size 256, got %d)' % len(doodad))
		id = len(self._doodads)
		self._doodads.append(doodad)
		return id

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'dddata.dat')
		if len(data) != 262144:
			raise PyMSError('Load',"'%s' is an invalid dddata.bin file" % file)
		doodads: list[list[int]] = []
		try:
			o = 0
			while o + 511 < len(data):
				doodads.append(list(int(v) for v in struct.unpack('<256H', data[o:o+512])))
				o += 512
		except:
			raise PyMSError('Load',"Unsupported dddata.dat file '%s', could possibly be corrupt" % file)
		self._doodads = doodads

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for d in self._doodads:
			data += struct.pack('<256H', *d)
		if isinstance(file, str):
			try:
				f = AtomicWriter(file)
				f.write(data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the dddata.dat to '%s'" % file)
		else:
			file.write(data)
			file.close()
