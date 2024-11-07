
from .CodeBlock import CodeBlock
from .CodeCommand import CodeCommandDefinition, CodeCommand

from .. import Struct
from ..PyMSError import PyMSError
from ..BytesScanner import BytesScanner

class ByteCodeHandler:
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

	def register_commands(self, cmd_defs: list[CodeCommandDefinition]) -> None:
		for cmd_def in cmd_defs:
			self.register_command(cmd_def)

	def _decompile_block(self, address: int) -> tuple[CodeBlock, CodeBlock | None]:
		if address in self.block_refs:
			block = self.block_refs[address]
			return (block, None)
		elif address in self.cmd_refs:
			block = CodeBlock()
			self.block_refs[address] = block
			prev_block, start_cmd = self.cmd_refs[address]
			index = prev_block.commands.index(start_cmd)
			while index < len(prev_block.commands):
				cmd = prev_block.commands.pop(index)
				assert cmd.original_location is not None
				self.cmd_refs[cmd.original_location] = (block, cmd)
				block.commands.append(cmd)
			block.prev_block = prev_block
			if prev_block.next_block:
				block.next_block = prev_block.next_block
			prev_block.next_block = block
			return (block, prev_block)
		else:
			scanner = BytesScanner(self.data, address)
			block = CodeBlock()
			active_block = block
			self.block_refs[address] = block
			while not scanner.at_end():
				cmd_address = scanner.address
				cmd_id = scanner.scan(Struct.l_u8)
				cmd_def = self.cmd_defs.get(cmd_id)
				if not cmd_def:
					raise PyMSError('Byte Code', "Invalid command id '%d'" % cmd_id)
				cmd = cmd_def.decompile(scanner)
				cmd.original_location = cmd_address
				for n,param_type in enumerate(cmd.definition.param_types):
					if param_type._block_reference:
						new_block, split_block = self._decompile_block(cmd.params[n])
						cmd.params[n] = new_block
						if split_block == active_block:
							active_block = new_block
				active_block.add_command(cmd)
				self.cmd_refs[cmd_address] = (active_block, cmd)
				if cmd.definition.ends_flow:
					break
				if scanner.address in self.block_refs:
					active_block.next_block = self.block_refs[scanner.address]
					active_block.next_block.prev_block = active_block
					break
			return (block, None)

	def decompile_block(self, address: int) -> CodeBlock:
		block, _ = self._decompile_block(address)
		return block
