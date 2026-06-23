
from ....PyICE.CodeGenerators import CodeGenerator as CG
from ....PyICE.CodeGenerators.CodeGeneratorMath import CodeGeneratorTypeMath
from ....Utilities.PyMSError import PyMSError

import unittest


class Test_CodeGeneratorTypeMath(unittest.TestCase):
	def test_type_name(self) -> None:
		self.assertEqual(CodeGeneratorTypeMath.type_name(), 'math')

	def test_count_is_infinite(self) -> None:
		self.assertIsNone(CodeGeneratorTypeMath('1+1').count())

	def test_value_evaluates_expression(self) -> None:
		self.assertEqual(CodeGeneratorTypeMath('2 * (3 + 4)').value(lambda _: '0'), '14')

	def test_value_returns_a_string(self) -> None:
		# The result must be a str so it can be substituted back into other expressions.
		self.assertIsInstance(CodeGeneratorTypeMath('1+1').value(lambda _: '0'), str)

	def test_value_substitutes_variables(self) -> None:
		self.assertEqual(CodeGeneratorTypeMath('$frameset * 17').value(lambda _: '3'), '51')

	def test_value_chains_through_another_math_result(self) -> None:
		# A math variable referencing another math variable must not break substitution.
		inner = CodeGeneratorTypeMath('2 * 3')

		def lookup(name: str) -> str:
			if name == 'a':
				return inner.value(lookup)
			return '0'

		self.assertEqual(CodeGeneratorTypeMath('$a + 1').value(lookup), '7')

	def test_value_rejects_non_math_characters(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CodeGeneratorTypeMath('__import__("os")').value(lambda _: '0')
		self.assertIn('only numbers, +, -, /, *, (, ), and whitespace allowed', str(cm.exception))

	def test_value_rejects_unsafe_substituted_content(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CodeGeneratorTypeMath('$x').value(lambda _: 'abc')
		self.assertIn("Invalid math expression 'abc'", str(cm.exception))

	def test_value_evaluation_error_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CodeGeneratorTypeMath('1/0').value(lambda _: '0')
		self.assertIn("Error evaluating math expression '1/0'", str(cm.exception))

	def test_description_is_the_expression(self) -> None:
		self.assertEqual(CodeGeneratorTypeMath('$a + 1').description(), '$a + 1')

	def test_to_json(self) -> None:
		self.assertEqual(CodeGeneratorTypeMath('$a + 1').to_json(), {'type': 'math', 'math': '$a + 1'})

	def test_from_json_round_trip(self) -> None:
		generator = CodeGeneratorTypeMath('5 * 5')
		self.assertEqual(CodeGeneratorTypeMath.from_json(generator.to_json()), generator)

	def test_registered_as_math(self) -> None:
		self.assertIs(CG.lookup_type('math'), CodeGeneratorTypeMath)
