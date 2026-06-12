
from ...PyDAT.EntryNameOverrides import apply_name_override, remove_name_override, RE_OVERRIDE

import unittest


class Test_apply_name_override(unittest.TestCase):
	def test_inserts_new_override(self) -> None:
		overrides: dict[int, tuple[bool, str]] = {}
		apply_name_override(overrides, 5, 'Marine', True)
		self.assertEqual(overrides, {5: (True, 'Marine')})

	def test_updates_existing_override(self) -> None:
		overrides = {5: (True, 'Marine')}
		apply_name_override(overrides, 5, 'Firebat', False)
		self.assertEqual(overrides, {5: (False, 'Firebat')})

	def test_blank_name_removes_existing(self) -> None:
		overrides = {5: (True, 'Marine')}
		apply_name_override(overrides, 5, '', False)
		self.assertEqual(overrides, {})

	def test_blank_name_on_missing_is_noop(self) -> None:
		overrides: dict[int, tuple[bool, str]] = {}
		apply_name_override(overrides, 9, '', False)
		self.assertEqual(overrides, {})


class Test_remove_name_override(unittest.TestCase):
	def test_removes_existing(self) -> None:
		overrides = {3: (False, 'X')}
		remove_name_override(overrides, 3)
		self.assertEqual(overrides, {})

	def test_missing_is_noop(self) -> None:
		overrides = {3: (False, 'X')}
		remove_name_override(overrides, 9)
		self.assertEqual(overrides, {3: (False, 'X')})


class Test_RE_OVERRIDE(unittest.TestCase):
	def test_parses_with_append_marker(self) -> None:
		match = RE_OVERRIDE.match('  12 + :Hi there')
		assert match is not None
		self.assertEqual(match.groups(), ('12', '+', 'Hi there'))

	def test_parses_without_append_marker(self) -> None:
		match = RE_OVERRIDE.match('3:Foo')
		assert match is not None
		self.assertEqual(match.groups(), ('3', '', 'Foo'))

	def test_parses_empty_name(self) -> None:
		match = RE_OVERRIDE.match('7:')
		assert match is not None
		self.assertEqual(match.groups(), ('7', '', ''))

	def test_rejects_non_numeric_id(self) -> None:
		self.assertIsNone(RE_OVERRIDE.match('abc:Foo'))

	def test_rejects_missing_colon(self) -> None:
		self.assertIsNone(RE_OVERRIDE.match('12 Foo'))

	def test_rejects_more_than_five_digits(self) -> None:
		self.assertIsNone(RE_OVERRIDE.match('123456:Foo'))
