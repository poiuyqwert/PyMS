
from ...Utilities.CodeHandlers import Formatters

import unittest


class Test_BlockFormatters(unittest.TestCase):
	def test_colon(self) -> None:
		self.assertEqual(Formatters.ColonBlockFormatter().serialize('start'), ':start')

	def test_hyphen(self) -> None:
		self.assertEqual(Formatters.HyphenBlockFormatter().serialize('start'), '--start--')


class Test_CommandFormatters(unittest.TestCase):
	def test_flat_no_params(self) -> None:
		self.assertEqual(Formatters.FlatCommandFormatter().serialize('nop', []), 'nop')

	def test_flat_with_params(self) -> None:
		self.assertEqual(Formatters.FlatCommandFormatter().serialize('inc', ['5', '6']), 'inc 5 6')

	def test_parens_no_params(self) -> None:
		self.assertEqual(Formatters.ParensCommandFormatter().serialize('nop', []), 'nop()')

	def test_parens_with_params(self) -> None:
		self.assertEqual(Formatters.ParensCommandFormatter().serialize('inc', ['5', '6']), 'inc(5, 6)')


class Test_CommentFormatters(unittest.TestCase):
	def test_hash_symbol(self) -> None:
		self.assertEqual(Formatters.HashCommentFormatter().symbol(), '#')

	def test_hash_serialize_joins_comments(self) -> None:
		self.assertEqual(Formatters.HashCommentFormatter().serialize(['a', 'b']), '\t# a, b')

	def test_semicolon_symbol(self) -> None:
		self.assertEqual(Formatters.SemicolonCommentFormatter().symbol(), ';')

	def test_semicolon_serialize_joins_comments(self) -> None:
		self.assertEqual(Formatters.SemicolonCommentFormatter().serialize(['a', 'b']), '\t; a, b')


class Test_FormattersDefaults(unittest.TestCase):
	def test_default_formatter_selection(self) -> None:
		formatters = Formatters.Formatters()
		self.assertIsInstance(formatters.block, Formatters.ColonBlockFormatter)
		self.assertIsInstance(formatters.command, Formatters.FlatCommandFormatter)
		self.assertIsInstance(formatters.comment, Formatters.HashCommentFormatter)
		self.assertFalse(formatters.indent_bodies)

	def test_default_formatters_not_shared_between_instances(self) -> None:
		a = Formatters.Formatters()
		b = Formatters.Formatters()
		self.assertIsNot(a.block, b.block)
		self.assertIsNot(a.command, b.command)
		self.assertIsNot(a.comment, b.comment)


if __name__ == '__main__':
	unittest.main()
