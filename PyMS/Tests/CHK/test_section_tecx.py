
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionTECx import CHKSectionTECx
from ...FileFormats.CHK.Sections.CHKSectionTECS import CHKSectionTECS

import unittest


class Test_CHKSectionTECx(unittest.TestCase):
	def test_extends_tecs_with_broodwar_count(self) -> None:
		self.assertTrue(issubclass(CHKSectionTECx, CHKSectionTECS))
		self.assertEqual(CHKSectionTECx.TECHS, 44)
		self.assertEqual(CHKSectionTECx.NAME, b'TECx')

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionTECx(chk)
		section.stats[43].energyUsed = 250
		section.stats[0].default = False
		data = section.save_data()
		reloaded = CHKSectionTECx(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.stats[43].energyUsed, 250)
		self.assertFalse(reloaded.stats[0].default)
		self.assertEqual(reloaded.save_data(), data)
