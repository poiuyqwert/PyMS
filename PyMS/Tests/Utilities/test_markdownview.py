
from ...Utilities.MarkdownView import _list_numbered, _list_lettered, _list_roman

import unittest


class Test_list_numbered(unittest.TestCase):
	def test_first(self) -> None:
		self.assertEqual(_list_numbered(1), '1. ')

	def test_arbitrary(self) -> None:
		self.assertEqual(_list_numbered(42), '42. ')


class Test_list_lettered(unittest.TestCase):
	def test_first_letter(self) -> None:
		self.assertEqual(_list_lettered(1), 'a. ')

	def test_last_single_letter(self) -> None:
		self.assertEqual(_list_lettered(26), 'z. ')

	def test_wraps_to_two_letters(self) -> None:
		self.assertEqual(_list_lettered(27), 'aa. ')

	def test_second_letter_increments_least_significant(self) -> None:
		# The least-significant letter advances independently of the first.
		self.assertEqual(_list_lettered(28), 'ab. ')

	def test_last_of_first_two_letter_run(self) -> None:
		self.assertEqual(_list_lettered(52), 'az. ')

	def test_carries_to_next_first_letter(self) -> None:
		self.assertEqual(_list_lettered(53), 'ba. ')


class Test_list_roman(unittest.TestCase):
	def test_first(self) -> None:
		self.assertEqual(_list_roman(1), 'i. ')

	def test_four_uses_subtractive(self) -> None:
		self.assertEqual(_list_roman(4), 'iv. ')

	def test_composite(self) -> None:
		self.assertEqual(_list_roman(2024), 'mmxxiv. ')
