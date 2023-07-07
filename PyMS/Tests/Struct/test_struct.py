
from __future__ import annotations

from ...Utilities import Struct

import unittest

class Sub(Struct.Struct):
	u8: int
	s64: int
	double: float

	_fields = (
		('u8', Struct.t_u8),
		('s64', Struct.t_s64),
		('double', Struct.t_double)
	)

	def __eq__(self, other) -> bool:
		if not isinstance(other, Sub):
			return False
		if other.u8 != self.u8:
			return False
		if other.s64 != self.s64:
			return False
		if other.double != self.double:
			return False
		return True

	@staticmethod
	def min() -> Sub:
		sub = Sub()
		sub.u8 = 0
		sub.s64 = -9223372036854775808
		sub.double = -1.7976931348623157e+308
		return sub

	@staticmethod
	def zero() -> Sub:
		sub = Sub()
		sub.u8 = 0
		sub.s64 = 0
		sub.double = 0.0
		return sub

	@staticmethod
	def max() -> Sub:
		sub = Sub()
		sub.u8 = 255
		sub.s64 = 9223372036854775807
		sub.double = 1.7976931348623157e+308
		return sub

	@staticmethod
	def inc(start: int) -> Sub:
		sub = Sub()
		sub.u8 = start
		sub.s64 = start+1
		sub.double = start+2
		return sub

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

	sub: Sub
	asub: list[Sub]

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

	mix: list[int]
	
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
		('sub', Sub),
		('asub', Struct.StructArray(Sub, 2)),
		Struct.t_pad(4),
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
		Struct.t_pad(5),
		('mix', Struct.MixedInts((Struct.t_u8, Struct.t_u16, Struct.t_pad(2), Struct.t_u32, Struct.t_u64)))
	)

	def __eq__(self, other) -> bool:
		if not isinstance(other, Test):
			return False
		if other.s8 != self.s8:
			return False
		if other.u8 != self.u8:
			return False
		if other.s16 != self.s16:
			return False
		if other.u16 != self.u16:
			return False
		if other.s32 != self.s32:
			return False
		if other.u32 != self.u32:
			return False
		if other.s64 != self.s64:
			return False
		if other.u64 != self.u64:
			return False
		if other.float_ != self.float_:
			return False
		if other.double != self.double:
			return False
		if other.char != self.char:
			return False
		if other.pstr != self.pstr:
			return False
		if other.str_ != self.str_:
			return False
		if other.sub != self.sub:
			return False
		if other.asub != self.asub:
			return False
		if other.as8 != self.as8:
			return False
		if other.au8 != self.au8:
			return False
		if other.as16 != self.as16:
			return False
		if other.au16 != self.au16:
			return False
		if other.as32 != self.as32:
			return False
		if other.au32 != self.au32:
			return False
		if other.as64 != self.as64:
			return False
		if other.au64 != self.au64:
			return False
		if other.afloat != self.afloat:
			return False
		if other.adouble != self.adouble:
			return False
		if other.mix != self.mix:
			return False
		return True
	
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
		test.sub = Sub.min()
		test.asub = [Sub.min(), Sub.min()]
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
		test.mix = [0, 0, 0, 0]
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
		test.float_ = 0.0
		test.double = 0.0
		test.char = ' '
		test.pstr = ''
		test.str_ = ''
		test.sub = Sub.zero()
		test.asub = [Sub.zero(), Sub.zero()]
		test.as8 = [0, 0]
		test.au8 = [0, 0]
		test.as16 = [0, 0]
		test.au16 = [0, 0]
		test.as32 = [0, 0]
		test.au32 = [0, 0]
		test.as64 = [0, 0]
		test.au64 = [0, 0]
		test.afloat = [0.0, 0.0]
		test.adouble = [0.0, 0.0]
		test.mix = [0, 0, 0, 0]
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
		test.sub = Sub.max()
		test.asub = [Sub.max(), Sub.max()]
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
		test.mix = [255, 65535, 4294967295, 18446744073709551615]
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
		test.sub = Sub.inc(11)
		test.asub = [Sub.inc(14), Sub.inc(17)]
		test.sub.u8 = 20
		test.sub.s64 = 21
		test.sub.double = 22.0
		test.as8 = [23, 24]
		test.au8 = [25, 26]
		test.as16 = [27, 28]
		test.au16 = [29, 30]
		test.as32 = [31, 32]
		test.au32 = [33, 34]
		test.as64 = [35, 36]
		test.au64 = [37, 38]
		test.afloat = [39.0, 40.0]
		test.adouble = [41.0, 42.0]
		test.mix = [43, 44, 45, 46]
		return test

MIN_DATA = b'\x00\x80\x00\x00\x80\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00\x00\x00\x00\x00\x00\x00\x80\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00\x00\x00\x00\x00\x00\x00\x80\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00\x00\x00\x80\x80\x00\x00\x00\x80\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xef\xff\xff\xff\xff\xff\xff\xff\xef\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
ZERO_DATA = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
MAX_DATA = b'\x00\x7f\xff\xff\x7f\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\x00\x00Z\x04PyMSPyMS\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\x00\x00\x00\x00\x7f\x7f\xff\xff\xff\x7f\xff\x7f\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\x7f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x7f\xff\xff\x7f\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\xff\xff\xff\xff\xff\xff\xef\x7f\x00\x00\x00\x00\x00\xff\xff\xff\x00\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
INC_DATA = b'\x00\x01\x02\x03\x00\x04\x00\x05\x00\x00\x00\x06\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10A\x00\x00\x00\x00\x00\x00$@\x00\x00Z\x04PyMSPyMS!\x00\x00\x00\x14\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x006@\x0e\x0f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000@\x11\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x003@\x00\x00\x00\x00\x17\x18\x19\x1a\x1b\x00\x1c\x00\x1d\x00\x1e\x00\x1f\x00\x00\x00 \x00\x00\x00!\x00\x00\x00"\x00\x00\x00#\x00\x00\x00\x00\x00\x00\x00$\x00\x00\x00\x00\x00\x00\x00%\x00\x00\x00\x00\x00\x00\x00&\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1cB\x00\x00 B\x00\x00\x00\x00\x00\x80D@\x00\x00\x00\x00\x00\x00E@\x00\x00\x00\x00\x00+,\x00\x00\x00-\x00\x00\x00.\x00\x00\x00\x00\x00\x00\x00'

class Test_Struct(unittest.TestCase):
	def test_format(self) -> None:
		self.assertEqual(Test.format(), ('<xbBhHlLqQfd2xc5p5s3x', Sub, Struct.StructArray(Sub, 2), '<4x2b2B2h2H2l2L2q2Q2f2d5x', Struct.MixedInts((Struct.t_u8, Struct.t_u16, Struct.t_pad(2), Struct.t_u32, Struct.t_u64))))

	def test_size(self) -> None:
		self.assertEqual(Test.calcsize(), 220)

	def test_pack(self) -> None:
		self.assertEqual(Test.min().pack(), MIN_DATA)
		self.assertEqual(Test.zero().pack(), ZERO_DATA)
		self.assertEqual(Test.max().pack(), MAX_DATA)
		self.assertEqual(Test.inc().pack(), INC_DATA)

	def test_unpack(self) -> None:
		self.assertEqual(Test.unpack(MIN_DATA), Test.min())
		self.assertEqual(Test.unpack(ZERO_DATA), Test.zero())
		self.assertEqual(Test.unpack(MAX_DATA), Test.max())
		self.assertEqual(Test.unpack(INC_DATA), Test.inc())
