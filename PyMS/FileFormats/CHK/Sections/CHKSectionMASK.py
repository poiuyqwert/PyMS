
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, binary

import struct

class CHKSectionMASK(CHKSection):
	NAME = b'MASK'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)

	raw_map: bytes
	map: list[list[int]] | None = None

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
			self.raw_map += b'\xff' * diff
		struct_format = f'<{dims.width}B'
		for y in range(dims.height):
			offset = y*dims.width
			self.map.append(list(int(t) for t in struct.unpack(struct_format, self.raw_map[offset:offset+dims.width])))

	def save_data(self) -> bytes:
		dims = self.chk.get_section(CHKSectionDIM)
		assert dims is not None
		assert self.map is not None
		result = b''
		struct_format = f'<{dims.width}B'
		for r in self.map:
			result += struct.pack(struct_format, *r)
		return result

	def decompile(self) -> str:
		assert self.map is not None
		result = f'{self.NAME.decode("ascii")}:\n'
		for row in self.map:
			for t in row:
				result += pad(binary(t,8),span=9)
			result += '\n'
		return result
