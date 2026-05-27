
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from typing import BinaryIO

class DDDataBIN:
	def __init__(self) -> None:
		self._doodads = [[0]*256 for _ in range(512)]

	def doodad_count(self) -> int:
		return len(self._doodads)

	def get_doodad(self, doodad_id: int) -> list[int]:
		return self._doodads[doodad_id]

	def add_doodad(self, doodad: list[int]) -> int:
		if len(doodad) != 256:
			raise PyMSError('Add Doodad', f'Incorrect doodad placeability (expected list of size 256, got {len(doodad)})')
		doodad_id = len(self._doodads)
		self._doodads.append(doodad)
		return doodad_id

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'dddata.dat')
		if len(data) != 262144:
			raise PyMSError('Load', f"'{file}' is an invalid dddata.bin file")
		doodads: list[list[int]] = []
		try:
			o = 0
			while o + 511 < len(data):
				doodads.append(list(int(v) for v in struct.unpack('<256H', data[o:o+512])))
				o += 512
		except Exception as exc:
			raise PyMSError('Load', f"Unsupported dddata.dat file '{file}', could possibly be corrupt") from exc
		self._doodads = doodads

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for d in self._doodads:
			data += struct.pack('<256H', *d)
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except Exception as exc:
				raise PyMSError('Save', f"Could not save the dddata.dat to '{file}'") from exc
		else:
			file.write(data)
			file.close()
