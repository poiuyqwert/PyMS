
from __future__ import annotations

from .CodeBlock import CodeBlock

from .. import Struct

from typing import Protocol

class BuilderContext(Protocol):
	def add_data(self, data: bytes | bytearray) -> int:
		...

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> int:
		...

	def set_data(self, address: int, data: bytes | bytearray, can_expand: bool = False) -> None:
		...

	def get_updater(self) -> BuilderUpdater:
		...

class BuilderUpdater:
	def __init__(self, address: int, builder_context: BuilderContext) -> None:
		self.address = address
		self.builder_context = builder_context

	def update_data(self, data: bytes | bytearray):
		self.builder_context.set_data(self.address, data)
		self.address += len(data)

	def skip(self, bytes: int) -> None:
		self.address += bytes
