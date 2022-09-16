
from .CHKSectionUPGR import CHKSectionUPGR

from ..CHKRequirements import CHKRequirements

class CHKSectionPUPx(CHKSectionUPGR):
	NAME = 'PUPx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 61
