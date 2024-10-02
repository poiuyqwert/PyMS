
from .CodeBlock import CodeBlock
from .BuilderContext import BuilderContext

from ..PyMSError import PyMSError
from .. import Struct

class ByteCodeBuilder(BuilderContext):
	def __init__(self) -> None:
		self.data = bytearray()
		self.block_offsets: dict[CodeBlock, int] = {}
		self.next_blocks: list[CodeBlock] = []
		self.block_refs: dict[CodeBlock, list[tuple[int, Struct.IntField]]] = {}

	def _get_block_offset(self, block: CodeBlock) -> int | None:
		return self.block_offsets.get(block)

	@property
	def current_offset(self) -> int:
		return len(self.data)

	def _resolve_block_refs(self, block: CodeBlock) -> None:
		if not block in self.block_refs:
			return
		for ref_address,type in self.block_refs.pop(block):
			block_address = self._get_block_offset(block)
			if not block_address:
				raise PyMSError('Internal', 'Block is not compiled')
			# Clamp offset to allow saving to check file size
			# TODO: Is there a better way?
			self.data[ref_address: ref_address + type.size] = type.pack(block_address, clamp=True)

	def _compile_block(self, block: CodeBlock) -> None:
		if block in self.block_offsets:
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

	def add_data(self, data: bytes) -> None:
		self.data += data

	def add_block_ref(self, block: CodeBlock, type: Struct.IntField) -> None:
		if block in self.block_offsets:
			# Clamp offset to allow saving to check file size
			# TODO: Is there a better way?
			self.add_data(type.pack(self.block_offsets[block], clamp=True))
		else:
			if not block in self.block_refs:
				self.block_refs[block] = []
			self.block_refs[block].append((self.current_offset, type))
			if not block in self.next_blocks:
				self.next_blocks.append(block)
			self.add_data(type.pack(0)) # Pack 0 for the offset now, which will be updated later once the block is compiled
