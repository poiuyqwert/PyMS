
from __future__ import annotations

from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import struct

class VX4Minitile:
	def __init__(self, image_id: int = 0, flipped: bool = False) -> None:
		self.image_id = image_id
		self.flipped = flipped

	def load_data(self, data: bytes) -> None:
		if len(data) == 2:
			struct_format = '<H'
		else:
			struct_format = '<L'
		value = int(struct.unpack(struct_format, data)[0])
		self.flipped = bool(value & 1)
		self.image_id = value >> 1

	def save_data(self, expanded: bool) -> bytes:
		if expanded:
			struct_format = '<L'
		else:
			struct_format = '<H'
		return struct.pack(struct_format, int(self.flipped) | (self.image_id << 1))

	def __hash__(self) -> int:
		return hash((self.image_id, self.flipped))

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, VX4Minitile):
			return NotImplemented
		return self.image_id == other.image_id and self.flipped == other.flipped

class VX4Megatile:
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

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, VX4Megatile):
			return NotImplemented
		return self.minitiles == other.minitiles

class VX4:
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
		# Verify each hash hit with `==` so colliding-but-distinct megatiles
		# don't get treated as duplicates (callers reuse the returned tile ids).
		candidates = self._lookup.get(hash(megatile), [])
		return [tile_id for tile_id in candidates if self._megatiles[tile_id] == megatile]

	def get_megatile(self, tile_id: int) -> VX4Megatile:
		return self._megatiles[tile_id]

	def add_megatile(self, megatile: VX4Megatile) -> None:
		tile_id = len(self._megatiles)
		self._megatiles.append(megatile)
		megatile_hash = hash(megatile)
		if not megatile_hash in self._lookup:
			self._lookup[megatile_hash] = []
		self._lookup[megatile_hash].append(tile_id)

	def set_megatile(self, tile_id: int, megatile: VX4Megatile) -> None:
		old_hash = hash(self._megatiles[tile_id])
		self._lookup[old_hash].remove(tile_id)
		if len(self._lookup[old_hash]) == 0:
			del self._lookup[old_hash]
		self._megatiles[tile_id] = megatile
		megatile_hash = hash(megatile)
		if not megatile_hash in self._lookup:
			self._lookup[megatile_hash] = []
		self._lookup[megatile_hash].append(tile_id)

	# expanded = True, False, or None (None = .vx4ex file extension detection)
	def load(self, any_input: IO.AnyInputBytes, expanded: bool | None = None) -> None:
		if expanded is None and isinstance(any_input, str):
			expanded = (any_input[-6:].lower() == '.vx4ex')
		with IO.InputBytes(any_input) as f:
			data = f.read()
		if expanded is None:
			expanded = (len(data) // 32 >= VX4.MAX_ID)
		struct_size = (64 if expanded else 32)
		file_type = 'Expanded VX4 file' if expanded else 'VX4 file'
		if data and len(data) % struct_size:
			raise PyMSError('Load', f"Invalid {file_type}")
		megatiles: list[VX4Megatile] = []
		lookup: dict[int, list[int]] = {}
		try:
			o = 0
			for tile_id in range(len(data) // struct_size):
				megatile = VX4Megatile()
				megatile.load_data(data[o:o+struct_size])
				o += struct_size
				megatiles.append(megatile)
				megatile_hash = hash(megatile)
				if not megatile_hash in lookup:
					lookup[megatile_hash] = []
				lookup[megatile_hash].append(tile_id)
		except Exception as exc:
			raise PyMSError('Load', f"Unsupported {file_type}, could possibly be corrupt") from exc
		self._megatiles = megatiles
		self._lookup = lookup
		self._expanded = expanded

	def save(self, output: IO.AnyOutputBytes) -> None:
		data = b''
		for megatile in self._megatiles:
			data += megatile.save_data(self._expanded)
		with IO.OutputBytes(output) as f:
			f.write(data)
