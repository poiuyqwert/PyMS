
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionPUNI import CHKSectionPUNI

import unittest


class Test_CHKSectionPUNI(unittest.TestCase):
	def test_defaults(self) -> None:
		section = CHKSectionPUNI(make_chk())
		self.assertEqual(len(section.availability), 228)
		self.assertEqual(len(section.availability[0]), 12)
		self.assertTrue(section.availability[0][0].available)
		self.assertEqual(section.globalAvailability, [True] * 228)

	def test_fresh_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionPUNI(chk)
		section.availability[5][2].available = False
		section.availability[5][2].default = False
		section.globalAvailability[7] = False
		data = section.save_data()
		self.assertEqual(len(data), 228 * 12 * 2 + 228)
		reloaded = CHKSectionPUNI(chk)
		reloaded.load_data(data)
		self.assertFalse(reloaded.availability[5][2].available)
		self.assertFalse(reloaded.availability[5][2].default)
		self.assertFalse(reloaded.globalAvailability[7])
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionPUNI(make_chk()).decompile().startswith('PUNI:'))
