
from ...Utilities import Struct

import unittest

class Test_Type_Format(unittest.TestCase):
	def test_pad(self) -> None:
		self.assertEqual(Struct.t_pad().format, 'x')
		self.assertEqual(Struct.t_pad(1).format, 'x')
		self.assertEqual(Struct.t_pad(2).format, '2x')
		self.assertEqual(Struct.t_pad(10).format, '10x')

	def test_s8(self) -> None:
		self.assertEqual(Struct.t_s8.format, 'b')

	def test_u8(self) -> None:
		self.assertEqual(Struct.t_u8.format, 'B')

	def test_s16(self) -> None:
		self.assertEqual(Struct.t_s16.format, 'h')

	def test_u16(self) -> None:
		self.assertEqual(Struct.t_u16.format, 'H')

	def test_s32(self) -> None:
		self.assertEqual(Struct.t_s32.format, 'l')

	def test_u32(self) -> None:
		self.assertEqual(Struct.t_u32.format, 'L')

	def test_s64(self) -> None:
		self.assertEqual(Struct.t_s64.format, 'q')

	def test_u64(self) -> None:
		self.assertEqual(Struct.t_u64.format, 'Q')

	def test_float(self) -> None:
		self.assertEqual(Struct.t_float.format, 'f')

	def test_double(self) -> None:
		self.assertEqual(Struct.t_double.format, 'd')

	def test_char(self) -> None:
		self.assertEqual(Struct.t_char.format, 'c')

	def test_pstr(self) -> None:
		self.assertEqual(Struct.t_pstr(1).format, '1p')
		self.assertEqual(Struct.t_pstr(2).format, '2p')
		self.assertEqual(Struct.t_pstr(10).format, '10p')

	def test_str(self) -> None:
		self.assertEqual(Struct.t_str(1).format, '1s')
		self.assertEqual(Struct.t_str(2).format, '2s')
		self.assertEqual(Struct.t_str(10).format, '10s')

class Test_Type_Signed(unittest.TestCase):
	def test_pad(self) -> None:
		self.assertFalse(Struct.t_pad().is_signed)

	def test_s8(self) -> None:
		self.assertTrue(Struct.t_s8.is_signed)

	def test_u8(self) -> None:
		self.assertFalse(Struct.t_u8.is_signed)

	def test_s16(self) -> None:
		self.assertTrue(Struct.t_s16.is_signed)

	def test_u16(self) -> None:
		self.assertFalse(Struct.t_u16.is_signed)

	def test_s32(self) -> None:
		self.assertTrue(Struct.t_s32.is_signed)

	def test_u32(self) -> None:
		self.assertFalse(Struct.t_u32.is_signed)

	def test_s64(self) -> None:
		self.assertTrue(Struct.t_s64.is_signed)

	def test_u64(self) -> None:
		self.assertFalse(Struct.t_u64.is_signed)

	def test_float(self) -> None:
		self.assertTrue(Struct.t_float.is_signed)

	def test_double(self) -> None:
		self.assertTrue(Struct.t_double.is_signed)

	def test_char(self) -> None:
		self.assertFalse(Struct.t_char.is_signed)

	def test_pstr(self) -> None:
		self.assertFalse(Struct.t_pstr(1).is_signed)

	def test_str(self) -> None:
		self.assertFalse(Struct.t_str(1).is_signed)

class Test_Array_Format(unittest.TestCase):
	def test_as8(self) -> None:
		self.assertEqual(Struct.t_as8(2).format, '2b')
		self.assertEqual(Struct.t_as8(10).format, '10b')

	def test_au8(self) -> None:
		self.assertEqual(Struct.t_au8(2).format, '2B')
		self.assertEqual(Struct.t_au8(10).format, '10B')

	def test_as16(self) -> None:
		self.assertEqual(Struct.t_as16(2).format, '2h')
		self.assertEqual(Struct.t_as16(10).format, '10h')

	def test_au16(self) -> None:
		self.assertEqual(Struct.t_au16(2).format, '2H')
		self.assertEqual(Struct.t_au16(10).format, '10H')

	def test_as32(self) -> None:
		self.assertEqual(Struct.t_as32(2).format, '2l')
		self.assertEqual(Struct.t_as32(10).format, '10l')

	def test_au32(self) -> None:
		self.assertEqual(Struct.t_au32(2).format, '2L')
		self.assertEqual(Struct.t_au32(10).format, '10L')

	def test_as64(self) -> None:
		self.assertEqual(Struct.t_as64(2).format, '2q')
		self.assertEqual(Struct.t_as64(10).format, '10q')

	def test_au64(self) -> None:
		self.assertEqual(Struct.t_au64(2).format, '2Q')
		self.assertEqual(Struct.t_au64(10).format, '10Q')

	def test_afloat(self) -> None:
		self.assertEqual(Struct.t_afloat(2).format, '2f')
		self.assertEqual(Struct.t_afloat(10).format, '10f')

	def test_adouble(self) -> None:
		self.assertEqual(Struct.t_adouble(2).format, '2d')
		self.assertEqual(Struct.t_adouble(10).format, '10d')

class Test_Array_Signed(unittest.TestCase):
	def test_as8(self) -> None:
		self.assertTrue(Struct.t_as8(2).is_signed)

	def test_au8(self) -> None:
		self.assertFalse(Struct.t_au8(2).is_signed)

	def test_as16(self) -> None:
		self.assertTrue(Struct.t_as16(2).is_signed)

	def test_au16(self) -> None:
		self.assertFalse(Struct.t_au16(2).is_signed)

	def test_as32(self) -> None:
		self.assertTrue(Struct.t_as32(2).is_signed)

	def test_au32(self) -> None:
		self.assertFalse(Struct.t_au32(2).is_signed)

	def test_as64(self) -> None:
		self.assertTrue(Struct.t_as64(2).is_signed)

	def test_au64(self) -> None:
		self.assertFalse(Struct.t_au64(2).is_signed)

	def test_afloat(self) -> None:
		self.assertTrue(Struct.t_afloat(2).is_signed)

	def test_adouble(self) -> None:
		self.assertTrue(Struct.t_adouble(2).is_signed)
