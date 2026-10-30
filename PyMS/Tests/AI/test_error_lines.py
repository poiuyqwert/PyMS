from . import utils

from ...FileFormats.AIBIN import AIBIN
from ...FileFormats.AIBIN.CodeHandlers.AIParseContext import AIParseContext
from ...FileFormats.AIBIN.CodeHandlers.DataContext import DataContext
from ...FileFormats.TBL import TBL

from ...Utilities.PyMSError import PyMSError

import unittest
from typing import Any

HEADER = """script TEST {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point S
}
"""

def _compile(code: str, data_context: DataContext | None = None) -> AIParseContext:
	parse_context = utils.parse_context(code, data_context=data_context)
	AIBIN.AIBIN.compile(parse_context)
	return parse_context

def _commands(parse_context: AIParseContext, block_name: str = 'S') -> list[tuple[str, list[Any]]]:
	return [(command.definition.name, command.params) for command in parse_context.blocks[block_name].commands]

def _unit_names(names: list[str]) -> DataContext:
	tbl = TBL()
	tbl.strings = names
	return DataContext(stattxt_tbl=tbl)


class Test_UnquotedParenStrings(unittest.TestCase):
	def assert_print_compiles(self, text: str, next_line: str, next_command: tuple[str, list[Any]]) -> None:
		parse_context = _compile(f':S\nprint({text})\n{next_line}\nstop\n' + HEADER)
		self.assertEqual(_commands(parse_context), [('print', [text]), next_command, ('stop', [])])

	def test_unquoted_string_ends_at_closing_paren(self) -> None:
		# Characters no token type matches must not absorb the closing `)`,
		# so the string ends on its own line and the next command is intact.
		for text in ('Hello!', 'a-b', '100%', 'say "hi', 'é', 'what?', 'a/b+c*d', '$x', 'a[b]', 'a<b>c', 'a\\b', "lone '"):
			with self.subTest(text=text):
				self.assert_print_compiles(text, 'wait(1)', ('wait', [1]))

	def test_unquoted_string_does_not_swallow_following_commas(self) -> None:
		for text in ('Hello!', 'a-b', '100%'):
			with self.subTest(text=text):
				parse_context = _compile(f':S\nprint({text})\nwait(1)\ndebug(S, x)\n' + HEADER)
				commands = _commands(parse_context)
				self.assertEqual(commands[0], ('print', [text]))
				self.assertEqual(commands[1], ('wait', [1]))
				self.assertEqual(commands[2][0], 'debug')
				self.assertEqual(commands[2][1][1], 'x')

	def test_plain_and_quoted_strings_are_unchanged(self) -> None:
		self.assert_print_compiles('plain words', 'wait(1)', ('wait', [1]))
		parse_context = _compile(':S\nprint("quoted; text")\nwait(1)\nstop\n' + HEADER)
		self.assertEqual(_commands(parse_context)[0], ('print', ['quoted; text']))

	def test_unquoted_unit_name_ends_at_closing_paren(self) -> None:
		data_context = _unit_names(['Marine', 'Ghost!', 'Vulture'])
		parse_context = _compile(':S\nwait_train(1, Ghost!)\nwait(1)\nstop\n' + HEADER, data_context)
		self.assertEqual(_commands(parse_context), [('wait_train', [1, 1]), ('wait', [1]), ('stop', [])])

	def test_missing_close_paren_errors_on_its_own_line(self) -> None:
		code = ':S\nprint(Hello\nwait(1)\nstop\n' + HEADER
		with self.assertRaises(PyMSError) as cm:
			_compile(code)
		self.assertIn('expected `)` to end parameters', str(cm.exception))
		self.assertEqual(cm.exception.line, 2)
		self.assertEqual(cm.exception.code, 'print(Hello')

	def test_comment_inside_unquoted_string_errors_on_its_own_line(self) -> None:
		for line in ('print(a;b)', 'print(a # b)'):
			with self.subTest(line=line):
				with self.assertRaises(PyMSError) as cm:
					_compile(f':S\n{line}\ndebug(S, x)\n' + HEADER)
				self.assertIn('expected `)` to end parameters', str(cm.exception))
				self.assertIn('start a comment', str(cm.exception))
				self.assertEqual(cm.exception.line, 2)
				self.assertEqual(cm.exception.code, line)

	def test_missing_close_paren_at_end_of_file(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(HEADER + ':S\nprint(Hello')
		self.assertIn('Unexpected end of file', str(cm.exception))
		self.assertEqual(cm.exception.code, 'print(Hello')


class Test_ErrorLines(unittest.TestCase):
	def assert_error_line(self, body: str, line: int, message: str) -> None:
		code = body + HEADER
		with self.assertRaises(PyMSError) as cm:
			_compile(code)
		self.assertIn(message, str(cm.exception))
		self.assertEqual(cm.exception.line, line)
		self.assertEqual(cm.exception.code, code.split('\n')[line - 1])

	def test_missing_argument_is_reported_on_the_command_line(self) -> None:
		self.assert_error_line(':S\nwait 1\nwait\nstop\n', 3, 'for `word` (expected integer)')
		self.assert_error_line(':S\nwait 1\ntrain 1\nstop\n', 3, 'for `military` (expected integer)')
		self.assert_error_line(':S\nwait 1\nwait(\nstop\n', 3, 'for `word` (expected integer)')

	def test_command_outside_block_is_reported_on_the_command_line(self) -> None:
		self.assert_error_line(':S\nstop\nwait 1\n:T\nstop\n', 3, "'wait' command defined outside of any block")

	def test_duplicate_header_command_is_reported_on_its_line(self) -> None:
		code = ':S\nstop\n' + HEADER.replace('    broodwar_only 0\n', '    broodwar_only 0\n    broodwar_only 0\n')
		with self.assertRaises(PyMSError) as cm:
			_compile(code)
		self.assertIn("Duplicate script header command 'broodwar_only'", str(cm.exception))
		self.assertEqual(cm.exception.line, 7)
		self.assertEqual(cm.exception.code, '    broodwar_only 0')

	def test_mid_line_errors_are_reported_on_their_line(self) -> None:
		self.assert_error_line(':S\nwait 1\nwait abc\nstop\n', 3, 'Invalid value `abc` for `word`')
		self.assert_error_line(':S\nwait 1\nbogus_cmd 5\nstop\n', 3, "Unexpected token 'bogus_cmd'")
		self.assert_error_line(':S\nwait 1\nwait 1 2\nstop\n', 3, 'expected end of line or file')

	def test_duplicate_block_message_uses_displayed_line_number(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(':S\nstop\n:S\nstop\n' + HEADER)
		self.assertIn("A block named 'S' is already defined on line 1", str(cm.exception))
		self.assertEqual(cm.exception.line, 3)

	def test_duplicate_script_message_uses_displayed_line_number(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			_compile(':S\nstop\n' + HEADER + HEADER)
		self.assertIn("A script with id 'TEST' is already defined on line 3", str(cm.exception))
		self.assertEqual(cm.exception.line, 11)
