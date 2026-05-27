
from ...Utilities.Bidict import Bidict

import unittest


class Test_init(unittest.TestCase):
	def test_empty(self) -> None:
		b: Bidict[str, int] = Bidict({})
		self.assertEqual(list(b.keys()), [])
		self.assertEqual(list(b.values()), [])

	def test_from_dict(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		self.assertEqual(b['a'], 1)
		self.assertEqual(b['b'], 2)
		self.assertEqual(b.key_of(1), 'a')
		self.assertEqual(b.key_of(2), 'b')


class Test_getitem(unittest.TestCase):
	def test_returns_value(self) -> None:
		b = Bidict({'a': 1})
		self.assertEqual(b['a'], 1)

	def test_missing_key_raises(self) -> None:
		b: Bidict[str, int] = Bidict({})
		with self.assertRaises(KeyError):
			_ = b['missing']


class Test_key_of(unittest.TestCase):
	def test_returns_key(self) -> None:
		b = Bidict({'a': 1})
		self.assertEqual(b.key_of(1), 'a')

	def test_missing_value_raises(self) -> None:
		b: Bidict[str, int] = Bidict({'a': 1})
		with self.assertRaises(KeyError):
			b.key_of(99)


class Test_get_key_of(unittest.TestCase):
	def test_returns_key_when_present(self) -> None:
		b = Bidict({'a': 1})
		self.assertEqual(b.get_key_of(1), 'a')

	def test_returns_default_when_absent(self) -> None:
		b: Bidict[str, int] = Bidict({'a': 1})
		self.assertIsNone(b.get_key_of(99))
		self.assertEqual(b.get_key_of(99, 'fallback'), 'fallback')


class Test_setitem(unittest.TestCase):
	def test_insert_new_pair(self) -> None:
		b: Bidict[str, int] = Bidict({})
		b['a'] = 1
		self.assertEqual(b['a'], 1)
		self.assertEqual(b.key_of(1), 'a')

	def test_overwrite_value_removes_stale_reverse_entry(self) -> None:
		b = Bidict({'a': 1})
		b['a'] = 2
		self.assertEqual(b['a'], 2)
		self.assertEqual(b.key_of(2), 'a')
		self.assertFalse(b.has_value(1))
		with self.assertRaises(KeyError):
			b.key_of(1)

	def test_overwrite_preserves_bijection(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		b['a'] = 3
		for value in b.values():
			self.assertEqual(b._value_map[b._key_map[value]], value) # pylint: disable=protected-access
		for key in b.keys():
			self.assertEqual(b._key_map[b._value_map[key]], key) # pylint: disable=protected-access

	def test_assigning_value_already_used_removes_old_key(self) -> None:
		# Symmetric case: if the new value is already mapped under a different key,
		# the old key must be evicted to keep the bijection.
		b = Bidict({'a': 1, 'b': 2})
		b['a'] = 2
		self.assertEqual(b['a'], 2)
		self.assertEqual(b.key_of(2), 'a')
		self.assertNotIn('b', b)
		self.assertFalse(b.has_value(1))


class Test_delitem(unittest.TestCase):
	def test_removes_from_both_maps(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		del b['a']
		self.assertNotIn('a', b)
		self.assertFalse(b.has_value(1))
		# b still intact
		self.assertEqual(b['b'], 2)
		self.assertEqual(b.key_of(2), 'b')

	def test_missing_key_raises(self) -> None:
		b: Bidict[str, int] = Bidict({})
		with self.assertRaises(KeyError):
			del b['missing']


class Test_contains(unittest.TestCase):
	def test_true_for_present_key(self) -> None:
		b = Bidict({'a': 1})
		self.assertIn('a', b)

	def test_false_for_absent_key(self) -> None:
		b: Bidict[str, int] = Bidict({'a': 1})
		self.assertNotIn('b', b)


class Test_has_value(unittest.TestCase):
	def test_true_for_present_value(self) -> None:
		b = Bidict({'a': 1})
		self.assertTrue(b.has_value(1))

	def test_false_for_absent_value(self) -> None:
		b: Bidict[str, int] = Bidict({'a': 1})
		self.assertFalse(b.has_value(99))

	def test_false_after_overwrite(self) -> None:
		b = Bidict({'a': 1})
		b['a'] = 2
		self.assertFalse(b.has_value(1))
		self.assertTrue(b.has_value(2))


class Test_keys_values_items(unittest.TestCase):
	def test_keys(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		self.assertEqual(set(b.keys()), {'a', 'b'})

	def test_values(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		self.assertEqual(set(b.values()), {1, 2})

	def test_items(self) -> None:
		b = Bidict({'a': 1, 'b': 2})
		self.assertEqual(set(b.items()), {('a', 1), ('b', 2)})
