
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKUnitAvailability:
	def __init__(self):
		self.available = True
		self.default = True

class CHKSectionPUNI(CHKSection):
	NAME = 'PUNI'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.availability = []
		for _ in range(228):
			self.availability.append([])
			for _ in range(12):
				self.availability[-1].append(CHKUnitAvailability())
		self.globalAvailability = [True] * 228
	
	def load_data(self, data):
		offset = 0
		for p in range(12):
			availability = list(struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].available = availability[u]
		self.globalAvailability = list(struct.unpack('<228B', data[offset:offset+228]))
		offset += 228
		for p in range(12):
			defaults = list(struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].default = defaults[u]
	
	def save_data(self):
		result = ''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(228)]
			result += struct.pack('<228B', *availability)
		result += struct.pack('<228B', *self.globalAvailability)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(228)]
			result += struct.pack('<228B', *defaults)
		return result

	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Available','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(228):
				result += '\t' + pad('Unit%03d' % u)
				result += pad(self.availability[u][p].available)
				result += '%s\n' % self.availability[u][p].default
		result += '\t%s\n' % pad('# Global','Available')
		for u in range(228):
			result += '\t%s\n' % pad('Unit%03d' % u, self.globalAvailability[u])
		return result
