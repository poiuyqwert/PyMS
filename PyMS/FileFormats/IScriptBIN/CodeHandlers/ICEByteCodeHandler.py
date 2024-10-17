
from . import CodeCommands

from ....Utilities.CodeHandlers.ByteCodeHandler import ByteCodeHandler

class ICEByteCodeHandler(ByteCodeHandler):
	def __init__(self, data: bytes) -> None:
		ByteCodeHandler.__init__(self, data)
		self.register_commands(CodeCommands.all_basic_commands)
