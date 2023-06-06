
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, binary

import struct

class CHKSectionMASK(CHKSection):
	NAME = 'MASK'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	raw_map: bytes
	map: list[list[int]]
	# def __init__(self, chk): # type: (CHK) -> None
	# 	CHKSection.__init__(self, chk)
	# 	self.raw_map = b''
	# 	self.map = None # types: list[list[int]] | None
	
	def load_data(self, data): # type: (bytes) -> None
		self.raw_map = data
	
	def requires_post_processing(self): # type: () -> bool
		return True
	
	def process_data(self): # type: () -> None
		if self.map is not None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += '\xFF' * diff
		struct_format = '<%dB' % dims.width
		for y in range(dims.height):
			offset = y*dims.width
			self.map.append(list(int(t) for t in struct.unpack(struct_format, self.raw_map[offset:offset+dims.width])))
	
	def save_data(self): # type: () -> bytes
		dims = self.chk.get_section(CHKSectionDIM)
		assert dims is not None
		result = b''
		struct_format = '<%dB' % dims.width
		for r in self.map:
			result += struct.pack(struct_format, *r)
		return result

	def decompile(self): # type: () -> str
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(binary(t,8),span=9)
			result += '\n'
		return result
