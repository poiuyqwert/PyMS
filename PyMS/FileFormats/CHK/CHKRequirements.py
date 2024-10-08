
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK

class CHKRequirements(object):
	VER_NONE = 0
	VER_VANILLA = (1 << 0)
	VER_HYBRID = (1 << 1)
	VER_BROODWAR = (1 << 2)
	VER_VANILLA_HYBRID = VER_VANILLA | VER_HYBRID
	VER_BROODWAR_HYBRID = VER_BROODWAR | VER_HYBRID
	VER_ALL = VER_VANILLA | VER_HYBRID | VER_BROODWAR

	MODE_NONE = 0
	MODE_MELEE = (1 << 0)
	MODE_UMS = (1 << 1)
	MODE_ALL = MODE_MELEE | MODE_UMS

	def __init__(self, vers: int = VER_ALL, modes: int = MODE_ALL) -> None:
		from .Sections.CHKSectionVER import CHKSectionVER
		self.vers: list[int] = []
		if vers & CHKRequirements.VER_VANILLA:
			self.vers.append(CHKSectionVER.SC100)
		if vers & CHKRequirements.VER_HYBRID:
			self.vers.append(CHKSectionVER.SC104)
		if vers & CHKRequirements.VER_BROODWAR:
			self.vers.append(CHKSectionVER.BW)

		self.modes = modes

	def is_required(self, chk: CHK, game_mode: int = MODE_ALL) -> bool:
		from .Sections.CHKSectionVER import CHKSectionVER
		verSect = chk.get_section(CHKSectionVER)
		if not verSect:
			return False
		if verSect.version in self.vers and game_mode & self.modes:
			return True
		return False
