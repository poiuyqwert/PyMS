
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionIVER(CHKSection):
	NAME = 'IVER'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	BETA = 9
	RELEASE = 10
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionIVER.BETA:'Beta',
			CHKSectionIVER.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVER.RELEASE
		from .CHKSectionVER import CHKSectionVER
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect and verSect.version == CHKSectionVER.BETA:
			self.version = CHKSectionIVER.BETA
	
	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionIVER.VER_NAME(self.version))
