
from ...Utilities import Config

import unittest

class Test_migrate_field(unittest.TestCase):
	def test_top_level_field(self) -> None:
		data: dict = {'old': 42}
		Config.migrate_field(data, ('old',), ('new',))
		self.assertEqual(data['new'], 42)

	def test_nested_source_field(self) -> None:
		data: dict = {'a': {'b': {'c': 'value'}}}
		Config.migrate_field(data, ('a', 'b', 'c'), ('moved',))
		self.assertEqual(data['moved'], 'value')

	def test_nested_destination(self) -> None:
		data: dict = {'old': 'value'}
		Config.migrate_field(data, ('old',), ('a', 'b', 'c'))
		self.assertEqual(data['a']['b']['c'], 'value')

	def test_nested_source_and_destination(self) -> None:
		data: dict = {'src': {'inner': 7}}
		Config.migrate_field(data, ('src', 'inner'), ('dst', 'inner'))
		self.assertEqual(data['dst']['inner'], 7)

	def test_missing_intermediate_key_does_nothing(self) -> None:
		data: dict = {'a': {'b': {}}}
		Config.migrate_field(data, ('a', 'b', 'missing'), ('new',))
		self.assertNotIn('new', data)

	def test_missing_top_level_key_does_nothing(self) -> None:
		data: dict = {'a': {'b': 1}}
		Config.migrate_field(data, ('missing',), ('new',))
		self.assertNotIn('new', data)

	def test_non_dict_in_path_does_nothing(self) -> None:
		data: dict = {'a': 'not a dict'}
		Config.migrate_field(data, ('a', 'b'), ('new',))
		self.assertNotIn('new', data)

	def test_destination_overwrites_existing(self) -> None:
		data: dict = {'a': {'b': 'new_value'}, 'target': 'old_value'}
		Config.migrate_field(data, ('a', 'b'), ('target',))
		self.assertEqual(data['target'], 'new_value')

	def test_value_preserves_object_identity(self) -> None:
		nested = {'inner': [1, 2, 3]}
		data: dict = {'a': {'b': nested}}
		Config.migrate_field(data, ('a', 'b'), ('moved',))
		self.assertIs(data['moved'], nested)


class Test_migrate_nest(unittest.TestCase):
	def test_creates_missing_nested_dicts(self) -> None:
		data: dict = {}
		Config.migrate_nest(data, ('a', 'b'))
		self.assertEqual(data, {'a': {'b': {}}})

	def test_returns_innermost_dict(self) -> None:
		data: dict = {}
		inner = Config.migrate_nest(data, ('a', 'b'))
		inner['x'] = 1
		self.assertEqual(data, {'a': {'b': {'x': 1}}})

	def test_preserves_existing_dicts(self) -> None:
		data: dict = {'a': {'x': 1}}
		result = Config.migrate_nest(data, ('a',))
		self.assertEqual(result, {'x': 1})
		self.assertEqual(data, {'a': {'x': 1}})

	def test_replaces_non_dict_value(self) -> None:
		data: dict = {'a': 5}
		Config.migrate_nest(data, ('a',))
		self.assertEqual(data, {'a': {}})


class Test_migrate_fields(unittest.TestCase):
	def test_applies_each_migration(self) -> None:
		data: dict = {'old1': 1, 'old2': 2}
		Config.migrate_fields(data, ((('old1',), ('new1',)), (('old2',), ('new2',))))
		self.assertEqual(data['new1'], 1)
		self.assertEqual(data['new2'], 2)

	def test_supports_nested_destinations(self) -> None:
		data: dict = {'flat': 7}
		Config.migrate_fields(data, ((('flat',), ('nested', 'value')),))
		self.assertEqual(data['nested']['value'], 7)

	def test_missing_source_is_skipped(self) -> None:
		data: dict = {'present': 1}
		Config.migrate_fields(data, ((('absent',), ('new',)),))
		self.assertNotIn('new', data)
