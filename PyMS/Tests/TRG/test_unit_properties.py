
from ...FileFormats.TRG.UnitProperties import UnitProperties, FieldFlag, StateFlag

import io
import unittest


def _props_with_owner(owner: int) -> UnitProperties:
	props = UnitProperties()
	props.owner = owner
	props.fields_available_flags |= FieldFlag.owner
	return props


class Test_decompile(unittest.TestCase):
	def _decompile(self, props: UnitProperties, props_id: int = 1) -> str:
		output = io.StringIO()
		props.decompile(props_id, output)
		return output.getvalue()

	def test_header(self) -> None:
		self.assertTrue(self._decompile(UnitProperties(), 3).startswith('UnitProperties(3):'))

	def test_only_available_fields_emitted(self) -> None:
		props = _props_with_owner(5)
		props.hit_points = 99  # set but not flagged available
		text = self._decompile(props)
		self.assertIn('Owner(5)', text)
		self.assertNotIn('Health(', text)

	def test_state_flags_emitted_without_value(self) -> None:
		props = UnitProperties()
		props.state_flags |= StateFlag.cloaked
		text = self._decompile(props)
		self.assertIn('Cloaked()', text)

	def test_unset_states_not_emitted(self) -> None:
		text = self._decompile(UnitProperties())
		self.assertNotIn('Cloaked()', text)


class Test_eq(unittest.TestCase):
	def test_equal_when_available_fields_match(self) -> None:
		self.assertEqual(_props_with_owner(5), _props_with_owner(5))

	def test_not_equal_when_available_field_differs(self) -> None:
		self.assertNotEqual(_props_with_owner(5), _props_with_owner(6))

	def test_ignores_unavailable_field_values(self) -> None:
		# `hit_points` differs but isn't flagged available, so equality ignores it.
		a = _props_with_owner(5)
		b = _props_with_owner(5)
		a.hit_points = 10
		b.hit_points = 200
		self.assertEqual(a, b)

	def test_not_equal_when_field_availability_differs(self) -> None:
		plain = _props_with_owner(5)
		with_health = _props_with_owner(5)
		with_health.fields_available_flags |= FieldFlag.hit_points
		self.assertNotEqual(plain, with_health)

	def test_not_equal_when_state_flags_differ(self) -> None:
		a = UnitProperties()
		b = UnitProperties()
		b.state_flags |= StateFlag.burrowed
		self.assertNotEqual(a, b)

	def test_not_equal_to_non_properties(self) -> None:
		self.assertNotEqual(UnitProperties(), 'not properties')
