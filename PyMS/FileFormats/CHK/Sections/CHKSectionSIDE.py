
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionSIDE(CHKSection):
	NAME = 'SIDE'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	ZERG = 0
	TERRAN = 1
	PROTOSS = 2
	UNUSED_INDEPENDENT = 3
	UNUSED_NEUTRAL = 4
	USER_SELECT = 5
	RANDOM = 6
	INACTIVE = 7
	@staticmethod
	def SIDE_NAME(v):
		names = {
			CHKSectionSIDE.ZERG:'Zerg',
			CHKSectionSIDE.TERRAN:'Terran',
			CHKSectionSIDE.PROTOSS:'Protoss',
			CHKSectionSIDE.UNUSED_INDEPENDENT: 'Unused (Independent)',
			CHKSectionSIDE.UNUSED_NEUTRAL: 'Unused (Neutral)',
			CHKSectionSIDE.USER_SELECT: 'User Select',
			CHKSectionSIDE.RANDOM: 'Random',
			CHKSectionSIDE.INACTIVE: 'Inactive'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.sides = [CHKSectionSIDE.RANDOM] * 8 + [CHKSectionSIDE.INACTIVE] * 4
	
	def load_data(self, data):
		self.sides = list(struct.unpack('<12B', data[:12]))
	
	def save_data(self):
		return struct.pack('<12B', *self.sides)
	
	def decompile(self):
		result = '%s:\n' % self.NAME
		for n,value in enumerate(self.sides):
			result += '\t%s # %s\n' % (pad('Slot%02d' % n,value), CHKSectionSIDE.SIDE_NAME(value))
		return result
