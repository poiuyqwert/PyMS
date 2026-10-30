
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionPTEC import CHKSectionPTEC

import unittest


def _populate(section: CHKSectionPTEC) -> None:
	section.globalAvailability = [1] * section.TECHS
	section.globallyResearched = [0] * section.TECHS
	section.globalAvailability[0] = 0
	section.globallyResearched[1] = 1
	section.availability[2][3].available = 0
	section.availability[2][3].researched = 1
	section.availability[2][3].default = False


class Test_CHKSectionPTEC(unittest.TestCase):
	def test_tech_count(self) -> None:
		self.assertEqual(CHKSectionPTEC.TECHS, 24)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionPTEC(chk)
		_populate(section)
		data = section.save_data()
		reloaded = CHKSectionPTEC(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.globalAvailability[0], 0)
		self.assertEqual(reloaded.globallyResearched[1], 1)
		self.assertEqual(reloaded.availability[2][3].available, 0)
		self.assertEqual(reloaded.availability[2][3].researched, 1)
		self.assertFalse(reloaded.availability[2][3].default)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		section = CHKSectionPTEC(make_chk())
		_populate(section)
		self.assertTrue(section.decompile().startswith('PTEC:'))
