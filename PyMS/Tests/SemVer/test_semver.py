
from ...Utilities.SemVer import SemVer

import unittest


class Test_init(unittest.TestCase):
	def test_parses_components(self) -> None:
		version = SemVer('1.2.3')
		self.assertEqual((version.major, version.minor, version.patch), (1, 2, 3))

	def test_multi_digit_components(self) -> None:
		version = SemVer('10.20.30')
		self.assertEqual((version.major, version.minor, version.patch), (10, 20, 30))

	def test_meta_is_none_by_default(self) -> None:
		self.assertIsNone(SemVer('1.2.3').meta)

	def test_parses_meta(self) -> None:
		version = SemVer('1.2.3-beta')
		self.assertEqual((version.major, version.minor, version.patch), (1, 2, 3))
		self.assertEqual(version.meta, 'beta')

	def test_meta_keeps_trailing_dashes(self) -> None:
		version = SemVer('1.2.3-beta-2')
		self.assertEqual((version.major, version.minor, version.patch), (1, 2, 3))
		self.assertEqual(version.meta, 'beta-2')

	def test_too_few_components_raises(self) -> None:
		with self.assertRaises(ValueError):
			SemVer('1.2')

	def test_too_many_components_raises(self) -> None:
		with self.assertRaises(ValueError):
			SemVer('1.2.3.4')

	def test_non_integer_component_raises(self) -> None:
		with self.assertRaises(ValueError):
			SemVer('1.2.x')


class Test_lt(unittest.TestCase):
	def test_less_by_major(self) -> None:
		self.assertTrue(SemVer('1.9.9') < SemVer('2.0.0'))

	def test_less_by_minor(self) -> None:
		self.assertTrue(SemVer('1.1.9') < SemVer('1.2.0'))

	def test_less_by_patch(self) -> None:
		self.assertTrue(SemVer('1.1.1') < SemVer('1.1.2'))

	def test_equal_is_not_less(self) -> None:
		self.assertFalse(SemVer('1.2.3') < SemVer('1.2.3'))

	def test_greater_is_not_less(self) -> None:
		self.assertFalse(SemVer('2.0.0') < SemVer('1.0.0'))

	def test_non_semver_is_not_less(self) -> None:
		self.assertFalse(SemVer('1.0.0') < 'not a version')


class Test_gt(unittest.TestCase):
	def test_greater_by_major(self) -> None:
		self.assertTrue(SemVer('2.0.0') > SemVer('1.9.9'))

	def test_greater_by_minor(self) -> None:
		self.assertTrue(SemVer('1.2.0') > SemVer('1.1.9'))

	def test_greater_by_patch(self) -> None:
		self.assertTrue(SemVer('1.1.2') > SemVer('1.1.1'))

	def test_equal_is_not_greater(self) -> None:
		self.assertFalse(SemVer('1.2.3') > SemVer('1.2.3'))

	def test_less_is_not_greater(self) -> None:
		self.assertFalse(SemVer('1.0.0') > SemVer('2.0.0'))

	def test_non_semver_is_not_greater(self) -> None:
		self.assertFalse(SemVer('1.0.0') > 'not a version')


class Test_eq(unittest.TestCase):
	def test_equal_components(self) -> None:
		self.assertEqual(SemVer('1.2.3'), SemVer('1.2.3'))

	def test_ignores_meta(self) -> None:
		self.assertEqual(SemVer('1.2.3-alpha'), SemVer('1.2.3-beta'))
		self.assertEqual(SemVer('1.2.3-alpha'), SemVer('1.2.3'))

	def test_different_major_not_equal(self) -> None:
		self.assertNotEqual(SemVer('1.2.3'), SemVer('2.2.3'))

	def test_different_minor_not_equal(self) -> None:
		self.assertNotEqual(SemVer('1.2.3'), SemVer('1.9.3'))

	def test_different_patch_not_equal(self) -> None:
		self.assertNotEqual(SemVer('1.2.3'), SemVer('1.2.9'))

	def test_not_equal_to_non_semver(self) -> None:
		self.assertNotEqual(SemVer('1.2.3'), '1.2.3')


class Test_ge(unittest.TestCase):
	def test_greater_is_ge(self) -> None:
		self.assertTrue(SemVer('1.0.1') >= SemVer('1.0.0'))

	def test_equal_is_ge(self) -> None:
		self.assertTrue(SemVer('1.0.0') >= SemVer('1.0.0'))

	def test_less_is_not_ge(self) -> None:
		self.assertFalse(SemVer('1.0.0') >= SemVer('1.0.1'))

	def test_comparison_with_non_semver_raises(self) -> None:
		with self.assertRaises(TypeError):
			_ = SemVer('1.0.0') >= 5  # type: ignore[operator]


class Test_repr(unittest.TestCase):
	def test_without_meta(self) -> None:
		self.assertEqual(repr(SemVer('1.2.3')), '<SemVer 1.2.3>')

	def test_with_meta(self) -> None:
		self.assertEqual(repr(SemVer('1.2.3-beta')), '<SemVer 1.2.3-beta>')
