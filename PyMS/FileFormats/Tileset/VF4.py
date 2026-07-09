
from __future__ import annotations

from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import struct

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

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, VF4Megatile):
			return NotImplemented
		return other.flags == self.flags

class VF4:
	MAX_ID = 65535

	def __init__(self) -> None:
		self._megatile: list[VF4Megatile] = []

	def megatile_count(self) -> int:
		return len(self._megatile)

	def megatiles_remaining(self) -> int:
		return (VF4.MAX_ID+1) - len(self._megatile)

	def get_megatile(self, tile_id: int) -> VF4Megatile:
		return self._megatile[tile_id]

	def add_megatile(self, flags: VF4Megatile) -> int:
		tile_id = len(self._megatile)
		self._megatile.append(flags)
		return tile_id

	def load(self, any_input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		if data and len(data) % 32:
			raise PyMSError('Load', "Invalid VF4 file")
		all_megatile: list[VF4Megatile] = []
		try:
			o = 0
			while o + 31 < len(data):
				flags = VF4Megatile()
				flags.load_data(data[o:o+32])
				all_megatile.append(flags)
				o += 32
		except Exception as exc:
			raise PyMSError('Load', "Unsupported VF4 file, could possibly be corrupt") from exc
		self._megatile = all_megatile

	def save(self, output: IO.AnyOutputBytes) -> None:
		data = b''
		for flags in self._megatile:
			data += flags.save_data()
		with IO.OutputBytes(output) as f:
			f.write(data)
