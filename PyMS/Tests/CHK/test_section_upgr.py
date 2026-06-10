
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUPGR import CHKSectionUPGR

import unittest


def _populate(section: CHKSectionUPGR) -> None:
	section.maxLevels = [3] * section.UPGRADES
	section.startLevels = [0] * section.UPGRADES
	section.maxLevels[0] = 5
	section.startLevels[0] = 2
	section.levels[1][2].maxLevel = 4
	section.levels[1][2].startLevel = 1
	section.levels[1][2].default = False


class Test_CHKSectionUPGR(unittest.TestCase):
	def test_upgrade_count(self) -> None:
		self.assertEqual(CHKSectionUPGR.UPGRADES, 46)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUPGR(chk)
		_populate(section)
		data = section.save_data()
		reloaded = CHKSectionUPGR(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.maxLevels[0], 5)
		self.assertEqual(reloaded.startLevels[0], 2)
		self.assertEqual(reloaded.levels[1][2].maxLevel, 4)
		self.assertEqual(reloaded.levels[1][2].startLevel, 1)
		self.assertFalse(reloaded.levels[1][2].default)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		section = CHKSectionUPGR(make_chk())
		_populate(section)
		self.assertTrue(section.decompile().startswith('UPGR:'))
