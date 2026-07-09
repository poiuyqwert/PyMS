
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKTechStats:
	def __init__(self) -> None:
		self.default = True
		self.costMinerals = 0
		self.costGas = 0
		self.buildTime = 0
		self.energyUsed = 0

class CHKSectionTECS(CHKSection):
	NAME = b'TECS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_VANILLA_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 24

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.stats: list[CHKTechStats] = []
		for _ in range(self.TECHS):
			self.stats.append(CHKTechStats())

	def load_data(self, data: bytes) -> None:
		o = 0
		defaults = list(bool(v) for v in struct.unpack(f'<{self.TECHS}B', data[o:o+self.TECHS]))
		o += self.TECHS
		costMinerals = list(int(v) for v in struct.unpack(f'<{self.TECHS}H', data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		costGas = list(int(v) for v in struct.unpack(f'<{self.TECHS}H', data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		buildTimes = list(int(v) for v in struct.unpack(f'<{self.TECHS}H', data[o:o+self.TECHS*2]))
		o += self.TECHS*2
		energyUsed = list(int(v) for v in struct.unpack(f'<{self.TECHS}H', data[o:o+self.TECHS*2]))
		for n,values in enumerate(zip(defaults,costMinerals,costGas,buildTimes,energyUsed)):
			stat = self.stats[n]
			stat.default,stat.costMinerals,stat.costGas,stat.buildTime,stat.energyUsed = values

	def save_data(self) -> bytes:
		defaults: list[bool] = []
		costMinerals: list[int] = []
		costGas: list[int] = []
		buildTimes: list[int] = []
		energyUsed: list[int] = []
		for stat in self.stats:
			defaults.append(stat.default)
			costMinerals.append(stat.costMinerals)
			costGas.append(stat.costGas)
			buildTimes.append(stat.buildTime)
			energyUsed.append(stat.energyUsed)
		result = struct.pack(f'<{self.TECHS}B', *defaults)
		result += struct.pack(f'<{self.TECHS}H', *costMinerals)
		result += struct.pack(f'<{self.TECHS}H', *costGas)
		result += struct.pack(f'<{self.TECHS}H', *buildTimes)
		result += struct.pack(f'<{self.TECHS}H', *energyUsed)
		return result

	def decompile(self) -> str:
		result = f'{self.NAME.decode("ascii")}:\n'
		result += '\t' + pad('#')
		for name in ['Use Defaults','Minerals','Gas','Build Time','Energy Used']:
			result += pad(name)
		result += '\n'
		for n,stat in enumerate(self.stats):
			result += '\t' + pad(f'Tech{n:02d}')
			result += pad(str(stat.default))
			result += pad(str(stat.costMinerals))
			result += pad(str(stat.costGas))
			result += pad(str(stat.buildTime))
			result += f'{stat.energyUsed}\n'
		return result
