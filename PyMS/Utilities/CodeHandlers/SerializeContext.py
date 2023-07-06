
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .DefinitionsHandler import DefinitionsHandler
	from .CodeBlock import CodeBlock

class SerializeContext(object):
	def __init__(self, definitions: DefinitionsHandler | None = None) -> None:
		self.definitions = definitions
		self._label_prefix: str = 'label'
		self._label_counts: dict[str, int] = {}
		self._block_labels: dict[CodeBlock, str] = {}
		self._blocks_serialized: set[CodeBlock] = set()

	def set_label_prefix(self, label_prefix: str) -> None:
		self._label_prefix = label_prefix

	def block_label(self, block: CodeBlock) -> str:
		if not block in self._block_labels:
			prefix = self._label_prefix
			if len(block.owners) > 1:
				prefix = 'shared'
			if not prefix in self._label_counts:
				self._label_counts[prefix] = 0
			index = self._label_counts[prefix]
			self._label_counts[prefix] += 1
			self._block_labels[block] = '%s_%04d' % (prefix, index)
		return self._block_labels[block]

	def is_block_serialized(self, block: CodeBlock) -> bool:
		return block in self._blocks_serialized

	def mark_block_serialized(self, block: CodeBlock) -> None:
		self._blocks_serialized.add(block)
