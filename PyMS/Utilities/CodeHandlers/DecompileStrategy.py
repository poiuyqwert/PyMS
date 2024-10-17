
from __future__ import annotations

from .CodeBlock import CodeBlock

from ..PyMSError import PyMSError

import re
from dataclasses import dataclass

from typing import TYPE_CHECKING, Iterable, Mapping
if TYPE_CHECKING:
	from .CodeHeader import CodeHeader

@dataclass
class DecompileStrategy:
	items: Iterable[CodeHeader | CodeBlock]
	labels: Mapping[CodeBlock, str]

	external_headers: Iterable[CodeHeader]
	block_comments: Mapping[CodeBlock, str]

	@staticmethod
	def empty() -> DecompileStrategy:
		return DecompileStrategy([], {}, [], {})

	def block_label(self, block: CodeBlock) -> str:
		if not block in self.labels:
			raise PyMSError('Internal', 'Decompile strategy missing label for block')
		return self.labels[block]

	def block_comment(self, block: CodeBlock) -> str | None:
		return self.block_comments.get(block)

class DecompileStrategyBuilder:
	def __init__(self) -> None:
		self.items: list[CodeHeader | CodeBlock] = []
		self.active_header: CodeHeader | None = None
		self.block_headers: dict[CodeBlock, list[CodeHeader]] = {}
		self._next_blocks: list[CodeBlock] = []
		self._external_headers: list[CodeHeader] = []
		self._block_suffixes: dict[CodeBlock, str] = {}

	def add_header(self, header: CodeHeader) -> None:
		if header in self.items:
			return
		if header in self._external_headers:
			self._external_headers.remove(header)
		self.active_header = header
		self.items.append(header)
		for entry_point, suffix in header.get_entry_points():
			self.add_block(entry_point, suffix)

	def _add_block(self, block: CodeBlock, suffix: str | None = None) -> None:
		if suffix is not None and not block in self._block_suffixes:
			self._block_suffixes[block] = suffix
		if block in self.items:
			if self.active_header is not None and (block_headers := self.block_headers.get(block)) and not self.active_header in block_headers:
				block_headers.append(self.active_header)
			return
		if block.prev_block and not block.prev_block in self.items:
			self._add_block(block.prev_block)
			return
		self.items.append(block)
		for owner in block.owners:
			if not owner in self.items and not owner in self._external_headers:
				self._external_headers.append(owner)
		block_headers = []
		if self.active_header is not None:
			block_headers.append(self.active_header)
		self.block_headers[block] = block_headers
		for ref_block in block.ref_blocks:
			self._next_blocks.append(ref_block)
		if block.next_block:
			self._add_block(block.next_block)

	def add_block(self, block: CodeBlock, suffix: str | None = None) -> None:
		self._add_block(block, suffix)
		while self._next_blocks:
			self._add_block(self._next_blocks.pop(0))

	RE_SANITIZE_LABEL = re.compile(r'^[^a-zA-Z]|[^a-zA-Z0-9]')
	def build(self) -> DecompileStrategy:
		index = 0
		while index < len(self._external_headers):
			self.add_header(self._external_headers[index])
		labels: dict[CodeBlock, str] = {}
		label_counts: dict[str, int] = {}
		block_comments: dict[CodeBlock, str] = {}
		for item in self.items:
			if not isinstance(item, CodeBlock):
				continue
			block_headers = self.block_headers.get(item, [])
			suffix: str | None = None
			if len(block_headers) == 0:
				label = 'unused'
			elif len(block_headers) == 1:
				label = block_headers[0].get_name()
				suffix = self._block_suffixes.get(item)
			else:
				label = 'shared'
				block_comments[item] = 'Shared by: ' + ', '.join(sorted(header.get_name() for header in block_headers))
			label = DecompileStrategyBuilder.RE_SANITIZE_LABEL.sub('_', label)
			if suffix:
				label += f'_{suffix}'
			index = label_counts.get(label, 0)
			label_counts[label] = index + 1
			if not suffix:
				label += f'_{index:04}'
			elif index > 0:
				label += str(index + 1)
			labels[item] = label
		return DecompileStrategy(self.items, labels, self._external_headers, block_comments)
