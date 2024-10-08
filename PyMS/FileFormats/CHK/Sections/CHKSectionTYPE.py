
from __future__ import annotations

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
	from ..CHK import CHK

class CHKSectionTYPE(CHKSection):
	NAME = "TYPE"
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	STARCRAFT = b"RAWS"
	BROODWAR = b"RAWB"
	@staticmethod
	def TYPE_NAME(t: bytes) -> str:
		names = {
			CHKSectionTYPE.STARCRAFT:'StarCraft',
			CHKSectionTYPE.BROODWAR:'BroodWar'
		}
		return names.get(t,'Unknown')

	def __init__(self, chk: CHK) -> None:
		CHKSection.__init__(self, chk)
		self.type = CHKSectionTYPE.BROODWAR
		from .CHKSectionVER import CHKSectionVER
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect:
			verSect = cast(CHKSectionVER, verSect)
			if not verSect.version == CHKSectionVER.BW:
				self.type = CHKSectionTYPE.STARCRAFT

	def load_data(self, data: bytes) -> None:
		self.type = data[:4]

	def save_data(self) -> bytes:
		return self.type

	def decompile(self) -> str:
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Type',str(self.type)), CHKSectionTYPE.TYPE_NAME(self.type))
