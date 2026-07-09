
from ._helpers import HelperLexer

from ...Utilities.CodeHandlers.Lexer import Lexer, Stop
from ...Utilities.CodeHandlers import Tokens

import unittest


class Test_NextToken(unittest.TestCase):
	def test_consumes_and_advances_offset(self) -> None:
		lexer = HelperLexer('foo bar')
		first = lexer.next_token()
		self.assertIsInstance(first, Tokens.IdentifierToken)
		self.assertEqual(first.raw_value, 'foo')
		second = lexer.next_token()
		self.assertEqual(second.raw_value, 'bar')

	def test_returns_eof_at_end(self) -> None:
		lexer = HelperLexer('foo')
		lexer.next_token()
		self.assertIsInstance(lexer.next_token(), Tokens.EOFToken)

	def test_empty_input_is_eof(self) -> None:
		self.assertIsInstance(HelperLexer('').next_token(), Tokens.EOFToken)

	def test_skip_tokens_are_skipped(self) -> None:
		# Whitespace and comments are registered as skip tokens.
		lexer = HelperLexer('   # comment\nfoo')
		token = lexer.next_token()
		self.assertIsInstance(token, Tokens.NewlineToken)
		self.assertEqual(lexer.next_token().raw_value, 'foo')

	def test_unmatched_character_falls_back_to_unknown(self) -> None:
		# A lexer with no registered token types still yields an UnknownToken
		# rather than raising.
		lexer = Lexer('$$$')
		token = lexer.next_token()
		self.assertIsInstance(token, Tokens.UnknownToken)


class Test_Peek(unittest.TestCase):
	def test_peek_returns_same_token_as_next_read(self) -> None:
		lexer = HelperLexer('foo bar')
		peeked = lexer.next_token(peek=True)
		read = lexer.next_token()
		self.assertEqual(peeked.raw_value, read.raw_value)
		self.assertEqual(peeked.raw_value, 'foo')

	def test_repeated_peek_is_stable(self) -> None:
		lexer = HelperLexer('foo')
		self.assertEqual(lexer.next_token(peek=True).raw_value, 'foo')
		self.assertEqual(lexer.next_token(peek=True).raw_value, 'foo')

	def test_peeking_does_not_change_lexer_position(self) -> None:
		# Peeking should be side-effect free: the offset must be unchanged so a
		# caller can peek without first capturing a rollback.
		lexer = HelperLexer('   foo')
		before = lexer.state.offset
		lexer.next_token(peek=True)
		self.assertEqual(lexer.state.offset, before)


class Test_GetToken(unittest.TestCase):
	def test_returns_token_when_type_matches(self) -> None:
		lexer = HelperLexer('foo')
		token = lexer.get_token(Tokens.IdentifierToken)
		assert token is not None
		self.assertEqual(token.raw_value, 'foo')

	def test_returns_none_when_type_does_not_match(self) -> None:
		lexer = HelperLexer('123')
		self.assertIsNone(lexer.get_token(Tokens.IdentifierToken))

	def test_does_not_consume_on_mismatch(self) -> None:
		lexer = HelperLexer('123')
		lexer.get_token(Tokens.IdentifierToken)
		# The integer is still available to read afterwards.
		self.assertEqual(lexer.next_token().raw_value, '123')


class Test_CheckToken(unittest.TestCase):
	def test_returns_matching_token(self) -> None:
		lexer = HelperLexer('foo')
		token = lexer.check_token(Tokens.IdentifierToken)
		self.assertEqual(token.raw_value, 'foo')

	def test_falls_back_to_next_token_on_mismatch(self) -> None:
		# When the requested type does not match, the actual next token is
		# consumed and returned instead.
		lexer = HelperLexer('123')
		token = lexer.check_token(Tokens.IdentifierToken)
		self.assertIsInstance(token, Tokens.IntegerToken)


class Test_Skip(unittest.TestCase):
	def test_skips_over_given_types(self) -> None:
		lexer = HelperLexer('\n\n\nfoo')
		token = lexer.skip(Tokens.NewlineToken)
		self.assertEqual(token.raw_value, 'foo')

	def test_skip_with_peek_leaves_token_available(self) -> None:
		lexer = HelperLexer('\nfoo')
		token = lexer.skip(Tokens.NewlineToken, peek=True)
		self.assertEqual(token.raw_value, 'foo')
		# Peeking variant should leave `foo` for the next real read.
		self.assertEqual(lexer.next_token().raw_value, 'foo')


class Test_ReadOpenString(unittest.TestCase):
	def test_reads_until_excluded_token(self) -> None:
		lexer = HelperLexer('hello world)')
		token = lexer.read_open_string(lambda t: Stop.exclude if t.raw_value == ')' else Stop.proceed)
		self.assertEqual(token.raw_value, 'hello world')
		# The terminator is left unconsumed.
		self.assertEqual(lexer.next_token().raw_value, ')')

	def test_reads_until_eof(self) -> None:
		lexer = HelperLexer('one two three')
		token = lexer.read_open_string(lambda t: Stop.proceed)
		self.assertEqual(token.raw_value, 'one two three')

	def test_include_consumes_terminator(self) -> None:
		lexer = HelperLexer('hello;')
		token = lexer.read_open_string(lambda t: Stop.include if t.raw_value == ';' else Stop.proceed)
		self.assertEqual(token.raw_value, 'hello;')


class Test_Rollback(unittest.TestCase):
	def test_rollback_restores_position(self) -> None:
		lexer = HelperLexer('foo bar')
		state = lexer.get_rollback()
		lexer.next_token()
		lexer.next_token()
		lexer.rollback(state)
		self.assertEqual(lexer.next_token().raw_value, 'foo')

	def test_rollback_state_is_independent_copy(self) -> None:
		lexer = HelperLexer('foo bar')
		state = lexer.get_rollback()
		lexer.next_token()
		# Mutating the lexer must not retroactively change the saved state.
		self.assertEqual(state.offset, 0)


class Test_GetRaw(unittest.TestCase):
	def test_returns_source_between_states(self) -> None:
		lexer = HelperLexer('foo bar baz')
		start = lexer.get_rollback()
		lexer.next_token()
		lexer.next_token()
		self.assertEqual(lexer.get_raw(from_state=start), 'foo bar')


class Test_LineTracking(unittest.TestCase):
	def test_newline_advances_line_counter(self) -> None:
		lexer = HelperLexer('a\nb\nc')
		self.assertEqual(lexer.state.line, 0)
		lexer.next_token()  # a
		lexer.next_token()  # newline
		self.assertEqual(lexer.state.line, 1)
		lexer.next_token()  # b
		lexer.next_token()  # newline
		self.assertEqual(lexer.state.line, 2)


class Test_GetLineOfCode(unittest.TestCase):
	def test_splits_on_lf(self) -> None:
		lexer = Lexer('first\nsecond\nthird')
		self.assertEqual(lexer.get_line_of_code(0), 'first')
		self.assertEqual(lexer.get_line_of_code(1), 'second')
		self.assertEqual(lexer.get_line_of_code(2), 'third')

	def test_splits_on_crlf(self) -> None:
		lexer = Lexer('first\r\nsecond')
		self.assertEqual(lexer.get_line_of_code(0), 'first')
		self.assertEqual(lexer.get_line_of_code(1), 'second')

	def test_splits_on_lone_cr(self) -> None:
		lexer = Lexer('first\rsecond')
		self.assertEqual(lexer.get_line_of_code(0), 'first')
		self.assertEqual(lexer.get_line_of_code(1), 'second')

	def test_out_of_range_returns_none(self) -> None:
		lexer = Lexer('only')
		self.assertIsNone(lexer.get_line_of_code(5))
		self.assertIsNone(lexer.get_line_of_code(-1))

	def test_carriage_return_is_a_line_break_before_any_character(self) -> None:
		# A lone CR ends the line regardless of what follows it (here an `=`).
		lexer = Lexer('first\r=\nsecond')
		self.assertEqual(lexer.get_line_of_code(0), 'first')


class Test_TokenPriority(unittest.TestCase):
	def test_identifier_with_boolean_prefix_is_one_identifier(self) -> None:
		# A name like `truebox` is a single identifier, not the boolean `true`
		# followed by a stray `box`.
		lexer = HelperLexer('truebox')
		token = lexer.next_token()
		self.assertIsInstance(token, Tokens.IdentifierToken)
		self.assertEqual(token.raw_value, 'truebox')


class Test_IsAtEnd(unittest.TestCase):
	def test_false_at_start_with_content(self) -> None:
		self.assertFalse(HelperLexer('foo').is_at_end())

	def test_true_after_consuming_all(self) -> None:
		lexer = HelperLexer('foo')
		lexer.next_token()
		self.assertTrue(lexer.is_at_end())

	def test_empty_is_at_end(self) -> None:
		self.assertTrue(HelperLexer('').is_at_end())


if __name__ == '__main__':
	unittest.main()
