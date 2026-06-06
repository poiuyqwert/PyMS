
from __future__ import annotations

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import struct

import unittest


class Pair(Struct.Struct):
	a: int
	b: int

	_fields = (
		('a', Struct.t_u8),
		('b', Struct.t_u16),
	)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Pair):
			return NotImplemented
		return other.a == self.a and other.b == self.b


def make_pair(a: int, b: int) -> Pair:
	pair = Pair()
	pair.a = a
	pair.b = b
	return pair


class Test_init(unittest.TestCase):
	def test_default_address_is_zero(self) -> None:
		self.assertEqual(BytesScanner(b'abc').address, 0)

	def test_custom_address(self) -> None:
		self.assertEqual(BytesScanner(b'abc', 2).address, 2)

	def test_stores_data(self) -> None:
		self.assertEqual(BytesScanner(b'abc').data, b'abc')


class Test_matches(unittest.TestCase):
	def test_matching_prefix_consumes_by_default(self) -> None:
		scanner = BytesScanner(b'PREfix')
		self.assertTrue(scanner.matches(b'PRE'))
		self.assertEqual(scanner.address, 3)

	def test_consume_false_leaves_address(self) -> None:
		scanner = BytesScanner(b'PREfix')
		self.assertTrue(scanner.matches(b'PRE', consume=False))
		self.assertEqual(scanner.address, 0)

	def test_non_matching_data_returns_false(self) -> None:
		scanner = BytesScanner(b'PREfix')
		self.assertFalse(scanner.matches(b'XYZ'))

	def test_non_matching_data_does_not_consume(self) -> None:
		scanner = BytesScanner(b'PREfix')
		scanner.matches(b'XYZ')
		self.assertEqual(scanner.address, 0)

	def test_matches_at_non_zero_address(self) -> None:
		scanner = BytesScanner(b'xxPRE', 2)
		self.assertTrue(scanner.matches(b'PRE'))
		self.assertEqual(scanner.address, 5)

	def test_prefix_present_but_not_at_address_returns_false(self) -> None:
		scanner = BytesScanner(b'PREfix', 1)
		self.assertFalse(scanner.matches(b'PRE'))

	def test_empty_pattern_matches_without_advancing(self) -> None:
		scanner = BytesScanner(b'abc')
		self.assertTrue(scanner.matches(b''))
		self.assertEqual(scanner.address, 0)


class Test_skip(unittest.TestCase):
	def test_advances_by_size(self) -> None:
		scanner = BytesScanner(b'abcdef')
		scanner.skip(2)
		self.assertEqual(scanner.address, 2)

	def test_skip_is_cumulative(self) -> None:
		scanner = BytesScanner(b'abcdef')
		scanner.skip(2)
		scanner.skip(3)
		self.assertEqual(scanner.address, 5)


class Test_can_scan(unittest.TestCase):
	def test_format_string_enough_bytes(self) -> None:
		self.assertTrue(BytesScanner(b'\x01\x00').can_scan('<H'))

	def test_format_string_not_enough_bytes(self) -> None:
		self.assertFalse(BytesScanner(b'\x01').can_scan('<H'))

	def test_struct_object(self) -> None:
		self.assertTrue(BytesScanner(b'\x01\x00').can_scan(struct.Struct('<H')))
		self.assertFalse(BytesScanner(b'\x01').can_scan(struct.Struct('<H')))

	def test_field(self) -> None:
		self.assertTrue(BytesScanner(b'\x01\x00').can_scan(Struct.l_u16))
		self.assertFalse(BytesScanner(b'\x01').can_scan(Struct.l_u16))

	def test_struct_subclass(self) -> None:
		self.assertTrue(BytesScanner(b'\x01\x02\x00').can_scan(Pair))
		self.assertFalse(BytesScanner(b'\x01\x02').can_scan(Pair))

	def test_does_not_advance(self) -> None:
		scanner = BytesScanner(b'\x01\x00')
		scanner.can_scan('<H')
		self.assertEqual(scanner.address, 0)

	def test_respects_current_address(self) -> None:
		scanner = BytesScanner(b'\x01\x00\x02', 2)
		self.assertFalse(scanner.can_scan('<H'))


class Test_peek(unittest.TestCase):
	def test_format_string_returns_tuple(self) -> None:
		self.assertEqual(BytesScanner(b'\x01\x00').peek('<H'), (1,))

	def test_struct_object_returns_tuple(self) -> None:
		self.assertEqual(BytesScanner(b'\x01\x00').peek(struct.Struct('<H')), (1,))

	def test_int_field_returns_int(self) -> None:
		self.assertEqual(BytesScanner(b'\x05').peek(Struct.l_u8), 5)

	def test_string_field_returns_str(self) -> None:
		self.assertEqual(BytesScanner(b'hi\x00').peek(Struct.l_str(3)), 'hi')

	def test_array_field_returns_list(self) -> None:
		self.assertEqual(BytesScanner(b'\x01\x02\x03').peek(Struct.l_au8(3)), [1, 2, 3])

	def test_struct_subclass_returns_instance(self) -> None:
		self.assertEqual(BytesScanner(b'\x01\x02\x00').peek(Pair), make_pair(1, 2))

	def test_does_not_advance(self) -> None:
		scanner = BytesScanner(b'\x01\x00')
		scanner.peek('<H')
		self.assertEqual(scanner.address, 0)

	def test_peek_twice_returns_same(self) -> None:
		scanner = BytesScanner(b'\x01\x00')
		self.assertEqual(scanner.peek('<H'), scanner.peek('<H'))

	def test_respects_current_address(self) -> None:
		self.assertEqual(BytesScanner(b'\x09\x05', 1).peek(Struct.l_u8), 5)


class Test_scan(unittest.TestCase):
	def test_format_string_advances(self) -> None:
		scanner = BytesScanner(b'\x01\x00rest')
		self.assertEqual(scanner.scan('<H'), (1,))
		self.assertEqual(scanner.address, 2)

	def test_struct_object_advances(self) -> None:
		scanner = BytesScanner(b'\x01\x00')
		self.assertEqual(scanner.scan(struct.Struct('<H')), (1,))
		self.assertEqual(scanner.address, 2)

	def test_int_field_advances(self) -> None:
		scanner = BytesScanner(b'\x05\x06')
		self.assertEqual(scanner.scan(Struct.l_u8), 5)
		self.assertEqual(scanner.address, 1)

	def test_struct_subclass_advances(self) -> None:
		scanner = BytesScanner(b'\x01\x02\x00')
		self.assertEqual(scanner.scan(Pair), make_pair(1, 2))
		self.assertEqual(scanner.address, 3)

	def test_sequential_scans(self) -> None:
		scanner = BytesScanner(b'\x05\x01\x00')
		self.assertEqual(scanner.scan(Struct.l_u8), 5)
		self.assertEqual(scanner.scan(Struct.l_u16), 1)
		self.assertTrue(scanner.at_end())


class Test_can_scan_bytes(unittest.TestCase):
	def test_enough_bytes(self) -> None:
		self.assertTrue(BytesScanner(b'abc').can_scan_bytes(3))

	def test_not_enough_bytes(self) -> None:
		self.assertFalse(BytesScanner(b'abc').can_scan_bytes(4))

	def test_respects_current_address(self) -> None:
		self.assertFalse(BytesScanner(b'abc', 1).can_scan_bytes(3))


class Test_peek_bytes(unittest.TestCase):
	def test_returns_slice(self) -> None:
		self.assertEqual(BytesScanner(b'abcdef').peek_bytes(3), b'abc')

	def test_does_not_advance(self) -> None:
		scanner = BytesScanner(b'abcdef')
		scanner.peek_bytes(3)
		self.assertEqual(scanner.address, 0)

	def test_respects_current_address(self) -> None:
		self.assertEqual(BytesScanner(b'abcdef', 2).peek_bytes(2), b'cd')

	def test_beyond_end_returns_truncated(self) -> None:
		self.assertEqual(BytesScanner(b'abc').peek_bytes(10), b'abc')


class Test_scan_bytes(unittest.TestCase):
	def test_returns_slice_and_advances(self) -> None:
		scanner = BytesScanner(b'abcdef')
		self.assertEqual(scanner.scan_bytes(3), b'abc')
		self.assertEqual(scanner.address, 3)

	def test_sequential(self) -> None:
		scanner = BytesScanner(b'abcdef')
		self.assertEqual(scanner.scan_bytes(2), b'ab')
		self.assertEqual(scanner.scan_bytes(2), b'cd')


class Test_scan_cstr(unittest.TestCase):
	def test_reads_until_terminator_including_null(self) -> None:
		scanner = BytesScanner(b'abc\x00rest')
		self.assertEqual(scanner.scan_cstr(), 'abc\x00')

	def test_advances_past_terminator(self) -> None:
		scanner = BytesScanner(b'abc\x00rest')
		scanner.scan_cstr()
		self.assertEqual(scanner.address, 4)

	def test_empty_string_is_just_terminator(self) -> None:
		scanner = BytesScanner(b'\x00rest')
		self.assertEqual(scanner.scan_cstr(), '\x00')
		self.assertEqual(scanner.address, 1)

	def test_sequential_strings(self) -> None:
		scanner = BytesScanner(b'a\x00b\x00')
		self.assertEqual(scanner.scan_cstr(), 'a\x00')
		self.assertEqual(scanner.scan_cstr(), 'b\x00')

	def test_respects_current_address(self) -> None:
		self.assertEqual(BytesScanner(b'xx\x00', 2).scan_cstr(), '\x00')

	def test_missing_terminator_raises(self) -> None:
		with self.assertRaises(PyMSError):
			BytesScanner(b'abc').scan_cstr()

	def test_custom_encoding(self) -> None:
		scanner = BytesScanner('caf\xe9\x00'.encode('latin-1'))
		self.assertEqual(scanner.scan_cstr('latin-1'), 'caf\xe9\x00')


class Test_clone(unittest.TestCase):
	def test_copies_current_address(self) -> None:
		scanner = BytesScanner(b'abcdef', 2)
		self.assertEqual(scanner.clone().address, 2)

	def test_override_address(self) -> None:
		scanner = BytesScanner(b'abcdef', 2)
		self.assertEqual(scanner.clone(4).address, 4)

	def test_shares_data(self) -> None:
		scanner = BytesScanner(b'abcdef')
		self.assertEqual(scanner.clone().data, b'abcdef')

	def test_clone_is_independent(self) -> None:
		scanner = BytesScanner(b'abcdef')
		clone = scanner.clone()
		clone.skip(3)
		self.assertEqual(scanner.address, 0)
		self.assertEqual(clone.address, 3)


class Test_at_end(unittest.TestCase):
	def test_true_at_end(self) -> None:
		self.assertTrue(BytesScanner(b'abc', 3).at_end())

	def test_false_before_end(self) -> None:
		self.assertFalse(BytesScanner(b'abc', 2).at_end())

	def test_true_for_empty_data(self) -> None:
		self.assertTrue(BytesScanner(b'').at_end())


class Test_is_offset_valid(unittest.TestCase):
	def test_valid_offset(self) -> None:
		self.assertTrue(BytesScanner(b'abc').is_offset_valid(0))
		self.assertTrue(BytesScanner(b'abc').is_offset_valid(2))

	def test_offset_at_length_is_invalid(self) -> None:
		self.assertFalse(BytesScanner(b'abc').is_offset_valid(3))

	def test_negative_offset_is_invalid(self) -> None:
		self.assertFalse(BytesScanner(b'abc').is_offset_valid(-1))


class Test_jump_to(unittest.TestCase):
	def test_sets_address(self) -> None:
		scanner = BytesScanner(b'abcdef')
		scanner.jump_to(4)
		self.assertEqual(scanner.address, 4)


class Test_remaining_len(unittest.TestCase):
	def test_full_at_start(self) -> None:
		self.assertEqual(BytesScanner(b'abcdef').remaining_len(), 6)

	def test_decreases_after_scan(self) -> None:
		scanner = BytesScanner(b'abcdef')
		scanner.scan_bytes(2)
		self.assertEqual(scanner.remaining_len(), 4)

	def test_zero_at_end(self) -> None:
		self.assertEqual(BytesScanner(b'abcdef', 6).remaining_len(), 0)
