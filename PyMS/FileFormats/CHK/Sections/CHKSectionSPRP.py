
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
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.scenarioName = 0
		self.description = 0
	
	def load_data(self, data): # type: (bytes) -> None
		self.scenarioName,self.description = tuple(int(v) for v in struct.unpack('<HH', data[:4]))
	
	def save_data(self): # type: () -> bytes
		return struct.pack('<HH', self.scenarioName, self.description)
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		result += '\t%s\n' % pad('ScenarioName', 'String %d' % self.scenarioName)
		result += '\t%s\n' % pad('Description', 'String %d' % self.description)
		return result
