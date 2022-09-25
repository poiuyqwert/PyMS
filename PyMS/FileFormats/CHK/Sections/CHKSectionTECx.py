
from .CHKSectionTECS import CHKSectionTECS

from ..CHKRequirements import CHKRequirements

class CHKSectionTECx(CHKSectionTECS):
	NAME = 'TECx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 44
