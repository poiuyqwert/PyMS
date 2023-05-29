
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionUPUS(CHKSection):
	NAME = 'UPUS'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.properties_used = [False] * 64
	
	def load_data(self, data): # type: (bytes) -> None
		self.properties_used = list(struct.unpack('<64B', data[:64]))
	
	def save_data(self): # type: () -> bytes
		return struct.pack('<64B', *self.properties_used)
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for n,u in enumerate(self.properties_used):
			result += '\t%s\n' % pad('Properties%02d' % n, u)
		return result
