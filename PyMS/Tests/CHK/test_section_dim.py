
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionDIM import CHKSectionDIM

import struct
import unittest


class Test_CHKSectionDIM(unittest.TestCase):
	def test_default_is_medium(self) -> None:
		section = CHKSectionDIM(make_chk())
		self.assertEqual((section.width, section.height), (CHKSectionDIM.MEDIUM, CHKSectionDIM.MEDIUM))

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionDIM(chk)
		section.width, section.height = CHKSectionDIM.LARGE, CHKSectionDIM.HUGE
		reloaded = CHKSectionDIM(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual((reloaded.width, reloaded.height), (192, 256))
		self.assertEqual(reloaded.save_data(), struct.pack('<2H', 192, 256))

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionDIM(make_chk()).decompile().startswith('DIM :'))
