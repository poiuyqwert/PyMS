
from __future__ import annotations

from .CodeBlock import CodeBlock

from ..PyMSError import PyMSError
from .. import Struct

from typing import Protocol

class ByteCodeBuilderType(Protocol):
	def add_data(self, data: bytes | bytearray) -> int:
		...

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> int:
		...

	def set_data(self, address: int, data: bytes | bytearray, can_expand: bool = False) -> None:
		...

	def get_updater(self) -> BuilderUpdater:
		...

class BuilderUpdater:
	def __init__(self, address: int, builder: ByteCodeBuilderType) -> None:
		self.address = address
		self.builder = builder

	def update_data(self, data: bytes | bytearray):
		self.builder.set_data(self.address, data)
		self.address += len(data)

	def skip(self, bytes: int) -> None:
		self.address += bytes

class ByteCodeCompiler(ByteCodeBuilderType):
	def __init__(self) -> None:
		self.data = bytearray()
		self.block_offsets: dict[CodeBlock, int] = {}
		self.next_blocks: list[CodeBlock] = []
		self.block_refs: dict[CodeBlock, list[tuple[int, Struct.IntField]]] = {}

	@property
	def current_offset(self) -> int:
		return len(self.data)

	def _resolve_block_refs(self, block: CodeBlock) -> None:
		if not block in self.block_refs:
			return
		for ref_address,type in self.block_refs.pop(block):
			block_address = self.block_offsets.get(block)
			if not block_address:
				raise PyMSError('Internal', 'Block is not compiled')
			# Clamp offset to allow saving to check file size
			# TODO: Is there a better way?
			self.set_data(ref_address, type.pack(block_address, clamp=True))

	def _compile_block(self, block: CodeBlock) -> None:
		if block in self.block_offsets:
			return
		if block.prev_block is not None and not block.prev_block in self.block_offsets:
			self._compile_block(block.prev_block)
			return
		offset = self.current_offset
		self.block_offsets[block] = offset
		for cmd in block.commands:
			cmd.compile(self)
		self._resolve_block_refs(block)
		if block.next_block:
			self._compile_block(block.next_block)

	def compile_block(self, block: CodeBlock) -> int:
		self._compile_block(block)
		block_offset = self.block_offsets[block]
		while self.next_blocks:
			block = self.next_blocks.pop(0)
			self._compile_block(block)
		return block_offset

	def add_data(self, data: bytes | bytearray) -> int:
		offset = len(self.data)
		self.data += data
		return offset

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> int:
		if block in self.block_offsets:
			# Clamp offset to allow saving to check file size
			# TODO: Is there a better way?
			return self.add_data(type.pack(self.block_offsets[block], clamp=True))
		else:
			if not block in self.block_refs:
				self.block_refs[block] = []
			self.block_refs[block].append((self.current_offset, type))
			if not block in self.next_blocks:
				self.next_blocks.append(block)
			return self.add_data(type.pack(0)) # Pack 0 for the offset now, which will be updated later once the block is compiled

	def set_data(self, address: int, data: bytes | bytearray, can_expand: bool = False) -> None:
		if address + len(data) > len(self.data) and not can_expand:
			raise PyMSError('Internal', f'Attempting to set data of size {len(data)} at address {address} with only {len(self.data)}B of space')
		self.data[address:address+len(data)] = data

	def get_updater(self) -> BuilderUpdater:
		return BuilderUpdater(self.current_offset, self)
