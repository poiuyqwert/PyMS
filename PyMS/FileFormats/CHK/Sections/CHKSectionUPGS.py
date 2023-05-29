
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKUpgradeStats(object):
	def __init__(self): # type: () -> None
		self.default = True
		self.costMinerals = 0
		self.costMineralsIncrease = 0
		self.costGas = 0
		self.costGasIncrease = 0
		self.buildTime = 0
		self.buildTimeIncrease = 0

class CHKSectionUPGS(CHKSection):
	NAME = 'UPGS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 46
	PAD = False
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.stats = [] # type: list[CHKUpgradeStats]
		for _ in range(self.UPGRADES):
			self.stats.append(CHKUpgradeStats())
	
	def load_data(self, data): # type: (bytes) -> None
		o = 0
		defaults = list(bool(v) for v in struct.unpack('<%dB' % self.UPGRADES, data[o:o+self.UPGRADES]))
		o += self.UPGRADES+self.PAD
		costMinerals = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costMineralsIncreases = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costGas = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		costGasIncreases = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		buildTimes = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		o += self.UPGRADES*2
		buildTimeIncreases = list(int(v) for v in struct.unpack('<%dH' % self.UPGRADES, data[o:o+self.UPGRADES*2]))
		for n,values in enumerate(zip(defaults,costMinerals,costMineralsIncreases,costGas,costGasIncreases,buildTimes,buildTimeIncreases)):
			stat = self.stats[n]
			stat.default,stat.costMinerals,stat.costMineralsIncrease,stat.costGas,stat.costGasIncrease,stat.buildTime,stat.buildTimeIncrease = values

	def save_data(self): # type: () -> bytes
		defaults = [] # type: list[bool]
		costMinerals = [] # type: list[int]
		costMineralsIncreases = [] # type: list[int]
		costGas = [] # type: list[int]
		costGasIncreases = [] # type: list[int]
		buildTimes = [] # type: list[int]
		buildTimeIncreases = [] # type: list[int]
		for stat in self.stats:
			defaults.append(stat.default)
			costMinerals.append(stat.costMinerals)
			costMineralsIncreases.append(stat.costMineralsIncrease)
			costGas.append(stat.costGas)
			costGasIncreases.append(stat.costGasIncrease)
			buildTimes.append(stat.buildTime)
			buildTimeIncreases.append(stat.buildTimeIncrease)
		result = struct.pack('<%dB' % self.UPGRADES, *defaults)
		if self.PAD:
			result += b'\0'
		result += struct.pack('<%dH' % self.UPGRADES, *costMinerals)
		result += struct.pack('<%dH' % self.UPGRADES, *costMineralsIncreases)
		result += struct.pack('<%dH' % self.UPGRADES, *costGas)
		result += struct.pack('<%dH' % self.UPGRADES, *costGasIncreases)
		result += struct.pack('<%dH' % self.UPGRADES, *buildTimes)
		result += struct.pack('<%dH' % self.UPGRADES, *buildTimeIncreases)
		return result
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Minerals','Minerals Increase','Gas','Gas Increase','Build Time','Build Time Increase']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.stats):
			result += '\t' + pad('Upgrade%02d' % n)
			result += pad(stat.default)
			result += pad(stat.costMinerals)
			result += pad(stat.costMineralsIncrease)
			result += pad(stat.costGas)
			result += pad(stat.costGasIncrease)
			result += pad(stat.buildTime)
			result += '%s\n' % stat.buildTimeIncrease
		return result
