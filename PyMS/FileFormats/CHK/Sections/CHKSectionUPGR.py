
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKUpgradeLevels:
	def __init__(self):
		self.maxLevel = 3
		self.startLevel = 0
		self.default = True

class CHKSectionUPGR(CHKSection):
	NAME = 'UPGR'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 46
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.levels = []
		for _ in range(self.UPGRADES):
			self.levels.append([])
			for _ in range(12):
				self.levels[-1].append(CHKUpgradeLevels())
		self.maxLevels = []
		self.startLevels = []
	
	def load_data(self, data):
		o = 0
		for p in range(12):
			maxLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			startLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			for u in range(self.UPGRADES):
				self.levels[u][p].maxLevel = maxLevels[u]
				self.levels[u][p].startLevel = startLevels[u]
		self.maxLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES
		self.startLevels = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES
		for p in range(12):
			defaults = list(struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
			o += self.UPGRADES
			for u in range(self.UPGRADES):
				self.levels[u][p].default = defaults[u]

	def save_data(self):
		result = ''
		for p in range(12):
			maxLevels = [self.levels[u][p].maxLevel for u in range(self.UPGRADES)]
			startLevels = [self.levels[u][p].startLevel for u in range(self.UPGRADES)]
			result += struct.pack('<%dB' % self.UPGRADES, *maxLevels)
			result += struct.pack('<%dB' % self.UPGRADES, *startLevels)
		result += struct.pack('<%dB' % self.UPGRADES, *self.maxLevels)
		result += struct.pack('<%dB' % self.UPGRADES, *self.startLevels)
		for p in range(12):
			defaults = [self.levels[u][p].default for u in range(self.UPGRADES)]
			result += struct.pack('<%dB' % self.UPGRADES, *defaults)
		return result
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Max Levels','Start Level','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(self.UPGRADES):
				result += '\t' + pad('Upgrade%02d' % u)
				result += pad(self.levels[u][p].maxLevel)
				result += pad(self.levels[u][p].startLevel)
				result += '%s\n' % self.levels[u][p].default
		result += '\t' + pad('# Global')
		for name in ['Max Levels','Start Level']:
			result += pad(name)
		result += '\n'
		for u in range(self.UPGRADES):
			result += '\t' + pad('Upgrade%02d' % u)
			result += pad(self.maxLevels[u])
			result += '%s\n' % self.startLevels[u]
		return result
