
from .utils import make_chk
from ...FileFormats.CHK.Sections.CHKSectionDD2 import CHKSectionDD2, CHKDoodadVisual

import unittest


def _doodad(chk) -> CHKDoodadVisual:
	doodad = CHKDoodadVisual(chk)
	doodad.doodadID = 5
	doodad.position = [12, 34]
	doodad.owner = 2
	doodad.enabled = True
	return doodad


class Test_CHKDoodadVisual(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		doodad = _doodad(chk)
		data = doodad.save_data()
		self.assertEqual(len(data), 8)
		reloaded = CHKDoodadVisual(chk)
		reloaded.load_data(data)
		self.assertEqual(reloaded.doodadID, 5)
		self.assertEqual(reloaded.position, [12, 34])
		self.assertEqual(reloaded.owner, 2)
		self.assertTrue(reloaded.enabled)
		self.assertEqual(reloaded.save_data(), data)


class Test_CHKSectionDD2(unittest.TestCase):
	def test_round_trip(self) -> None:
		chk = make_chk()
		section = CHKSectionDD2(chk)
		section.doodads = [_doodad(chk), _doodad(chk)]
		data = section.save_data()
		self.assertEqual(len(data), 16)
		reloaded = CHKSectionDD2(make_chk())
		reloaded.load_data(data)
		self.assertEqual(len(reloaded.doodads), 2)
		self.assertEqual(reloaded.save_data(), data)

	def test_empty_save(self) -> None:
		self.assertEqual(CHKSectionDD2(make_chk()).save_data(), b'')

	def test_decompile(self) -> None:
		chk = make_chk()
		section = CHKSectionDD2(chk)
		section.doodads = [_doodad(chk)]
		self.assertTrue(section.decompile().startswith('DD2 :'))
