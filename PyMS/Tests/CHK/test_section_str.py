
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionSTR import CHKSectionSTR

import unittest


def _section() -> CHKSectionSTR:
	return CHKSectionSTR(make_chk())


class Test_CHKSectionSTR(unittest.TestCase):
	def test_add_string_assigns_sequential_ids(self) -> None:
		section = _section()
		first = section.add_string('Alpha')
		second = section.add_string('Beta')
		self.assertEqual((first.string_id, second.string_id), (0, 1))
		self.assertEqual(section.string_count(), 2)

	def test_add_string_reuses_existing(self) -> None:
		section = _section()
		first = section.add_string('Alpha')
		again = section.add_string('Alpha')
		self.assertIs(again, first)
		self.assertEqual(first.references, 2)

	def test_add_string_without_reuse_creates_new(self) -> None:
		section = _section()
		first = section.add_string('Alpha')
		again = section.add_string('Alpha', reuse=False)
		self.assertIsNot(again, first)
		self.assertEqual(section.string_count(), 2)

	def test_lookup_string(self) -> None:
		section = _section()
		string = section.add_string('Find Me')
		self.assertIs(section.lookup_string('Find Me'), string)
		self.assertIsNone(section.lookup_string('Missing'))

	def test_remove_string_releases(self) -> None:
		section = _section()
		string = section.add_string('Once')
		section.remove_string(string.string_id)
		self.assertFalse(section.string_exists(string.string_id))

	def test_remove_text(self) -> None:
		section = _section()
		string = section.add_string('Bye')
		section.remove_text('Bye')
		self.assertFalse(section.string_exists(string.string_id))

	def test_set_string_mutates_single_reference(self) -> None:
		section = _section()
		string = section.add_string('Before')
		result = section.set_string(string.string_id, 'After')
		self.assertIs(result, string)
		self.assertEqual(string.text, 'After')

	def test_get_text_default(self) -> None:
		section = _section()
		self.assertEqual(section.get_text(99, 'fallback'), 'fallback')

	def test_highest_index(self) -> None:
		section = _section()
		section.add_string('A')
		section.add_string('B')
		self.assertEqual(section.highest_index(), 1)

	def test_dense_round_trip(self) -> None:
		section = _section()
		for text in ('Alpha', 'Beta', 'Gamma'):
			section.add_string(text)
		reloaded = CHKSectionSTR(make_chk())
		reloaded.load_data(section.save_data())
		self.assertEqual([reloaded.get_text(i) for i in range(3)], ['Alpha', 'Beta', 'Gamma'])

	def test_sparse_round_trip(self) -> None:
		# A released slot has no "gap" representation, so it round-trips as empty.
		section = _section()
		first = section.add_string('Hello')
		section.add_string('World')
		first.release()
		reloaded = CHKSectionSTR(make_chk())
		reloaded.load_data(section.save_data())
		self.assertEqual([reloaded.get_text(i) for i in range(2)], ['', 'World'])

	def test_decompile(self) -> None:
		section = _section()
		section.add_string('Hi "there"')
		text = section.decompile()
		self.assertTrue(text.startswith('STR :'))
		self.assertIn('\\"there\\"', text)


class Test_CHKString(unittest.TestCase):
	def test_retain_increments(self) -> None:
		section = _section()
		string = section.add_string('Text')
		string.retain()
		self.assertEqual(string.references, 2)

	def test_release_deletes_at_zero(self) -> None:
		section = _section()
		string = section.add_string('Text')
		self.assertEqual(string.references, 1)
		string.release()
		self.assertFalse(section.string_exists(string.string_id))

	def test_release_keeps_while_referenced(self) -> None:
		section = _section()
		string = section.add_string('Text')
		string.retain()
		string.release()
		self.assertTrue(section.string_exists(string.string_id))
		self.assertEqual(string.references, 1)
