
from .AILanguage import AILanguage

from ....Utilities.CodeHandlers.DecompileContext import DecompileContext

class AIDecompileContext(DecompileContext):
	def __init__(self, data: bytes) -> None:
		from .AISE import AISEContext
		self.aise_context = AISEContext()
		super().__init__(data, AILanguage())
