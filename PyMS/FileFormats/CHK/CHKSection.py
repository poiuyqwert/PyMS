
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CHK import CHK
	from .CHKRequirements import CHKRequirements

class CHKSection(object):
	NAME: str
	REQUIREMENTS: CHKRequirements

	def __init__(self, chk): # type: (CHK) -> None
		self.chk = chk

	def load_data(self, data): # type: (bytes) -> None
		raise NotImplementedError(self.__class__.__name__ + '.load_data()')

	def save_data(self): # type: () -> bytes
		raise NotImplementedError(self.__class__.__name__ + '.save_data()')

	def decompile(self): # type: () -> str
		raise NotImplementedError(self.__class__.__name__ + '.decompile()')

	def interpret(self, text): # type: (str) -> None
		raise NotImplementedError(self.__class__.__name__ + '.interpret()')

	def requires_post_processing(self): # type: () -> bool
		return False

	def process_data(self): # type: () -> None
		pass
