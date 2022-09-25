
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

class CHKSectionTYPE(CHKSection):
	NAME = "TYPE"
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_NONE, CHKRequirements.MODE_NONE)

	STARCRAFT = "RAWS"
	BROODWAR = "RAWB"
	@staticmethod
	def TYPE_NAME(t):
		names = {
			CHKSectionTYPE.STARCRAFT:'StarCraft',
			CHKSectionTYPE.BROODWAR:'BroodWar'
		}
		return names.get(t,'Unknown')

	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.type = CHKSectionTYPE.BROODWAR
		from .CHKSectionVER import CHKSectionVER
		verSect = chk.sections.get(CHKSectionVER.NAME)
		if verSect and not verSect.type == CHKSectionVER.BW:
			self.type = CHKSectionTYPE.STARCRAFT

	def load_data(self, data):
		self.type = data[:4]

	def save_data(self):
		return self.type

	def decompile(self):
		return '%s:\n\t%s # %s\n' % (self.NAME, pad('Type',self.type), CHKSectionTYPE.TYPE_NAME(self.type))
