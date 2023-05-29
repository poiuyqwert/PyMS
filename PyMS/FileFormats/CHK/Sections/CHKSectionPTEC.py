
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKTechAvailability(object):
	def __init__(self): # type: () -> None
		self.available = 3
		self.researched = 0
		self.default = True

class CHKSectionPTEC(CHKSection):
	NAME = 'PTEC'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.availability = [] # type: list[list[CHKTechAvailability]]
		for _ in range(self.TECHS):
			self.availability.append([])
			for _ in range(12):
				self.availability[-1].append(CHKTechAvailability())
		self.globalAvailability = [] # type: list[int]
		self.globallyResearched = [] # type: list[int]
	
	def load_data(self, data):
		o = 0
		for p in range(12):
			availability = list(int(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			researched = list(int(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].available = availability[u]
				self.availability[u][p].researched = researched[u]
		self.globalAvailability = list(int(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		self.globallyResearched = list(int(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
		o += self.TECHS
		for p in range(12):
			defaults = list(bool(v) for v in struct.unpack('<%dB' % self.TECHS, data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].default = defaults[u]

	def save_data(self): # type: () -> bytes
		result = b''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(self.TECHS)]
			researched = [self.availability[u][p].researched for u in range(self.TECHS)]
			result += struct.pack('<%dB' % self.TECHS, *availability)
			result += struct.pack('<%dB' % self.TECHS, *researched)
		result += struct.pack('<%dB' % self.TECHS, *self.globalAvailability)
		result += struct.pack('<%dB' % self.TECHS, *self.globallyResearched)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(self.TECHS)]
			result += struct.pack('<%dB' % self.TECHS, *defaults)
		return result
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		result += '\t' + pad('#')
		for name in ['Available','Researched','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += '\t# Player %d\n' % (p+1)
			for u in range(self.TECHS):
				result += '\t' + pad('Tech%02d' % u)
				result += pad(self.availability[u][p].available)
				result += pad(self.availability[u][p].researched)
				result += '%s\n' % self.availability[u][p].default
		result += '\t' + pad('# Global')
		for name in ['Available','Researched']:
			result += pad(name)
		result += '\n'
		for u in range(self.TECHS):
			result += '\t' + pad('Tech%02d' % u)
			result += pad(self.globalAvailability[u])
			result += '%s\n' % self.globallyResearched[u]
		return result
