
from __future__ import annotations

from dataclasses import dataclass
import re

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .DefinitionsHandler import DefinitionsHandler
	from .CodeBlock import CodeBlock

class BlockFormatter(Protocol):
	def serialize(self, block_name: str) -> str:
		...

class ColonBlockFormatter(BlockFormatter):
	def serialize(self, block_name: str) -> str:
		return f':{block_name}'

class HyphenBlockFormatter(BlockFormatter):
	def serialize(self, block_name: str) -> str:
		return f'--{block_name}--'

class CommandFormatter(Protocol):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		...

class FlatCommandFormatter(CommandFormatter):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		result = command_name
		for parameter in parameters:
			# TODO: Check for space in parameter
			result += f' {parameter}'
		return result

class ParensCommandFormatter(CommandFormatter):
	def serialize(self, command_name: str, parameters: list[str]) -> str:
		result = f'{command_name}('
		add_comma = False
		for parameter in parameters:
			if add_comma:
				result += ', '
			add_comma = True
			result += parameter
		result += ')'
		return result

class CommentFormatter(Protocol):
	def serialize(self, comments: list[str]) -> str:
		...

class HashCommentFormatter(CommentFormatter):
	def serialize(self, comments: list[str]) -> str:
		return f'# {", ".join(comments)}'

class SemicolonCommentFormatter(CommentFormatter):
	def serialize(self, comments: list[str]) -> str:
		return f'; {", ".join(comments)}'

@dataclass
class Formatters:
	block: BlockFormatter = ColonBlockFormatter()
	command: CommandFormatter = FlatCommandFormatter()
	comment: CommentFormatter = HashCommentFormatter()

class SerializeContext(object):
	def __init__(self, definitions: DefinitionsHandler | None = None, formatters: Formatters = Formatters()) -> None:
		self.definitions = definitions
		self.formatters = formatters
		self._label_prefix: str = 'label'
		self._label_counts: dict[str, int] = {}
		self._block_labels: dict[CodeBlock, str] = {}
		self._blocks_serialized: set[CodeBlock] = set()
		self._next_blocks: list[CodeBlock] = []

	RE_SANITIZE = re.compile(r'^[^a-zA-Z]|[^a-zA-Z0-9]')
	def set_label_prefix(self, label_prefix: str) -> None:
		self._label_prefix = SerializeContext.RE_SANITIZE.sub('_', label_prefix)

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
		if block in self._next_blocks:
			self._next_blocks.remove(block)

	def set_next_block(self, block: CodeBlock) -> None:
		if self.is_block_serialized(block):
			return
		if block in self._next_blocks:
			return
		self._next_blocks.insert(0, block)
		if block.prev_block:
			self.set_next_block(block.prev_block)

	def add_next_block(self, block: CodeBlock) -> None:
		if self.is_block_serialized(block):
			return
		if block in self._next_blocks:
			return
		if block.prev_block:
			self.add_next_block(block.prev_block)
		self._next_blocks.append(block)

	def get_next_block(self) -> CodeBlock | None:
		if not self._next_blocks:
			return None
		return self._next_blocks.pop(0)
