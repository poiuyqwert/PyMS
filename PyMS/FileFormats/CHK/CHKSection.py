
from __future__ import annotations

from .CHKRequirements import CHKRequirements

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK

class CHKSection(object):
	NAME: str
	REQUIREMENTS: CHKRequirements

	def __init__(self, chk: CHK) -> None:
		self.chk = chk

	def load_data(self, data: bytes) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.load_data()')

	def save_data(self) -> bytes:
		raise NotImplementedError(self.__class__.__name__ + '.save_data()')

	def decompile(self) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.decompile()')

	def interpret(self, text: str) -> None:
		raise NotImplementedError(self.__class__.__name__ + '.interpret()')

	def requires_post_processing(self) -> bool:
		return False

	def process_data(self) -> None:
		pass
