
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionTYPE import CHKSectionTYPE

import unittest


class Test_CHKSectionTYPE(unittest.TestCase):
	def test_default_is_broodwar(self) -> None:
		section = CHKSectionTYPE(make_chk())
		self.assertEqual(section.type, CHKSectionTYPE.BROODWAR)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionTYPE(chk)
		section.type = CHKSectionTYPE.STARCRAFT
		reloaded = CHKSectionTYPE(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.type, CHKSectionTYPE.STARCRAFT)
		self.assertEqual(reloaded.save_data(), b'RAWS')

	def test_type_name(self) -> None:
		self.assertEqual(CHKSectionTYPE.TYPE_NAME(CHKSectionTYPE.BROODWAR), 'BroodWar')
		self.assertEqual(CHKSectionTYPE.TYPE_NAME(b'????'), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionTYPE(make_chk()).decompile().startswith('TYPE:'))
