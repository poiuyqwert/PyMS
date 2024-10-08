
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....FileFormats.TRG import TRG

from ....Utilities import IO

import io

class CHKSectionTRIG(CHKSection):
	NAME = 'TRIG'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_UMS)
	
	trg: TRG.TRG
	
	def load_data(self, data: bytes) -> None:
		self.trg = TRG.TRG(self.chk.stat_txt, self.chk.aiscript)
		self.trg.load(data)
	
	def save_data(self) -> bytes:
		if self.trg:
			f = io.BytesIO()
			# TODO: Deal with warnings?
			warnings = self.trg.save(f)
			return f.getvalue()
		return b''
	
	def decompile(self) -> str:
		result = '%s:\n' % (self.NAME)
		if self.trg:
			result += IO.output_to_text(lambda f: self.trg.decompile(f))
		return result
