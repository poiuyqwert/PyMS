
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionIVE2 import CHKSectionIVE2

import unittest


class Test_CHKSectionIVE2(unittest.TestCase):
	def test_default_is_release(self) -> None:
		self.assertEqual(CHKSectionIVE2(make_chk()).version, CHKSectionIVE2.RELEASE)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionIVE2(chk)
		section.version = 42
		reloaded = CHKSectionIVE2(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.version, 42)

	def test_version_name(self) -> None:
		self.assertEqual(CHKSectionIVE2.VER_NAME(CHKSectionIVE2.RELEASE), 'Release')
		self.assertEqual(CHKSectionIVE2.VER_NAME(0), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionIVE2(make_chk()).decompile().startswith('IVE2:'))
