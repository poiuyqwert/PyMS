
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionSIDE import CHKSectionSIDE

import struct
import unittest


class Test_CHKSectionSIDE(unittest.TestCase):
	def test_default_sides(self) -> None:
		section = CHKSectionSIDE(make_chk())
		self.assertEqual(section.sides, [CHKSectionSIDE.RANDOM] * 8 + [CHKSectionSIDE.INACTIVE] * 4)

	def test_round_trip(self) -> None:
		chk = make_chk()
		sides = [CHKSectionSIDE.ZERG, CHKSectionSIDE.TERRAN, CHKSectionSIDE.PROTOSS] * 4
		section = CHKSectionSIDE(chk)
		section.sides = sides
		reloaded = CHKSectionSIDE(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.sides, sides)
		self.assertEqual(reloaded.save_data(), struct.pack('<12B', *sides))

	def test_side_name(self) -> None:
		self.assertEqual(CHKSectionSIDE.SIDE_NAME(CHKSectionSIDE.PROTOSS), 'Protoss')
		self.assertEqual(CHKSectionSIDE.SIDE_NAME(99), 'Unknown')

	def test_decompile(self) -> None:
		self.assertTrue(CHKSectionSIDE(make_chk()).decompile().startswith('SIDE:'))
