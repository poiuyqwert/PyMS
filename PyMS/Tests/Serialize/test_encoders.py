
from ...Utilities.Serialize import IntEncoder, FloatEncoder, BoolEncoder, StrEncoder, FlagEncoder, IntFlagEncoder, EnumValueEncoder, EnumNameEncoder
from ...Utilities.PyMSError import PyMSError

from enum import Enum, Flag
from collections import OrderedDict

import unittest


class Perm(Flag):
	READ = 1
	WRITE = 2
	EXEC = 4


class Mode(Enum):
	alpha = 1
	beta = 2


class Test_IntEncoder(unittest.TestCase):
	def test_encode_is_identity(self) -> None:
		self.assertEqual(IntEncoder().encode(42), 42)

	def test_decode_int(self) -> None:
		self.assertEqual(IntEncoder().decode(42), 42)

	def test_decode_numeric_string(self) -> None:
		self.assertEqual(IntEncoder().decode('007'), 7)

	def test_decode_non_numeric_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntEncoder().decode('12a')

	def test_decode_float_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntEncoder().decode(3.5)

	def test_decode_none_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntEncoder().decode(None)

	def test_decode_below_minimum_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntEncoder(min_value=0).decode(-1)

	def test_decode_at_minimum_allowed(self) -> None:
		self.assertEqual(IntEncoder(min_value=0).decode(0), 0)

	def test_decode_above_maximum_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntEncoder(max_value=10).decode(11)

	def test_decode_at_maximum_allowed(self) -> None:
		self.assertEqual(IntEncoder(max_value=10).decode(10), 10)

	def test_apply_returns_new_value(self) -> None:
		self.assertEqual(IntEncoder().apply(5, 99), 5)


class Test_FloatEncoder(unittest.TestCase):
	def test_encode_is_identity(self) -> None:
		self.assertEqual(FloatEncoder().encode(3.5), 3.5)

	def test_decode_float(self) -> None:
		self.assertEqual(FloatEncoder().decode(3.5), 3.5)

	def test_decode_int_allowed(self) -> None:
		self.assertEqual(FloatEncoder().decode(4), 4)

	def test_decode_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FloatEncoder().decode('3.5')

	def test_decode_none_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FloatEncoder().decode(None)

	def test_decode_below_minimum_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FloatEncoder(min_value=0.0).decode(-0.5)

	def test_decode_above_maximum_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FloatEncoder(max_value=1.0).decode(1.5)

	def test_decode_within_bounds_allowed(self) -> None:
		self.assertEqual(FloatEncoder(min_value=0.0, max_value=1.0).decode(0.5), 0.5)


class Test_BoolEncoder(unittest.TestCase):
	def test_encode_is_identity(self) -> None:
		self.assertEqual(BoolEncoder().encode(True), True)

	def test_parse_passthrough_bool(self) -> None:
		self.assertIs(BoolEncoder.parse(True), True)
		self.assertIs(BoolEncoder.parse(False), False)

	def test_parse_truthy_strings(self) -> None:
		for value in ('true', 'True', 'TRUE', 't', 'T', '1'):
			with self.subTest(value=value):
				self.assertIs(BoolEncoder.parse(value), True)

	def test_parse_falsy_strings(self) -> None:
		for value in ('false', 'False', 'FALSE', 'f', 'F', '0'):
			with self.subTest(value=value):
				self.assertIs(BoolEncoder.parse(value), False)

	def test_parse_numeric_zero_one(self) -> None:
		self.assertIs(BoolEncoder.parse(0), False)
		self.assertIs(BoolEncoder.parse(1), True)

	def test_parse_invalid_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			BoolEncoder.parse('maybe')

	def test_parse_invalid_number_raises(self) -> None:
		with self.assertRaises(PyMSError):
			BoolEncoder.parse(2)

	def test_decode_delegates_to_parse(self) -> None:
		self.assertIs(BoolEncoder().decode('t'), True)


class Test_StrEncoder(unittest.TestCase):
	def test_encode_is_identity(self) -> None:
		self.assertEqual(StrEncoder().encode('hello'), 'hello')

	def test_decode_string(self) -> None:
		self.assertEqual(StrEncoder().decode('hello'), 'hello')

	def test_decode_non_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			StrEncoder().decode(42)

	def test_decode_at_max_length_allowed(self) -> None:
		self.assertEqual(StrEncoder(max_length=3).decode('abc'), 'abc')

	def test_decode_over_max_length_raises(self) -> None:
		with self.assertRaises(PyMSError):
			StrEncoder(max_length=3).decode('abcd')


class Test_FlagEncoder(unittest.TestCase):
	def test_encode_reports_each_flag(self) -> None:
		result = FlagEncoder(Perm(0)).encode(Perm.READ | Perm.EXEC, None)
		self.assertEqual(result, {'READ': True, 'WRITE': False, 'EXEC': True})

	def test_encode_respects_field_filter(self) -> None:
		result = FlagEncoder(Perm(0)).encode(Perm.READ, {'READ': True, 'WRITE': True})
		self.assertEqual(result, {'READ': True, 'WRITE': False})

	def test_decode_builds_flags_map(self) -> None:
		result = FlagEncoder(Perm(0)).decode('1', 'READ', None)
		self.assertEqual(result, OrderedDict([('READ', True)]))

	def test_decode_accumulates_into_current(self) -> None:
		encoder = FlagEncoder(Perm(0))
		current = encoder.decode('1', 'READ', None)
		result = encoder.decode('0', 'WRITE', current)
		self.assertIs(result, current)
		self.assertEqual(result, OrderedDict([('READ', True), ('WRITE', False)]))

	def test_decode_invalid_flag_name_raises(self) -> None:
		with self.assertRaises(PyMSError):
			FlagEncoder(Perm(0)).decode('1', 'FLY', None)

	def test_apply_sets_and_clears_bits(self) -> None:
		result = FlagEncoder(Perm(0)).apply(OrderedDict([('READ', True), ('WRITE', False)]), Perm.WRITE)
		self.assertEqual(result, Perm.READ)

	def test_apply_only_touches_named_flags(self) -> None:
		result = FlagEncoder(Perm(0)).apply(OrderedDict([('READ', True)]), Perm.EXEC)
		self.assertEqual(result, Perm.READ | Perm.EXEC)


class Test_IntFlagEncoder(unittest.TestCase):
	FLAGS = {'a': 1, 'b': 2, 'c': 4}

	def test_encode_reports_each_flag_sorted_by_value(self) -> None:
		result = IntFlagEncoder(self.FLAGS).encode(5, None)
		assert isinstance(result, OrderedDict)
		self.assertEqual(list(result.items()), [('a', True), ('b', False), ('c', True)])

	def test_encode_respects_field_filter(self) -> None:
		result = IntFlagEncoder(self.FLAGS).encode(1, {'a': True, 'b': True})
		self.assertEqual(result, {'a': True, 'b': False})

	def test_decode_builds_flags_map(self) -> None:
		result = IntFlagEncoder(self.FLAGS).decode('1', 'a', None)
		self.assertEqual(result, OrderedDict([('a', True)]))

	def test_decode_invalid_flag_name_raises(self) -> None:
		with self.assertRaises(PyMSError):
			IntFlagEncoder(self.FLAGS).decode('1', 'z', None)

	def test_apply_sets_and_clears_bits(self) -> None:
		result = IntFlagEncoder(self.FLAGS).apply(OrderedDict([('a', True), ('c', False)]), 4)
		self.assertEqual(result, 1)

	def test_apply_ignores_unspecified_flags(self) -> None:
		# 'b' is absent from the map, so its bit must be preserved unchanged.
		result = IntFlagEncoder(self.FLAGS).apply(OrderedDict([('a', True)]), 2)
		self.assertEqual(result, 3)


class Test_EnumValueEncoder(unittest.TestCase):
	def test_encode_uses_value(self) -> None:
		self.assertEqual(EnumValueEncoder(Mode).encode(Mode.alpha), 1)

	def test_decode_by_value(self) -> None:
		self.assertEqual(EnumValueEncoder(Mode).decode(2), Mode.beta)

	def test_decode_invalid_value_raises(self) -> None:
		with self.assertRaises(PyMSError):
			EnumValueEncoder(Mode).decode(99)

	def test_apply_returns_new_value(self) -> None:
		self.assertEqual(EnumValueEncoder(Mode).apply(Mode.beta, Mode.alpha), Mode.beta)


class Test_EnumNameEncoder(unittest.TestCase):
	def test_encode_uses_name(self) -> None:
		self.assertEqual(EnumNameEncoder(Mode).encode(Mode.alpha), 'alpha')

	def test_decode_by_name(self) -> None:
		self.assertEqual(EnumNameEncoder(Mode).decode('beta'), Mode.beta)

	def test_decode_unknown_name_raises(self) -> None:
		with self.assertRaises(PyMSError):
			EnumNameEncoder(Mode).decode('gamma')

	def test_decode_non_string_raises(self) -> None:
		with self.assertRaises(PyMSError):
			EnumNameEncoder(Mode).decode(1)

	def test_apply_returns_new_value(self) -> None:
		self.assertEqual(EnumNameEncoder(Mode).apply(Mode.beta, Mode.alpha), Mode.beta)
