
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionUPUS import CHKSectionUPUS

import unittest


class Test_CHKSectionUPUS(unittest.TestCase):
	def test_default_unused(self) -> None:
		self.assertEqual(CHKSectionUPUS(make_chk()).properties_used, [False] * 64)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionUPUS(chk)
		section.properties_used = [bool(i % 2) for i in range(64)]
		data = section.save_data()
		self.assertEqual(len(data), 64)
		reloaded = CHKSectionUPUS(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.properties_used, section.properties_used)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionUPUS(make_chk()).decompile().startswith('UPUS:'))
