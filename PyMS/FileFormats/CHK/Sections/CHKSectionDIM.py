
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionDIM(CHKSection):
	NAME = 'DIM '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	TINY = 64
	SMALL = 96
	MEDIUM = 128
	LARGE = 192
	HUGE = 256
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.width = CHKSectionDIM.MEDIUM
		self.height = CHKSectionDIM.MEDIUM
	
	def load_data(self, data):
		self.width,self.height = struct.unpack('<2H', data[:4])
	
	def save_data(self):
		return struct.pack('<2H', self.width, self.height)
	
	def decompile(self):
		return '%s:\n\t%s\n\t%s\n' % (self.NAME, pad('Width',self.width), pad('Height',self.height))
