
from ...Utilities.Config import migrate_field

import unittest

class Test_migrate_field(unittest.TestCase):
	def test_top_level_field(self) -> None:
		data: dict = {'old': 42}
		migrate_field(data, ('old',), ('new',))
		self.assertEqual(data['new'], 42)

	def test_nested_source_field(self) -> None:
		data: dict = {'a': {'b': {'c': 'value'}}}
		migrate_field(data, ('a', 'b', 'c'), ('moved',))
		self.assertEqual(data['moved'], 'value')

	def test_nested_destination(self) -> None:
		data: dict = {'old': 'value'}
		migrate_field(data, ('old',), ('a', 'b', 'c'))
		self.assertEqual(data['a']['b']['c'], 'value')

	def test_nested_source_and_destination(self) -> None:
		data: dict = {'src': {'inner': 7}}
		migrate_field(data, ('src', 'inner'), ('dst', 'inner'))
		self.assertEqual(data['dst']['inner'], 7)

	def test_missing_intermediate_key_does_nothing(self) -> None:
		data: dict = {'a': {'b': {}}}
		migrate_field(data, ('a', 'b', 'missing'), ('new',))
		self.assertNotIn('new', data)

	def test_missing_top_level_key_does_nothing(self) -> None:
		data: dict = {'a': {'b': 1}}
		migrate_field(data, ('missing',), ('new',))
		self.assertNotIn('new', data)

	def test_non_dict_in_path_does_nothing(self) -> None:
		data: dict = {'a': 'not a dict'}
		migrate_field(data, ('a', 'b'), ('new',))
		self.assertNotIn('new', data)

	def test_destination_overwrites_existing(self) -> None:
		data: dict = {'a': {'b': 'new_value'}, 'target': 'old_value'}
		migrate_field(data, ('a', 'b'), ('target',))
		self.assertEqual(data['target'], 'new_value')

	def test_value_preserves_object_identity(self) -> None:
		nested = {'inner': [1, 2, 3]}
		data: dict = {'a': {'b': nested}}
		migrate_field(data, ('a', 'b'), ('moved',))
		self.assertIs(data['moved'], nested)
