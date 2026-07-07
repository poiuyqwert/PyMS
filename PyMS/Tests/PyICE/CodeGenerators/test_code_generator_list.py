
from ....PyICE.CodeGenerators import CodeGenerator as CG
from ....PyICE.CodeGenerators import CodeGeneratorList
from ....PyICE.CodeGenerators.CodeGeneratorList import _REPEATERS
from ....Utilities.PyMSError import PyMSError

import unittest

SIZE = 3


def _indices(repeater, count: int = 10) -> list:
	return [repeater.index(SIZE, n) for n in range(count)]


class Test_repeaters(unittest.TestCase):
	def test_dont_visits_each_once_then_stops(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterDont()
		self.assertEqual(repeater.count(SIZE), 3)
		self.assertEqual(_indices(repeater), [0, 1, 2, None, None, None, None, None, None, None])

	def test_once_replays_the_list_twice(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatOnce()
		self.assertEqual(repeater.count(SIZE), 6)
		self.assertEqual(_indices(repeater), [0, 1, 2, 0, 1, 2, None, None, None, None])

	def test_forever_cycles_indefinitely(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatForever()
		self.assertIsNone(repeater.count(SIZE))
		self.assertEqual(_indices(repeater), [0, 1, 2, 0, 1, 2, 0, 1, 2, 0])

	def test_last_forever_holds_the_final_index(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatLast()
		self.assertIsNone(repeater.count(SIZE))
		self.assertEqual(_indices(repeater), [0, 1, 2, 2, 2, 2, 2, 2, 2, 2])

	def test_inverted_once_bounces_back_without_repeating_ends(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatInvertedOnce()
		self.assertEqual(repeater.count(SIZE), 4)
		self.assertEqual(_indices(repeater), [0, 1, 2, 1, None, None, None, None, None, None])

	def test_inverted_forever_bounces_indefinitely(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatInvertedForever()
		self.assertIsNone(repeater.count(SIZE))
		self.assertEqual(_indices(repeater), [0, 1, 2, 1, 0, 1, 2, 1, 0, 1])

	def test_inverted_once_repeat_end_bounces_repeating_ends(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd()
		self.assertEqual(repeater.count(SIZE), 6)
		self.assertEqual(_indices(repeater), [0, 1, 2, 2, 1, 0, None, None, None, None])

	def test_inverted_forever_repeat_end_bounces_repeating_ends(self) -> None:
		repeater = CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd()
		self.assertIsNone(repeater.count(SIZE))
		self.assertEqual(_indices(repeater), [0, 1, 2, 2, 1, 0, 0, 1, 2, 2])

	def test_registry_maps_type_names(self) -> None:
		self.assertEqual(set(_REPEATERS.keys()), {
			'dont', 'once', 'forever', 'last_forever',
			'inverted_once', 'inverted_forever',
			'inverted_once_repeat_end', 'inverted_forever_repeat_end',
		})

	def test_display_names_present(self) -> None:
		for repeater in _REPEATERS.values():
			self.assertTrue(repeater.display_name())


class Test_CodeGeneratorTypeList(unittest.TestCase):
	def _list(self, values=None, repeater=None) -> CodeGeneratorList.CodeGeneratorTypeList:
		return CodeGeneratorList.CodeGeneratorTypeList(
			values if values is not None else ['a', 'b', 'c'],
			repeater or CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatForever(),
		)

	def test_type_name(self) -> None:
		self.assertEqual(CodeGeneratorList.CodeGeneratorTypeList.type_name(), 'list')

	def test_count_delegates_to_repeater(self) -> None:
		self.assertEqual(self._list(repeater=CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatOnce()).count(), 6)

	def test_value_picks_item_at_repeater_index(self) -> None:
		generator = self._list()
		self.assertEqual(generator.value(lambda _: '1'), 'b')

	def test_value_substitutes_variables(self) -> None:
		generator = self._list(values=['x$foo'])
		lookups = {'n': '0', 'foo': 'Y'}
		self.assertEqual(generator.value(lambda name: lookups[name]), 'xY')

	def test_value_out_of_range_returns_empty(self) -> None:
		generator = self._list(repeater=CodeGeneratorList.CodeGeneratorTypeListRepeaterDont())
		self.assertEqual(generator.value(lambda _: '9'), '')

	def test_description_lists_values(self) -> None:
		self.assertEqual(self._list().description(), 'Items from list: a, b, c')

	def test_to_json(self) -> None:
		generator = self._list(repeater=CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatOnce())
		self.assertEqual(generator.to_json(), {'type': 'list', 'list': ['a', 'b', 'c'], 'repeater': 'once'})

	def test_from_json_round_trip(self) -> None:
		generator = self._list(repeater=CodeGeneratorList.CodeGeneratorTypeListRepeaterRepeatLast())
		restored = CodeGeneratorList.CodeGeneratorTypeList.from_json(generator.to_json())
		self.assertEqual(restored.values, generator.values)
		self.assertEqual(restored.repeater.type_name(), 'last_forever')

	def test_from_json_invalid_repeater_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CodeGeneratorList.CodeGeneratorTypeList.from_json({'type': 'list', 'list': ['a'], 'repeater': 'bogus'})
		self.assertIn('`repeater` has invalid value', str(cm.exception))

	def test_registered_as_list(self) -> None:
		self.assertIs(CG.lookup_type('list'), CodeGeneratorList.CodeGeneratorTypeList)
