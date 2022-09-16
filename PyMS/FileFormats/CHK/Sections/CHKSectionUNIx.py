
from .CHKSectionUNIS import CHKSectionUNIS

from ..CHKRequirements import CHKRequirements

class CHKSectionUNIx(CHKSectionUNIS):
	NAME = 'UNIx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	WEAPONS = 130
