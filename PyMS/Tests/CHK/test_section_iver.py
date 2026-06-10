
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionIVER import CHKSectionIVER

import unittest


class Test_CHKSectionIVER(unittest.TestCase):
	def test_default_is_release(self) -> None:
		self.assertEqual(CHKSectionIVER(make_chk()).version, CHKSectionIVER.RELEASE)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionIVER(chk)
		section.version = CHKSectionIVER.BETA
		reloaded = CHKSectionIVER(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.version, CHKSectionIVER.BETA)

	def test_version_name(self) -> None:
		self.assertEqual(CHKSectionIVER.VER_NAME(CHKSectionIVER.RELEASE), 'Release')
		self.assertEqual(CHKSectionIVER.VER_NAME(999), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionIVER(make_chk()).decompile().startswith('IVER:'))
