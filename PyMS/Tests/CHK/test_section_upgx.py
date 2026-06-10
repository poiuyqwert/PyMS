
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUPGx import CHKSectionUPGx
from ...FileFormats.CHK.Sections.CHKSectionUPGS import CHKSectionUPGS

import unittest


class Test_CHKSectionUPGx(unittest.TestCase):
	def test_extends_upgs_with_broodwar_count_and_padding(self) -> None:
		self.assertTrue(issubclass(CHKSectionUPGx, CHKSectionUPGS))
		self.assertEqual(CHKSectionUPGx.UPGRADES, 61)
		self.assertTrue(CHKSectionUPGx.PAD)
		self.assertEqual(CHKSectionUPGx.NAME, b'UPGx')

	def test_save_includes_padding_byte(self) -> None:
		# PAD adds one byte between the defaults block and the cost blocks.
		section = CHKSectionUPGx(make_chk())
		padded = len(section.save_data())
		section.PAD = False
		try:
			unpadded = len(section.save_data())
		finally:
			section.PAD = True
		self.assertEqual(padded, unpadded + 1)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUPGx(chk)
		section.stats[60].costMinerals = 321
		section.stats[0].default = False
		data = section.save_data()
		reloaded = CHKSectionUPGx(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.stats[60].costMinerals, 321)
		self.assertFalse(reloaded.stats[0].default)
		self.assertEqual(reloaded.save_data(), data)
