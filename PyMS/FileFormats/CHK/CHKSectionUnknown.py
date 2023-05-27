
from .CHKSection import CHKSection

from ...Utilities.utils import pad

class CHKSectionUnknown(CHKSection):
	def __init__(self, chk, name):
		CHKSection.__init__(self, chk)
		self.NAME = name
		self.data = None

	def load_data(self, data):
		self.data = data

	def save_data(self):
		return self.data

	def decompile(self):
		return '%s: # Unknown\n\t%s\n' % (self.NAME, pad('Data',self.data.encode('hex')))
