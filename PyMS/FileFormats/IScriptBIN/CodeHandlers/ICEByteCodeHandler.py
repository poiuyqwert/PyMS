
from . import CodeCommands

from ....Utilities.CodeHandlers.ByteCodeDecompiler import ByteCodeDecompiler

class ICEByteCodeHandler(ByteCodeDecompiler):
	def __init__(self, data: bytes) -> None:
		ByteCodeDecompiler.__init__(self, data)
		self.register_commands(CodeCommands.all_basic_commands)
