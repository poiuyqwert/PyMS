
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionPTEx import CHKSectionPTEx
from ...FileFormats.CHK.Sections.CHKSectionPTEC import CHKSectionPTEC

import unittest


class Test_CHKSectionPTEx(unittest.TestCase):
	def test_extends_ptec_with_broodwar_count(self) -> None:
		self.assertTrue(issubclass(CHKSectionPTEx, CHKSectionPTEC))
		self.assertEqual(CHKSectionPTEx.TECHS, 44)
		self.assertEqual(CHKSectionPTEx.NAME, b'PTEx')

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionPTEx(chk)
		section.globalAvailability = [1] * section.TECHS
		section.globallyResearched = [0] * section.TECHS
		section.availability[43][11].researched = 1
		data = section.save_data()
		reloaded = CHKSectionPTEx(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.availability[43][11].researched, 1)
		self.assertEqual(reloaded.save_data(), data)
