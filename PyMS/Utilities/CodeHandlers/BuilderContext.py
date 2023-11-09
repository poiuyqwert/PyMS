
from .CodeBlock import CodeBlock

from .. import Struct

from typing import Protocol

class BuilderContext(Protocol):
	def add_data(self, data: bytes) -> None:
		...

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> None:
		...
