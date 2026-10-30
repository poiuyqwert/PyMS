
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionTHG2 import CHKSectionTHG2, CHKDoodad

import unittest


def _doodad(chk) -> CHKDoodad:
	doodad = CHKDoodad(chk)
	doodad.doodadID = 9
	doodad.position = [44, 55]
	doodad.owner = 1
	doodad.flags = CHKDoodad.SPRITE | CHKDoodad.DISABLED
	return doodad


class Test_CHKDoodad(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		doodad = _doodad(chk)
		data = doodad.save_data()
		self.assertEqual(len(data), 10)
		reloaded = CHKDoodad(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.doodadID, 9)
		self.assertEqual(reloaded.position, [44, 55])
		self.assertEqual(reloaded.owner, 1)
		self.assertEqual(reloaded.flags, CHKDoodad.SPRITE | CHKDoodad.DISABLED)
		self.assertEqual(reloaded.save_data(), data)


class Test_CHKSectionTHG2(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionTHG2(chk)
		section.doodads = [_doodad(chk), _doodad(chk)]
		data = section.save_data()
		self.assertEqual(len(data), 20)
		reloaded = CHKSectionTHG2(make_chk())
		reloaded.load_data(data)
		self.assertEqual(len(reloaded.doodads), 2)
		self.assertEqual(reloaded.save_data(), data)

	def test_decompile(self) -> None:
		chk = make_chk()
		section = CHKSectionTHG2(chk)
		section.doodads = [_doodad(chk)]
		self.assertTrue(section.decompile().startswith('THG2:'))
