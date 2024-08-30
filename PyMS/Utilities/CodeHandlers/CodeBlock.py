
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
		self.references: list[CodeBlock] = []

	def serialize(self, context: SerializeContext, add_label: bool = True) -> str:
		context.mark_block_serialized(self)
		result = ''
		if add_label:
			result = context.formatters.block.serialize(context.block_label(self))
		for cmd in self.commands:
			if len(result):
				result += '\n'
			result += cmd.serialize(context)
			if cmd.definition.separate or cmd.definition.ends_flow:
				result += '\n'
		if self.next_block:
			context.set_next_block(self.next_block)
		return result

	def decompile(self, context: SerializeContext) -> str:
		result = self.serialize(context)
		while (next_block := context.get_next_block()):
			if not result.endswith('\n'):
				result += '\n'
			result += '\n' + next_block.serialize(context)
		return result
