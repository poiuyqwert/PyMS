
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionWAV(CHKSection):
	NAME = 'WAV '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.paths = [0] * 512
	
	def load_data(self, data):
		self.paths = list(struct.unpack('<512L', data[:2048]))
	
	def save_data(self):
		return struct.pack('<512L', *self.paths)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		for w in range(512):
			result += '\t%s\n' % pad('Wav%03d' % w, 'String %d' % self.paths[w])
		return result
