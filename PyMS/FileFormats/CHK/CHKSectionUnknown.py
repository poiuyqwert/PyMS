
from __future__ import annotations

from .CHKSection import CHKSection

from ...Utilities.utils import pad

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK

class CHKSectionUnknown(CHKSection):
	data: bytes

	def __init__(self, chk: CHK, name: bytes) -> None:
		CHKSection.__init__(self, chk)
		self.NAME = name

	def load_data(self, data: bytes) -> None:
		self.data = data

	def save_data(self) -> bytes:
		return self.data

	def decompile(self) -> str:
		# TODO: NAME can be invalid ascii
		return f'{self.NAME.decode("ascii")}: # Unknown\n\t{pad("Data",self.data.hex())}\n'
