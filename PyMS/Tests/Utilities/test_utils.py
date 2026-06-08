
from ...Utilities.utils import nearest_multiple, named_flags, binary, flags_code, fit, fit2, float_to_str, rpad, lpad, pad, format_byte_size

import math
import unittest

from typing import Any


class Test_nearest_multiple(unittest.TestCase):
	def test_rounds_down(self) -> None:
		self.assertEqual(nearest_multiple(7, 5), 5)

	def test_rounds_up(self) -> None:
		self.assertEqual(nearest_multiple(8, 5), 10)

	def test_exact_multiple(self) -> None:
		self.assertEqual(nearest_multiple(10, 5), 10)

	def test_custom_ceil(self) -> None:
		self.assertEqual(nearest_multiple(11, 5, math.ceil), 15)

	def test_custom_floor(self) -> None:
		self.assertEqual(nearest_multiple(13, 5, math.floor), 10)


class Test_binary(unittest.TestCase):
	def test_msb_first(self) -> None:
		self.assertEqual(binary(5, 4), '0101')

	def test_zero_padded_to_count(self) -> None:
		self.assertEqual(binary(5, 8), '00000101')

	def test_zero(self) -> None:
		self.assertEqual(binary(0, 3), '000')

	def test_all_bits_set(self) -> None:
		self.assertEqual(binary(7, 3), '111')

	def test_single_bit(self) -> None:
		self.assertEqual(binary(1, 1), '1')


class Test_flags_code(unittest.TestCase):
	def test_joins_set_flags(self) -> None:
		self.assertEqual(flags_code(5, {1: 'A', 2: 'B', 4: 'C'}), 'A | C')

	def test_no_flags_returns_zero(self) -> None:
		self.assertEqual(flags_code(0, {1: 'A'}), '0')

	def test_sorted_by_flag_value(self) -> None:
		self.assertEqual(flags_code(3, {4: 'C', 1: 'A', 2: 'B'}), 'A | B')

	def test_single_flag(self) -> None:
		self.assertEqual(flags_code(2, {1: 'A', 2: 'B'}), 'B')


class Test_float_to_str(unittest.TestCase):
	def test_strips_zero_decimals(self) -> None:
		self.assertEqual(float_to_str(5.0), '5')

	def test_keeps_zero_decimals_when_disabled(self) -> None:
		self.assertEqual(float_to_str(5.0, strip_zero_decimals=False), '5.0')

	def test_keeps_nonzero_decimals(self) -> None:
		self.assertEqual(float_to_str(1.5), '1.5')

	def test_truncates_to_default_max_decimals(self) -> None:
		self.assertEqual(float_to_str(3.14159), '3.1415')

	def test_truncates_to_custom_max_decimals(self) -> None:
		self.assertEqual(float_to_str(3.14159, max_decimals=2), '3.14')

	def test_zero(self) -> None:
		self.assertEqual(float_to_str(0.0), '0')


class Test_rpad(unittest.TestCase):
	def test_pads_between_label_and_value(self) -> None:
		self.assertEqual(rpad('ab', 'X', span=5), 'ab   X')

	def test_custom_padding(self) -> None:
		self.assertEqual(rpad('ab', span=5, padding='.'), 'ab...')

	def test_default_span(self) -> None:
		self.assertEqual(rpad('ab'), 'ab' + ' ' * 18)

	def test_coerces_label_to_str(self) -> None:
		non_str_label: Any = 12
		self.assertEqual(rpad(non_str_label, span=4), '12  ')

	def test_label_longer_than_span(self) -> None:
		self.assertEqual(rpad('toolong', span=3), 'toolong')

	def test_pad_is_rpad(self) -> None:
		self.assertIs(pad, rpad)


class Test_lpad(unittest.TestCase):
	def test_left_pads(self) -> None:
		self.assertEqual(lpad('ab', span=5), '   ab')

	def test_custom_padding(self) -> None:
		self.assertEqual(lpad('ab', span=5, padding='0'), '000ab')

	def test_coerces_label_to_str(self) -> None:
		non_str_label: Any = 7
		self.assertEqual(lpad(non_str_label, span=3), '  7')


class Test_format_byte_size(unittest.TestCase):
	def test_bytes(self) -> None:
		self.assertEqual(format_byte_size(512), '512B')

	def test_kilobytes(self) -> None:
		self.assertEqual(format_byte_size(1024), '1KB')

	def test_fractional_kilobytes(self) -> None:
		self.assertEqual(format_byte_size(1536), '1.5KB')

	def test_megabytes(self) -> None:
		self.assertEqual(format_byte_size(1048576), '1MB')

	def test_gigabytes(self) -> None:
		self.assertEqual(format_byte_size(1073741824), '1GB')

	def test_caps_at_gigabytes(self) -> None:
		self.assertEqual(format_byte_size(5 * 1024 ** 3), '5GB')


class Test_named_flags(unittest.TestCase):
	def test_header_and_values(self) -> None:
		header, values = named_flags(0b101, ['A', 'B', 'C'], 3)
		self.assertEqual(header, pad('A') + pad('B') + pad('C'))
		self.assertEqual(values, pad('1') + pad('0') + pad('1'))

	def test_skip_offsets_names(self) -> None:
		header, values = named_flags(0, ['X'], 2, skip=1)
		self.assertEqual(header, pad('Unknown0') + pad('X'))
		self.assertEqual(values, pad('0') + pad('0'))

	def test_none_name_falls_back_to_unknown(self) -> None:
		header, _ = named_flags(0, [None], 1)
		self.assertEqual(header, pad('Unknown0'))

	def test_name_index_out_of_range_uses_unknown(self) -> None:
		header, _ = named_flags(0, ['A'], 2)
		self.assertEqual(header, pad('A') + pad('Unknown1'))


class Test_fit(unittest.TestCase):
	def test_single_line_fits(self) -> None:
		self.assertEqual(fit('Label: ', 'hello world'), 'Label: hello world')

	def test_wraps_to_width(self) -> None:
		self.assertEqual(fit('', 'aaa bbb ccc', width=5), 'aaa\nbbb\nccc')

	def test_continuation_indented_by_indent(self) -> None:
		self.assertEqual(fit('Lbl', 'aaa bbb', width=7, indent=3), 'Lblaaa\n   bbb')

	def test_end_appends_newline(self) -> None:
		self.assertEqual(fit('L: ', 'hi', end=True), 'L: hi\n')

	def test_blank_line_between_paragraphs(self) -> None:
		self.assertEqual(fit('', 'a\n\nb'), 'a\n\nb')


class Test_fit2(unittest.TestCase):
	def test_single_line(self) -> None:
		self.assertEqual(fit2('hello world'), 'hello world')

	def test_label_indents_continuation(self) -> None:
		self.assertEqual(fit2('one\ntwo', label='X: '), 'X: one\n   two')

	def test_wraps_to_width(self) -> None:
		self.assertEqual(fit2('aaaa bbbb cccc', width=10), 'aaaa bbbb\ncccc')

	def test_preserves_blank_lines(self) -> None:
		self.assertEqual(fit2('a\n\nb'), 'a\n\nb')
