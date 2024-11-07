
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionIVER(CHKSection):
	NAME = 'IVER'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	BETA = 9
	RELEASE = 10
	@staticmethod
	def VER_NAME(v: int) -> str:
		names = {
			CHKSectionIVER.BETA:'Beta',
			CHKSectionIVER.RELEASE:'Release'
		}
		return names.get(v,'Unknown')

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.version = CHKSectionIVER.RELEASE
		from .CHKSectionVER import CHKSectionVER
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect and cast(CHKSectionVER, verSect).version == CHKSectionVER.BETA:
			self.version = CHKSectionIVER.BETA
	
	def load_data(self, data: bytes) -> None:
		self.version = int(struct.unpack('<H', data[:2])[0])
	
	def save_data(self) -> bytes:
		return struct.pack('<H', self.version)

	def decompile(self) -> str:
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Version',str(self.version)), CHKSectionIVER.VER_NAME(self.version))
