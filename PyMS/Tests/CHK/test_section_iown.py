
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionIOWN import CHKSectionIOWN

import struct
import unittest


class Test_CHKSectionIOWN(unittest.TestCase):
	def test_default_owners(self) -> None:
		section = CHKSectionIOWN(make_chk())
		self.assertEqual(section.owners, [CHKSectionIOWN.HUMAN] * 8 + [CHKSectionIOWN.INACTIVE] * 4)

	def test_round_trip(self) -> None:
		chk = make_chk()
		owners = list(range(12))
		section = CHKSectionIOWN(chk)
		section.owners = owners
		reloaded = CHKSectionIOWN(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.owners, owners)
		self.assertEqual(reloaded.save_data(), struct.pack('<12B', *owners))

	def test_owner_name(self) -> None:
		self.assertEqual(CHKSectionIOWN.OWNER_NAME(CHKSectionIOWN.HUMAN), 'Human')
		self.assertEqual(CHKSectionIOWN.OWNER_NAME(99), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionIOWN(make_chk()).decompile().startswith('IOWN:'))
