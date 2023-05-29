
from ....FileFormats import TRG

from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

class CHKSectionMBRF(CHKSection):
	NAME = 'MBRF'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	trg: TRG.TRG
	
	def load_data(self, data): # type: (bytes) -> None
		self.trg = TRG.TRG(self.chk.stat_txt, self.chk.aiscript)
		self.trg.load_data(data, True, True)
	
	def save_data(self): # type: () -> bytes
		if self.trg:
			return self.trg.compile_data(True)
		return b''
	
	def decompile(self): # type: () -> str
		result = '%s:\n' % (self.NAME)
		if self.trg:
			result += self.trg.decompile_data()
		return result
