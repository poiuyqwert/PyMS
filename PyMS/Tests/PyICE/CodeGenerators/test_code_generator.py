
from ....PyICE.CodeGenerators import CodeGenerator as CG
from ....PyICE.CodeGenerators.CodeGeneratorList import CodeGeneratorTypeList
from ....PyICE.CodeGenerators.CodeGeneratorMath import CodeGeneratorTypeMath
from ....PyICE.CodeGenerators.CodeGeneratorRange import CodeGeneratorTypeRange
from ....Utilities.PyMSError import PyMSError

import unittest


class Test_registry(unittest.TestCase):
	def test_builtin_types_are_registered(self) -> None:
		# Importing the modules registers each generator type by name.
		self.assertIs(CG.lookup_type('list'), CodeGeneratorTypeList)
		self.assertIs(CG.lookup_type('math'), CodeGeneratorTypeMath)
		self.assertIs(CG.lookup_type('range'), CodeGeneratorTypeRange)

	def test_lookup_unknown_returns_none(self) -> None:
		self.assertIsNone(CG.lookup_type('does-not-exist'))


class Test_discriminate_type(unittest.TestCase):
	def test_resolves_known_type(self) -> None:
		self.assertIs(CG.discriminate_type({'type': 'range'}), CodeGeneratorTypeRange)

	def test_missing_discriminator_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CG.discriminate_type({})
		self.assertIn('object missing discriminator type', str(cm.exception))

	def test_non_string_discriminator_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CG.discriminate_type({'type': 5})
		self.assertIn('object missing discriminator type', str(cm.exception))

	def test_unknown_discriminator_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			CG.discriminate_type({'type': 'nope'})
		self.assertIn('object has invalid discriminator type `nope`', str(cm.exception))


class Test_CodeGeneratorType_base(unittest.TestCase):
	def test_to_json_includes_type_name(self) -> None:
		# Concrete subclasses get the discriminator from the base to_json.
		self.assertEqual(CodeGeneratorTypeRange(0, 1, 1).to_json()['type'], 'range')

	def test_unimplemented_methods_raise(self) -> None:
		generator = CG.CodeGeneratorType()
		self.assertRaises(NotImplementedError, CG.CodeGeneratorType.type_name)
		self.assertRaises(NotImplementedError, generator.count)
		self.assertRaises(NotImplementedError, generator.description)
		self.assertRaises(NotImplementedError, lambda: generator.value(lambda _: ''))
