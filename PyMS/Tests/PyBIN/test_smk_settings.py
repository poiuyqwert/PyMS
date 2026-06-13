
from ...FileFormats.DialogBIN import BINSMK
from ...Utilities.utils import pack_flags

import unittest


def _smk_flags() -> list[int]:
	return [v for k, v in vars(BINSMK).items() if k.startswith('FLAG_')]


class Test_flag_packing(unittest.TestCase):
	def test_flag_constants_are_distinct_single_bits(self) -> None:
		flags = _smk_flags()
		self.assertEqual(len(flags), len(set(flags)))
		for flag in flags:
			with self.subTest(flag=flag):
				self.assertNotEqual(flag, 0)
				self.assertEqual(flag & (flag - 1), 0)

	def test_pack_flags_round_trip_over_all_bits(self) -> None:
		flags = _smk_flags()
		original = 0
		for flag in flags:
			original |= flag
		packed = pack_flags([(1 if original & flag else 0, flag) for flag in flags])
		self.assertEqual(packed, original)

	def test_pack_flags_subset(self) -> None:
		packed = pack_flags([
			(1, BINSMK.FLAG_FADE_IN),
			(0, BINSMK.FLAG_DARK),
			(1, BINSMK.FLAG_REPEATS),
		])
		self.assertEqual(packed, BINSMK.FLAG_FADE_IN | BINSMK.FLAG_REPEATS)
