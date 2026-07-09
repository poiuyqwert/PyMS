
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionMTXM(CHKSection):
	NAME = b'MTXM'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	raw_map: bytes
	map: list[list[list[int]]] | None = None

	def load_data(self, data: bytes) -> None:
		self.raw_map = data
		self.map = None

	def requires_post_processing(self) -> bool:
		return True

	def process_data(self) -> None:
		if self.map is not None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM)
		assert dims is not None
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += b'\0' * diff
		struct_format = f'<{dims.width}H'
		for y in range(dims.height):
			offset = y*dims.width*2
			values = tuple(int(t) for t in struct.unpack(struct_format, self.raw_map[offset:offset+dims.width*2]))
			self.map.append([[(v & 0xFFF0) >> 4,v & 0xF] for v in values])

	def save_data(self) -> bytes:
		dims = self.chk.get_section(CHKSectionDIM)
		assert dims is not None
		assert self.map is not None
		result = b''
		struct_format = f'<{dims.width}H'
		for r in self.map:
			values = [(v[0] << 4) | v[1] for v in r]
			result += struct.pack(struct_format, *values)
		return result

	def decompile(self) -> str:
		assert self.map is not None
		result = f'{self.NAME.decode("ascii")}:\n'
		for row in self.map:
			for g,m in row:
				result += pad(f'{g},{m}',span=6)
			result += '\n'
		return result
