
from .DecompileContext import DecompileContext
from .CodeBlock import CodeBlock

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

class ByteCodeDecompiler:
	def decompile_block(self, address: int, context: DecompileContext) -> CodeBlock:
		if address in context.block_refs:
			return context.block_refs[address]
		elif address in context.cmd_refs:
			block = CodeBlock()
			context.block_refs[address] = block
			prev_block, start_cmd = context.cmd_refs[address]
			index = prev_block.commands.index(start_cmd)
			while index < len(prev_block.commands):
				cmd = prev_block.commands.pop(index)
				assert cmd.original_location is not None
				context.cmd_refs[cmd.original_location] = (block, cmd)
				block.commands.append(cmd)
			block.prev_block = prev_block
			if prev_block.next_block:
				block.next_block = prev_block.next_block
				block.next_block.prev_block = block
			prev_block.next_block = block
			return block
		else:
			scanner = BytesScanner(context.data, address)
			block = CodeBlock()
			active_block = block
			context.block_refs[address] = block
			while not scanner.at_end():
				cmd_address = scanner.address
				cmd_id = scanner.scan(Struct.l_u8)
				cmd_def = context.language.lookup_command(cmd_id, context.language_context)
				if not cmd_def:
					raise PyMSError('Byte Code', f"Invalid command id '{cmd_id}'")
				cmd = cmd_def.decompile(scanner, context)
				cmd.original_location = cmd_address
				# Register the command before decompiling its block params, so a jump
				# cycle back to this address splits the block instead of re-scanning
				# the same bytes into a duplicate command
				active_block.add_command(cmd)
				context.cmd_refs[cmd_address] = (active_block, cmd)
				for n,param_type in enumerate(cmd.definition.param_types):
					if param_type.block_reference:
						new_block = self.decompile_block(cmd.params[n], context)
						cmd.params[n] = new_block
						# A split (possibly deep in the recursion) may have moved this
						# command into a new block, so re-resolve which block holds it
						active_block = context.cmd_refs[cmd_address][0]
						# `add_command` couldn't capture this ref while the param was
						# still a raw address, so record it now
						active_block.ref_blocks.append(new_block)
				if cmd.definition.ends_flow:
					break
				if scanner.address in context.block_refs:
					active_block.next_block = context.block_refs[scanner.address]
					active_block.next_block.prev_block = active_block
					break
			return block
