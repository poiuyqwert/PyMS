
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .CodeHeader import CodeHeader
	from .SerializeContext import SerializeContext
	from .CodeCommand import CodeCommand

class CodeBlock:
	def __init__(self) -> None:
		self.commands: list[CodeCommand] = []
		self.prev_block: CodeBlock | None = None
		self.next_block: CodeBlock | None = None
		self.owners: list[CodeHeader] = []

	def serialize(self, context: SerializeContext) -> None:
		context.write('\n')
		context.write(context.formatters.block.serialize(context.strategy.block_label(self)))
		if (comment := context.strategy.block_comment(self)):
			context.write(context.formatters.comment.serialize([comment]))
		context.write('\n')
		for cmd in self.commands:
			cmd.serialize(context)
			if cmd.definition.separate or cmd.definition.ends_flow:
				context.write('\n')
