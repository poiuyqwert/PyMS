
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionTILE(CHKSection):
	NAME = 'TILE'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.raw_map = ''
		self.map = None
	
	def load_data(self, data):
		self.raw_map = data
	
	def process_data(self):
		if self.map != None:
			return
		self.map = []
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		diff = dims.width*dims.height - len(self.raw_map)
		if diff > 0:
			self.raw_map += '\0' * diff
		struct_format = '<%dH' % dims.width
		for y in range(dims.height):
			offset = y*dims.width*2
			values = struct.unpack(struct_format, self.raw_map[offset:offset+dims.width*2])
			self.map.append([[(v & 0xFFF0) >> 4,v & 0xF] for v in values])

	def save_data(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		result = ''
		struct_format = '<%dH' % dims.width
		for r in self.map:
			values = [v[0] << 4 + v[1] for v in r]
			result += struct.pack(struct_format, *values)
		return result

	def decompile(self):
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(t,span=6)
			result += '\n'
		return result
