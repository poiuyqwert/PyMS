
from ....PyICE.CodeGenerators import CodeGenerator as CG
from ....PyICE.CodeGenerators.CodeGeneratorRange import CodeGeneratorTypeRange
from ....Utilities.PyMSError import PyMSError

import unittest


class Test_CodeGeneratorTypeRange(unittest.TestCase):
	def test_type_name(self) -> None:
		self.assertEqual(CodeGeneratorTypeRange.type_name(), 'range')

	def test_count_is_inclusive_of_stop(self) -> None:
		# range(0, 10+1, 3) -> 0,3,6,9
		self.assertEqual(CodeGeneratorTypeRange(0, 10, 3).count(), 4)

	def test_count_single_value(self) -> None:
		self.assertEqual(CodeGeneratorTypeRange(5, 5, 1).count(), 1)

	def test_value_returns_nth_entry_as_string(self) -> None:
		generator = CodeGeneratorTypeRange(0, 10, 3)
		self.assertEqual(generator.value(lambda _: '0'), '0')
		self.assertEqual(generator.value(lambda _: '2'), '6')

	def test_value_out_of_range_returns_empty(self) -> None:
		self.assertEqual(CodeGeneratorTypeRange(0, 10, 3).value(lambda _: '99'), '')

	def test_description(self) -> None:
		self.assertEqual(CodeGeneratorTypeRange(0, 20, 1).description(), '0 to 20, by adding 1')

	def test_to_json(self) -> None:
		self.assertEqual(CodeGeneratorTypeRange(1, 9, 2).to_json(), {'type': 'range', 'start': 1, 'stop': 9, 'step': 2})

	def test_from_json_round_trip(self) -> None:
		generator = CodeGeneratorTypeRange(2, 8, 3)
		self.assertEqual(CodeGeneratorTypeRange.from_json(generator.to_json()), generator)

	def test_from_json_rejects_zero_step(self) -> None:
		with self.assertRaises(PyMSError):
			CodeGeneratorTypeRange.from_json({'type': 'range', 'start': 0, 'stop': 5, 'step': 0})

	def test_from_json_rejects_missing_field(self) -> None:
		with self.assertRaises(PyMSError):
			CodeGeneratorTypeRange.from_json({'type': 'range', 'start': 0, 'stop': 5})

	def test_registered_as_range(self) -> None:
		self.assertIs(CG.lookup_type('range'), CodeGeneratorTypeRange)
