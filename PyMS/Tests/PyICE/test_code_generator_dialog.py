
from ...PyICE.CodeGeneratorDialog import unique_variable_name

import unittest


class Test_unique_variable_name(unittest.TestCase):
	def test_unused_name_is_returned_unchanged(self) -> None:
		self.assertEqual(unique_variable_name('range', set()), 'range')
		self.assertEqual(unique_variable_name('range', {'math', 'list'}), 'range')

	def test_first_collision_appends_2(self) -> None:
		self.assertEqual(unique_variable_name('range', {'range'}), 'range2')

	def test_generated_name_is_unique_with_multiple_collisions(self) -> None:
		self.assertEqual(unique_variable_name('range', {'range', 'range2'}), 'range3')
		self.assertEqual(unique_variable_name('range', {'range', 'range2', 'range3'}), 'range4')

	def test_gap_in_numbered_names_is_used(self) -> None:
		self.assertEqual(unique_variable_name('range', {'range', 'range3'}), 'range2')

	def test_reserved_name_is_never_returned(self) -> None:
		self.assertEqual(unique_variable_name('n', set()), 'n2')

	def test_reserved_name_collisions_generate_well_formed_names(self) -> None:
		self.assertEqual(unique_variable_name('n', {'n2'}), 'n3')
		self.assertEqual(unique_variable_name('n', {'n2', 'n3'}), 'n4')
