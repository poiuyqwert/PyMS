
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionFORC import CHKSectionFORC, CHKForce

import struct
import unittest


class Test_CHKSectionFORC(unittest.TestCase):
	def test_defaults(self) -> None:
		section = CHKSectionFORC(make_chk())
		self.assertEqual(section.playerForces, [0] * 8)
		self.assertEqual(len(section.forces), 4)

	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionFORC(chk)
		section.playerForces = [0, 1, 2, 3, 0, 1, 2, 3]
		section.forces[0].name = 5
		section.forces[1].properties = CHKForce.ALLIES | CHKForce.ALLIED_VICTORY
		reloaded = CHKSectionFORC(chk)
		reloaded.load_data(section.save_data())
		self.assertEqual(reloaded.playerForces, [0, 1, 2, 3, 0, 1, 2, 3])
		self.assertEqual(reloaded.forces[0].name, 5)
		self.assertEqual(reloaded.forces[1].properties, CHKForce.ALLIES | CHKForce.ALLIED_VICTORY)
		self.assertEqual(reloaded.save_data(), section.save_data())

	def test_save_layout(self) -> None:
		section = CHKSectionFORC(make_chk())
		self.assertEqual(len(section.save_data()), struct.calcsize('<8B4H4B'))

	def test_decompile(self) -> None:
		text = CHKSectionFORC(make_chk()).decompile()
		self.assertTrue(text.startswith('FORC:'))
		self.assertIn('Player 1', text)
