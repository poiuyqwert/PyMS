
from ...Utilities.UIKit.Utils import Point, Size, Rect, Geometry, GeometryAdjust, parse_scrollregion, parse_resizable

import unittest


class Test_Point(unittest.TestCase):
	def test_of_builds_from_tuple(self) -> None:
		self.assertEqual(Point.of((1, 2)), Point(1, 2))

	def test_add_point(self) -> None:
		self.assertEqual(Point(1, 2) + Point(3, 4), Point(4, 6))

	def test_add_size(self) -> None:
		self.assertEqual(Point(1, 2) + Size(3, 4), Point(4, 6))

	def test_add_invalid_raises(self) -> None:
		with self.assertRaises(ValueError):
			_ = Point(1, 2) + 5

	def test_subtract_point(self) -> None:
		self.assertEqual(Point(5, 5) - Point(1, 2), Point(4, 3))

	def test_subtract_size(self) -> None:
		self.assertEqual(Point(5, 5) - Size(1, 2), Point(4, 3))

	def test_subtract_invalid_raises(self) -> None:
		with self.assertRaises(ValueError):
			_ = Point(1, 2) - 'x'

	def test_equals_two_tuple(self) -> None:
		self.assertEqual(Point(1, 2), (1, 2))

	def test_equals_point(self) -> None:
		self.assertEqual(Point(1, 2), Point(1, 2))

	def test_not_equal_to_different_point(self) -> None:
		self.assertNotEqual(Point(1, 2), Point(9, 9))

	def test_not_equal_to_wrong_length_tuple(self) -> None:
		self.assertNotEqual(Point(1, 2), (1, 2, 3))


class Test_Size(unittest.TestCase):
	def test_of_builds_from_tuple(self) -> None:
		self.assertEqual(Size.of((3, 4)), Size(3, 4))

	def test_floordiv_by_int(self) -> None:
		self.assertEqual(Size(10, 20) // 2, Size(5, 10))

	def test_floordiv_truncates(self) -> None:
		self.assertEqual(Size(10, 20) // 3, Size(3, 6))

	def test_floordiv_non_int_raises(self) -> None:
		with self.assertRaises(ValueError):
			_ = Size(10, 20) // 'x'

	def test_center(self) -> None:
		self.assertEqual(Size(10, 20).center, Point(5, 10))

	def test_centered_in(self) -> None:
		self.assertEqual(Size(10, 20).centered_in(Size(100, 100)), Point(45, 40))

	def test_equals_two_tuple(self) -> None:
		self.assertEqual(Size(3, 4), (3, 4))

	def test_equals_size(self) -> None:
		self.assertEqual(Size(3, 4), Size(3, 4))

	def test_not_equal_to_different_size(self) -> None:
		self.assertNotEqual(Size(3, 4), Size(9, 9))


class Test_Rect(unittest.TestCase):
	def test_center(self) -> None:
		self.assertEqual(Rect(Point(10, 20), Size(100, 200)).center, Point(60, 120))

	def test_max_x(self) -> None:
		self.assertEqual(Rect(Point(10, 20), Size(100, 200)).max_x, 110)

	def test_max_y(self) -> None:
		self.assertEqual(Rect(Point(10, 20), Size(100, 200)).max_y, 220)

	def test_equals_four_tuple(self) -> None:
		self.assertEqual(Rect(Point(1, 2), Size(3, 4)), (1, 2, 3, 4))

	def test_equals_pos_size_tuple(self) -> None:
		self.assertEqual(Rect(Point(1, 2), Size(3, 4)), (Point(1, 2), Size(3, 4)))

	def test_equals_rect(self) -> None:
		self.assertEqual(Rect(Point(1, 2), Size(3, 4)), Rect(Point(1, 2), Size(3, 4)))

	def test_not_equal(self) -> None:
		self.assertNotEqual(Rect(Point(1, 2), Size(3, 4)), (1, 2, 3, 5))

	def test_clamp_shrinks_to_fit(self) -> None:
		rect = Rect(Point(10, 10), Size(200, 200))
		rect.clamp(size=Size(100, 100))
		self.assertEqual(rect.pos, Point(10, 10))
		self.assertEqual(rect.size, Size(90, 90))

	def test_clamp_repositions_negative_origin(self) -> None:
		rect = Rect(Point(-5, -5), Size(50, 50))
		rect.clamp(size=Size(100, 100))
		self.assertEqual(rect.pos, Point(0, 0))
		self.assertEqual(rect.size, Size(50, 50))

	def test_clamp_enforces_min_size(self) -> None:
		rect = Rect(Point(0, 0), Size(50, 50))
		rect.clamp(size=Size(100, 100), min_size=Size(60, 60))
		self.assertEqual(rect.size, Size(60, 60))

	def test_clamp_enforces_max_size(self) -> None:
		rect = Rect(Point(0, 0), Size(80, 80))
		rect.clamp(size=Size(100, 100), max_size=Size(70, 70))
		self.assertEqual(rect.size, Size(70, 70))

	def test_clamp_with_offset_origin(self) -> None:
		rect = Rect(Point(0, 0), Size(200, 200))
		rect.clamp(size=Size(100, 100), pos=Point(50, 50))
		self.assertEqual(rect.pos, Point(50, 50))
		self.assertEqual(rect.size, Size(100, 100))


class Test_Geometry_parse(unittest.TestCase):
	def test_basic(self) -> None:
		geometry = Geometry.parse('550x380+100+200')
		assert geometry is not None
		self.assertEqual(geometry.size, Size(550, 380))
		self.assertEqual(geometry.pos, Point(100, 200))
		self.assertFalse(geometry.maximized)

	def test_maximized(self) -> None:
		geometry = Geometry.parse('550x380+100+200^')
		assert geometry is not None
		self.assertTrue(geometry.maximized)

	def test_negative_position(self) -> None:
		geometry = Geometry.parse('550x380+-10+-20')
		assert geometry is not None
		self.assertEqual(geometry.pos, Point(-10, -20))

	def test_invalid_returns_none(self) -> None:
		self.assertIsNone(Geometry.parse('garbage'))

	def test_text_round_trips(self) -> None:
		for text in ('550x380+100+200', '550x380+-10+-20', '550x380+100+200^'):
			with self.subTest(text=text):
				geometry = Geometry.parse(text)
				assert geometry is not None
				self.assertEqual(geometry.text, text)

	def test_str_matches_text(self) -> None:
		geometry = Geometry(Point(1, 2), Size(3, 4))
		self.assertEqual(str(geometry), geometry.text)


class Test_Geometry_adjust(unittest.TestCase):
	def test_adjust_center_at_default_origin(self) -> None:
		result = Geometry(Point(0, 0), Size(50, 50)).adjust_center_at()
		self.assertEqual(result, GeometryAdjust(pos=Point(-25, -25)))

	def test_adjust_center_at_position(self) -> None:
		result = Geometry(Point(0, 0), Size(50, 50)).adjust_center_at(Point(100, 100))
		self.assertEqual(result, GeometryAdjust(pos=Point(75, 75)))

	def test_adjust_center_in_default_origin(self) -> None:
		result = Geometry(Point(0, 0), Size(50, 50)).adjust_center_in(Size(200, 200))
		self.assertEqual(result, GeometryAdjust(pos=Point(75, 75)))

	def test_adjust_center_in_with_position(self) -> None:
		result = Geometry(Point(0, 0), Size(50, 50)).adjust_center_in(Size(200, 200), Point(10, 20))
		self.assertEqual(result, GeometryAdjust(pos=Point(85, 95)))


class Test_GeometryAdjust(unittest.TestCase):
	def test_parse_position_only(self) -> None:
		self.assertEqual(GeometryAdjust.parse('+10+20'), GeometryAdjust(pos=Point(10, 20)))

	def test_parse_with_size(self) -> None:
		self.assertEqual(GeometryAdjust.parse('100x200+10+20'), GeometryAdjust(pos=Point(10, 20), size=Size(100, 200)))

	def test_parse_maximized(self) -> None:
		adjust = GeometryAdjust.parse('100x200+10+20^')
		assert adjust is not None
		self.assertTrue(adjust.maximized)

	def test_parse_invalid_returns_none(self) -> None:
		self.assertIsNone(GeometryAdjust.parse('garbage'))

	def test_is_empty_true_when_unset(self) -> None:
		self.assertTrue(GeometryAdjust().is_empty)

	def test_is_empty_false_with_pos(self) -> None:
		self.assertFalse(GeometryAdjust(pos=Point(1, 2)).is_empty)

	def test_text_position_only(self) -> None:
		self.assertEqual(GeometryAdjust(pos=Point(1, 2)).text, '+1+2')

	def test_text_size_only(self) -> None:
		self.assertEqual(GeometryAdjust(size=Size(3, 4)).text, '3x4')

	def test_text_full(self) -> None:
		self.assertEqual(GeometryAdjust(pos=Point(1, 2), size=Size(3, 4), maximized=True).text, '3x4+1+2^')

	def test_text_empty_raises(self) -> None:
		with self.assertRaises(ValueError):
			_ = GeometryAdjust().text

	def test_geometry_when_complete(self) -> None:
		self.assertEqual(
			GeometryAdjust(pos=Point(1, 2), size=Size(3, 4)).geometry,
			Geometry(Point(1, 2), Size(3, 4))
		)

	def test_geometry_none_without_size(self) -> None:
		self.assertIsNone(GeometryAdjust(pos=Point(1, 2)).geometry)

	def test_geometry_none_without_pos(self) -> None:
		self.assertIsNone(GeometryAdjust(size=Size(3, 4)).geometry)


class Test_parse_scrollregion(unittest.TestCase):
	def test_parses_four_ints(self) -> None:
		self.assertEqual(parse_scrollregion('0 0 100 200'), (0, 0, 100, 200))

	def test_invalid_returns_default(self) -> None:
		self.assertEqual(parse_scrollregion('garbage'), (0, 0, 0, 0))

	def test_invalid_returns_custom_default(self) -> None:
		self.assertEqual(parse_scrollregion('garbage', (1, 2, 3, 4)), (1, 2, 3, 4))


class Test_parse_resizable(unittest.TestCase):
	def test_tuple(self) -> None:
		self.assertEqual(parse_resizable((0, 1)), (False, True))

	def test_tuple_both_set(self) -> None:
		self.assertEqual(parse_resizable((1, 0)), (True, False))

	def test_string(self) -> None:
		self.assertEqual(parse_resizable('0 1'), (False, True))

	def test_string_both_set(self) -> None:
		self.assertEqual(parse_resizable('1 1'), (True, True))

	def test_invalid_returns_default(self) -> None:
		self.assertEqual(parse_resizable('garbage'), (False, False))

	def test_invalid_returns_custom_default(self) -> None:
		self.assertEqual(parse_resizable('garbage', (True, True)), (True, True))
