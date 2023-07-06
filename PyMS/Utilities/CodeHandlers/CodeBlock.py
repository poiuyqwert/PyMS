
from __future__ import annotations

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from .SerializeContext import SerializeContext
	from .CodeCommand import CodeCommand

class CodeBlock(object):
	def __init__(self) -> None:
		self.commands: list[CodeCommand] = []
		self.prev_block: CodeBlock | None = None
		self.next_block: CodeBlock | None = None
		self.owners: set[Any] = set()

	def serialize(self, context: SerializeContext, add_label: bool = True) -> str:
		result = ''
		if add_label:
			result = ':' + context.block_label(self)
		next_blocks = [] # type: list[CodeBlock]
		if self.next_block:
			next_blocks.append(self.next_block)
		for cmd in self.commands:
			if len(result):
				result += '\n'
			result += cmd.serialize(context)
			if cmd.definition.separate or cmd.definition.ends_flow:
				result += '\n'
			for param in cmd.params:
				if isinstance(param, CodeBlock) and not context.is_block_serialized(param):
					next_blocks.append(param)
					# context.mark_block_serialized(param)
					# result = param.serialize(context) + '\n\n' + result
		for next_block in next_blocks:
			if context.is_block_serialized(next_block):
				continue
			context.mark_block_serialized(next_block)
			if not result.endswith('\n'):
				result += '\n'
			result += '\n' + next_block.serialize(context)
		return result
