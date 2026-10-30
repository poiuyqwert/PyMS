
from ...PyDAT.DataID import DATID, DataID, UnitsTabID

import unittest


class Test_DATID(unittest.TestCase):
	FILENAMES = {
		DATID.units: 'units.dat',
		DATID.weapons: 'weapons.dat',
		DATID.flingy: 'flingy.dat',
		DATID.sprites: 'sprites.dat',
		DATID.images: 'images.dat',
		DATID.upgrades: 'upgrades.dat',
		DATID.techdata: 'techdata.dat',
		DATID.sfxdata: 'sfxdata.dat',
		DATID.portdata: 'portdata.dat',
		DATID.mapdata: 'mapdata.dat',
		DATID.orders: 'orders.dat',
	}

	def test_filename_for_every_member(self) -> None:
		for dat_id, filename in Test_DATID.FILENAMES.items():
			with self.subTest(dat_id=dat_id):
				self.assertEqual(dat_id.filename, filename)

	def test_filename_covers_all_members(self) -> None:
		self.assertEqual(set(Test_DATID.FILENAMES.keys()), set(DATID))

	def test_all_matches_every_member(self) -> None:
		self.assertEqual(DATID.units.ALL, tuple(DATID))

	def test_tab_id_is_value(self) -> None:
		self.assertEqual(DATID.units.tab_id, 'Units')


class Test_DataID(unittest.TestCase):
	def test_all_matches_every_member(self) -> None:
		self.assertEqual(DataID.stat_txt.ALL, tuple(DataID))


class Test_UnitsTabID(unittest.TestCase):
	def test_tab_name_is_value(self) -> None:
		self.assertEqual(UnitsTabID.basic.tab_name, 'Basic')
		self.assertEqual(UnitsTabID.ai_actions.tab_name, 'AI Actions')
