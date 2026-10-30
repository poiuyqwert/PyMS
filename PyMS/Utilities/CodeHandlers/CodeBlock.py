
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
		self.ref_blocks: list[CodeBlock] = []
		self.owners: list[CodeHeader] = []

	def add_command(self, command: CodeCommand) -> None:
		self.commands.append(command)
		for param in command.params:
			if isinstance(param, CodeBlock):
				self.ref_blocks.append(param)

	def serialize(self, context: SerializeContext) -> None:
		context.write('\n')
		if context.formatters.indent_bodies:
			context.dedent()
		context.write(context.formatters.block.serialize(context.strategy.block_label(self)))
		if (comment := context.strategy.block_comment(self)):
			context.write(context.formatters.comment.serialize([comment]))
		if context.formatters.indent_bodies:
			context.indent()
		context.write('\n')
		for cmd in self.commands:
			cmd.serialize(context)
			if cmd.definition.separate or cmd.definition.ends_flow:
				context.write('\n')
