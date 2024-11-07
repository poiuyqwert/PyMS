
from __future__ import annotations

from .CHKSection import CHKSection

from ...Utilities.utils import pad

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK

class CHKSectionUnknown(CHKSection):
	data: bytes

	def __init__(self, chk: CHK, name: str) -> None:
		CHKSection.__init__(self, chk)
		self.NAME = name

	def load_data(self, data: bytes) -> None:
		self.data = data

	def save_data(self) -> bytes:
		return self.data

	def decompile(self) -> str:
		return '%s: # Unknown\n\t%s\n' % (self.NAME, pad('Data',self.data.hex()))
