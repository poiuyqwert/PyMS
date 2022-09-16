
from .CHKSectionDIM import CHKSectionDIM

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad, binary

import struct

class CHKSectionMASK(CHKSection):
	NAME = 'MASK'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
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
			self.raw_map += '\xFF' * diff
		struct_format = '<%dB' % dims.width
		for y in range(dims.height):
			offset = y*dims.width
			self.map.append(list(struct.unpack(struct_format, self.raw_map[offset:offset+dims.width])))
	
	def save_data(self):
		dims = self.chk.get_section(CHKSectionDIM.NAME)
		result = ''
		struct_format = '<%dB' % dims.width
		for r in self.map:
			result += struct.pack(struct_format, *r)
		return result

	def decompile(self):
		result = '%s:\n' % self.NAME
		for row in self.map:
			for t in row:
				result += pad(binary(t,8),span=9)
			result += '\n'
		return result
