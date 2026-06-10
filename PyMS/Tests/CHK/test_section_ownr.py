
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionOWNR import CHKSectionOWNR

import struct
import unittest


class Test_CHKSectionOWNR(unittest.TestCase):
	def test_default_owners(self) -> None:
		section = CHKSectionOWNR(make_chk())
		expected = [CHKSectionOWNR.HUMAN] * 8 + [CHKSectionOWNR.INACTIVE] * 3 + [CHKSectionOWNR.NEUTRAL]
		self.assertEqual(section.owners, expected)

	def test_round_trip(self) -> None:
		chk = make_chk()
		owners = list(reversed(range(12)))
		section = CHKSectionOWNR(chk)
		section.owners = owners
		reloaded = CHKSectionOWNR(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.owners, owners)
		self.assertEqual(reloaded.save_data(), struct.pack('<12B', *owners))

	def test_owner_name(self) -> None:
		self.assertEqual(CHKSectionOWNR.OWNER_NAME(CHKSectionOWNR.COMPUTER), 'Computer')
		self.assertEqual(CHKSectionOWNR.OWNER_NAME(99), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionOWNR(make_chk()).decompile().startswith('OWNR:'))
