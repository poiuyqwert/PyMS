
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionDIM(CHKSection):
	NAME = 'DIM '
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)

	TINY = 64
	SMALL = 96
	MEDIUM = 128
	LARGE = 192
	HUGE = 256
	
	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.width = CHKSectionDIM.MEDIUM
		self.height = CHKSectionDIM.MEDIUM
	
	def load_data(self, data: bytes) -> None:
		self.width,self.height = tuple(int(d) for d in struct.unpack('<2H', data[:4]))
	
	def save_data(self) -> bytes:
		return struct.pack('<2H', self.width, self.height)
	
	def decompile(self) -> str:
		return '%s:\n\t%s\n\t%s\n' % (self.NAME, pad('Width',str(self.width)), pad('Height',str(self.height)))
