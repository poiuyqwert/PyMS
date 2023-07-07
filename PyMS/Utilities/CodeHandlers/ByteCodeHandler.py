
from .CodeBlock import CodeBlock
from .CodeCommand import CodeCommandDefinition, CodeCommand

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

from typing import Any

class ByteCodeHandler(object):
	def __init__(self, data: bytes) -> None:
		self.data = data
		self.cmd_defs: dict[int, CodeCommandDefinition] = {}
		self.block_refs: dict[int, CodeBlock] = {}
		self.cmd_refs: dict[int, tuple[CodeBlock, CodeCommand]] = {}

	def register_command(self, cmd_def: CodeCommandDefinition) -> None:
		if cmd_def.byte_code_id in self.cmd_defs:
			raise PyMSError('Internal', "Command with id '%d' ('%s') already exists" % (cmd_def.byte_code_id, self.cmd_defs[cmd_def.byte_code_id].name))
		if cmd_def.byte_code_id is None:
			raise PyMSError('Internal', f"Command '{cmd_def.name}' does not support byte code")
		self.cmd_defs[cmd_def.byte_code_id] = cmd_def

	def decompile_block(self, address: int, owner: Any | None = None) -> CodeBlock:
		if address in self.block_refs:
			block = self.block_refs[address]
			if owner:
				block.owners.add(owner)
				if len(block.owners) > 1:
					print(block)
			return block
		elif address in self.cmd_refs:
			block = CodeBlock()
			self.block_refs[address] = block
			if owner:
				block.owners.add(owner)
				if len(block.owners) > 1:
					print(block)
			prev_block, start_cmd = self.cmd_refs[address]
			index = prev_block.commands.index(start_cmd)
			while index < len(prev_block.commands):
				cmd = prev_block.commands.pop(index)
				assert cmd.original_address is not None
				self.cmd_refs[cmd.original_address] = (block, cmd)
				block.commands.append(cmd)
			block.prev_block = prev_block
			prev_block.next_block = block
			return block
		else:
			scanner = BytesScanner(self.data, address)
			block = CodeBlock()
			self.block_refs[address] = block
			if owner:
				block.owners.add(owner)
				if len(block.owners) > 1:
					print(block)
			while not scanner.at_end():
				cmd_address = scanner.address
				cmd_id = scanner.scan(Struct.l_u8)
				cmd_def = self.cmd_defs.get(cmd_id)
				if not cmd_def:
					# print('%d %d' % (cmd_address, cmd_id))
					raise PyMSError('Byte Code', "Invalid command id '%d'" % cmd_id)
				# print('%d %d (%s)' % (cmd_address, cmd_id, cmd_def._name))
				cmd = cmd_def.decompile(scanner)
				cmd.original_address = cmd_address
				block.commands.append(cmd)
				self.cmd_refs[cmd_address] = (block, cmd)
				for n,param_type in enumerate(cmd.definition.param_types):
					if param_type._block_reference:
						cmd.params[n] = self.decompile_block(cmd.params[n])
				if cmd.definition.ends_flow:
					break
				if scanner.address in self.block_refs:
					block.next_block = self.block_refs[scanner.address]
					block.next_block.prev_block = block
					break
			return block
