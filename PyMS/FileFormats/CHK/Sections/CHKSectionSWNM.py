
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionSWNM(CHKSection):
	NAME = 'SWNM'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.names = [0] * 256
	
	def load_data(self, data): # type: (bytes) -> None
		self.names = list(struct.unpack('<256L', data[:256*4]))
	
	def save_data(self): # type: () -> bytes
		return struct.pack('<256L', *self.names)
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for n,name in enumerate(self.names):
			result += '\t%s\n' % (pad('Switch %d' % n, 'String %d' % name))
		return result
