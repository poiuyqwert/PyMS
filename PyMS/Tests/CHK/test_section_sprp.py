
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionSPRP import CHKSectionSPRP

import struct
import unittest


class Test_CHKSectionSPRP(unittest.TestCase):
	def test_defaults(self) -> None:
		section = CHKSectionSPRP(make_chk())
		self.assertEqual((section.scenarioName, section.description), (0, 0))

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionSPRP(chk)
		section.scenarioName, section.description = 5, 9
		reloaded = CHKSectionSPRP(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual((reloaded.scenarioName, reloaded.description), (5, 9))
		self.assertEqual(reloaded.save_data(), struct.pack('<HH', 5, 9))

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionSPRP(make_chk()).decompile().startswith('SPRP:'))
