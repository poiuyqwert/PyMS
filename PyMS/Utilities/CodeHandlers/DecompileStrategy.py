
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

	def add_header(self, header: CodeHeader) -> None:
		if header in self.items:
			return
		if header in self._external_headers:
			self._external_headers.remove(header)
		self.active_header = header
		self.items.append(header)
		for entry_point in header.get_entry_points():
			self.add_block(entry_point)

	def _add_block(self, block: CodeBlock) -> None:
		if block in self.items:
			if self.active_header is not None and (block_headers := self.block_headers.get(block)) and not self.active_header in block_headers:
				block_headers.append(self.active_header)
			return
		for owner in block.owners:
			if not owner in self.items and not owner in self._external_headers:
				self._external_headers.append(owner)
		if block.prev_block:
			self._add_block(block.prev_block)
		block_headers = []
		if self.active_header is not None:
			block_headers.append(self.active_header)
		self.block_headers[block] = block_headers
		self.items.append(block)
		for command in block.commands:
			for param in command.params:
				if isinstance(param, CodeBlock):
					self._next_blocks.append(param)
		if block.next_block:
			self._add_block(block.next_block)

	def add_block(self, block: CodeBlock) -> None:
		self._add_block(block)
		for next_block in self._next_blocks:
			self._add_block(next_block)

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
			if len(block_headers) == 0:
				label = 'unused'
			elif len(block_headers) == 1:
				label = block_headers[0].get_name()
			else:
				label = 'shared'
				block_comments[item] = 'Shared by: ' + ', '.join(sorted(header.get_name() for header in block_headers))
			label = DecompileStrategyBuilder.RE_SANITIZE_LABEL.sub('_', label)
			index = label_counts.get(label, 0)
			label_counts[label] = index + 1
			labels[item] = f'{label}_{index:04}'
		return DecompileStrategy(self.items, labels, self._external_headers, block_comments)
