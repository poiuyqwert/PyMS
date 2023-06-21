
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionIVE2(CHKSection):
	NAME = 'IVE2'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	RELEASE = 11
	@staticmethod
	def VER_NAME(v): # type: (int) -> str
		names = {
			CHKSectionIVE2.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVE2.RELEASE
	
	def load_data(self, data): # type: (bytes) -> None
		self.version = int(struct.unpack('<H', data[:2])[0])
	
	def save_data(self): # type: () -> bytes
		return struct.pack('<H', self.version)

	def decompile(self): # type: () -> str
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',str(self.version)), CHKSectionIVE2.VER_NAME(self.version))
