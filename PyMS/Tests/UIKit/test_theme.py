
from ...Utilities.UIKit.Theme import _WildcardMatcher

import unittest


class Test_WildcardMatcher_parse(unittest.TestCase):
	def test_single_star_matches_one(self) -> None:
		matcher = _WildcardMatcher.parse('*')
		self.assertIsNotNone(matcher)
		assert matcher is not None
		self.assertFalse(matcher.many)

	def test_double_star_matches_many(self) -> None:
		matcher = _WildcardMatcher.parse('**')
		self.assertIsNotNone(matcher)
		assert matcher is not None
		self.assertTrue(matcher.many)

	def test_empty_token_is_not_a_wildcard(self) -> None:
		self.assertIsNone(_WildcardMatcher.parse(''))

	def test_non_wildcard_token_is_rejected(self) -> None:
		self.assertIsNone(_WildcardMatcher.parse('foo'))
