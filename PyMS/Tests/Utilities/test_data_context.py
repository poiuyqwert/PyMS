
from ...Utilities.DataContext import DataContext
from ...FileFormats.TBL import TBL
from ...FileFormats.Graft.ButtonsGraft import ButtonsGraft
from ...Utilities import Assets
from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT, WeaponsDAT, ImagesDAT, SpritesDAT, FlingyDAT, SoundsDAT

from ..utils import resource_path

import os
import unittest

def _tbl(strings: list[str]) -> TBL:
	tbl = TBL()
	tbl.strings = strings
	return tbl

def _vanilla_stat_txt() -> TBL:
	tbl = TBL()
	tbl.load(resource_path(os.path.join('..', 'DAT', 'stat_txt.tbl'), __file__))
	return tbl

def _upgrades_dat(labels: dict[int, int]) -> UpgradesDAT:
	upgrades_dat = UpgradesDAT()
	upgrades_dat.new_file()
	for upgrade_id in range(upgrades_dat.entry_count()):
		upgrades_dat.get_entry(upgrade_id).label = labels.get(upgrade_id, 0)
	return upgrades_dat

def _techdata_dat(labels: dict[int, int]) -> TechDAT:
	techdata_dat = TechDAT()
	techdata_dat.new_file()
	for tech_id in range(techdata_dat.entry_count()):
		techdata_dat.get_entry(tech_id).label = labels.get(tech_id, 0)
	return techdata_dat

def _images_dat(grp_files: dict[int, int]) -> ImagesDAT:
	images_dat = ImagesDAT()
	images_dat.new_file()
	for image_id in range(images_dat.entry_count()):
		images_dat.get_entry(image_id).grp_file = grp_files.get(image_id, 0)
	return images_dat

def _sprites_dat(images: dict[int, int]) -> SpritesDAT:
	# Sprites not in `images` use the last image, which `_images_dat` leaves without a name
	sprites_dat = SpritesDAT()
	sprites_dat.new_file()
	for sprite_id in range(sprites_dat.entry_count()):
		sprites_dat.get_entry(sprite_id).image = images.get(sprite_id, ImagesDAT.FORMAT.entries - 1)
	return sprites_dat

def _flingy_dat(sprites: dict[int, int]) -> FlingyDAT:
	# Flingy not in `sprites` use the last sprite, which `_sprites_dat` leaves without a name
	flingy_dat = FlingyDAT()
	flingy_dat.new_file()
	for flingy_id in range(flingy_dat.entry_count()):
		flingy_dat.get_entry(flingy_id).sprite = sprites.get(flingy_id, SpritesDAT.FORMAT.entries - 1)
	return flingy_dat

def _sounds_dat(sound_files: dict[int, int]) -> SoundsDAT:
	sounds_dat = SoundsDAT()
	sounds_dat.new_file()
	for sound_id in range(sounds_dat.entry_count()):
		sounds_dat.get_entry(sound_id).sound_file = sound_files.get(sound_id, 0)
	return sounds_dat

class Test_StatTxt(unittest.TestCase):
	def test_valid_id_returns_string(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Marine\x00', 'Ghost\x00', 'Vulture\x00']))
		self.assertEqual(data_context.stat_txt_string(0), 'Marine')
		self.assertEqual(data_context.stat_txt_string(2), 'Vulture')

	def test_out_of_upper_bound_returns_none(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Marine\x00']))
		self.assertIsNone(data_context.stat_txt_string(1))

	def test_negative_id_returns_none(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Marine\x00', 'Ghost\x00', 'Vulture\x00']))
		self.assertIsNone(data_context.stat_txt_string(-1))

	def test_no_tbl_returns_none(self) -> None:
		data_context = DataContext()
		self.assertIsNone(data_context.stat_txt_string(0))
		self.assertIsNone(data_context.stat_txt_strings())
		self.assertIsNone(data_context.stat_txt_id('Marine'))

	def test_strings_and_id_round_trip(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Marine\x00', 'Ghost\x00']))
		self.assertEqual(data_context.stat_txt_strings(), ['Marine', 'Ghost'])
		self.assertEqual(data_context.stat_txt_id('Ghost'), 1)
		self.assertIsNone(data_context.stat_txt_id('Vulture'))

class Test_Units(unittest.TestCase):
	def test_vanilla_names_keep_subtitle_separator(self) -> None:
		data_context = DataContext(stat_txt_tbl=_vanilla_stat_txt())
		self.assertEqual(data_context.unit_name(0), 'Terran Marine')
		self.assertEqual(data_context.unit_name(5), 'Terran Siege Tank<0>Tank Mode')
		self.assertEqual(data_context.unit_name(20), 'Jim Raynor<0>Marine')

	def test_vanilla_display_names_combine_data_and_tbl_names(self) -> None:
		data_context = DataContext(stat_txt_tbl=_vanilla_stat_txt())
		self.assertEqual(data_context.unit_display_name(0), 'Terran Marine')
		self.assertEqual(data_context.unit_display_name(20), 'Jim Raynor (Marine)')

	def test_only_units_come_from_stat_txt(self) -> None:
		strings = ['Unit\x00*\x00'] * (UnitsDAT.FORMAT.entries + 5)
		data_context = DataContext(stat_txt_tbl=_tbl(strings))
		self.assertEqual(data_context.unit_ids('Unit'), tuple(range(UnitsDAT.FORMAT.entries)))

	def test_unitnames_tbl_takes_precedence(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Marine\x00*\x00']), unitnames_tbl=_tbl(['Custom\x00*\x00']))
		self.assertEqual(data_context.unit_name(0), 'Custom')

	def test_no_tbl_has_no_names(self) -> None:
		data_context = DataContext()
		self.assertIsNone(data_context.unit_name(0))
		self.assertEqual(data_context.unit_ids('Terran Marine'), ())
		self.assertEqual(data_context.unit_display_name(0), 'Terran Marine')

	def test_entry_count_defaults_to_format(self) -> None:
		self.assertEqual(DataContext().unit_entry_count, UnitsDAT.FORMAT.entries)

	def test_entry_count_follows_dat(self) -> None:
		units_dat = UnitsDAT()
		units_dat.new_file()
		self.assertEqual(DataContext(units_dat=units_dat).unit_entry_count, units_dat.entry_count())

	def test_entry_count_is_limited_by_shorter_unitnames_tbl(self) -> None:
		data_context = DataContext(unitnames_tbl=_tbl(['Unit\x00*\x00'] * 10))
		self.assertEqual(data_context.unit_entry_count, 10)
		self.assertIsNone(data_context.unit_display_name(10))

	def test_entry_count_is_limited_by_shorter_dat(self) -> None:
		data_context = DataContext(unitnames_tbl=_tbl([f'Unit {n}\x00*\x00' for n in range(UnitsDAT.FORMAT.entries + 10)]))
		self.assertEqual(data_context.unit_entry_count, UnitsDAT.FORMAT.entries)
		self.assertIsNone(data_context.unit_name(UnitsDAT.FORMAT.entries))

	def test_name_of_multiple_ids(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Same\x00*\x00', 'Same\x00*\x00', 'Other\x00*\x00']))
		self.assertEqual(data_context.unit_ids('Same'), (0, 1))
		self.assertIsNone(data_context.unit_name(0))
		self.assertIsNone(data_context.unit_name(1))
		self.assertEqual(data_context.unit_name(2), 'Other')
		self.assertEqual(data_context.unit_display_name(0), 'Terran Marine (Same)')

	def test_out_of_range_ids_have_no_names(self) -> None:
		data_context = DataContext(stat_txt_tbl=_vanilla_stat_txt())
		self.assertIsNone(data_context.unit_name(-1))
		self.assertIsNone(data_context.unit_name(UnitsDAT.FORMAT.entries))
		self.assertIsNone(data_context.unit_display_name(-1))
		self.assertIsNone(data_context.unit_display_name(UnitsDAT.FORMAT.entries))

class Test_LabelNames(unittest.TestCase):
	def test_upgrade_name_uses_label(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Zero\x00', 'One\x00']), upgrades_dat=_upgrades_dat({3: 2}))
		self.assertEqual(data_context.upgrade_name(3), 'One')
		self.assertEqual(data_context.upgrade_ids('One'), (3,))

	def test_no_label_has_no_name_but_has_display_name(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Zero\x00']), upgrades_dat=_upgrades_dat({}))
		self.assertIsNone(data_context.upgrade_name(0))
		self.assertEqual(data_context.upgrade_display_name(0), 'Terran Infantry Armor')

	def test_label_past_tbl_has_no_name(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Zero\x00']), upgrades_dat=_upgrades_dat({0: 5}))
		self.assertIsNone(data_context.upgrade_name(0))

	def test_no_dat_has_no_names(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Zero\x00']))
		self.assertIsNone(data_context.upgrade_name(0))
		self.assertIsNone(data_context.tech_name(0))
		self.assertIsNone(data_context.order_name(0))
		self.assertIsNone(data_context.weapon_name(0))

	def test_hotkey_and_subtitle_are_dropped(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Stim Packs\x00t\x00\x00']), techdata_dat=_techdata_dat({0: 1}))
		self.assertEqual(data_context.tech_name(0), 'Stim Packs')

	def test_unique_name(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Same\x00']), upgrades_dat=_upgrades_dat({0: 1, 1: 1}))
		self.assertEqual(data_context.upgrade_ids('Same'), (0, 1))
		self.assertIsNone(data_context.upgrade_name(1))

	def test_out_of_range_ids_have_no_names(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Zero\x00']), upgrades_dat=_upgrades_dat({}))
		self.assertIsNone(data_context.upgrade_name(-1))
		self.assertIsNone(data_context.upgrade_name(UpgradesDAT.FORMAT.entries))
		self.assertIsNone(data_context.upgrade_display_name(-1))

	def test_entry_counts(self) -> None:
		data_context = DataContext()
		self.assertEqual(data_context.upgrade_entry_count, UpgradesDAT.FORMAT.entries)
		self.assertEqual(data_context.tech_entry_count, TechDAT.FORMAT.entries)
		self.assertEqual(data_context.order_entry_count, OrdersDAT.FORMAT.entries)
		self.assertEqual(data_context.weapon_entry_count, WeaponsDAT.FORMAT.entries)
		self.assertEqual(data_context.image_entry_count, ImagesDAT.FORMAT.entries)
		self.assertEqual(data_context.sprite_entry_count, SpritesDAT.FORMAT.entries)
		self.assertEqual(data_context.flingy_entry_count, FlingyDAT.FORMAT.entries)
		self.assertEqual(data_context.sound_entry_count, SoundsDAT.FORMAT.entries)
		empty_upgrades_dat = UpgradesDAT()
		data_context.set_upgrades_dat(empty_upgrades_dat)
		self.assertEqual(data_context.upgrade_entry_count, empty_upgrades_dat.entry_count())

class Test_GraphicsNames(unittest.TestCase):
	def test_sprite_and_flingy_use_image_name(self) -> None:
		data_context = DataContext(images_tbl=_tbl(['zerg\\avenger.grp\x00']), images_dat=_images_dat({4: 1}), sprites_dat=_sprites_dat({2: 4}), flingy_dat=_flingy_dat({7: 2}))
		self.assertEqual(data_context.image_name(4), 'zerg\\avenger.grp')
		self.assertEqual(data_context.sprite_name(2), 'zerg\\avenger.grp')
		self.assertEqual(data_context.flingy_name(7), 'zerg\\avenger.grp')

	def test_sound_name_uses_sound_file(self) -> None:
		data_context = DataContext(sounds_tbl=_tbl(['Misc\\Buzz.wav\x00']), sounds_dat=_sounds_dat({3: 1}))
		self.assertEqual(data_context.sound_name(3), 'Misc\\Buzz.wav')

class Test_SharedImageNames(unittest.TestCase):
	def test_sprite_and_flingy_are_named_by_a_shared_image_name(self) -> None:
		# Images 0 and 1 share a GRP, but only sprite 0 (and flingy 0) use them, so those names are unique
		data_context = DataContext(images_tbl=_tbl(['shared.grp\x00']), images_dat=_images_dat({0: 1, 1: 1}), sprites_dat=_sprites_dat({0: 1}), flingy_dat=_flingy_dat({0: 0}))
		self.assertEqual(data_context.image_ids('shared.grp'), (0, 1))
		self.assertIsNone(data_context.image_name(0))
		self.assertEqual(data_context.sprite_name(0), 'shared.grp')
		self.assertEqual(data_context.flingy_name(0), 'shared.grp')

class Test_Invalidation(unittest.TestCase):
	def test_stat_txt_tbl(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['Old\x00*\x00']), upgrades_dat=_upgrades_dat({0: 1}), techdata_dat=_techdata_dat({0: 1}))
		self.assertEqual((data_context.unit_name(0), data_context.upgrade_name(0), data_context.tech_name(0)), ('Old', 'Old', 'Old'))
		self.assertEqual(data_context.unit_ids('Old'), (0,))
		self.assertIn('Old', data_context.upgrade_display_name(0) or '')
		data_context.set_stat_txt_tbl(_tbl(['New\x00*\x00']))
		self.assertEqual((data_context.unit_name(0), data_context.upgrade_name(0), data_context.tech_name(0)), ('New', 'New', 'New'))
		self.assertEqual(data_context.unit_ids('Old'), ())
		self.assertIn('New', data_context.upgrade_display_name(0) or '')

	def test_unitnames_tbl(self) -> None:
		data_context = DataContext(unitnames_tbl=_tbl(['Old\x00*\x00']))
		self.assertEqual(data_context.unit_name(0), 'Old')
		data_context.set_unitnames_tbl(_tbl(['New\x00*\x00', 'Other\x00*\x00']))
		self.assertEqual(data_context.unit_name(0), 'New')
		self.assertEqual(data_context.unit_entry_count, 2)

	def test_units_dat(self) -> None:
		data_context = DataContext(unitnames_tbl=_tbl([f'Name {n}\x00*\x00' for n in range(5)]), units_dat=UnitsDAT())
		self.assertIsNone(data_context.unit_name(0))
		units_dat = UnitsDAT()
		units_dat.new_file()
		data_context.set_units_dat(units_dat)
		self.assertEqual(data_context.unit_name(0), 'Name 0')

	def test_upgrades_dat(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['A\x00', 'B\x00']), upgrades_dat=_upgrades_dat({0: 1}))
		self.assertEqual(data_context.upgrade_name(0), 'A')
		data_context.set_upgrades_dat(_upgrades_dat({0: 2}))
		self.assertEqual(data_context.upgrade_name(0), 'B')

	def test_techdata_dat(self) -> None:
		data_context = DataContext(stat_txt_tbl=_tbl(['A\x00', 'B\x00']), techdata_dat=_techdata_dat({0: 1}))
		self.assertEqual(data_context.tech_name(0), 'A')
		data_context.set_techdata_dat(_techdata_dat({0: 2}))
		self.assertEqual(data_context.tech_name(0), 'B')

	def test_orders_dat(self) -> None:
		orders_dat = OrdersDAT()
		orders_dat.new_file()
		orders_dat.get_entry(0).label = 1
		data_context = DataContext(stat_txt_tbl=_tbl(['A\x00', 'B\x00']))
		self.assertIsNone(data_context.order_name(0))
		data_context.set_orders_dat(orders_dat)
		self.assertEqual(data_context.order_name(0), 'A')

	def test_weapons_dat(self) -> None:
		weapons_dat = WeaponsDAT()
		weapons_dat.new_file()
		weapons_dat.get_entry(0).label = 2
		data_context = DataContext(stat_txt_tbl=_tbl(['A\x00', 'B\x00']))
		self.assertIsNone(data_context.weapon_name(0))
		data_context.set_weapons_dat(weapons_dat)
		self.assertEqual(data_context.weapon_name(0), 'B')

	def test_images_tbl(self) -> None:
		data_context = DataContext(images_tbl=_tbl(['old.grp\x00']), images_dat=_images_dat({0: 1}), sprites_dat=_sprites_dat({0: 0}), flingy_dat=_flingy_dat({0: 0}))
		self.assertEqual((data_context.image_name(0), data_context.sprite_name(0), data_context.flingy_name(0)), ('old.grp', 'old.grp', 'old.grp'))
		data_context.set_images_tbl(_tbl(['new.grp\x00']))
		self.assertEqual((data_context.image_name(0), data_context.sprite_name(0), data_context.flingy_name(0)), ('new.grp', 'new.grp', 'new.grp'))

	def test_images_dat(self) -> None:
		data_context = DataContext(images_tbl=_tbl(['a.grp\x00', 'b.grp\x00']), images_dat=_images_dat({0: 1}), sprites_dat=_sprites_dat({0: 0}), flingy_dat=_flingy_dat({0: 0}))
		self.assertEqual((data_context.image_name(0), data_context.sprite_name(0), data_context.flingy_name(0)), ('a.grp', 'a.grp', 'a.grp'))
		data_context.set_images_dat(_images_dat({0: 2}))
		self.assertEqual((data_context.image_name(0), data_context.sprite_name(0), data_context.flingy_name(0)), ('b.grp', 'b.grp', 'b.grp'))

	def test_sprites_dat(self) -> None:
		data_context = DataContext(images_tbl=_tbl(['a.grp\x00', 'b.grp\x00']), images_dat=_images_dat({0: 1, 1: 2}), sprites_dat=_sprites_dat({0: 0}), flingy_dat=_flingy_dat({0: 0}))
		self.assertEqual((data_context.sprite_name(0), data_context.flingy_name(0)), ('a.grp', 'a.grp'))
		data_context.set_sprites_dat(_sprites_dat({0: 1}))
		self.assertEqual((data_context.sprite_name(0), data_context.flingy_name(0)), ('b.grp', 'b.grp'))

	def test_flingy_dat(self) -> None:
		data_context = DataContext(images_tbl=_tbl(['a.grp\x00', 'b.grp\x00']), images_dat=_images_dat({0: 1, 1: 2}), sprites_dat=_sprites_dat({0: 0, 1: 1}), flingy_dat=_flingy_dat({0: 0}))
		self.assertEqual(data_context.flingy_name(0), 'a.grp')
		data_context.set_flingy_dat(_flingy_dat({0: 1}))
		self.assertEqual(data_context.flingy_name(0), 'b.grp')

	def test_sounds_tbl_and_dat(self) -> None:
		data_context = DataContext(sounds_tbl=_tbl(['a.wav\x00', 'b.wav\x00']), sounds_dat=_sounds_dat({0: 1}))
		self.assertEqual(data_context.sound_name(0), 'a.wav')
		data_context.set_sounds_dat(_sounds_dat({0: 2}))
		self.assertEqual(data_context.sound_name(0), 'b.wav')
		data_context.set_sounds_tbl(_tbl(['c.wav\x00', 'd.wav\x00']))
		self.assertEqual(data_context.sound_name(0), 'd.wav')

class Test_Paths(unittest.TestCase):
	def test_image_path_uses_one_based_grp_file(self) -> None:
		images_dat = _images_dat({0: 1, 1: 2})
		data_context = DataContext(images_tbl=_tbl(['zerg\\avenger.grp\x00', 'zerg\\zavbirth.grp\x00']), images_dat=images_dat)
		self.assertEqual(data_context.image_path(0), 'zerg\\avenger.grp')
		self.assertEqual(data_context.image_path(1), 'zerg\\zavbirth.grp')
		self.assertIsNone(data_context.image_path(2))
		self.assertIsNone(data_context.image_path(-1))
		self.assertIsNone(data_context.image_path(images_dat.entry_count()))

	def test_sound_path_uses_one_based_sound_file(self) -> None:
		sounds_dat = _sounds_dat({0: 2})
		data_context = DataContext(sounds_tbl=_tbl(['Misc\\Buzz.wav\x00', 'Misc\\PError.wav\x00']), sounds_dat=sounds_dat)
		self.assertEqual(data_context.sound_path(0), 'Misc\\PError.wav')
		self.assertIsNone(data_context.sound_path(1))
		self.assertIsNone(data_context.sound_path(-1))
		self.assertIsNone(data_context.sound_path(sounds_dat.entry_count()))

	def test_no_files_have_no_paths(self) -> None:
		data_context = DataContext()
		self.assertIsNone(data_context.image_path(0))
		self.assertIsNone(data_context.sound_path(0))

class Test_OtherNames(unittest.TestCase):
	def test_icon_and_button_set_names(self) -> None:
		data_context = DataContext()
		self.assertIsNotNone(data_context.icon_name(0))
		self.assertIsNone(data_context.icon_name(-1))
		self.assertIsNotNone(data_context.button_set_name(0))
		self.assertIsNone(data_context.button_set_name(-1))

	def test_button_card_names_are_units_then_special_button_cards(self) -> None:
		data_context = DataContext(stat_txt_tbl=_vanilla_stat_txt())
		self.assertEqual(data_context.button_card_name(0), data_context.unit_display_name(0))
		self.assertEqual(data_context.button_card_name(ButtonsGraft.SPECIAL_BUTTON_CARDS_START - 1), data_context.unit_display_name(ButtonsGraft.SPECIAL_BUTTON_CARDS_START - 1))
		self.assertEqual(data_context.button_card_name(ButtonsGraft.SPECIAL_BUTTON_CARDS_START), Assets.data_cache(Assets.DataReference.ButtonCards)[0])
		self.assertIsNone(data_context.button_card_name(-1))
		self.assertIsNone(data_context.button_card_name(ButtonsGraft.SPECIAL_BUTTON_CARDS_START + len(Assets.data_cache(Assets.DataReference.ButtonCards))))
