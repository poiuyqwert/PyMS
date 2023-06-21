
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionWAV(CHKSection):
	NAME = 'WAV '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)
	
	def __init__(self, chk): # type: (CHK) -> None
		CHKSection.__init__(self, chk)
		self.paths = [0] * 512
	
	def load_data(self, data): # type: (bytes) -> None
		self.paths = list(int(v) for v in struct.unpack('<512L', data[:2048]))
	
	def save_data(self): # type: () -> bytes
		return struct.pack('<512L', *self.paths)
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		for w in range(512):
			result += '\t%s\n' % pad('Wav%03d' % w, 'String %d' % self.paths[w])
		return result
