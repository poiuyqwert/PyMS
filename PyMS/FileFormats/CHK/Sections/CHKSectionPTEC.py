
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKTechAvailability:
	def __init__(self) -> None:
		self.available = 3
		self.researched = 0
		self.default = True

class CHKSectionPTEC(CHKSection):
	NAME = 'PTEC'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.availability: list[list[CHKTechAvailability]] = []
		for _ in range(self.TECHS):
			self.availability.append([])
			for _ in range(12):
				self.availability[-1].append(CHKTechAvailability())
		self.globalAvailability: list[int] = []
		self.globallyResearched: list[int] = []

	def load_data(self, data: bytes) -> None:
		o = 0
		for p in range(12):
			availability = list(int(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
			o += self.TECHS
			researched = list(int(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].available = availability[u]
				self.availability[u][p].researched = researched[u]
		self.globalAvailability = list(int(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
		o += self.TECHS
		self.globallyResearched = list(int(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
		o += self.TECHS
		for p in range(12):
			defaults = list(bool(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
			o += self.TECHS
			for u in range(self.TECHS):
				self.availability[u][p].default = defaults[u]

	def save_data(self) -> bytes:
		result = b''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(self.TECHS)]
			researched = [self.availability[u][p].researched for u in range(self.TECHS)]
			result += struct.pack(f'<{self.TECHS}B', *availability)
			result += struct.pack(f'<{self.TECHS}B', *researched)
		result += struct.pack(f'<{self.TECHS}B', *self.globalAvailability)
		result += struct.pack(f'<{self.TECHS}B', *self.globallyResearched)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(self.TECHS)]
			result += struct.pack(f'<{self.TECHS}B', *defaults)
		return result

	def decompile(self) -> str:
		result = f'{self.NAME}:\n'
		result += '\t' + pad('#')
		for name in ['Available','Researched','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += f'\t# Player {p+1}\n'
			for u in range(self.TECHS):
				result += '\t' + pad(f'Tech{u:02d}')
				result += pad(str(self.availability[u][p].available))
				result += pad(str(self.availability[u][p].researched))
				result += f'{self.availability[u][p].default}\n'
		result += '\t' + pad('# Global')
		for name in ['Available','Researched']:
			result += pad(name)
		result += '\n'
		for u in range(self.TECHS):
			result += '\t' + pad(f'Tech{u:02d}')
			result += pad(str(self.globalAvailability[u]))
			result += f'{self.globallyResearched[u]}\n'
		return result
