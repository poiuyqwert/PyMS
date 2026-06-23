
# pylint: disable=protected-access

from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeCompiler
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import unittest


AddrType = CodeType.AddressCodeType('addr', 'addr', Struct.l_u16)
JumpCommand = CodeCommand.CodeCommandDefinition('jump', 'jump', 0, [AddrType], ends_flow=True)
NopCommand = CodeCommand.CodeCommandDefinition('nop', 'nop', 1, [])


def block_with(*commands: CodeCommand.CodeCommand) -> CodeBlock:
	block = CodeBlock()
	for command in commands:
		block.add_command(command)
	return block


class Test_AddData(unittest.TestCase):
	def test_appends_and_returns_offset(self) -> None:
		builder = ByteCodeCompiler()
		self.assertEqual(builder.add_data(b'\x01\x02'), 0)
		self.assertEqual(builder.add_data(b'\x03'), 2)
		self.assertEqual(builder.data, b'\x01\x02\x03')

	def test_current_offset_tracks_length(self) -> None:
		builder = ByteCodeCompiler()
		builder.add_data(b'\xff\xff\xff')
		self.assertEqual(builder.current_offset, 3)


class Test_SetData(unittest.TestCase):
	def test_overwrites_in_place(self) -> None:
		builder = ByteCodeCompiler()
		builder.add_data(b'\x00\x00\x00\x00')
		builder.set_data(1, b'\xaa\xbb')
		self.assertEqual(builder.data, b'\x00\xaa\xbb\x00')

	def test_out_of_range_without_expand_raises(self) -> None:
		builder = ByteCodeCompiler()
		builder.add_data(b'\x00\x00')
		with self.assertRaises(PyMSError) as cm:
			builder.set_data(1, b'\xaa\xbb')
		self.assertIn('Attempting to set data of size', str(cm.exception))


class Test_CompileBlock(unittest.TestCase):
	def test_single_block_of_commands(self) -> None:
		block = block_with(CodeCommand.CodeCommand(NopCommand, []), CodeCommand.CodeCommand(NopCommand, []))
		builder = ByteCodeCompiler()
		offset = builder.compile_block(block)
		self.assertEqual(offset, 0)
		self.assertEqual(builder.data, b'\x01\x01')

	def test_forward_reference_is_backpatched(self) -> None:
		# A jump to a block compiled later has its placeholder offset filled in
		# once the target block is laid down.
		target = block_with(CodeCommand.CodeCommand(NopCommand, []))
		entry = block_with(CodeCommand.CodeCommand(JumpCommand, [target]))
		builder = ByteCodeCompiler()
		builder.compile_block(entry)
		# jump id, target offset (=3), nop of target
		self.assertEqual(builder.data, b'\x00\x03\x00\x01')

	def test_backward_reference_uses_known_offset(self) -> None:
		target = block_with(CodeCommand.CodeCommand(NopCommand, []))
		entry = block_with(CodeCommand.CodeCommand(JumpCommand, [target]))
		target.next_block = entry
		entry.prev_block = target
		builder = ByteCodeCompiler()
		builder.compile_block(target)
		# nop of target at offset 0, then jump referencing offset 0
		self.assertEqual(builder.data, b'\x01\x00\x00\x00')

	def test_long_block_chain_compiles_without_recursion_error(self) -> None:
		# A long linear chain of blocks (realistic for large scripts) must
		# compile without exhausting Python's recursion limit.
		head = block_with(CodeCommand.CodeCommand(NopCommand, []))
		current = head
		for _ in range(3000):
			nxt = block_with(CodeCommand.CodeCommand(NopCommand, []))
			current.next_block = nxt
			current = nxt
		builder = ByteCodeCompiler()
		builder.compile_block(head)
		self.assertEqual(len(builder.data), 3001)

	def test_recompiling_same_block_is_idempotent(self) -> None:
		block = block_with(CodeCommand.CodeCommand(NopCommand, []))
		builder = ByteCodeCompiler()
		builder.compile_block(block)
		size_after_first = len(builder.data)
		builder.compile_block(block)
		self.assertEqual(len(builder.data), size_after_first)


class Test_AddBlockRef(unittest.TestCase):
	def test_known_block_writes_offset_immediately(self) -> None:
		builder = ByteCodeCompiler()
		block = CodeBlock()
		builder.block_offsets[block] = 0x12
		builder.add_block_ref(block, Struct.l_u16)
		self.assertEqual(builder.data, b'\x12\x00')

	def test_unknown_block_writes_placeholder_and_records_ref(self) -> None:
		builder = ByteCodeCompiler()
		block = CodeBlock()
		builder.add_block_ref(block, Struct.l_u16)
		self.assertEqual(builder.data, b'\x00\x00')
		self.assertIn(block, builder.block_refs)
		self.assertIn(block, builder.next_blocks)


class Test_ResolveBlockRefs(unittest.TestCase):
	def test_block_compiled_at_offset_zero_resolves_its_refs(self) -> None:
		# A block whose compiled offset is 0 (the first block written) must
		# still have references to it resolved, not be rejected as uncompiled.
		builder = ByteCodeCompiler()
		block = CodeBlock()
		builder.data = bytearray(b'\xff\xff')
		builder.block_offsets[block] = 0
		builder.block_refs[block] = [(0, Struct.l_u16)]
		builder._resolve_block_refs(block)
		self.assertEqual(builder.data, b'\x00\x00')


if __name__ == '__main__':
	unittest.main()
