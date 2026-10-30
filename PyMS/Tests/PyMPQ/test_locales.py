
from ...PyMPQ.Locales import LOCALE_CHOICES, find_locale_index

import unittest


class Test_find_locale_index(unittest.TestCase):
	def test_every_known_locale_returns_its_entry(self) -> None:
		for index,(_,locale) in enumerate(LOCALE_CHOICES):
			if locale is None:
				continue
			self.assertEqual(find_locale_index(locale), index)

	def test_unknown_locale_returns_other_entry(self) -> None:
		other_index = find_locale_index(0x1234)
		name,locale = LOCALE_CHOICES[other_index]
		self.assertEqual(name, 'Other')
		self.assertIsNone(locale)
