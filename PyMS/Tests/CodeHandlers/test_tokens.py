
from ...Utilities.CodeHandlers import Tokens

import unittest


class Test_RegexTokenMatching(unittest.TestCase):
	def test_match_returns_instance_with_matched_text(self) -> None:
		token = Tokens.IntegerToken.match('123abc', 0)
		self.assertIsInstance(token, Tokens.IntegerToken)
		assert token is not None
		self.assertEqual(token.raw_value, '123')

	def test_match_is_anchored_at_offset(self) -> None:
		# A regex token must match at exactly `offset`, not search ahead.
		self.assertIsNone(Tokens.IntegerToken.match('abc123', 0))

	def test_match_can_start_partway_through_string(self) -> None:
		token = Tokens.IntegerToken.match('abc123', 3)
		assert token is not None
		self.assertEqual(token.raw_value, '123')

	def test_match_failure_returns_none(self) -> None:
		self.assertIsNone(Tokens.IntegerToken.match('hello', 0))


class Test_IdentifierToken(unittest.TestCase):
	def test_multi_character_identifier(self) -> None:
		token = Tokens.IdentifierToken.match('hello', 0)
		assert token is not None
		self.assertEqual(token.raw_value, 'hello')

	def test_identifier_with_digits_and_underscore(self) -> None:
		token = Tokens.IdentifierToken.match('_foo9Bar', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '_foo9Bar')

	def test_identifier_cannot_start_with_digit(self) -> None:
		self.assertIsNone(Tokens.IdentifierToken.match('9abc', 0))

	def test_identifier_stops_at_non_word_character(self) -> None:
		token = Tokens.IdentifierToken.match('foo bar', 0)
		assert token is not None
		self.assertEqual(token.raw_value, 'foo')

	def test_single_character_name_is_an_identifier(self) -> None:
		# A name of a single letter is a valid identifier (variables, commands,
		# enum cases can be one character long).
		token = Tokens.IdentifierToken.match('x', 0)
		assert token is not None
		self.assertEqual(token.raw_value, 'x')


class Test_IntegerToken(unittest.TestCase):
	def test_positive(self) -> None:
		token = Tokens.IntegerToken.match('42', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '42')

	def test_negative(self) -> None:
		token = Tokens.IntegerToken.match('-42', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '-42')

	def test_does_not_consume_decimal_point(self) -> None:
		token = Tokens.IntegerToken.match('3.14', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '3')


class Test_HexToken(unittest.TestCase):
	def test_lowercase(self) -> None:
		token = Tokens.HexToken.match('0xabc', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '0xabc')

	def test_uppercase_digits(self) -> None:
		token = Tokens.HexToken.match('0xFF', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '0xFF')

	def test_negative_hex(self) -> None:
		token = Tokens.HexToken.match('-0x10', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '-0x10')

	def test_requires_0x_prefix(self) -> None:
		self.assertIsNone(Tokens.HexToken.match('FF', 0))


class Test_FloatToken(unittest.TestCase):
	def test_basic(self) -> None:
		token = Tokens.FloatToken.match('3.14', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '3.14')

	def test_negative(self) -> None:
		token = Tokens.FloatToken.match('-0.5', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '-0.5')

	def test_requires_fraction_digits(self) -> None:
		# An integer with a trailing dot is not a float per the pattern.
		self.assertIsNone(Tokens.FloatToken.match('3.', 0))

	def test_requires_a_dot(self) -> None:
		self.assertIsNone(Tokens.FloatToken.match('3', 0))


class Test_StringToken(unittest.TestCase):
	def test_double_quoted(self) -> None:
		token = Tokens.StringToken.match('"hello"', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '"hello"')

	def test_single_quoted(self) -> None:
		token = Tokens.StringToken.match("'hello'", 0)
		assert token is not None
		self.assertEqual(token.raw_value, "'hello'")

	def test_escaped_quote_inside(self) -> None:
		token = Tokens.StringToken.match(r'"a\"b"', 0)
		assert token is not None
		self.assertEqual(token.raw_value, r'"a\"b"')

	def test_stops_at_closing_quote(self) -> None:
		token = Tokens.StringToken.match('"hi" rest', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '"hi"')

	def test_unterminated_string_does_not_match(self) -> None:
		self.assertIsNone(Tokens.StringToken.match('"unterminated', 0))


class Test_WhitespaceToken(unittest.TestCase):
	def test_spaces_and_tabs(self) -> None:
		token = Tokens.WhitespaceToken.match(' \t  x', 0)
		assert token is not None
		self.assertEqual(token.raw_value, ' \t  ')

	def test_does_not_match_newline(self) -> None:
		self.assertIsNone(Tokens.WhitespaceToken.match('\n', 0))


class Test_NewlineToken(unittest.TestCase):
	def test_single_newline_count(self) -> None:
		token = Tokens.NewlineToken.match('\n', 0)
		assert token is not None
		self.assertEqual(token.newline_count(), 1)

	def test_multiple_newlines_count(self) -> None:
		token = Tokens.NewlineToken.match('\n\n\n', 0)
		assert token is not None
		self.assertEqual(token.newline_count(), 3)

	def test_crlf_counts_as_single_line(self) -> None:
		token = Tokens.NewlineToken.match('\r\n', 0)
		assert token is not None
		self.assertEqual(token.newline_count(), 1)

	def test_lone_cr_counts_as_a_line(self) -> None:
		token = Tokens.NewlineToken.match('\r', 0)
		assert token is not None
		self.assertEqual(token.newline_count(), 1)


class Test_CommentToken(unittest.TestCase):
	def test_hash_comment(self) -> None:
		token = Tokens.CommentToken.match('# a comment', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '# a comment')

	def test_semicolon_comment(self) -> None:
		token = Tokens.CommentToken.match('; a comment', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '; a comment')

	def test_comment_stops_at_newline(self) -> None:
		token = Tokens.CommentToken.match('# a comment\nnext', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '# a comment')


class Test_BooleanToken(unittest.TestCase):
	def test_true(self) -> None:
		token = Tokens.BooleanToken.match('true', 0)
		assert token is not None
		self.assertEqual(token.raw_value, 'true')

	def test_false(self) -> None:
		token = Tokens.BooleanToken.match('false', 0)
		assert token is not None
		self.assertEqual(token.raw_value, 'false')

	def test_one_and_zero(self) -> None:
		self.assertIsNotNone(Tokens.BooleanToken.match('1', 0))
		self.assertIsNotNone(Tokens.BooleanToken.match('0', 0))


class Test_EOFToken(unittest.TestCase):
	def test_match_always_none(self) -> None:
		self.assertIsNone(Tokens.EOFToken.match('anything', 0))

	def test_empty_raw_value(self) -> None:
		self.assertEqual(Tokens.EOFToken().raw_value, '')


class Test_LiteralsToken(unittest.TestCase):
	class Symbols(Tokens.LiteralsToken):
		_literals = ('==', '=', '(')

	class OtherSymbols(Tokens.LiteralsToken):
		_literals = ('@',)

	def test_matches_a_literal(self) -> None:
		token = Test_LiteralsToken.Symbols.match('(rest', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '(')

	def test_longest_alternative_can_be_ordered_first(self) -> None:
		# `==` is listed before `=` so it wins where both could match.
		token = Test_LiteralsToken.Symbols.match('==x', 0)
		assert token is not None
		self.assertEqual(token.raw_value, '==')

	def test_no_match_returns_none(self) -> None:
		self.assertIsNone(Test_LiteralsToken.Symbols.match('xyz', 0))

	def test_distinct_subclasses_do_not_share_literals(self) -> None:
		# Each LiteralsToken subclass must match only its own literals, even
		# though the compiled-regex cache lives on the shared base class.
		self.assertIsNotNone(Test_LiteralsToken.OtherSymbols.match('@', 0))
		self.assertIsNone(Test_LiteralsToken.OtherSymbols.match('=', 0))
		self.assertIsNone(Test_LiteralsToken.Symbols.match('@', 0))


if __name__ == '__main__':
	unittest.main()
