
from ....Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities import Struct

class AIByteCodeCompiler(ByteCodeCompiler):
	def __init__(self) -> None:
		from .AISE import AISEContext
		self.aise_context = AISEContext()
		super().__init__()

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> int:
		if self.aise_context.expanded and block in self.aise_context.saving_long_jumps and type == Struct.l_u16:
			# Clamp offset to allow saving to check file size
			# TODO: Is there a better way?
			return self.add_data(type.pack(self.aise_context.saving_long_jumps[block], clamp=True))
		return super().add_block_ref(block, type)
