
from ....FileFormats import TRG

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

class CHKSectionMBRF(CHKSection):
	NAME = 'MBRF'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.trg = None
	
	def load_data(self, data):
		self.trg = TRG.TRG(self.chk.stat_txt, self.chk.aiscript)
		self.trg.load_data(data, True, True)
	
	def save_data(self):
		if self.trg:
			return self.trg.compile_data(True)
		return ''
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		if self.trg:
			result += self.trg.decompile_data()
		return result
