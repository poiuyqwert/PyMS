
from ...FileFormats.Tileset.Serialize import GroupTypeEncoder, MiniFlagsMultiEncoder
from ...Utilities.PyMSError import PyMSError

import unittest

FLAG = 0x04


class Test_GroupTypeEncoder(unittest.TestCase):
	def test_accepts_non_doodad_types(self) -> None:
		self.assertEqual(GroupTypeEncoder().decode(0), 0)
		self.assertEqual(GroupTypeEncoder().decode(2), 2)

	def test_accepts_numeric_string(self) -> None:
		self.assertEqual(GroupTypeEncoder().decode('5'), 5)

	def test_rejects_doodad_type(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			GroupTypeEncoder().decode(1)
		self.assertIn("'TileGroup' can't have type 1 (doodad type)", str(cm.exception))

	def test_rejects_non_integer(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			GroupTypeEncoder().decode('not a number')
		self.assertIn("Expected an integer, got 'not a number'", str(cm.exception))


class Test_MiniFlagsMultiEncoder(unittest.TestCase):
	def test_encode_four_lines_of_four(self) -> None:
		values = [FLAG, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, FLAG]
		self.assertEqual(MiniFlagsMultiEncoder(FLAG).encode(values), '1000\n0000\n0000\n0001')

	def test_encode_ignores_other_flag_bits(self) -> None:
		# A different bit set should not register as this flag.
		self.assertEqual(MiniFlagsMultiEncoder(FLAG).encode([0x01] * 16), '0000\n0000\n0000\n0000')

	def test_decode_to_bools(self) -> None:
		result = MiniFlagsMultiEncoder(FLAG).decode('1000\n0000\n0000\n0001', None)
		expected = [True, False, False, False] + [False] * 11 + [True]
		self.assertEqual(result, expected)

	def test_decode_accepts_true_false_chars(self) -> None:
		result = MiniFlagsMultiEncoder(FLAG).decode('TFFF\nFFFF\nFFFF\nFFFT', None)
		self.assertEqual(result[0], True)
		self.assertEqual(result[1], False)
		self.assertEqual(result[14], False)
		self.assertEqual(result[15], True)

	def test_decode_wrong_line_count_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			MiniFlagsMultiEncoder(FLAG).decode('0000\n0000', None)
		self.assertIn('Expected 4 lines of flags', str(cm.exception))

	def test_decode_wrong_flag_count_raises(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			MiniFlagsMultiEncoder(FLAG).decode('000\n0000\n0000\n0000', None)
		self.assertIn('Expected 4 flags', str(cm.exception))

	def test_apply_sets_and_clears_flag(self) -> None:
		bools = [True] + [False] * 15
		result = MiniFlagsMultiEncoder(FLAG).apply(bools, [FLAG] * 16)
		self.assertEqual(result[0], FLAG)
		self.assertEqual(result[1], 0)

	def test_apply_preserves_other_bits(self) -> None:
		result = MiniFlagsMultiEncoder(FLAG).apply([False] * 16, [0x01] * 16)
		self.assertEqual(result, [0x01] * 16)

	def test_encode_decode_apply_round_trip(self) -> None:
		values = [FLAG if n in (0, 5, 15) else 0 for n in range(16)]
		encoder = MiniFlagsMultiEncoder(FLAG)
		bools = encoder.decode(encoder.encode(values), None)
		self.assertEqual(encoder.apply(bools, [0] * 16), values)
