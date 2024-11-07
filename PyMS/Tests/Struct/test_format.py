
from ...Utilities import Struct

import unittest

class Test_Format_Format(unittest.TestCase):
	def test_pad(self) -> None:
		self.assertEqual(Struct.Format.pad.value, 'x')

	def test_s8(self) -> None:
		self.assertEqual(Struct.Format.s8.value, 'b')

	def test_u8(self) -> None:
		self.assertEqual(Struct.Format.u8.value, 'B')

	def test_s16(self) -> None:
		self.assertEqual(Struct.Format.s16.value, 'h')

	def test_u16(self) -> None:
		self.assertEqual(Struct.Format.u16.value, 'H')

	def test_s32(self) -> None:
		self.assertEqual(Struct.Format.s32.value, 'l')

	def test_u32(self) -> None:
		self.assertEqual(Struct.Format.u32.value, 'L')

	def test_s64(self) -> None:
		self.assertEqual(Struct.Format.s64.value, 'q')

	def test_u64(self) -> None:
		self.assertEqual(Struct.Format.u64.value, 'Q')

	def test_float(self) -> None:
		self.assertEqual(Struct.Format.float.value, 'f')

	def test_double(self) -> None:
		self.assertEqual(Struct.Format.double.value, 'd')

	def test_char(self) -> None:
		self.assertEqual(Struct.Format.char.value, 'c')

	def test_pstr(self) -> None:
		self.assertEqual(Struct.Format.pstr.value, 'p')

	def test_str(self) -> None:
		self.assertEqual(Struct.Format.str.value, 's')

class Test_Format_Signed(unittest.TestCase):
	def test_pad(self) -> None:
		self.assertFalse(Struct.Format.pad.is_signed)

	def test_s8(self) -> None:
		self.assertTrue(Struct.Format.s8.is_signed)

	def test_u8(self) -> None:
		self.assertFalse(Struct.Format.u8.is_signed)

	def test_s16(self) -> None:
		self.assertTrue(Struct.Format.s16.is_signed)

	def test_u16(self) -> None:
		self.assertFalse(Struct.Format.u16.is_signed)

	def test_s32(self) -> None:
		self.assertTrue(Struct.Format.s32.is_signed)

	def test_u32(self) -> None:
		self.assertFalse(Struct.Format.u32.is_signed)

	def test_s64(self) -> None:
		self.assertTrue(Struct.Format.s64.is_signed)

	def test_u64(self) -> None:
		self.assertFalse(Struct.Format.u64.is_signed)

	def test_float(self) -> None:
		self.assertTrue(Struct.Format.float.is_signed)

	def test_double(self) -> None:
		self.assertTrue(Struct.Format.double.is_signed)

	def test_char(self) -> None:
		self.assertFalse(Struct.Format.char.is_signed)

	def test_pstr(self) -> None:
		self.assertFalse(Struct.Format.pstr.is_signed)

	def test_str(self) -> None:
		self.assertFalse(Struct.Format.str.is_signed)
