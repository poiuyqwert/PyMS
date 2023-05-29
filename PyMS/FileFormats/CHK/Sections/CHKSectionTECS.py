
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKTechStats(object):
	def __init__(self):
		self.default = True
		self.costMinerals = 0
		self.costGas = 0
		self.buildTime = 0
		self.energyUsed = 0

class CHKSectionTECS(CHKSection):
	NAME = 'TECS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.stats = [] # type: list[CHKTechStats]
		for _ in range(self.TECHS):
			self.stats.append(CHKTechStats())
	
	def load_data(self, data): # type: (bytes) -> None
		o = 0
		defaults = list(bool(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		costMinerals = list(int(v) for v in struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		costGas = list(int(v) for v in struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		buildTimes = list(int(v) for v in struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		energyUsed = list(int(v) for v in struct.unpack('<%dH' % self.TECHS, data[o:o+self.TECHS*2]))
		for n,values in enumerate(zip(defaults,costMinerals,costGas,buildTimes,energyUsed)):
			stat = self.stats[n]
			stat.default,stat.costMinerals,stat.costGas,stat.buildTime,stat.energyUsed = values

	def save_data(self): # type: () -> bytes
		defaults = [] # type: list[bool]
		costMinerals = [] # type: list[int]
		costGas = [] # type: list[int]
		buildTimes = [] # type: list[int]
		energyUsed = [] # type: list[int]
		for stat in self.stats:
			defaults.append(stat.default)
			costMinerals.append(stat.costMinerals)
			costGas.append(stat.costGas)
			buildTimes.append(stat.buildTime)
			energyUsed.append(stat.energyUsed)
		result = struct.pack('<%dB' % self.TECHS, *defaults)
		result += struct.pack('<%dH' % self.TECHS, *costMinerals)
		result += struct.pack('<%dH' % self.TECHS, *costGas)
		result += struct.pack('<%dH' % self.TECHS, *buildTimes)
		result += struct.pack('<%dH' % self.TECHS, *energyUsed)
		return result
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Use Defaults','Minerals','Gas','Build Time','Energy Used']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.stats):
			result += '\t' + pad('Tech%02d' % n)
			result += pad(stat.default)
			result += pad(stat.costMinerals)
			result += pad(stat.costGas)
			result += pad(stat.buildTime)
			result += '%s\n' % stat.energyUsed
		return result
