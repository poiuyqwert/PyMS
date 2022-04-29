
from ...FileFormats.DAT import *
from ...FileFormats.TBL import TBL

from ...Utilities.DataCache import DATA_CACHE

from ..utils import resource_path

import unittest

class Test_Entry_Name(unittest.TestCase):
	def test_unit_name(self):
		entry_ids = (0, 114, 227, 228, 250, 251)
		stat_txt = TBL()
		stat_txt.load_file(resource_path('stat_txt.tbl', __file__))
		unitnamestbl = TBL()
		unitnamestbl.load_file(resource_path('unitnames.tbl', __file__))

		expected_names = (
			'Unit #0',
			'Unit #114',
			'Unit #227',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id),
				expected_name
			)

		expected_names = (
			'Terran Marine',
			'Terran Starport',
			'Terran Vespene Gas Tank Type 2',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt']),
				expected_name,
			)

		expected_names = (
			'Terran Marine<0>*<0>Ground Units',
			'Terran Starport<0>*<0>Buildings',
			'Vespene Tank<0>Terran Type 2<0>Resources',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names_usage=DataNamesUsage.ignore, stat_txt=stat_txt),
				expected_name,
			)

		expected_names = (
			'Terran Marine<0>*<0>Ground Units',
			'Terran Starport<0>*<0>Buildings',
			'Vespene Tank<0>Terran Type 2<0>Resources',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'My Cool Unit<0>*<0>My Cool Race'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names_usage=DataNamesUsage.ignore, stat_txt=stat_txt, unitnamestbl=unitnamestbl),
				expected_name,
			)

		expected_names = (
			'Terran Marine',
			'Terran Starport',
			'Vespene Tank (Terran Type 2)',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name,
			)

		expected_names = (
			'Terran Marine',
			'Terran Starport',
			'Vespene Tank (Terran Type 2)',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'My Cool Unit'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name,
			)

		expected_names = (
			'Terran Marine',
			'Terran Starport',
			'Terran Vespene Gas Tank Type 2',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.use),
				expected_name,
			)

		expected_names = (
			'Terran Marine (Terran Marine<0>*<0>Ground Units)',
			'Terran Starport (Terran Starport<0>*<0>Buildings)',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank<0>Terran Type 2<0>Resources)',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name,
			)

		expected_names = (
			'Terran Marine (Terran Marine<0>*<0>Ground Units)',
			'Terran Starport (Terran Starport<0>*<0>Buildings)',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank<0>Terran Type 2<0>Resources)',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251 (My Cool Unit<0>*<0>My Cool Race)'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine),
				expected_name,
			)

		expected_names = (
			'Terran Marine (Terran Marine)',
			'Terran Starport (Terran Starport)',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank (Terran Type 2))',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251 (My Cool Unit)'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
				expected_name,
			)

		expected_names = (
			'My Other Cool Unit',
			'My Last Cool Unit',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank (Terran Type 2))',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Not A Cool Unit'
		)
		name_overrides = {
			0: (False, 'My Other Cool Unit'),
			114: (False, 'My Last Cool Unit'),
			228: (False, "Won't Work"),
			251: (False, 'Not A Cool Unit')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name,
			)

		expected_names = (
			'Terran Marine (Terran Marine) [V1]',
			'Terran Starport (Terran Starport) [V2]',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank (Terran Type 2))',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251 (My Cool Unit) [V3]'
		)
		name_overrides = {
			0: (True, '[V1]'),
			114: (True, '[V2]'),
			228: (True, "Won't Work"),
			251: (True, '[V3]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=DATA_CACHE['Units.txt'], stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name,
			)

	def test_weapon_name(self):
		entry_ids = (0, 61, 129, 130)
		stat_txt = TBL()
		stat_txt.load_file(resource_path('stat_txt.tbl', __file__))
		weaponsdat = WeaponsDAT()
		weaponsdat.load_file(resource_path('weapons.dat', __file__))
		weaponsdat.expand_entries()
		weaponsdat.get_entry(130).label = 570 # "General Duke<0>"

		expected_names = (
			'Weapon #0',
			'Weapon #61',
			'Weapon #129',
			'Expanded Weapon #130',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal)',
			'Consume',
			'Unknown129',
			'Expanded Weapon #130',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=DATA_CACHE['Weapons.txt']),
				expected_name
			)

		expected_names = (
			'Gauss Rifle',
			'c<3><3>C<1>onsume',
			'Gauss Rifle',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Gauss Rifle',
			'Consume',
			'Gauss Rifle',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal) (Gauss Rifle)',
			'Consume (c<3><3>C<1>onsume)',
			'Unknown129 (Gauss Rifle)',
			'Expanded Weapon #130 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=DATA_CACHE['Weapons.txt'], weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal) (Gauss Rifle)',
			'Consume (Consume)',
			'Unknown129 (Gauss Rifle)',
			'Expanded Weapon #130 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=DATA_CACHE['Weapons.txt'], weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'My Cool Weapon',
			'My Other Cool Weapon',
			'Meh Weapon',
			'Not A Cool Weapon',
		)
		name_overrides = {
			0: (False, 'My Cool Weapon'),
			61: (False, 'My Other Cool Weapon'),
			129: (False, 'Meh Weapon'),
			130: (False, 'Not A Cool Weapon')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=DATA_CACHE['Weapons.txt'], weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal) (Gauss Rifle) [V1]',
			'Consume (Consume) [V2]',
			'Unknown129 (Gauss Rifle) [V3]',
			'Expanded Weapon #130 (General Duke) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			61: (True, '[V2]'),
			129: (True, '[V3]'),
			130: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=DATA_CACHE['Weapons.txt'], weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

	def test_image_name(self):
		entry_ids = (0, 499, 998, 999)
		imagesdat = ImagesDAT()
		imagesdat.load_file(resource_path('images.dat', __file__))
		imagesdat.expand_entries()
		imagesdat.get_entry(999).grp_file = 3 # zerg\\zavBirth.grp
		imagestbl = TBL()
		imagestbl.load_file(resource_path('images.tbl', __file__))

		expected_names = (
			'Image #0',
			'Image #499',
			'Image #998',
			'Expanded Image #999',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id),
				expected_name
			)

		expected_names = (
			'Scourge',
			'Building Lifting Dust Type1',
			'Maelstrom Hit',
			'Expanded Image #999',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id, data_names=DATA_CACHE['Images.txt']),
				expected_name
			)

		expected_names = (
			'zerg\\avenger.grp',
			'thingy\\dust06.grp',
			'thingy\\MaelHit.grp',
			'zerg\\zavBirth.grp',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Scourge (zerg\\avenger.grp)',
			'Building Lifting Dust Type1 (thingy\\dust06.grp)',
			'Maelstrom Hit (thingy\\MaelHit.grp)',
			'Expanded Image #999 (zerg\\zavBirth.grp)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id, data_names=DATA_CACHE['Images.txt'], imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Image',
			'My Other Cool Image',
			'Meh Image',
			'Not A Cool Image',
		)
		name_overrides = {
			0: (False, 'My Cool Image'),
			499: (False, 'My Other Cool Image'),
			998: (False, 'Meh Image'),
			999: (False, 'Not A Cool Image')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id, data_names=DATA_CACHE['Images.txt'], imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Scourge (zerg\\avenger.grp) [V1]',
			'Building Lifting Dust Type1 (thingy\\dust06.grp) [V2]',
			'Maelstrom Hit (thingy\\MaelHit.grp) [V3]',
			'Expanded Image #999 (zerg\\zavBirth.grp) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			499: (True, '[V2]'),
			998: (True, '[V3]'),
			999: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.image(entry_id, data_names=DATA_CACHE['Images.txt'], imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_sprite_name(self):
		entry_ids = (0, 258, 516, 517)
		spritesdat = SpritesDAT()
		spritesdat.load_file(resource_path('sprites.dat', __file__))
		spritesdat.expand_entries()
		spritesdat.get_entry(517).image = 999
		imagesdat = ImagesDAT()
		imagesdat.load_file(resource_path('images.dat', __file__))
		imagesdat.expand_entries()
		imagesdat.get_entry(999).grp_file = 3 # zerg\\zavBirth.grp
		imagestbl = TBL()
		imagestbl.load_file(resource_path('images.tbl', __file__))

		expected_names = (
			'Sprite #0',
			'Sprite #258',
			'Sprite #516',
			'Expanded Sprite #517',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id),
				expected_name
			)

		expected_names = (
			'2/38 Ash',
			'Machine Shop',
			'Khalis',
			'Expanded Sprite #517',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Sprites.txt']),
				expected_name
			)

		expected_names = (
			'thingy\\tileset\\AshWorld\\rock01.grp',
			'terran\\machines.grp',
			'neutral\\Khalis.grp',
			'zerg\\zavBirth.grp',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'2/38 Ash (thingy\\tileset\\AshWorld\\rock01.grp)',
			'Machine Shop (terran\\machines.grp)',
			'Khalis (neutral\\Khalis.grp)',
			'Expanded Sprite #517 (zerg\\zavBirth.grp)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Sprites.txt'], spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Image',
			'My Other Cool Image',
			'Meh Image',
			'Not A Cool Image',
		)
		name_overrides = {
			0: (False, 'My Cool Image'),
			258: (False, 'My Other Cool Image'),
			516: (False, 'Meh Image'),
			517: (False, 'Not A Cool Image')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Sprites.txt'], spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'2/38 Ash (thingy\\tileset\\AshWorld\\rock01.grp) [V1]',
			'Machine Shop (terran\\machines.grp) [V2]',
			'Khalis (neutral\\Khalis.grp) [V3]',
			'Expanded Sprite #517 (zerg\\zavBirth.grp) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			258: (True, '[V2]'),
			516: (True, '[V3]'),
			517: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sprite(entry_id, data_names=DATA_CACHE['Sprites.txt'], spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_flingy_name(self):
		entry_ids = (0, 104, 208, 209)
		flingydat = FlingyDAT()
		flingydat.load_file(resource_path('flingy.dat', __file__))
		flingydat.expand_entries()
		flingydat.get_entry(209).sprite = 517
		spritesdat = SpritesDAT()
		spritesdat.load_file(resource_path('sprites.dat', __file__))
		spritesdat.expand_entries()
		spritesdat.get_entry(517).image = 999
		imagesdat = ImagesDAT()
		imagesdat.load_file(resource_path('images.dat', __file__))
		imagesdat.expand_entries()
		imagesdat.get_entry(999).grp_file = 3 # zerg\\zavBirth.grp
		imagestbl = TBL()
		imagestbl.load_file(resource_path('images.tbl', __file__))

		expected_names = (
			'Flingy #0',
			'Flingy #104',
			'Flingy #208',
			'Expanded Flingy #209',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id),
				expected_name
			)

		expected_names = (
			'Scourge',
			'Bunker',
			'Khalis',
			'Expanded Flingy #209',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id, data_names=DATA_CACHE['Flingy.txt']),
				expected_name
			)

		expected_names = (
			'zerg\\avenger.grp',
			'terran\\PillBox.grp',
			'neutral\\Khalis.grp',
			'zerg\\zavBirth.grp',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id, flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Scourge (zerg\\avenger.grp)',
			'Bunker (terran\\PillBox.grp)',
			'Khalis (neutral\\Khalis.grp)',
			'Expanded Flingy #209 (zerg\\zavBirth.grp)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id, data_names=DATA_CACHE['Flingy.txt'], flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Image',
			'My Other Cool Image',
			'Meh Image',
			'Not A Cool Image',
		)
		name_overrides = {
			0: (False, 'My Cool Image'),
			104: (False, 'My Other Cool Image'),
			208: (False, 'Meh Image'),
			209: (False, 'Not A Cool Image')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id, data_names=DATA_CACHE['Flingy.txt'], flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Scourge (zerg\\avenger.grp) [V1]',
			'Bunker (terran\\PillBox.grp) [V2]',
			'Khalis (neutral\\Khalis.grp) [V3]',
			'Expanded Flingy #209 (zerg\\zavBirth.grp) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			104: (True, '[V2]'),
			208: (True, '[V3]'),
			209: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.flingy(entry_id, data_names=DATA_CACHE['Flingy.txt'], flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)
