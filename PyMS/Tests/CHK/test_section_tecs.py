
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionTECS import CHKSectionTECS

import unittest


def _populate(section: CHKSectionTECS) -> None:
	section.stats[0].default = False
	section.stats[0].costMinerals = 200
	section.stats[0].costGas = 200
	section.stats[0].buildTime = 1500
	section.stats[0].energyUsed = 100


class Test_CHKSectionTECS(unittest.TestCase):
	def test_tech_count(self) -> None:
		self.assertEqual(CHKSectionTECS.TECHS, 24)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionTECS(chk)
		_populate(section)
		data = section.save_data()
		reloaded = CHKSectionTECS(chk)
		reloaded.load_data(data)
		self.assertFalse(reloaded.stats[0].default)
		self.assertEqual(reloaded.stats[0].costMinerals, 200)
		self.assertEqual(reloaded.stats[0].costGas, 200)
		self.assertEqual(reloaded.stats[0].buildTime, 1500)
		self.assertEqual(reloaded.stats[0].energyUsed, 100)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionTECS(make_chk()).decompile().startswith('TECS:'))
