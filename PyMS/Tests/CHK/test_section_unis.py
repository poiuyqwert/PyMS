
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUNIS import CHKSectionUNIS

import unittest


def _populate(section: CHKSectionUNIS) -> None:
	section.unit_stats[0].default = False
	section.unit_stats[0].health = 256 * 50
	section.unit_stats[0].costMinerals = 75
	section.unit_stats[0].name = 9
	section.weapon_stats[0].damage = 12
	section.weapon_stats[0].damageUpgrade = 3


class Test_CHKSectionUNIS(unittest.TestCase):
	def test_counts(self) -> None:
		self.assertEqual(CHKSectionUNIS.UNITS, 228)
		self.assertEqual(CHKSectionUNIS.WEAPONS, 100)
		section = CHKSectionUNIS(make_chk())
		self.assertEqual(len(section.unit_stats), 228)
		self.assertEqual(len(section.weapon_stats), 100)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUNIS(chk)
		_populate(section)
		data = section.save_data()
		reloaded = CHKSectionUNIS(chk)
		reloaded.load_data(data)
		self.assertFalse(reloaded.unit_stats[0].default)
		self.assertEqual(reloaded.unit_stats[0].health, 256 * 50)
		self.assertEqual(reloaded.unit_stats[0].costMinerals, 75)
		self.assertEqual(reloaded.unit_stats[0].name, 9)
		self.assertEqual(reloaded.weapon_stats[0].damage, 12)
		self.assertEqual(reloaded.weapon_stats[0].damageUpgrade, 3)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionUNIS(make_chk()).decompile().startswith('UNIS:'))
