
from .CHKSectionUPGS import CHKSectionUPGS

from ..CHKRequirements import CHKRequirements

class CHKSectionUPGx(CHKSectionUPGS):
	NAME = 'UPGx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	UPGRADES = 61
	PAD = True
