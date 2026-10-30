
from __future__ import annotations

from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import struct

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

	def load(self, any_input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		if len(data) != 262144:
			raise PyMSError('Load', "Invalid dddata.bin file")
		doodads: list[list[int]] = []
		try:
			o = 0
			while o + 511 < len(data):
				doodads.append(list(int(v) for v in struct.unpack('<256H', data[o:o+512])))
				o += 512
		except Exception as exc:
			raise PyMSError('Load', "Unsupported dddata.dat file, could possibly be corrupt") from exc
		self._doodads = doodads

	def save(self, output: IO.AnyOutputBytes) -> None:
		data = b''
		for d in self._doodads:
			data += struct.pack('<256H', *d)
		with IO.OutputBytes(output) as f:
			f.write(data)
