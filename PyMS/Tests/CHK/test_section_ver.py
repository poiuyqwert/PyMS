
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionVER import CHKSectionVER

import struct
import unittest


class Test_CHKSectionVER(unittest.TestCase):
	def test_default_is_broodwar(self) -> None:
		self.assertEqual(CHKSectionVER(make_chk()).version, CHKSectionVER.BW)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionVER(chk)
		section.version = CHKSectionVER.SC104
		reloaded = CHKSectionVER(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.version, CHKSectionVER.SC104)
		self.assertEqual(reloaded.save_data(), struct.pack('<H', CHKSectionVER.SC104))

	def test_version_name(self) -> None:
		self.assertEqual(CHKSectionVER.VER_NAME(CHKSectionVER.BW), 'BroodWar')
		self.assertEqual(CHKSectionVER.VER_NAME(999), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionVER(make_chk()).decompile().startswith('VER :'))
