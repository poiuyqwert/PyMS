
from ._helpers import make_parse_context, ByteType

from ...Utilities.CodeHandlers import CodeCommand
from ...Utilities.CodeHandlers.CodeDirective import DirectiveType, CodeDirectiveDefinition
from ...Utilities.PyMSError import PyMSError

import unittest


class IntDirectiveType(DirectiveType[int]):
	def lex(self, parse_context) -> int:
		token = parse_context.lexer.next_token()
		return int(token.raw_value)


IntParam = IntDirectiveType('number', 'a number')
NoArgDirective = CodeDirectiveDefinition('flag', 'a flag', [])
OneArgDirective = CodeDirectiveDefinition('value', 'a value', [IntParam])


def parse_directive(definition, code: str):
	# `CodeDirectiveDefinition.parse` runs after `@name` is consumed.
	context = make_parse_context(code, with_block=False)
	return definition.parse(context)


class Test_FindByName(unittest.TestCase):
	def test_found(self) -> None:
		self.assertIs(CodeDirectiveDefinition.find_by_name('value', [NoArgDirective, OneArgDirective]), OneArgDirective)

	def test_missing(self) -> None:
		self.assertIsNone(CodeDirectiveDefinition.find_by_name('zzz', [NoArgDirective]))


class Test_Parse(unittest.TestCase):
	def test_no_arguments(self) -> None:
		directive = parse_directive(NoArgDirective, '()')
		self.assertEqual(directive.params, [])

	def test_one_argument(self) -> None:
		directive = parse_directive(OneArgDirective, '(7)')
		self.assertEqual(directive.params, [7])

	def test_missing_open_paren_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_directive(OneArgDirective, '7)')

	def test_missing_close_paren_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_directive(OneArgDirective, '(7')

	def test_trailing_token_rejected(self) -> None:
		with self.assertRaises(PyMSError):
			parse_directive(OneArgDirective, '(7) extra')

	def test_parameter_validation_runs_during_parse(self) -> None:
		# A directive parameter's `validate` must run while parsing, the same as
		# command parameters, so out-of-range values are rejected.
		class EvenOnly(DirectiveType[int]):
			def lex(self, parse_context) -> int:
				return int(parse_context.lexer.next_token().raw_value)

			def validate(self, value, parse_context, token=None) -> None:
				if value % 2 != 0:
					raise PyMSError('Parse', 'value must be even')

		even_directive = CodeDirectiveDefinition('even', 'an even value', [EvenOnly('even', 'an even number')])
		self.assertEqual(parse_directive(even_directive, '(4)').params, [4])
		with self.assertRaises(PyMSError):
			parse_directive(even_directive, '(3)')


class Test_FullHelpText(unittest.TestCase):
	def test_placeholder_resolves_to_parameter(self) -> None:
		directive = CodeDirectiveDefinition('value', 'set {0} now', [IntParam])
		help_text = directive.full_help_text()
		self.assertIn('number', help_text)

	def test_placeholder_indexing_matches_commands(self) -> None:
		# Commands and directives must use the same help-text placeholder
		# convention so the same template resolves the first parameter the same
		# way for both.
		command = CodeCommand.CodeCommandDefinition('cmd', 'set {1} now', 0, [ByteType])
		directive = CodeDirectiveDefinition('dir', 'set {1} now', [IntParam])
		command_resolved = '{1}' not in command.full_help_text()
		directive_resolved = '{1}' not in directive.full_help_text()
		self.assertEqual(command_resolved, directive_resolved)


if __name__ == '__main__':
	unittest.main()
