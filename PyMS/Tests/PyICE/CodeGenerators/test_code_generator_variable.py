
from ....PyICE.CodeGenerators.CodeGeneratorVariable import CodeGeneratorVariable
from ....PyICE.CodeGenerators.CodeGeneratorRange import CodeGeneratorTypeRange
from ....PyICE.CodeGenerators.CodeGeneratorMath import CodeGeneratorTypeMath
from ....Utilities.PyMSError import PyMSError

import unittest


class Test_CodeGeneratorVariable(unittest.TestCase):
	def test_to_json_embeds_generator(self) -> None:
		variable = CodeGeneratorVariable('frame', CodeGeneratorTypeRange(0, 10, 1))
		self.assertEqual(variable.to_json(), {
			'name': 'frame',
			'generator': {'type': 'range', 'start': 0, 'stop': 10, 'step': 1},
		})

	def test_from_json_discriminates_generator(self) -> None:
		variable = CodeGeneratorVariable.from_json({
			'name': 'frame',
			'generator': {'type': 'math', 'math': '$x * 2'},
		})
		self.assertEqual(variable.name, 'frame')
		self.assertIsInstance(variable.generator, CodeGeneratorTypeMath)

	def test_round_trip(self) -> None:
		variable = CodeGeneratorVariable('offset', CodeGeneratorTypeRange(0, 5, 1))
		restored = CodeGeneratorVariable.from_json(variable.to_json())
		self.assertEqual(restored, variable)

	def test_from_json_invalid_generator_type_raises(self) -> None:
		with self.assertRaises(PyMSError):
			CodeGeneratorVariable.from_json({
				'name': 'frame',
				'generator': {'type': 'not-a-real-type'},
			})

	def test_from_json_missing_name_raises(self) -> None:
		with self.assertRaises(PyMSError):
			CodeGeneratorVariable.from_json({'generator': {'type': 'range', 'start': 0, 'stop': 1, 'step': 1}})
