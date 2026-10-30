
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.DecompileStrategy import DecompileStrategy
from ...Utilities import Struct

import unittest, io


AddrType = CodeType.AddressCodeType('addr', 'addr', Struct.l_u16)
NopCommand = CodeCommand.CodeCommandDefinition('nop', 'nop', 1, [])
JumpCommand = CodeCommand.CodeCommandDefinition('jump', 'jump', 0, [AddrType], ends_flow=True)


class Test_AddCommand(unittest.TestCase):
	def test_appends_command(self) -> None:
		block = CodeBlock()
		command = CodeCommand.CodeCommand(NopCommand, [])
		block.add_command(command)
		self.assertEqual(block.commands, [command])

	def test_records_block_params_as_references(self) -> None:
		block = CodeBlock()
		target = CodeBlock()
		block.add_command(CodeCommand.CodeCommand(JumpCommand, [target]))
		self.assertIn(target, block.ref_blocks)

	def test_non_block_params_are_not_references(self) -> None:
		block = CodeBlock()
		block.add_command(CodeCommand.CodeCommand(NopCommand, []))
		self.assertEqual(block.ref_blocks, [])


class Test_Serialize(unittest.TestCase):
	def test_writes_label_then_commands(self) -> None:
		block = CodeBlock()
		block.add_command(CodeCommand.CodeCommand(NopCommand, []))
		output = io.StringIO()
		context = SerializeContext(output)
		context.strategy = DecompileStrategy([block], {block: 'entry'}, [], {})
		block.serialize(context)
		self.assertEqual(output.getvalue(), '\n:entry\nnop\n')

	def test_includes_block_comment_when_present(self) -> None:
		block = CodeBlock()
		block.add_command(CodeCommand.CodeCommand(NopCommand, []))
		output = io.StringIO()
		context = SerializeContext(output)
		context.strategy = DecompileStrategy([block], {block: 'entry'}, [], {block: 'shared note'})
		block.serialize(context)
		self.assertIn('shared note', output.getvalue())


if __name__ == '__main__':
	unittest.main()
