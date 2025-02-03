
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKUnitAvailability:
	def __init__(self) -> None:
		self.available = True
		self.default = True

class CHKSectionPUNI(CHKSection):
	NAME = 'PUNI'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.availability: list[list[CHKUnitAvailability]] = []
		for _ in range(228):
			self.availability.append([])
			for _ in range(12):
				self.availability[-1].append(CHKUnitAvailability())
		self.globalAvailability = [True] * 228

	def load_data(self, data: bytes) -> None:
		offset = 0
		for p in range(12):
			availability = list(bool(v) for v in struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].available = availability[u]
		self.globalAvailability = list(bool(v) for v in struct.unpack('<228B', data[offset:offset+228]))
		offset += 228
		for p in range(12):
			defaults = list(bool(v) for v in struct.unpack('<228B', data[offset:offset+228]))
			offset += 228
			for u in range(228):
				self.availability[u][p].default = defaults[u]

	def save_data(self) -> bytes:
		result = b''
		for p in range(12):
			availability = [self.availability[u][p].available for u in range(228)]
			result += struct.pack('<228B', *availability)
		result += struct.pack('<228B', *self.globalAvailability)
		for p in range(12):
			defaults = [self.availability[u][p].default for u in range(228)]
			result += struct.pack('<228B', *defaults)
		return result

	def decompile(self) -> str:
		result = f'{self.NAME}:\n'
		result += '\t' + pad('#')
		for name in ['Available','Use Defaults']:
			result += pad(name)
		result += '\n'
		for p in range(12):
			result += f'\t# Player {p+1}\n'
			for u in range(228):
				result += '\t' + pad(f'Unit{u:03d}')
				result += pad(str(self.availability[u][p].available))
				result += f'{self.availability[u][p].default}\n'
		result += f'\t{pad('# Global','Available')}\n'
		for u in range(228):
			result += f'\t{pad(f'Unit{u:03d}', str(self.globalAvailability[u]))}\n'
		return result
