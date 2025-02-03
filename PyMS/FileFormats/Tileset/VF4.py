
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

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

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, VF4Megatile):
			return False
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

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'VF4')
		if data and len(data) % 32:
			raise PyMSError('Load', f"'{file}' is an invalid VF4 file")
		all_megatile: list[VF4Megatile] = []
		try:
			o = 0
			while o + 31 < len(data):
				flags = VF4Megatile()
				flags.load_data(data[o:o+32])
				all_megatile.append(flags)
				o += 32
		except Exception as exc:
			raise PyMSError('Load', f"Unsupported VF4 file '{file}', could possibly be corrupt") from exc
		self._megatile = all_megatile

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for flags in self._megatile:
			data += flags.save_data()
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except Exception as exc:
				raise PyMSError('Save', f"Could not save the VF4 to '{file}'") from exc
		else:		
			file.write(data)
			file.close()
