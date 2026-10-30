
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

from typing import Self
from dataclasses import dataclass

import unittest


@dataclass
class Point:
	x: int
	y: int

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(x=JSON.get(json, 'x', int), y=JSON.get(json, 'y', int))

	def to_json(self) -> JSON.Object:
		return {'x': self.x, 'y': self.y}


@dataclass
class Named:
	name: str

	@classmethod
	def from_json(cls, json: JSON.Object) -> Self:
		return cls(name=JSON.get(json, 'name', str))

	def to_json(self) -> JSON.Object:
		return {'name': self.name}


class Test_is_json_object(unittest.TestCase):
	def test_validates_keys_and_values(self) -> None:
		self.assertTrue(JSON.is_json_object({'name': 'value', 'count': 3}))

	def test_rejects_non_dict(self) -> None:
		self.assertFalse(JSON.is_json_object(['name', 'value']))

	def test_rejects_non_string_keys(self) -> None:
		self.assertFalse(JSON.is_json_object({1: 'value'}))

	def test_rejects_invalid_values(self) -> None:
		self.assertFalse(JSON.is_json_object({'when': object()}))

	def test_validates_keys_longer_than_two_chars(self) -> None:
		self.assertTrue(JSON.is_json_object({'longkey': 1}))

	def test_lazy_skips_value_validation(self) -> None:
		self.assertTrue(JSON.is_json_object({'when': object()}, lazy=True))


class Test_get(unittest.TestCase):
	def test_returns_int(self) -> None:
		self.assertEqual(JSON.get({'n': 42}, 'n', int), 42)

	def test_returns_str(self) -> None:
		self.assertEqual(JSON.get({'s': 'hello'}, 's', str), 'hello')

	def test_returns_float(self) -> None:
		self.assertEqual(JSON.get({'f': 3.14}, 'f', float), 3.14)

	def test_returns_bool(self) -> None:
		self.assertEqual(JSON.get({'b': True}, 'b', bool), True)

	def test_returns_list(self) -> None:
		self.assertEqual(JSON.get({'l': [1, 2, 3]}, 'l', list), [1, 2, 3])

	def test_returns_dict(self) -> None:
		self.assertEqual(JSON.get({'d': {'a': 1}}, 'd', dict), {'a': 1})

	def test_missing_key_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get({}, 'missing', int)
		self.assertIn('Invalid JSON format (missing `missing`)', str(cm.exception))

	def test_wrong_type_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get({'n': 'not an int'}, 'n', int)
		self.assertIn('Invalid JSON format (invalid `n`)', str(cm.exception))

	def test_none_value_for_int_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get({'n': None}, 'n', int)
		self.assertIn('Invalid JSON format (invalid `n`)', str(cm.exception))

	def test_codable_decoded(self) -> None:
		result = JSON.get({'p': {'x': 1, 'y': 2}}, 'p', Point)
		self.assertIsInstance(result, Point)
		self.assertEqual(result, Point(x=1, y=2))

	def test_codable_non_dict_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get({'p': [1, 2]}, 'p', Point)
		self.assertIn('Invalid JSON format (invalid `p`)', str(cm.exception))

	def test_codable_missing_key_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get({}, 'p', Point)
		self.assertIn('Invalid JSON format (missing `p`)', str(cm.exception))


class Test_get_obj(unittest.TestCase):
	def test_discriminator_selects_type(self) -> None:
		def discriminator(obj: JSON.Object) -> type:
			return Point if 'x' in obj else Named
		result: Point | Named = JSON.get_obj({'item': {'x': 5, 'y': 6}}, 'item', discriminator)
		self.assertEqual(result, Point(x=5, y=6))

	def test_discriminator_selects_alternate_type(self) -> None:
		def discriminator(obj: JSON.Object) -> type:
			return Point if 'x' in obj else Named
		result: Point | Named = JSON.get_obj({'item': {'name': 'foo'}}, 'item', discriminator)
		self.assertEqual(result, Named(name='foo'))

	def test_missing_key_raises(self) -> None:
		def discriminator(_: JSON.Object) -> type:
			return Point
		with self.assertRaises(PyMSError) as cm:
			JSON.get_obj({}, 'item', discriminator)
		self.assertIn('Invalid JSON format (missing `item`)', str(cm.exception))

	def test_non_dict_value_raises(self) -> None:
		def discriminator(_: JSON.Object) -> type:
			return Point
		with self.assertRaises(PyMSError) as cm:
			JSON.get_obj({'item': 'not a dict'}, 'item', discriminator)
		self.assertIn('Invalid JSON format (invalid `item`)', str(cm.exception))


class Test_get_array(unittest.TestCase):
	def test_array_of_ints(self) -> None:
		self.assertEqual(JSON.get_array({'a': [1, 2, 3]}, 'a', int), [1, 2, 3])

	def test_array_of_strs(self) -> None:
		self.assertEqual(JSON.get_array({'a': ['x', 'y']}, 'a', str), ['x', 'y'])

	def test_empty_array(self) -> None:
		self.assertEqual(JSON.get_array({'a': []}, 'a', int), [])

	def test_missing_key_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get_array({}, 'missing', int)
		self.assertIn('Invalid JSON format (missing `missing`)', str(cm.exception))

	def test_non_list_value_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get_array({'a': 'not a list'}, 'a', int)
		self.assertIn('Invalid JSON format (invalid `a`)', str(cm.exception))

	def test_wrong_element_type_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get_array({'a': [1, 'two', 3]}, 'a', int)
		self.assertIn('Invalid JSON format (array `a` contains invalid value at index 1)', str(cm.exception))

	def test_codable_elements_are_decoded(self) -> None:
		raw: JSON.Object = {'pts': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]}
		result = JSON.get_array(raw, 'pts', Point)
		self.assertEqual(result, [Point(x=1, y=2), Point(x=3, y=4)])
		for item in result:
			self.assertIsInstance(item, Point)

	def test_codable_invalid_element_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			JSON.get_array({'pts': [{'x': 1, 'y': 2}, {'x': 'bad'}]}, 'pts', Point)
		self.assertIn('Invalid JSON format (array `pts` contains invalid value at index 1)', str(cm.exception))

	def test_returns_fresh_list_does_not_mutate_input(self) -> None:
		original: JSON.Array = [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]
		raw: JSON.Object = {'pts': original}
		result = JSON.get_array(raw, 'pts', Point)
		self.assertIsNot(result, original)
		# Caller's input should still contain raw dicts
		self.assertEqual(original, [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}])
		self.assertIsInstance(original[0], dict)

	def test_codable_empty_array(self) -> None:
		self.assertEqual(JSON.get_array({'pts': []}, 'pts', Point), [])


class Test_get_array_obj(unittest.TestCase):
	def test_discriminator_picks_type_for_array(self) -> None:
		def discriminator(_: JSON.Object) -> type:
			return Point
		raw: JSON.Object = {'pts': [{'x': 1, 'y': 2}, {'x': 3, 'y': 4}]}
		result: list[Point] = JSON.get_array_obj(raw, 'pts', discriminator)
		self.assertEqual(result, [Point(x=1, y=2), Point(x=3, y=4)])

	def test_missing_array_raises(self) -> None:
		def discriminator(_: JSON.Object) -> type:
			return Point
		with self.assertRaises(PyMSError) as cm:
			JSON.get_array_obj({}, 'pts', discriminator)
		self.assertIn('Invalid JSON format (missing `pts`)', str(cm.exception))
