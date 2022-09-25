
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionERA(CHKSection):
	NAME = 'ERA '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	BADLANDS = 0
	SPACE = 1
	INSTALLATION = 2
	ASHWORLD = 3
	JUNGLE = 4
	DESERT = 5
	ARCTIC = 6
	TWILIGHT = 7
	@staticmethod
	def TILESET_NAME(t):
		return ['Badlands','Space Platform','Installation','Ashworld','Jungle','Desert','Arctic','Twilight'][t % (CHKSectionERA.TWILIGHT+1)]

	@staticmethod
	def TILESET_FILE(t):
		return ['badlands','platform','install','ashworld','jungle','desert','ice','twilight'][t % (CHKSectionERA.TWILIGHT+1)]

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.tileset = CHKSectionERA.BADLANDS
	
	def load_data(self, data):
		self.tileset = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.tileset)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Tileset',self.tileset), CHKSectionERA.TILESET_NAME(self.tileset))
