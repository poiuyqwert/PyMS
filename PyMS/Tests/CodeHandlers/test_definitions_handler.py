
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities import Struct

import unittest


IntType = CodeType.IntCodeType('int', 'i', Struct.l_u16)
BoolType = CodeType.BooleanCodeType('bool', 'b', Struct.l_u8)


class Test_SetGetVariable(unittest.TestCase):
	def test_set_and_get(self) -> None:
		definitions = DefinitionsHandler()
		definitions.set_variable('foo', 5, IntType)
		variable = definitions.get_variable('foo')
		assert variable is not None
		self.assertEqual(variable.name, 'foo')
		self.assertEqual(variable.value, 5)
		self.assertIs(variable.type, IntType)

	def test_get_missing_returns_none(self) -> None:
		self.assertIsNone(DefinitionsHandler().get_variable('absent'))

	def test_set_overwrites(self) -> None:
		definitions = DefinitionsHandler()
		definitions.set_variable('foo', 5, IntType)
		definitions.set_variable('foo', 9, IntType)
		variable = definitions.get_variable('foo')
		assert variable is not None
		self.assertEqual(variable.value, 9)


class Test_LookupVariable(unittest.TestCase):
	def test_finds_variable_by_value_and_type(self) -> None:
		definitions = DefinitionsHandler()
		definitions.set_variable('foo', 5, IntType)
		found = definitions.lookup_variable(5, IntType)
		assert found is not None
		self.assertEqual(found.name, 'foo')

	def test_no_match_returns_none(self) -> None:
		definitions = DefinitionsHandler()
		definitions.set_variable('foo', 5, IntType)
		self.assertIsNone(definitions.lookup_variable(99, IntType))

	def test_prefers_exact_type_over_compatible_base_type(self) -> None:
		# When two variables share a value, the one whose type exactly matches
		# the requested type should be chosen over a merely-compatible one,
		# regardless of definition order.
		definitions = DefinitionsHandler()
		definitions.set_variable('as_int', 1, IntType)    # base type, defined first
		definitions.set_variable('as_bool', 1, BoolType)  # exact match for the lookup
		found = definitions.lookup_variable(1, BoolType)
		assert found is not None
		self.assertEqual(found.name, 'as_bool')


if __name__ == '__main__':
	unittest.main()
