
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionSPRP(CHKSection):
	NAME = 'SPRP'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.scenarioName = 0
		self.description = 0

	def load_data(self, data: bytes) -> None:
		self.scenarioName,self.description = tuple(int(v) for v in struct.unpack('<HH', data[:4]))

	def save_data(self) -> bytes:
		return struct.pack('<HH', self.scenarioName, self.description)

	def decompile(self) -> str:
		result = f'{self.NAME}:\n'
		result += f'\t{pad('ScenarioName', f'String {self.scenarioName}')}\n'
		result += f'\t{pad('Description', f'String {self.description}')}\n'
		return result
