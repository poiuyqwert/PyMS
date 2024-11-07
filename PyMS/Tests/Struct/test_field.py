
from ...Utilities import Struct

import unittest

class Test_Field_Format(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.format, '<b')

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.format, '<B')

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.format, '<h')

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.format, '<H')

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.format, '<l')

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.format, '<L')

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.format, '<q')

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.format, '<Q')

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.format, '<f')

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.format, '<d')

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.format, '<c')

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(1).format, '<1p')
		self.assertEqual(Struct.l_pstr(2).format, '<2p')
		self.assertEqual(Struct.l_pstr(10).format, '<10p')

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).format, '<1s')
		self.assertEqual(Struct.l_str(2).format, '<2s')
		self.assertEqual(Struct.l_str(10).format, '<10s')

class Test_Field_Signed(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertTrue(Struct.l_s8.is_signed)

	def test_u8(self) -> None:
		self.assertFalse(Struct.l_u8.is_signed)

	def test_s16(self) -> None:
		self.assertTrue(Struct.l_s16.is_signed)

	def test_u16(self) -> None:
		self.assertFalse(Struct.l_u16.is_signed)

	def test_s32(self) -> None:
		self.assertTrue(Struct.l_s32.is_signed)

	def test_u32(self) -> None:
		self.assertFalse(Struct.l_u32.is_signed)

	def test_s64(self) -> None:
		self.assertTrue(Struct.l_s64.is_signed)

	def test_u64(self) -> None:
		self.assertFalse(Struct.l_u64.is_signed)

	def test_float(self) -> None:
		self.assertTrue(Struct.l_float.is_signed)

	def test_double(self) -> None:
		self.assertTrue(Struct.l_double.is_signed)

	def test_char(self) -> None:
		self.assertFalse(Struct.l_char.is_signed)

	def test_pstr(self) -> None:
		self.assertFalse(Struct.l_pstr(1).is_signed)

	def test_str(self) -> None:
		self.assertFalse(Struct.l_str(1).is_signed)

class Test_Field_Size(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.size, 1)

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.size, 1)

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.size, 2)

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.size, 2)

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.size, 4)

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.size, 4)

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.size, 8)

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.size, 8)

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.size, 4)

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.size, 8)

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.size, 1)

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(1).size, 1)
		self.assertEqual(Struct.l_pstr(2).size, 2)
		self.assertEqual(Struct.l_pstr(10).size, 10)

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).size, 1)
		self.assertEqual(Struct.l_str(2).size, 2)
		self.assertEqual(Struct.l_str(10).size, 10)

class Test_Field_Min(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.min, -128)

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.min, 0)

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.min, -32768)

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.min, 0)

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.min, -2147483648)

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.min, 0)

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.min, -9223372036854775808)

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.min, 0)

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.min, -3.4028234663852886e+38)

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.min, -1.7976931348623157e+308)

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.min, 0)

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(1).min, 0)
		self.assertEqual(Struct.l_pstr(2).min, 0)
		self.assertEqual(Struct.l_pstr(10).min, 0)

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).min, 0)
		self.assertEqual(Struct.l_str(2).min, 0)
		self.assertEqual(Struct.l_str(10).min, 0)

class Test_Field_Max(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.max, 127)

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.max, 255)

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.max, 32767)

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.max, 65535)

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.max, 2147483647)

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.max, 4294967295)

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.max, 9223372036854775807)

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.max, 18446744073709551615)

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.max, 3.4028234663852886e+38)

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.max, 1.7976931348623157e+308)

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.max, 255)

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(1).max, 255)
		self.assertEqual(Struct.l_pstr(2).max, 255)
		self.assertEqual(Struct.l_pstr(10).max, 255)

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).max, 255)
		self.assertEqual(Struct.l_str(2).max, 255)
		self.assertEqual(Struct.l_str(10).max, 255)

class Test_Field_Pack(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.pack(-128), b'\x80')
		self.assertEqual(Struct.l_s8.pack(-1), b'\xFF')
		self.assertEqual(Struct.l_s8.pack(0), b'\x00')
		self.assertEqual(Struct.l_s8.pack(1), b'\x01')
		self.assertEqual(Struct.l_s8.pack(127), b'\x7F')

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.pack(0), b'\x00')
		self.assertEqual(Struct.l_u8.pack(1), b'\x01')
		self.assertEqual(Struct.l_u8.pack(255), b'\xFF')

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.pack(-32768), b'\x00\x80')
		self.assertEqual(Struct.l_s16.pack(-1), b'\xFF\xFF')
		self.assertEqual(Struct.l_s16.pack(0), b'\x00\x00')
		self.assertEqual(Struct.l_s16.pack(1), b'\x01\x00')
		self.assertEqual(Struct.l_s16.pack(32767), b'\xFF\x7F')

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.pack(0), b'\x00\x00')
		self.assertEqual(Struct.l_u16.pack(1), b'\x01\x00')
		self.assertEqual(Struct.l_u16.pack(65535), b'\xFF\xFF')

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.pack(-2147483648), b'\x00\x00\x00\x80')
		self.assertEqual(Struct.l_s32.pack(-1), b'\xFF\xFF\xFF\xFF')
		self.assertEqual(Struct.l_s32.pack(0), b'\x00\x00\x00\x00')
		self.assertEqual(Struct.l_s32.pack(1), b'\x01\x00\x00\x00')
		self.assertEqual(Struct.l_s32.pack(2147483647), b'\xFF\xFF\xFF\x7F')

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.pack(0), b'\x00\x00\x00\x00')
		self.assertEqual(Struct.l_u32.pack(1), b'\x01\x00\x00\x00')
		self.assertEqual(Struct.l_u32.pack(4294967295), b'\xFF\xFF\xFF\xFF')

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.pack(-9223372036854775808), b'\x00\x00\x00\x00\x00\x00\x00\x80')
		self.assertEqual(Struct.l_s64.pack(-1), b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')
		self.assertEqual(Struct.l_s64.pack(0), b'\x00\x00\x00\x00\x00\x00\x00\x00')
		self.assertEqual(Struct.l_s64.pack(1), b'\x01\x00\x00\x00\x00\x00\x00\x00')
		self.assertEqual(Struct.l_s64.pack(9223372036854775807), b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F')

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.pack(0), b'\x00\x00\x00\x00\x00\x00\x00\x00')
		self.assertEqual(Struct.l_u64.pack(1), b'\x01\x00\x00\x00\x00\x00\x00\x00')
		self.assertEqual(Struct.l_u64.pack(18446744073709551615), b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.pack(-3.4028234663852886e+38), b'\xFF\xFF\x7F\xFF')
		self.assertEqual(Struct.l_float.pack(-1.0), b'\x00\x00\x80\xBF')
		self.assertEqual(Struct.l_float.pack(0.0), b'\x00\x00\x00\x00')
		self.assertEqual(Struct.l_float.pack(1.0), b'\x00\x00\x80\x3F')
		self.assertEqual(Struct.l_float.pack(3.4028234663852886e+38), b'\xFF\xFF\x7F\x7F')

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.pack(-1.7976931348623157e+308), b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\xFF')
		self.assertEqual(Struct.l_double.pack(-1.0), b'\x00\x00\x00\x00\x00\x00\xF0\xBF')
		self.assertEqual(Struct.l_double.pack(0.0), b'\x00\x00\x00\x00\x00\x00\x00\x00')
		self.assertEqual(Struct.l_double.pack(1.0), b'\x00\x00\x00\x00\x00\x00\xF0\x3F')
		self.assertEqual(Struct.l_double.pack(1.7976931348623157e+308), b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\x7F')

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.pack(' '), b' ')
		self.assertEqual(Struct.l_char.pack('a'), b'a')
		self.assertEqual(Struct.l_char.pack('Z'), b'Z')

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(2).pack(' '), b'\x01 ')
		self.assertEqual(Struct.l_pstr(3).pack('a'), b'\x01a\x00')
		self.assertEqual(Struct.l_pstr(10).pack('Zed'), b'\x03Zed\x00\x00\x00\x00\x00\x00')

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).pack(' '), b' ')
		self.assertEqual(Struct.l_str(2).pack('a'), b'a\x00')
		self.assertEqual(Struct.l_str(10).pack('Zed'), b'Zed\x00\x00\x00\x00\x00\x00\x00')

class Test_Field_Unpack(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_s8.unpack(b'\x80'), -128)
		self.assertEqual(Struct.l_s8.unpack(b'\xFF'), -1)
		self.assertEqual(Struct.l_s8.unpack(b'\x00'), 0)
		self.assertEqual(Struct.l_s8.unpack(b'\x01'), 1)
		self.assertEqual(Struct.l_s8.unpack(b'\x7F'), 127)

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_u8.unpack(b'\x00'), 0)
		self.assertEqual(Struct.l_u8.unpack(b'\x01'), 1)
		self.assertEqual(Struct.l_u8.unpack(b'\xFF'), 255)

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_s16.unpack(b'\x00\x80'), -32768)
		self.assertEqual(Struct.l_s16.unpack(b'\xFF\xFF'), -1)
		self.assertEqual(Struct.l_s16.unpack(b'\x00\x00'), 0)
		self.assertEqual(Struct.l_s16.unpack(b'\x01\x00'), 1)
		self.assertEqual(Struct.l_s16.unpack(b'\xFF\x7F'), 32767)

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_u16.unpack(b'\x00\x00'), 0)
		self.assertEqual(Struct.l_u16.unpack(b'\x01\x00'), 1)
		self.assertEqual(Struct.l_u16.unpack(b'\xFF\xFF'), 65535)

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_s32.unpack(b'\x00\x00\x00\x80'), -2147483648)
		self.assertEqual(Struct.l_s32.unpack(b'\xFF\xFF\xFF\xFF'), -1)
		self.assertEqual(Struct.l_s32.unpack(b'\x00\x00\x00\x00'), 0)
		self.assertEqual(Struct.l_s32.unpack(b'\x01\x00\x00\x00'), 1)
		self.assertEqual(Struct.l_s32.unpack(b'\xFF\xFF\xFF\x7F'), 2147483647)

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_u32.unpack(b'\x00\x00\x00\x00'), 0)
		self.assertEqual(Struct.l_u32.unpack(b'\x01\x00\x00\x00'), 1)
		self.assertEqual(Struct.l_u32.unpack(b'\xFF\xFF\xFF\xFF'), 4294967295)

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_s64.unpack(b'\x00\x00\x00\x00\x00\x00\x00\x80'), -9223372036854775808)
		self.assertEqual(Struct.l_s64.unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'), -1)
		self.assertEqual(Struct.l_s64.unpack(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 0)
		self.assertEqual(Struct.l_s64.unpack(b'\x01\x00\x00\x00\x00\x00\x00\x00'), 1)
		self.assertEqual(Struct.l_s64.unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F'), 9223372036854775807)

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_u64.unpack(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 0)
		self.assertEqual(Struct.l_u64.unpack(b'\x01\x00\x00\x00\x00\x00\x00\x00'), 1)
		self.assertEqual(Struct.l_u64.unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'), 18446744073709551615)

	def test_float(self) -> None:
		self.assertEqual(Struct.l_float.unpack(b'\xFF\xFF\x7F\xFF'), -3.4028234663852886e+38)
		self.assertEqual(Struct.l_float.unpack(b'\x00\x00\x80\xBF'), -1.0)
		self.assertEqual(Struct.l_float.unpack(b'\x00\x00\x00\x00'), 0.0)
		self.assertEqual(Struct.l_float.unpack(b'\x00\x00\x80\x3F'), 1.0)
		self.assertEqual(Struct.l_float.unpack(b'\xFF\xFF\x7F\x7F'), 3.4028234663852886e+38)

	def test_double(self) -> None:
		self.assertEqual(Struct.l_double.unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\xFF'), -1.7976931348623157e+308)
		self.assertEqual(Struct.l_double.unpack(b'\x00\x00\x00\x00\x00\x00\xF0\xBF'), -1.0)
		self.assertEqual(Struct.l_double.unpack(b'\x00\x00\x00\x00\x00\x00\x00\x00'), 0.0)
		self.assertEqual(Struct.l_double.unpack(b'\x00\x00\x00\x00\x00\x00\xF0\x3F'), 1.0)
		self.assertEqual(Struct.l_double.unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\x7F'), 1.7976931348623157e+308)

	def test_char(self) -> None:
		self.assertEqual(Struct.l_char.unpack(b' '), ' ')
		self.assertEqual(Struct.l_char.unpack(b'a'), 'a')
		self.assertEqual(Struct.l_char.unpack(b'Z'), 'Z')

	def test_pstr(self) -> None:
		self.assertEqual(Struct.l_pstr(2).unpack(b'\x01 '), ' ')
		self.assertEqual(Struct.l_pstr(3).unpack(b'\x01a\x00'), 'a')
		self.assertEqual(Struct.l_pstr(10).unpack(b'\x03Zed\x00\x00\x00\x00\x00\x00'), 'Zed')

	def test_str(self) -> None:
		self.assertEqual(Struct.l_str(1).unpack(b' '), ' ')
		self.assertEqual(Struct.l_str(2).unpack(b'a\x00'), 'a')
		self.assertEqual(Struct.l_str(10).unpack(b'Zed\x00\x00\x00\x00\x00\x00\x00'), 'Zed')

class Test_ArrayField_Format(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_as8(2).format, '<2b')
		self.assertEqual(Struct.l_as8(10).format, '<10b')

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_au8(2).format, '<2B')
		self.assertEqual(Struct.l_au8(10).format, '<10B')

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_as16(2).format, '<2h')
		self.assertEqual(Struct.l_as16(10).format, '<10h')

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_au16(2).format, '<2H')
		self.assertEqual(Struct.l_au16(10).format, '<10H')

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_as32(2).format, '<2l')
		self.assertEqual(Struct.l_as32(10).format, '<10l')

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_au32(2).format, '<2L')
		self.assertEqual(Struct.l_au32(10).format, '<10L')

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_as64(2).format, '<2q')
		self.assertEqual(Struct.l_as64(10).format, '<10q')

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_au64(2).format, '<2Q')
		self.assertEqual(Struct.l_au64(10).format, '<10Q')

	def test_float(self) -> None:
		self.assertEqual(Struct.l_afloat(2).format, '<2f')
		self.assertEqual(Struct.l_afloat(10).format, '<10f')

	def test_double(self) -> None:
		self.assertEqual(Struct.l_adouble(2).format, '<2d')
		self.assertEqual(Struct.l_adouble(10).format, '<10d')

class Test_ArrayField_Signed(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertTrue(Struct.l_as8(2).is_signed)

	def test_u8(self) -> None:
		self.assertFalse(Struct.l_au8(2).is_signed)

	def test_s16(self) -> None:
		self.assertTrue(Struct.l_as16(2).is_signed)

	def test_u16(self) -> None:
		self.assertFalse(Struct.l_au16(2).is_signed)

	def test_s32(self) -> None:
		self.assertTrue(Struct.l_as32(2).is_signed)

	def test_u32(self) -> None:
		self.assertFalse(Struct.l_au32(2).is_signed)

	def test_s64(self) -> None:
		self.assertTrue(Struct.l_as64(2).is_signed)

	def test_u64(self) -> None:
		self.assertFalse(Struct.l_au64(2).is_signed)

	def test_float(self) -> None:
		self.assertTrue(Struct.l_afloat(2).is_signed)

	def test_double(self) -> None:
		self.assertTrue(Struct.l_adouble(2).is_signed)

class Test_ArrayField_Size(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_as8(2).size, 2)
		self.assertEqual(Struct.l_as8(10).size, 10)

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_au8(2).size, 2)
		self.assertEqual(Struct.l_au8(10).size, 10)

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_as16(2).size, 4)
		self.assertEqual(Struct.l_as16(10).size, 20)

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_au16(2).size, 4)
		self.assertEqual(Struct.l_au16(10).size, 20)

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_as32(2).size, 8)
		self.assertEqual(Struct.l_as32(10).size, 40)

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_au32(2).size, 8)
		self.assertEqual(Struct.l_au32(10).size, 40)

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_as64(2).size, 16)
		self.assertEqual(Struct.l_as64(10).size, 80)

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_au64(2).size, 16)
		self.assertEqual(Struct.l_au64(10).size, 80)

	def test_float(self) -> None:
		self.assertEqual(Struct.l_afloat(2).size, 8)
		self.assertEqual(Struct.l_afloat(10).size, 40)

	def test_double(self) -> None:
		self.assertEqual(Struct.l_adouble(2).size, 16)
		self.assertEqual(Struct.l_adouble(10).size, 80)

class Test_ArrayField_Pack(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_as8(5).pack((-128, -1, 0, 1, 127)), b'\x80\xFF\x00\x01\x7F')

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_au8(3).pack((0, 1, 255)), b'\x00\x01\xFF')

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_as16(5).pack((-32768, -1, 0, 1, 32767)), b'\x00\x80\xFF\xFF\x00\x00\x01\x00\xFF\x7F')

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_au16(3).pack((0, 1, 65535)), b'\x00\x00\x01\x00\xFF\xFF')

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_as32(5).pack((-2147483648, -1, 0, 1, 2147483647)), b'\x00\x00\x00\x80\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\x7F')

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_au32(3).pack((0, 1, 4294967295)), b'\x00\x00\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF')

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_as64(5).pack((-9223372036854775808, -1, 0, 1, 9223372036854775807)), b'\x00\x00\x00\x00\x00\x00\x00\x80\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F')

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_au64(3).pack((0, 1, 18446744073709551615)), b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF')

	def test_float(self) -> None:
		self.assertEqual(Struct.l_afloat(5).pack((-3.4028234663852886e+38, -1.0, 0.0, 1.0, 3.4028234663852886e+38)), b'\xFF\xFF\x7F\xFF\x00\x00\x80\xBF\x00\x00\x00\x00\x00\x00\x80\x3F\xFF\xFF\x7F\x7F')

	def test_double(self) -> None:
		self.assertEqual(Struct.l_adouble(5).pack((-1.7976931348623157e+308, -1.0, 0.0, 1.0, 1.7976931348623157e+308)), b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\xFF\x00\x00\x00\x00\x00\x00\xF0\xBF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF0\x3F\xFF\xFF\xFF\xFF\xFF\xFF\xEF\x7F')

class Test_ArrayField_Unpack(unittest.TestCase):
	def test_s8(self) -> None:
		self.assertEqual(Struct.l_as8(5).unpack(b'\x80\xFF\x00\x01\x7F'), [-128, -1, 0, 1, 127])

	def test_u8(self) -> None:
		self.assertEqual(Struct.l_au8(3).unpack(b'\x00\x01\xFF'), [0, 1, 255])

	def test_s16(self) -> None:
		self.assertEqual(Struct.l_as16(5).unpack(b'\x00\x80\xFF\xFF\x00\x00\x01\x00\xFF\x7F'), [-32768, -1, 0, 1, 32767])

	def test_u16(self) -> None:
		self.assertEqual(Struct.l_au16(3).unpack(b'\x00\x00\x01\x00\xFF\xFF'), [0, 1, 65535])

	def test_s32(self) -> None:
		self.assertEqual(Struct.l_as32(5).unpack(b'\x00\x00\x00\x80\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\x7F'), [-2147483648, -1, 0, 1, 2147483647])

	def test_u32(self) -> None:
		self.assertEqual(Struct.l_au32(3).unpack(b'\x00\x00\x00\x00\x01\x00\x00\x00\xFF\xFF\xFF\xFF'), [0, 1, 4294967295])

	def test_s64(self) -> None:
		self.assertEqual(Struct.l_as64(5).unpack(b'\x00\x00\x00\x00\x00\x00\x00\x80\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F'), [-9223372036854775808, -1, 0, 1, 9223372036854775807])

	def test_u64(self) -> None:
		self.assertEqual(Struct.l_au64(3).unpack(b'\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF'), [0, 1, 18446744073709551615])

	def test_float(self) -> None:
		self.assertEqual(Struct.l_afloat(5).unpack(b'\xFF\xFF\x7F\xFF\x00\x00\x80\xBF\x00\x00\x00\x00\x00\x00\x80\x3F\xFF\xFF\x7F\x7F'), [-3.4028234663852886e+38, -1.0, 0.0, 1.0, 3.4028234663852886e+38])

	def test_double(self) -> None:
		self.assertEqual(Struct.l_adouble(5).unpack(b'\xFF\xFF\xFF\xFF\xFF\xFF\xEF\xFF\x00\x00\x00\x00\x00\x00\xF0\xBF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xF0\x3F\xFF\xFF\xFF\xFF\xFF\xFF\xEF\x7F'), [-1.7976931348623157e+308, -1.0, 0.0, 1.0, 1.7976931348623157e+308])
