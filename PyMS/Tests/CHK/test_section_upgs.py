
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUPGS import CHKSectionUPGS

import unittest


def _populate(section: CHKSectionUPGS) -> None:
	section.stats[0].default = False
	section.stats[0].costMinerals = 100
	section.stats[0].costMineralsIncrease = 50
	section.stats[0].costGas = 75
	section.stats[0].buildTime = 200
	section.stats[0].buildTimeIncrease = 25


class Test_CHKSectionUPGS(unittest.TestCase):
	def test_upgrade_count(self) -> None:
		self.assertEqual(CHKSectionUPGS.UPGRADES, 46)
		self.assertFalse(CHKSectionUPGS.PAD)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUPGS(chk)
		_populate(section)
		data = section.save_data()
		reloaded = CHKSectionUPGS(chk)
		reloaded.load_data(data)
		self.assertFalse(reloaded.stats[0].default)
		self.assertEqual(reloaded.stats[0].costMinerals, 100)
		self.assertEqual(reloaded.stats[0].costMineralsIncrease, 50)
		self.assertEqual(reloaded.stats[0].costGas, 75)
		self.assertEqual(reloaded.stats[0].buildTime, 200)
		self.assertEqual(reloaded.stats[0].buildTimeIncrease, 25)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionUPGS(make_chk()).decompile().startswith('UPGS:'))
