
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionIOWN(CHKSection):
	NAME = 'IOWN'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	INACTIVE = 0
	COMPUTER_GAME_INVALID = 1 # INVALID
	OCCUPIED_HUMAN_INVALID = 2 # INVALID
	RESUE_PASSIVE = 3
	UNUSED = 4
	COMPUTER = 5
	HUMAN = 6
	NEUTRAL = 7
	CLOSED_INVALID = 8 # INVALID
	@staticmethod
	def OWNER_NAME(v):
		names = {
			CHKSectionIOWN.INACTIVE:'Inactive',
			CHKSectionIOWN.COMPUTER_GAME_INVALID:'Occupied by Computer (Invalid)',
			CHKSectionIOWN.OCCUPIED_HUMAN_INVALID:'Occupied by Human Player (Invalid)',
			CHKSectionIOWN.RESUE_PASSIVE: 'Rescue Passive',
			CHKSectionIOWN.UNUSED: 'Unused',
			CHKSectionIOWN.COMPUTER: 'Computer',
			CHKSectionIOWN.HUMAN: 'Human',
			CHKSectionIOWN.NEUTRAL: 'Neutral',
			CHKSectionIOWN.CLOSED_INVALID: 'Closed (Invalid)'
		}
		return names.get(v,'Unknown')
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.owners = [CHKSectionIOWN.HUMAN]*8 + [CHKSectionIOWN.INACTIVE]*4
	
	def load_data(self, data):
		self.owners = list(struct.unpack('<12B', data[:12]))
	
	def save_data(self):
		return struct.pack('<12B', *self.owners)

	def decompile(self):
		result = '%s:\n' % self.NAME
		for n,value in enumerate(self.owners):
			result += '\t%s # %s\n' % (pad('Slot%02d' % n,value), CHKSectionIOWN.OWNER_NAME(value))
		return result
