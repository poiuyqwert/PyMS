
from .CHKSectionPTEC import CHKSectionPTEC

from ..CHKRequirements import CHKRequirements

class CHKSectionPTEx(CHKSectionPTEC):
	NAME = 'PTEx'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_BROODWAR_HYBRID, CHKRequirements.MODE_UMS)

	TECHS = 44
