
from __future__ import annotations

from ...Utilities import Struct

import unittest

class Test(Struct.Struct):
	s8: int
	u8: int
	s16: int
	u16: int
	s32: int
	u32: int
	s64: int
	u64: int
	float_: float
	double: float

	char: str
	pstr: str
	str_: str

	as8: list[int]
	au8: list[int]
	as16: list[int]
	au16: list[int]
	as32: list[int]
	au32: list[int]
	as64: list[int]
	au64: list[int]
	afloat: list[float]
	adouble: list[float]
	
	_fields = (
		Struct.t_pad(),
		('s8', Struct.t_s8),
		('u8', Struct.t_u8),
		('s16', Struct.t_s16),
		('u16', Struct.t_u16),
		('s32', Struct.t_s32),
		('u32', Struct.t_u32),
		('s64', Struct.t_s64),
		('u64', Struct.t_u64),
		('float_', Struct.t_float),
		('double', Struct.t_double),
		Struct.t_pad(2),
		('char', Struct.t_char),
		('pstr', Struct.t_pstr(5)),
		('str_', Struct.t_str(5)),
		Struct.t_pad(3),
		('as8', Struct.t_as8(2)),
		('au8', Struct.t_au8(2)),
		('as16', Struct.t_as16(2)),
		('au16', Struct.t_au16(2)),
		('as32', Struct.t_as32(2)),
		('au32', Struct.t_au32(2)),
		('as64', Struct.t_as64(2)),
		('au64', Struct.t_au64(2)),
		('afloat', Struct.t_afloat(2)),
		('adouble', Struct.t_adouble(2)),
		Struct.t_pad(4),
	)

	def __eq__(self, other) -> bool:
		if not isinstance(other, Test):
			return False
		return other.s8 == self.s8 and other.u8 == self.u8 and other.s16 == self.s16 and other.u16 == self.u16 and other.s32 == self.s32 and other.u32 == self.u32 and other.s64 == self.s64 and other.u64 == self.u64 and other.float_ == self.float_ and other.double == self.double and other.char == self.char and other.pstr == self.pstr and other.str_ == self.str_ and other.as8 == self.as8 and other.au8 == self.au8 and other.as16 == self.as16 and other.au16 == self.au16 and other.as32 == self.as32 and other.au32 == self.au32 and other.as64 == self.as64 and other.au64 == self.au64 and other.afloat == self.afloat and other.adouble == self.adouble
	
	@staticmethod
	def min() -> Test:
		test = Test()
		test.s8 = -128
		test.u8 = 0
		test.s16 = -32768
		test.u16 = 0
		test.s32 = -2147483648
		test.u32 = 0
		test.s64 = -9223372036854775808
		test.u64 = 0
		test.float_ = -3.4028234663852886e+38
		test.double = -1.7976931348623157e+308
		test.char = ' '
		test.pstr = ''
		test.str_ = ''
		test.as8 = [-128, -128]
		test.au8 = [0, 0]
		test.as16 = [-32768, -32768]
		test.au16 = [0, 0]
		test.as32 = [-2147483648, -2147483648]
		test.au32 = [0, 0]
		test.as64 = [-9223372036854775808, -9223372036854775808]
		test.au64 = [0, 0]
		test.afloat = [-3.4028234663852886e+38, -3.4028234663852886e+38]
		test.adouble = [-1.7976931348623157e+308, -1.7976931348623157e+308]
		return test

	@staticmethod
	def zero() -> Test:
		test = Test()
		test.s8 = 0
		test.u8 = 0
		test.s16 = 0
		test.u16 = 0
		test.s32 = 0
		test.u32 = 0
		test.s64 = 0
		test.u64 = 0
		test.float_ = 0
		test.double = 0
		test.char = ' '
		test.pstr = ''
		test.str_ = ''
		test.as8 = [0, 0]
		test.au8 = [0, 0]
		test.as16 = [0, 0]
		test.au16 = [0, 0]
		test.as32 = [0, 0]
		test.au32 = [0, 0]
		test.as64 = [0, 0]
		test.au64 = [0, 0]
		test.afloat = [0, 0]
		test.adouble = [0, 0]
		return test

	@staticmethod
	def max() -> Test:
		test = Test()
		test.s8 = 127
		test.u8 = 255
		test.s16 = 32767
		test.u16 = 65535
		test.s32 = 2147483647
		test.u32 = 4294967295
		test.s64 = 9223372036854775807
		test.u64 = 18446744073709551615
		test.float_ = 3.4028234663852886e+38
		test.double = 1.7976931348623157e+308
		test.char = 'Z'
		test.pstr = 'PyMS'
		test.str_ = 'PyMS'
		test.as8 = [127, 127]
		test.au8 = [255, 255]
		test.as16 = [32767, 32767]
		test.au16 = [65535, 65535]
		test.as32 = [2147483647, 2147483647]
		test.au32 = [4294967295, 4294967295]
		test.as64 = [9223372036854775807, 9223372036854775807]
		test.au64 = [18446744073709551615, 18446744073709551615]
		test.afloat = [3.4028234663852886e+38, 3.4028234663852886e+38]
		test.adouble = [1.7976931348623157e+308, 1.7976931348623157e+308]
		return test

	@staticmethod
	def inc() -> Test:
		test = Test()
		test.s8 = 1
		test.u8 = 2
		test.s16 = 3
		test.u16 = 4
		test.s32 = 5
		test.u32 = 6
		test.s64 = 7
		test.u64 = 8
		test.float_ = 9.0
		test.double = 10.0
		test.char = 'Z'
		test.pstr = 'PyMS'
		test.str_ = 'PyMS!'
		test.as8 = [14, 15]
		test.au8 = [16, 17]
		test.as16 = [18, 19]
		test.au16 = [20, 21]
		test.as32 = [22, 23]
		test.au32 = [24, 25]
		test.as64 = [26, 27]
		test.au64 = [28, 29]
		test.afloat = [30.0, 31.0]
		test.adouble = [32.0, 33.0]
		return test

MIN_DATA = b'\x00\x80\x00\x00\x80\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x80\x00\x00\x00\x80\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00\x00\x00'
ZERO_DATA = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
MAX_DATA = b'\x00\x7f\xff\xff\x7f\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\x00\x00Z\x04PyMSPyMS\x00\x00\x00\x00\x7f\x7f\xff\xff\xff\x7f\xff\x7f\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x7f\xff\xff\x7f\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\x00\x00\x00\x00'
INC_DATA = b'\x00\x01\x02\x03\x00\x04\x00\x05\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10A\x00\x00\x00\x00\x00\x00$@\x00\x00Z\x04PyMSPyMS!\x00\x00\x00\x0e\x0f\x10\x11\x12\x00\x13\x00\x14\x00\x15\x00\x16\x00\x00\x00\x17\x00\x00\x00\x18\x00\x00\x00\x19\x00\x00\x00\x1a\x00\x00\x00\x00\x00\x00\x00\x1b\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0A\x00\x00\xf8A\x00\x00\x00\x00\x00\x00@@\x00\x00\x00\x00\x00\x80@@\x00\x00\x00\x00'

class Test_Struct(unittest.TestCase):
	def test_format(self) -> None:
		self.assertEqual(Test.format(), '<xbBhHlLqQfd2xc5p5s3x2b2B2h2H2l2L2q2Q2f2d4x')

	def test_size(self) -> None:
		self.assertEqual(Test.calcsize(), 147)

	def test_pack(self) -> None:
		self.assertEqual(Test.min().pack(), MIN_DATA)
		self.assertEqual(Test.zero().pack(), ZERO_DATA)
		self.assertEqual(Test.max().pack(), MAX_DATA)
		self.assertEqual(Test.inc().pack(), INC_DATA)

	def test_unpack(self) -> None:
		self.assertEqual(Test.unpack(MIN_DATA), Test.min())
