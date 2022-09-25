
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionIVE2(CHKSection):
	NAME = 'IVE2'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	RELEASE = 11
	@staticmethod
	def VER_NAME(v):
		names = {
			CHKSectionIVE2.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVE2.RELEASE
	
	def load_data(self, data):
		self.version = struct.unpack('<H', data[:2])[0]
	
	def save_data(self):
		return struct.pack('<H', self.version)

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',self.version), CHKSectionIVE2.VER_NAME(self.version))
