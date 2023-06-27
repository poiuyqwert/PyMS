
from . import SerializeContext
from .CodeCommand import CodeCommand

class CodeBlock(object):
	def __init__(self):
		self.commands = [] # type: list[CodeCommand]
		self.prev_block = None # type: CodeBlock
		self.next_block = None # type: CodeBlock
		self.owners = set()

	def serialize(self, context, add_label=True): # type: (SerializeContext.SerializeContext, bool) -> str
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
			if cmd._separate or cmd._ends_flow:
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
