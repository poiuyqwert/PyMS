
from ....Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler

class AIByteCodeCompiler(ByteCodeCompiler):
	def __init__(self, expanded: bool = False) -> None:
		from .AISE import AISEContext
		self.aise_context = AISEContext()
		super().__init__()
