
from ._helpers import make_parse_context, make_language, ByteType

from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.SourceCodeParser import (
	BlockSourceCodeParser,
	CommandSourceCodeParser,
	DirectiveSourceCodeParser,
	DefineSourceCodeParser,
)
from ...Utilities.CodeHandlers.SourceCodeHandler import SourceCodeHandler
from ...Utilities.CodeHandlers.CodeDirective import CodeDirectiveDefinition
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities.CodeHandlers.CodeBlock import CodeBlock
from ...Utilities.PyMSError import PyMSError

import unittest


IncCommand = CodeCommand.CodeCommandDefinition('inc', 'inc', 0, [ByteType])
EndCommand = CodeCommand.CodeCommandDefinition('end', 'end', 1, [], ends_flow=True)
LANGUAGE = make_language([IncCommand, EndCommand], [ByteType])


class Test_BlockSourceCodeParser(unittest.TestCase):
	def test_colon_block_sets_active_block(self) -> None:
		context = make_parse_context(':start\n', LANGUAGE, with_block=False)
		self.assertTrue(BlockSourceCodeParser().parse(context))
		assert context.active_block is not None
		metadata = context.lookup_block_metadata(context.active_block)
		assert metadata is not None
		self.assertEqual(metadata.name, 'start')

	def test_hyphen_block_form(self) -> None:
		context = make_parse_context('--start--\n', LANGUAGE, with_block=False)
		self.assertTrue(BlockSourceCodeParser().parse(context))
		self.assertIsNotNone(context.active_block)

	def test_links_to_preceding_active_block(self) -> None:
		# Defining a new block while one is active chains them together.
		previous = CodeBlock()
		context = make_parse_context(':second\n', LANGUAGE, with_block=False)
		context.active_block = previous
		BlockSourceCodeParser().parse(context)
		self.assertIs(previous.next_block, context.active_block)
		self.assertIs(context.active_block.prev_block, previous)

	def test_block_keyword_without_name_raises(self) -> None:
		context = make_parse_context(':123\n', LANGUAGE, with_block=False)
		with self.assertRaises(PyMSError):
			BlockSourceCodeParser().parse(context)


class Test_CommandSourceCodeParser(unittest.TestCase):
	def test_parses_command_into_active_block(self) -> None:
		context = make_parse_context('inc 5\n', LANGUAGE)
		self.assertTrue(CommandSourceCodeParser().parse(context))
		assert context.active_block is not None
		self.assertEqual(context.active_block.commands[-1].definition.name, 'inc')

	def test_command_outside_block_raises(self) -> None:
		context = make_parse_context('inc 5\n', LANGUAGE, with_block=False)
		with self.assertRaises(PyMSError):
			CommandSourceCodeParser().parse(context)

	def test_flow_ending_command_clears_active_block(self) -> None:
		context = make_parse_context('end\n', LANGUAGE)
		CommandSourceCodeParser().parse(context)
		self.assertIsNone(context.active_block)

	def test_returns_false_for_non_command(self) -> None:
		context = make_parse_context(':label\n', LANGUAGE)
		self.assertFalse(CommandSourceCodeParser().parse(context))


class Test_DefineSourceCodeParser(unittest.TestCase):
	def test_defines_a_variable(self) -> None:
		definitions = DefinitionsHandler()
		context = make_parse_context('byte foo = 5\n', LANGUAGE, definitions=definitions, with_block=False)
		self.assertTrue(DefineSourceCodeParser().parse(context))
		variable = definitions.get_variable('foo')
		assert variable is not None
		self.assertEqual(variable.value, 5)

	def test_duplicate_variable_raises(self) -> None:
		definitions = DefinitionsHandler()
		definitions.set_variable('foo', 1, ByteType)
		context = make_parse_context('byte foo = 5\n', LANGUAGE, definitions=definitions, with_block=False)
		with self.assertRaises(PyMSError):
			DefineSourceCodeParser().parse(context)

	def test_without_definitions_does_nothing(self) -> None:
		context = make_parse_context('byte foo = 5\n', LANGUAGE, with_block=False)
		self.assertFalse(DefineSourceCodeParser().parse(context))


class Test_DirectiveSourceCodeParser(unittest.TestCase):
	def test_parses_known_directive(self) -> None:
		directive_def = CodeDirectiveDefinition('mark', 'mark', [])
		context = make_parse_context('@mark()\n', LANGUAGE, with_block=False)
		self.assertTrue(DirectiveSourceCodeParser([directive_def]).parse(context))

	def test_unknown_directive_raises(self) -> None:
		context = make_parse_context('@nope()\n', LANGUAGE, with_block=False)
		with self.assertRaises(PyMSError):
			DirectiveSourceCodeParser([]).parse(context)

	def test_register_same_definition_twice_is_ok(self) -> None:
		directive_def = CodeDirectiveDefinition('mark', 'mark', [])
		parser = DirectiveSourceCodeParser()
		parser.register_directive(directive_def)
		parser.register_directive(directive_def)  # no raise
		self.assertIn('mark', parser.directive_defs)

	def test_register_conflicting_definition_raises(self) -> None:
		parser = DirectiveSourceCodeParser([CodeDirectiveDefinition('mark', 'mark', [])])
		with self.assertRaises(PyMSError):
			parser.register_directive(CodeDirectiveDefinition('mark', 'different', []))


class Test_SourceCodeHandler(unittest.TestCase):
	def make_handler(self) -> SourceCodeHandler:
		handler = SourceCodeHandler()
		handler.register_parsers([BlockSourceCodeParser(), CommandSourceCodeParser()])
		return handler

	def test_parses_block_with_commands(self) -> None:
		context = make_parse_context(':start\ninc 5\nend\n', LANGUAGE, with_block=False)
		self.make_handler().parse(context)
		block = context.blocks['start']
		self.assertEqual([cmd.definition.name for cmd in block.commands], ['inc', 'end'])

	def test_unexpected_token_raises(self) -> None:
		context = make_parse_context('%%%\n', LANGUAGE, with_block=False)
		with self.assertRaises(PyMSError):
			self.make_handler().parse(context)

	def test_no_registered_parsers_raises_pyms_error(self) -> None:
		# With no parsers registered, unparseable input reports a parse error
		# rather than referencing an unbound local.
		context = make_parse_context('inc 5\n', LANGUAGE, with_block=False)
		with self.assertRaises(PyMSError):
			SourceCodeHandler().parse(context)


if __name__ == '__main__':
	unittest.main()
