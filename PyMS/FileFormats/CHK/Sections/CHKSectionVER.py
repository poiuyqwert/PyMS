
from ..CHKSection import CHKSection

from ....Utilities.utils import pad

import struct

class CHKSectionVER(CHKSection):
	NAME = "VER "

	BETA = 57
	SC100 = 59
	SC104 = 63
	BW = 205
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionVER.BETA:'Beta',
			CHKSectionVER.SC100:'StarCraft 1.00',
			CHKSectionVER.SC104:'StarCraft 1.04+',
			CHKSectionVER.BW:'BroodWar'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionVER.BW
		from .CHKSectionTYPE import CHKSectionTYPE
		typeSect = chk.sections.get(CHKSectionTYPE.NAME)
		if typeSect and not typeSect.type == CHKSectionTYPE.BROODWAR:
			self.version = CHKSectionVER.SC104

	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]

	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionVER.VER_NAME(self.version))
