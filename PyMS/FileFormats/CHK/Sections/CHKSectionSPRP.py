
from ..CHKSection import CHKSection
from ..CHKRequirements import CHKRequirements

from ....Utilities.utils import pad

import struct

class CHKSectionSPRP(CHKSection):
	NAME = 'SPRP'
	REQUIREMENTS = CHKRequirements(CHKRequirements.VER_ALL, CHKRequirements.MODE_ALL)
	
	def __init__(self, chk):
		CHKSection.__init__(self, chk)
		self.scenarioName = 0
		self.description = 0
	
	def load_data(self, data):
		self.scenarioName,self.description = struct.unpack('<HH', data[:4])
	
	def save_data(self):
		return struct.pack('<HH', self.scenarioName, self.description)
	
	def decompile(self):
		result = '%s:\n' % (self.NAME)
		result += '\t%s\n' % pad('ScenarioName', 'String %d' % self.scenarioName)
		result += '\t%s\n' % pad('Description', 'String %d' % self.description)
		return result
