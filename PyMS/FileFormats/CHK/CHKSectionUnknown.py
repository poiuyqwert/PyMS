
from .CHKSection import CHKSection

from ...Utilities.utils import pad

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK

class CHKSectionUnknown(CHKSection):
	data: bytes

	def __init__(self, chk, name): # type: (CHK, str) -> None
		CHKSection.__init__(self, chk)
		self.NAME = name

	def load_data(self, data): # type: (bytes) -> None
		self.data = data

	def save_data(self): # type: () -> bytes
		return self.data

	def decompile(self): # type: () -> str
		return '%s: # Unknown\n\t%s\n' % (self.NAME, pad('Data',self.data.hex()))
