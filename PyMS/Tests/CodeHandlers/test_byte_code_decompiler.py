
from ._helpers import make_language

from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.ByteCodeDecompiler import ByteCodeDecompiler
from ...Utilities.CodeHandlers.DecompileContext import DecompileContext
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import unittest


AddrType = CodeType.AddressCodeType('addr', 'addr', Struct.l_u16)
JumpCommand = CodeCommand.CodeCommandDefinition('jump', 'jump', 0, [AddrType], ends_flow=True)
NopCommand = CodeCommand.CodeCommandDefinition('nop', 'nop', 1, [])
BranchCommand = CodeCommand.CodeCommandDefinition('branch', 'branch', 2, [AddrType])
ForkCommand = CodeCommand.CodeCommandDefinition('fork', 'fork', 3, [AddrType, AddrType, AddrType], ends_flow=True)

LANGUAGE = make_language([JumpCommand, NopCommand, BranchCommand, ForkCommand], [AddrType])


def decompile(data: bytes, address: int = 0):
	context = DecompileContext(data, LANGUAGE)
	block = ByteCodeDecompiler().decompile_block(address, context)
	return block, context


class Test_LinearDecompile(unittest.TestCase):
	def test_reads_commands_until_flow_ends(self) -> None:
		# nop, nop, jump->0
		data = b'\x01\x01\x00\x00\x00'
		block, _ = decompile(data)
		self.assertEqual([cmd.definition.name for cmd in block.commands], ['nop', 'nop', 'jump'])

	def test_command_original_locations_recorded(self) -> None:
		data = b'\x01\x01\x00\x00\x00'
		block, _ = decompile(data)
		self.assertEqual([cmd.original_location for cmd in block.commands], [0, 1, 2])

	def test_unknown_command_id_raises(self) -> None:
		data = b'\x7f'
		with self.assertRaises(PyMSError) as cm:
			decompile(data)
		self.assertIn("Invalid command id '127'", str(cm.exception))


class Test_BlockSplitting(unittest.TestCase):
	def test_jump_into_middle_splits_block(self) -> None:
		# nop@0, nop@1, jump@2 -> 1 (middle of the block)
		data = b'\x01\x01\x00\x01\x00'
		block, _ = decompile(data)
		# Original block keeps the first command; the split block holds the rest.
		self.assertEqual([cmd.definition.name for cmd in block.commands], ['nop'])
		split = block.next_block
		assert split is not None
		self.assertEqual([cmd.definition.name for cmd in split.commands], ['nop', 'jump'])

	def test_split_block_back_pointer_is_consistent(self) -> None:
		data = b'\x01\x01\x00\x01\x00'
		block, _ = decompile(data)
		split = block.next_block
		assert split is not None
		self.assertIs(split.prev_block, block)

	def test_cycle_to_in_flight_command_splits_instead_of_duplicating(self) -> None:
		# nop@0, branch@1 -> 1 (a jump cycle back to the command currently being
		# decompiled), nop@4, jump@5 -> 0. The cycle must split the block at the
		# branch, not re-scan the same bytes into duplicate commands.
		data = b'\x01\x02\x01\x00\x01\x00\x00\x00'
		block, context = decompile(data)
		self.assertEqual([cmd.definition.name for cmd in block.commands], ['nop'])
		split = block.next_block
		assert split is not None
		self.assertEqual([cmd.definition.name for cmd in split.commands], ['branch', 'nop', 'jump'])
		# The branch targets the block it now lives in
		self.assertIs(split.commands[0].params[0], split)
		# Every decompiled command is unique (its address maps back to itself)
		total_commands = len(block.commands) + len(split.commands)
		self.assertEqual(total_commands, len(context.cmd_refs))

	def test_cycle_split_records_ref_blocks(self) -> None:
		data = b'\x01\x02\x01\x00\x01\x00\x00\x00'
		block, _ = decompile(data)
		split = block.next_block
		assert split is not None
		# branch -> split itself, jump -> entry block; both must be recorded on
		# the block that ended up holding the commands or decompile strategies
		# will not visit (and label) the referenced blocks
		self.assertEqual(split.ref_blocks, [split, block])
		self.assertEqual(block.ref_blocks, [])

	def test_block_reference_params_recorded_in_ref_blocks(self) -> None:
		# jump@0 -> 3; nop@3, jump@4 -> 3
		data = b'\x00\x03\x00\x01\x00\x03\x00'
		block, _ = decompile(data)
		target = block.commands[0].params[0]
		self.assertEqual(block.ref_blocks, [target])
		self.assertEqual(target.ref_blocks, [target])

	def test_double_split_keeps_doubly_linked_list_consistent(self) -> None:
		# fork@0 targets 7, 9, 8 (three params); a single block built at offset 7
		# (nop, nop, nop, jump) is split twice: first at offset 9, then at offset
		# 8 which is spliced *before* the first split. Every node's next_block
		# and its successor's prev_block must agree.
		#   fork id=3, addr=7, addr=9, addr=8 -> 03 07 00 09 00 08 00
		#   nop@7, nop@8, nop@9            -> 01 01 01
		#   jump@10 -> 7                   -> 00 07 00
		data = b'\x03\x07\x00\x09\x00\x08\x00\x01\x01\x01\x00\x07\x00'
		entry, _ = decompile(data)
		fork = entry.commands[0]
		first_target, second_split, first_split = fork.params
		# Layout after both splits: first_target -> first_split -> second_split
		self.assertIs(first_target.next_block, first_split)
		self.assertIs(first_split.next_block, second_split)
		# The node spliced in must be recorded as the successor's predecessor.
		self.assertIs(second_split.prev_block, first_split)


if __name__ == '__main__':
	unittest.main()
