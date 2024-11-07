
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionMTXM(CHKSection):
	NAME = 'MTXM'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	raw_map: bytes
	map: list[list[list[int]]]
	
	def load_data(self, data: bytes) -> None:
		self.raw_map = data
	
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
		struct_format = '<%dH' % dims.width
		for y in range(dims.height):
			offset = y*dims.width*2
			values = tuple(int(t) for t in struct.unpack(struct_format, self.raw_map[offset:offset+dims.width*2]))
			self.map.append([[(v & 0xFFF0) >> 4,v & 0xF] for v in values])
	
	def save_data(self) -> bytes:
		dims = self.chk.get_section(CHKSectionDIM)
		assert dims is not None
		result = b''
		struct_format = '<%dH' % dims.width
		for r in self.map:
			values = [v[0] << 4 + v[1] for v in r]
			result += struct.pack(struct_format, *values)
		return result

	def decompile(self) -> str:
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad('%d,%d' % t,span=6)
			result += '\n'
		return result
