
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionPUPx import CHKSectionPUPx
from ...FileFormats.CHK.Sections.CHKSectionUPGR import CHKSectionUPGR

import unittest


class Test_CHKSectionPUPx(unittest.TestCase):
	def test_extends_upgr_with_broodwar_count(self) -> None:
		self.assertTrue(issubclass(CHKSectionPUPx, CHKSectionUPGR))
		self.assertEqual(CHKSectionPUPx.UPGRADES, 61)
		self.assertEqual(CHKSectionPUPx.NAME, b'PUPx')

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionPUPx(chk)
		section.maxLevels = [3] * section.UPGRADES
		section.startLevels = [0] * section.UPGRADES
		section.levels[60][11].maxLevel = 7
		data = section.save_data()
		reloaded = CHKSectionPUPx(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.levels[60][11].maxLevel, 7)
		self.assertEqual(reloaded.save_data(), data)
