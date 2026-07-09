
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUNIx import CHKSectionUNIx
from ...FileFormats.CHK.Sections.CHKSectionUNIS import CHKSectionUNIS

import unittest


class Test_CHKSectionUNIx(unittest.TestCase):
	def test_extends_unis_with_broodwar_weapon_count(self) -> None:
		self.assertTrue(issubclass(CHKSectionUNIx, CHKSectionUNIS))
		self.assertEqual(CHKSectionUNIx.WEAPONS, 130)
		self.assertEqual(CHKSectionUNIx.UNITS, 228)
		self.assertEqual(CHKSectionUNIx.NAME, b'UNIx')

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUNIx(chk)
		section.weapon_stats[129].damage = 55
		section.unit_stats[0].costMinerals = 10
		data = section.save_data()
		reloaded = CHKSectionUNIx(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.weapon_stats[129].damage, 55)
		self.assertEqual(reloaded.unit_stats[0].costMinerals, 10)
		self.assertEqual(reloaded.save_data(), data)
