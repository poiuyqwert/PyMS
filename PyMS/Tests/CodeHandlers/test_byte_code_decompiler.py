
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
ForkCommand = CodeCommand.CodeCommandDefinition('fork', 'fork', 3, [AddrType, AddrType, AddrType], ends_flow=True)

LANGUAGE = make_language([JumpCommand, NopCommand, ForkCommand], [AddrType])


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
		with self.assertRaises(PyMSError):
			decompile(data)


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
