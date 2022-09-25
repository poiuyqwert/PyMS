
from ...FileFormats.DAT import *
from ...FileFormats.TBL import TBL, decompile_string

from ...Utilities import Assets

from ..utils import resource_path

import unittest

class Test_Entry_Name(unittest.TestCase):
	def test_generic_name(self):
		entry_ids = (0, 1, 2, 3)
		type = 'Entry'
		id_count = 3
		data_names = ['Name 1', 'Name 2', 'Name 3']

		expected_names = (
			'Entry #0',
			'Entry #1',
			'Entry #2',
			'Expanded Entry #3'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.generic(entry_id, type, id_count),
				expected_name
			)

		expected_names = (
			'Name 1',
			'Name 2',
			'Name 3',
			'Expanded Entry #3'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.generic(entry_id, type, id_count, data_names=data_names),
				expected_name
			)

		expected_names = (
			'Cool Name 1',
			'Name 2',
			'Cool Name 3',
			'Cool Name 4'
		)
		name_overrides = {
			0: (False, 'Cool Name 1'),
			2: (False, 'Cool Name 3'),
			3: (False, 'Cool Name 4')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.generic(entry_id, type, id_count, data_names=data_names, name_overrides=name_overrides),
				expected_name,
			)

		expected_names = (
			'Name 1 [V1]',
			'Name 2',
			'Name 3 [V2]',
			'Expanded Entry #3 [V3]'
		)
		name_overrides = {
			0: (True, '[V1]'),
			2: (True, '[V2]'),
			3: (True, '[V3]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.generic(entry_id, type, id_count, data_names=data_names, name_overrides=name_overrides),
				expected_name,
			)

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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units)),
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
				DATEntryName.unit(entry_id, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore),
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
		decompiled_stat_txt = TBL()
		decompiled_stat_txt.strings = [decompile_string(string) for string in stat_txt.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, stat_txt=decompiled_stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
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
				DATEntryName.unit(entry_id, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, unitnamestbl=unitnamestbl),
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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.use),
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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine),
				expected_name,
			)

		expected_names = (
			'Terran Marine',
			'Terran Starport',
			'Terran Vespene Gas Tank Type 2 (Vespene Tank (Terran Type 2))',
			'Reserved Unit #228',
			'Reserved Unit #250',
			'Expanded Unit #251 (My Cool Unit)'
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name,
			)

		expected_names = (
			'Terran Marine [V1]',
			'Terran Starport [V2]',
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
				DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=stat_txt, unitnamestbl=unitnamestbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
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
				DATEntryName.weapon(entry_id, data_names=Assets.data_cache(Assets.DataReference.Weapons)),
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
			'c<3><3>C<1>onsume',
			'Gauss Rifle',
			'General Duke',
		)
		decompiled_stat_txt = TBL()
		decompiled_stat_txt.strings = [decompile_string(string) for string in stat_txt.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, weaponsdat=weaponsdat, stat_txt=decompiled_stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
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
				DATEntryName.weapon(entry_id, data_names=Assets.data_cache(Assets.DataReference.Weapons), weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal) (Gauss Rifle)',
			'Consume',
			'Unknown129 (Gauss Rifle)',
			'Expanded Weapon #130 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.weapon(entry_id, data_names=Assets.data_cache(Assets.DataReference.Weapons), weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
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
				DATEntryName.weapon(entry_id, data_names=Assets.data_cache(Assets.DataReference.Weapons), weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Gauss Rifle (Normal) (Gauss Rifle) [V1]',
			'Consume [V2]',
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
				DATEntryName.weapon(entry_id, data_names=Assets.data_cache(Assets.DataReference.Weapons), weaponsdat=weaponsdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
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
				DATEntryName.image(entry_id, data_names=Assets.data_cache(Assets.DataReference.Images)),
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
				DATEntryName.image(entry_id, data_names=Assets.data_cache(Assets.DataReference.Images), imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
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
				DATEntryName.image(entry_id, data_names=Assets.data_cache(Assets.DataReference.Images), imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
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
				DATEntryName.image(entry_id, data_names=Assets.data_cache(Assets.DataReference.Images), imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
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
				DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sprites)),
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
				DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sprites), spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
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
				DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sprites), spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
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
				DATEntryName.sprite(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sprites), spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
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
				DATEntryName.flingy(entry_id, data_names=Assets.data_cache(Assets.DataReference.Flingy)),
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
				DATEntryName.flingy(entry_id, data_names=Assets.data_cache(Assets.DataReference.Flingy), flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine),
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
				DATEntryName.flingy(entry_id, data_names=Assets.data_cache(Assets.DataReference.Flingy), flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
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
				DATEntryName.flingy(entry_id, data_names=Assets.data_cache(Assets.DataReference.Flingy), flingydat=flingydat, spritesdat=spritesdat, imagesdat=imagesdat, imagestbl=imagestbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_upgrade_name(self):
		entry_ids = (0, 30, 60, 61)
		stat_txt = TBL()
		stat_txt.load_file(resource_path('stat_txt.tbl', __file__))
		upgradesdat = UpgradesDAT()
		upgradesdat.load_file(resource_path('upgrades.dat', __file__))
		upgradesdat.expand_entries()
		upgradesdat.get_entry(61).label = 570 # "General Duke<0>"

		expected_names = (
			'Upgrade #0',
			'Upgrade #30',
			'Upgrade #60',
			'Expanded Upgrade #61',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Unknown Upgrade60',
			'Expanded Upgrade #61',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades)),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Upgrade #60',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Upgrade #60',
			'General Duke',
		)
		decompiled_stat_txt = TBL()
		decompiled_stat_txt.strings = [decompile_string(string) for string in stat_txt.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, upgradesdat=upgradesdat, stat_txt=decompiled_stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Upgrade #60',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Unknown Upgrade60',
			'Expanded Upgrade #61 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades), upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor',
			'Grooved Spines',
			'Unknown Upgrade60',
			'Expanded Upgrade #61 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades), upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'My Cool Upgrade',
			'My Other Cool Upgrade',
			'Meh Upgrade',
			'Not A Cool Upgrade',
		)
		name_overrides = {
			0: (False, 'My Cool Upgrade'),
			30: (False, 'My Other Cool Upgrade'),
			60: (False, 'Meh Upgrade'),
			61: (False, 'Not A Cool Upgrade')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades), upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Terran Infantry Armor [V1]',
			'Grooved Spines [V2]',
			'Unknown Upgrade60 [V3]',
			'Expanded Upgrade #61 (General Duke) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			30: (True, '[V2]'),
			60: (True, '[V3]'),
			61: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades), upgradesdat=upgradesdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

	def test_tech_name(self):
		entry_ids = (0, 21, 43, 44)
		stat_txt = TBL()
		stat_txt.load_file(resource_path('stat_txt.tbl', __file__))
		techdatadat = TechDAT()
		techdatadat.load_file(resource_path('techdata.dat', __file__))
		techdatadat.expand_entries()
		techdatadat.get_entry(44).label = 570 # "General Duke<0>"

		expected_names = (
			'Tech #0',
			'Tech #21',
			'Tech #43',
			'Expanded Tech #44',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Unknown Tech43',
			'Expanded Tech #44',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata)),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Tech #43',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Tech #43',
			'General Duke',
		)
		decompiled_stat_txt = TBL()
		decompiled_stat_txt.strings = [decompile_string(string) for string in stat_txt.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, techdatadat=techdatadat, stat_txt=decompiled_stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Tech #43',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Unknown Tech43',
			'Expanded Tech #44 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata), techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'Stim Packs',
			'Recall',
			'Unknown Tech43',
			'Expanded Tech #44 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata), techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'My Cool Tech',
			'My Other Cool Tech',
			'Meh Tech',
			'Not A Cool Tech',
		)
		name_overrides = {
			0: (False, 'My Cool Tech'),
			21: (False, 'My Other Cool Tech'),
			43: (False, 'Meh Tech'),
			44: (False, 'Not A Cool Tech')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata), techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Stim Packs [V1]',
			'Recall [V2]',
			'Unknown Tech43 [V3]',
			'Expanded Tech #44 (General Duke) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			21: (True, '[V2]'),
			43: (True, '[V3]'),
			44: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata), techdatadat=techdatadat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

	def test_sound_name(self):
		entry_ids = (0, 571, 1143, 1144)
		sfxdatatbl = TBL()
		sfxdatatbl.load_file(resource_path('sfxdata.tbl', __file__))
		sfxdatadat = SoundsDAT()
		sfxdatadat.load_file(resource_path('sfxdata.dat', __file__))
		sfxdatadat.expand_entries()
		sfxdatadat.get_entry(1144).sound_file = 2 # Misc\\Buzz.wav

		expected_names = (
			'Sound #0',
			'Sound #571',
			'Sound #1143',
			'Expanded Sound #1144',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id),
				expected_name
			)

		expected_names = (
			'No sound',
			'Protoss\\ARCHON\\PArPss02.WAV',
			'Protoss\\Artanis\\PAtYes03.wav',
			'Expanded Sound #1144',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sfxdata)),
				expected_name
			)

		expected_names = (
			'Sound #0',
			'Protoss\\ARCHON\\PArPss02.WAV',
			'Protoss\\Artanis\\PAtYes03.wav',
			'Misc\\Buzz.wav',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, sfxdatadat=sfxdatadat, sfxdatatbl=sfxdatatbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Sound #0',
			'Protoss\\ARCHON\\PArPss02.WAV',
			'Protoss\\Artanis\\PAtYes03.wav',
			'Misc\\Buzz.wav',
		)
		decompiled_sfxdatatbl = TBL()
		decompiled_sfxdatatbl.strings = [decompile_string(string) for string in sfxdatatbl.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, sfxdatadat=sfxdatadat, sfxdatatbl=decompiled_sfxdatatbl, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'No sound',
			'Protoss\\ARCHON\\PArPss02.WAV',
			'Protoss\\Artanis\\PAtYes03.wav',
			'Misc\\Buzz.wav',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, sfxdatadat=sfxdatadat, sfxdatatbl=sfxdatatbl, none_name='No sound', data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'No sound',
			'Protoss\\ARCHON\\PArPss02.WAV',
			'Protoss\\Artanis\\PAtYes03.wav',
			'Expanded Sound #1144 (Misc\\Buzz.wav)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sfxdata), sfxdatadat=sfxdatadat, sfxdatatbl=sfxdatatbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Sound',
			'My Other Cool Sound',
			'Meh Sound',
			'Not A Cool Sound',
		)
		name_overrides = {
			0: (False, 'My Cool Sound'),
			571: (False, 'My Other Cool Sound'),
			1143: (False, 'Meh Sound'),
			1144: (False, 'Not A Cool Sound')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sfxdata), sfxdatadat=sfxdatadat, sfxdatatbl=sfxdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'No sound [V1]',
			'Protoss\\ARCHON\\PArPss02.WAV [V2]',
			'Protoss\\Artanis\\PAtYes03.wav [V3]',
			'Expanded Sound #1144 (Misc\\Buzz.wav) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			571: (True, '[V2]'),
			1143: (True, '[V3]'),
			1144: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.sound(entry_id, data_names=Assets.data_cache(Assets.DataReference.Sfxdata), sfxdatadat=sfxdatadat, sfxdatatbl=sfxdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_portrait_name(self):
		entry_ids = (0, 54, 109, 110)
		portdatatbl = TBL()
		portdatatbl.load_file(resource_path('portdata.tbl', __file__))
		portdatadat = PortraitsDAT()
		portdatadat.load_file(resource_path('portdata.dat', __file__))
		portdatadat.expand_entries()
		portdatadat.get_entry(110).sound_file = 2 # tmarine\\TMaFid0

		expected_names = (
			'Portrait #0',
			'Portrait #54',
			'Portrait #109',
			'Expanded Portrait #110',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id),
				expected_name
			)

		expected_names = (
			'Marine',
			'Gantrithor',
			'Flag (Blue) (Pl.12)',
			'Expanded Portrait #110',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, data_names=Assets.data_cache(Assets.DataReference.Portdata)),
				expected_name
			)

		expected_names = (
			'tmarine\\TMaTlk0',
			'UTassadar\\UTaTlk0',
			'UFlag12\\UF12Tlk0',
			'tmarine\\TMaFid0',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, portdatadat=portdatadat, portdatatbl=portdatatbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'tmarine\\TMaTlk0',
			'UTassadar\\UTaTlk0',
			'UFlag12\\UF12Tlk0',
			'tmarine\\TMaFid0',
		)
		decompiled_portdatatbl = TBL()
		decompiled_portdatatbl.strings = [decompile_string(string) for string in portdatatbl.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, portdatadat=portdatadat, portdatatbl=decompiled_portdatatbl, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'Marine (tmarine\\TMaTlk0)',
			'Gantrithor (UTassadar\\UTaTlk0)',
			'Flag (Blue) (Pl.12) (UFlag12\\UF12Tlk0)',
			'Expanded Portrait #110 (tmarine\\TMaFid0)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, data_names=Assets.data_cache(Assets.DataReference.Portdata), portdatadat=portdatadat, portdatatbl=portdatatbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Portrait',
			'My Other Cool Portrait',
			'Meh Portrait',
			'Not A Cool Portrait',
		)
		name_overrides = {
			0: (False, 'My Cool Portrait'),
			54: (False, 'My Other Cool Portrait'),
			109: (False, 'Meh Portrait'),
			110: (False, 'Not A Cool Portrait')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, data_names=Assets.data_cache(Assets.DataReference.Portdata), portdatadat=portdatadat, portdatatbl=portdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Marine (tmarine\\TMaTlk0) [V1]',
			'Gantrithor (UTassadar\\UTaTlk0) [V2]',
			'Flag (Blue) (Pl.12) (UFlag12\\UF12Tlk0) [V3]',
			'Expanded Portrait #110 (tmarine\\TMaFid0) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			54: (True, '[V2]'),
			109: (True, '[V3]'),
			110: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.portrait(entry_id, data_names=Assets.data_cache(Assets.DataReference.Portdata), portdatadat=portdatadat, portdatatbl=portdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_map_name(self):
		entry_ids = (0, 32, 64, 65)
		mapdatatbl = TBL()
		mapdatatbl.load_file(resource_path('mapdata.tbl', __file__))
		mapdatadat = CampaignDAT()
		mapdatadat.load_file(resource_path('mapdata.dat', __file__))
		mapdatadat.expand_entries()
		mapdatadat.get_entry(65).map_file = 2 # campaign\\terran\\terran01

		expected_names = (
			'Map #0',
			'Map #32',
			'Map #64',
			'Expanded Map #65',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id),
				expected_name
			)

		expected_names = (
			'tutorial',
			'BW - protoss02',
			'Unknown',
			'Expanded Map #65',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, data_names=Assets.data_cache(Assets.DataReference.Mapdata)),
				expected_name
			)

		expected_names = (
			'campaign\\terran\\tutorial',
			'campaign\\expprotoss\\protoss02',
			'Map #64',
			'campaign\\terran\\terran01',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, mapdatadat=mapdatadat, mapdatatbl=mapdatatbl, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'campaign\\terran\\tutorial',
			'campaign\\expprotoss\\protoss02',
			'Map #64',
			'campaign\\terran\\terran01',
		)
		decompiled_mapdatatbl = TBL()
		decompiled_mapdatatbl.strings = [decompile_string(string) for string in mapdatatbl.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, mapdatadat=mapdatadat, mapdatatbl=decompiled_mapdatatbl, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'tutorial (campaign\\terran\\tutorial)',
			'BW - protoss02 (campaign\\expprotoss\\protoss02)',
			'Unknown',
			'Expanded Map #65 (campaign\\terran\\terran01)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, data_names=Assets.data_cache(Assets.DataReference.Mapdata), mapdatadat=mapdatadat, mapdatatbl=mapdatatbl, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'My Cool Map',
			'My Other Cool Map',
			'Meh Map',
			'Not A Cool Map',
		)
		name_overrides = {
			0: (False, 'My Cool Map'),
			32: (False, 'My Other Cool Map'),
			64: (False, 'Meh Map'),
			65: (False, 'Not A Cool Map')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, data_names=Assets.data_cache(Assets.DataReference.Mapdata), mapdatadat=mapdatadat, mapdatatbl=mapdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'tutorial (campaign\\terran\\tutorial) [V1]',
			'BW - protoss02 (campaign\\expprotoss\\protoss02) [V2]',
			'Unknown [V3]',
			'Expanded Map #65 (campaign\\terran\\terran01) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			32: (True, '[V2]'),
			64: (True, '[V3]'),
			65: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.map(entry_id, data_names=Assets.data_cache(Assets.DataReference.Mapdata), mapdatadat=mapdatadat, mapdatatbl=mapdatatbl, data_names_usage=DataNamesUsage.combine, name_overrides=name_overrides),
				expected_name
			)

	def test_order_name(self):
		entry_ids = (0, 94, 188, 189)
		stat_txt = TBL()
		stat_txt.load_file(resource_path('stat_txt.tbl', __file__))
		ordersdat = OrdersDAT()
		ordersdat.load_file(resource_path('orders.dat', __file__))
		ordersdat.expand_entries()
		ordersdat.get_entry(189).label = 570 # "General Duke<0>"

		expected_names = (
			'Order #0',
			'Order #94',
			'Order #188',
			'Expanded Order #189',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id),
				expected_name
			)

		expected_names = (
			'Die',
			'Load Unit (Mobile Transport)',
			'Fatal',
			'Expanded Order #189',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders)),
				expected_name
			)

		expected_names = (
			'Die',
			'Pick Up',
			'Fatal',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore),
				expected_name
			)

		expected_names = (
			'Die',
			'Pick Up',
			'Fatal',
			'General Duke',
		)
		decompiled_stat_txt = TBL()
		decompiled_stat_txt.strings = [decompile_string(string) for string in stat_txt.strings]
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, ordersdat=ordersdat, stat_txt=decompiled_stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_decompile=False),
				expected_name
			)

		expected_names = (
			'Die',
			'Pick Up',
			'Fatal',
			'General Duke',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.ignore, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'Die',
			'Load Unit (Mobile Transport) (Pick Up)',
			'Fatal',
			'Expanded Order #189 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders), ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine),
				expected_name
			)

		expected_names = (
			'Die',
			'Load Unit (Mobile Transport) (Pick Up)',
			'Fatal',
			'Expanded Order #189 (General Duke)',
		)
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders), ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False),
				expected_name
			)

		expected_names = (
			'My Cool Order',
			'My Other Cool Order',
			'Meh Order',
			'Not A Cool Order',
		)
		name_overrides = {
			0: (False, 'My Cool Order'),
			94: (False, 'My Other Cool Order'),
			188: (False, 'Meh Order'),
			189: (False, 'Not A Cool Order')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders), ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)

		expected_names = (
			'Die [V1]',
			'Load Unit (Mobile Transport) (Pick Up) [V2]',
			'Fatal [V3]',
			'Expanded Order #189 (General Duke) [V4]',
		)
		name_overrides = {
			0: (True, '[V1]'),
			94: (True, '[V2]'),
			188: (True, '[V3]'),
			189: (True, '[V4]')
		}
		for (entry_id, expected_name) in zip(entry_ids, expected_names):
			self.assertEqual(
				DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders), ordersdat=ordersdat, stat_txt=stat_txt, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False, name_overrides=name_overrides),
				expected_name
			)
