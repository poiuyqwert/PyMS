
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionSWNM import CHKSectionSWNM

import unittest


class Test_CHKSectionSWNM(unittest.TestCase):
	def test_default_names(self) -> None:
		self.assertEqual(CHKSectionSWNM(make_chk()).names, [0] * 256)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionSWNM(chk)
		section.names[0] = 7
		section.names[255] = 99
		data = section.save_data()
		self.assertEqual(len(data), 256 * 4)
		reloaded = CHKSectionSWNM(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.names[0], 7)
		self.assertEqual(reloaded.names[255], 99)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionSWNM(make_chk()).decompile().startswith('SWNM:'))
