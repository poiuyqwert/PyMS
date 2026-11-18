
from ...Utilities.DataContext import DataContext, IconFrame, Race, CmdIconState
from ...Utilities.PyMSError import PyMSError
from ...Utilities.TextPreview.Layout import TextStyle
from ...FileFormats.TBL import TBL
from ...FileFormats.Graft.ButtonsGraft import ButtonsGraft
from ...Utilities import Assets
from ...FileFormats.GRP import CacheGRP
from ...FileFormats.FNT import FNT, COLOR_CODES_INGAME
from ...FileFormats.PCX import PCX
from ...FileFormats.DAT import DATUnit, DATImage, UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT, WeaponsDAT, ImagesDAT, SpritesDAT, FlingyDAT, SoundsDAT

from ..utils import resource_path

import os
import unittest
from unittest.mock import Mock, patch

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

def _icons_grp(frames: int) -> CacheGRP:
	grp = CacheGRP()
	grp.frames = frames
	grp.width = 40
	grp.height = 30
	return grp

# A ticon.pcx with `remap` after its enabled row (so from the disabled row on)
def _ticon_pcx(remap: list[int]) -> PCX:
	pcx = PCX()
	pcx.image = [[0] * 16 + remap]
	return pcx

FRAME_TO_PHOTO = 'PyMS.Utilities.DataContext.GRP.frame_to_photo'
FRAME_PIXELS = 'PyMS.Utilities.DataContext.GRP.frame_pixels'
IMAGE_BOUNDS = 'PyMS.Utilities.DataContext.GRP.image_bounds'

class Test_Icons(unittest.TestCase):
	PALETTE = [(index, index, index) for index in range(256)]

	def test_names_without_a_grp_are_the_known_icons(self) -> None:
		data_context = DataContext()
		self.assertEqual(tuple(data_context.icon_names()), Assets.data_cache(Assets.DataReference.Icons))
		self.assertEqual(data_context.icon_frame_count(), len(Assets.data_cache(Assets.DataReference.Icons)))
		self.assertEqual(data_context.icon_frame_size(), (36, 34))

	def test_names_match_the_grp_frames(self) -> None:
		known = Assets.data_cache(Assets.DataReference.Icons)
		data_context = DataContext(cmdicons_grp=_icons_grp(len(known) + 2))
		self.assertEqual(tuple(data_context.icon_names()), known + ('Unknown', 'Unknown'))
		data_context.set_cmdicons_grp(_icons_grp(3))
		self.assertEqual(tuple(data_context.icon_names()), known[:3])
		self.assertEqual(data_context.icon_frame_count(), 3)
		self.assertEqual(data_context.icon_frame_size(), (40, 30))

	def test_no_icon_without_a_grp_or_palette(self) -> None:
		self.assertIsNone(DataContext(palettes={'Icons': self.PALETTE}).get_cmdicon(0))
		self.assertIsNone(DataContext(cmdicons_grp=_icons_grp(3)).get_cmdicon(0))

	def test_no_icon_past_the_frames(self) -> None:
		data_context = DataContext(cmdicons_grp=_icons_grp(3), palettes={'Icons': self.PALETTE})
		self.assertIsNone(data_context.get_cmdicon(3))
		self.assertIsNone(data_context.get_cmdicon(-1))

	def test_icons_are_cached_until_the_files_change(self) -> None:
		data_context = DataContext(cmdicons_grp=_icons_grp(3), palettes={'Icons': self.PALETTE})
		with patch(FRAME_PIXELS, return_value=([[1]], 0)), patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO, side_effect=lambda *_, **__: object()) as frame_to_photo:
			image = data_context.get_cmdicon(1)
			self.assertIs(data_context.get_cmdicon(1), image)
			self.assertEqual(frame_to_photo.call_count, 1)
			for change in (lambda: data_context.set_cmdicons_grp(_icons_grp(3)), lambda: data_context.set_ticon_pcx(None), lambda: data_context.set_palette('Icons', self.PALETTE)):
				change()
				self.assertIsNot(data_context.get_cmdicon(1), image)
				image = data_context.get_cmdicon(1)

	def test_icon_states_remap_with_their_ticon_row(self) -> None:
		# ticon.pcx has a row of 16 remap colors per state: enabled (unused, the palette is drawn as it is), disabled, then highlighted
		data_context = DataContext(cmdicons_grp=_icons_grp(3), palettes={'Icons': self.PALETTE}, ticon_pcx=_ticon_pcx([100, 101] + [0] * 14 + [200, 201]))
		with patch(FRAME_PIXELS, return_value=([[1]], 0)), patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO) as frame_to_photo:
			data_context.get_cmdicon(0)
			self.assertEqual(frame_to_photo.call_args.args[0], self.PALETTE)
			data_context.get_cmdicon(0, CmdIconState.disabled)
			# Color 2 is remapped to color 0 as it was before the remap
			self.assertEqual(frame_to_photo.call_args.args[0][:3], [(100, 100, 100), (101, 101, 101), (0, 0, 0)])
			self.assertEqual(frame_to_photo.call_args.args[0][16], (16, 16, 16))
			data_context.get_cmdicon(0, CmdIconState.highlighted)
			self.assertEqual(frame_to_photo.call_args.args[0][:2], [(200, 200, 200), (201, 201, 201)])

	def test_states_past_the_end_of_ticon_are_not_remapped(self) -> None:
		data_context = DataContext(cmdicons_grp=_icons_grp(3), palettes={'Icons': self.PALETTE}, ticon_pcx=_ticon_pcx([100, 101]))
		with patch(FRAME_PIXELS, return_value=([[1]], 0)), patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO) as frame_to_photo:
			data_context.get_cmdicon(0, CmdIconState.highlighted)
			self.assertEqual(frame_to_photo.call_args.args[0], self.PALETTE)

def _resource_icons_grp(frames: int) -> CacheGRP:
	grp = CacheGRP()
	grp.frames = frames
	return grp

class Test_ResourceIcons(unittest.TestCase):
	PALETTE = [(index, index, index) for index in range(256)]

	def test_no_icon_without_a_grp_or_palette(self) -> None:
		self.assertIsNone(DataContext(palettes={'Units': self.PALETTE}).get_icon(IconFrame.minerals))
		self.assertIsNone(DataContext(icons_grp=_resource_icons_grp(10)).get_icon(IconFrame.minerals))

	def test_no_icon_past_the_frames(self) -> None:
		data_context = DataContext(icons_grp=_resource_icons_grp(3), palettes={'Units': self.PALETTE})
		self.assertIsNone(data_context.get_icon(IconFrame.zerg_supply))

	def test_icons_use_the_units_palette_and_are_cached_until_the_files_change(self) -> None:
		data_context = DataContext(icons_grp=_resource_icons_grp(10), palettes={'Units': self.PALETTE, 'Icons': []})
		with patch(FRAME_PIXELS, return_value=([[1]], 0)) as frame_pixels, patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO, side_effect=lambda *_, **__: object()) as frame_to_photo:
			icon = data_context.get_icon(IconFrame.terran_gas)
			self.assertEqual(frame_pixels.call_args.args[1], IconFrame.terran_gas)
			self.assertEqual(frame_to_photo.call_args.args[0], self.PALETTE)
			self.assertIs(data_context.get_icon(IconFrame.terran_gas), icon)
			# Other palettes don't affect the icons
			data_context.set_palette('Icons', self.PALETTE)
			self.assertIs(data_context.get_icon(IconFrame.terran_gas), icon)
			for change in (lambda: data_context.set_icons_grp(_resource_icons_grp(10)), lambda: data_context.set_palette('Units', self.PALETTE)):
				change()
				self.assertIsNot(data_context.get_icon(IconFrame.terran_gas), icon)
				icon = data_context.get_icon(IconFrame.terran_gas)

	def test_race_frames(self) -> None:
		self.assertEqual(IconFrame.gas(Race.terran), IconFrame.terran_gas)
		self.assertEqual(IconFrame.supply(Race.protoss), IconFrame.protoss_supply)
		self.assertEqual(IconFrame.energy(Race.zerg), IconFrame.zerg_energy)
		# Without a race, the Zerg icons are used
		self.assertEqual(IconFrame.gas(None), IconFrame.zerg_gas)
		self.assertEqual(IconFrame.supply(None), IconFrame.zerg_supply)
		self.assertEqual(IconFrame.energy(None), IconFrame.zerg_energy)

LETTER_TO_PHOTO = 'PyMS.Utilities.DataContext.letter_to_photo'

def _font(letters: int) -> FNT:
	font = FNT()
	font.start = 32
	font.letters = [[[1]] for _ in range(letters)]
	font.sizes = [(1, 1, 0, 0) for _ in range(letters)]
	return font

class Test_TextGlyphs(unittest.TestCase):
	def test_no_glyph_for_unknown_letters_or_colors(self) -> None:
		font = _font(2)
		data_context = DataContext(font8_fnt=font, tfontgam_pcx=PCX())
		assert data_context.tfontgam_pcx is not None
		with patch(LETTER_TO_PHOTO) as letter_to_photo:
			self.assertIsNone(data_context.text_glyph(TextStyle(font, data_context.tfontgam_pcx, COLOR_CODES_INGAME), 2, 2))
			# 9 isn't a color code in game
			self.assertIsNone(data_context.text_glyph(TextStyle(font, data_context.tfontgam_pcx, COLOR_CODES_INGAME), 0, 9))
		letter_to_photo.assert_not_called()

	def test_glyphs_are_drawn_with_the_remap_and_cached_until_the_fonts_change(self) -> None:
		font = _font(2)
		tfontgam = PCX()
		data_context = DataContext(font8_fnt=font, tfontgam_pcx=tfontgam)
		style = TextStyle(font, tfontgam, COLOR_CODES_INGAME)
		with patch(LETTER_TO_PHOTO, side_effect=lambda *_: object()) as letter_to_photo:
			glyph = data_context.text_glyph(style, 1, 4)
			self.assertEqual(letter_to_photo.call_args.args, (tfontgam, font.letters[1], 4, COLOR_CODES_INGAME))
			self.assertIs(data_context.text_glyph(style, 1, 4), glyph)
			self.assertIsNot(data_context.text_glyph(style, 1, 3), glyph)
			changes = (
				lambda: data_context.set_font8_fnt(font),
				lambda: data_context.set_font10_fnt(None),
				lambda: data_context.set_font14_fnt(None),
				lambda: data_context.set_font16_fnt(None),
				lambda: data_context.set_font16x_fnt(None),
				lambda: data_context.set_tfontgam_pcx(tfontgam),
				lambda: data_context.set_tfont_pcx(None),
			)
			for change in changes:
				change()
				self.assertIsNot(data_context.text_glyph(style, 1, 4), glyph)
				glyph = data_context.text_glyph(style, 1, 4)

MPQ_SUPPORTED = 'PyMS.Utilities.DataContext.MPQ.supported'
CACHE_GRP = 'PyMS.Utilities.DataContext.GRP.CacheGRP'

class _StubCacheGRP:
	def __init__(self) -> None:
		self.frames = 0
		self.loaded: list[object] = []

	def load(self, file: object) -> None:
		self.frames = 3
		self.loaded.append(file)

class Test_GRPFrames(unittest.TestCase):
	PALETTE = [(index, index, index) for index in range(256)]

	def _data_context(self, **kwargs: object) -> tuple[DataContext, Mock]:
		mpq_handler = Mock()
		mpq_handler.load_file.side_effect = lambda path: path
		data_context = DataContext(mpq_handler=mpq_handler, palettes={'Units': self.PALETTE, 'Terrain': self.PALETTE, 'gfire': self.PALETTE}, **kwargs) # type: ignore[arg-type]
		return data_context, mpq_handler

	def test_no_frame_without_a_handler_palette_or_mpq_support(self) -> None:
		with patch(MPQ_SUPPORTED, return_value=True):
			self.assertIsNone(DataContext(palettes={'Units': self.PALETTE}).get_grp_frame('marine.grp'))
			data_context, _ = self._data_context()
			self.assertIsNone(data_context.get_grp_frame('marine.grp', palette='bfire'))
		with patch(MPQ_SUPPORTED, return_value=False):
			data_context, _ = self._data_context()
			self.assertIsNone(data_context.get_grp_frame('marine.grp'))

	def test_no_frame_when_the_grp_fails_to_load(self) -> None:
		data_context, mpq_handler = self._data_context()
		mpq_handler.load_file.side_effect = PyMSError('Load', 'Missing file')
		with patch(MPQ_SUPPORTED, return_value=True):
			self.assertIsNone(data_context.get_grp_frame('marine.grp'))

	def test_frames_load_from_the_unit_folder_with_a_palette_from_the_path(self) -> None:
		data_context, mpq_handler = self._data_context()
		with patch(MPQ_SUPPORTED, return_value=True), patch(CACHE_GRP, _StubCacheGRP), patch(FRAME_PIXELS, return_value=([[1]], 0)), patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO) as frame_to_photo:
			data_context.get_grp_frame('terran\\marine.grp')
			mpq_handler.load_file.assert_called_with('MPQ:unit\\terran\\marine.grp')
			data_context.get_grp_frame('thingy\\tileset\\x.grp', is_full_path=True)
			mpq_handler.load_file.assert_called_with('MPQ:thingy\\tileset\\x.grp')
			data_context.get_grp_frame('fire.grp', draw_function=DATImage.DrawFunction.use_remapping, remapping=DATImage.Remapping.gfire)
		self.assertEqual(frame_to_photo.call_count, 3)

	def test_each_frame_is_drawn_and_cached(self) -> None:
		data_context, mpq_handler = self._data_context()
		with patch(MPQ_SUPPORTED, return_value=True), patch(CACHE_GRP, _StubCacheGRP), patch(FRAME_PIXELS, return_value=([[1]], 0)) as frame_pixels, patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO, side_effect=lambda *_, **__: object()):
			first = data_context.get_grp_frame('marine.grp', frame=0)
			second = data_context.get_grp_frame('marine.grp', frame=1)
			self.assertIsNot(first, second)
			self.assertEqual([call.args[1] for call in frame_pixels.call_args_list], [0, 1])
			self.assertIs(data_context.get_grp_frame('marine.grp', frame=1), second)
			self.assertIsNone(data_context.get_grp_frame('marine.grp', frame=3))
			# The GRP is only loaded once for all its frames
			self.assertEqual(mpq_handler.load_file.call_count, 1)
			data_context.set_palette('Units', self.PALETTE)
			self.assertIsNot(data_context.get_grp_frame('marine.grp', frame=1), second)

	def test_image_frames_use_the_images_tbl_path(self) -> None:
		images_dat = _images_dat({0: 2, 1: 0})
		data_context, mpq_handler = self._data_context(images_dat=images_dat, images_tbl=_tbl(['a.grp\x00', 'zerg\\drone.grp<0>']))
		with patch(MPQ_SUPPORTED, return_value=True), patch(CACHE_GRP, _StubCacheGRP), patch(FRAME_PIXELS, return_value=([[1]], 0)), patch(IMAGE_BOUNDS), patch(FRAME_TO_PHOTO):
			self.assertIsNotNone(data_context.get_image_frame(0))
			mpq_handler.load_file.assert_called_with('MPQ:unit\\zerg\\drone.grp')
			# No GRP file
			self.assertIsNone(data_context.get_image_frame(1))
		self.assertIsNone(DataContext().get_image_frame(0))

class Test_Race(unittest.TestCase):
	def test_from_staredit_group_flags(self) -> None:
		self.assertEqual(Race.from_staredit_group_flags(DATUnit.StarEditGroupFlag.protoss | DATUnit.StarEditGroupFlag.men), Race.protoss)
		# The game checks Zerg, then Protoss, then Terran
		self.assertEqual(Race.from_staredit_group_flags(DATUnit.StarEditGroupFlag.terran | DATUnit.StarEditGroupFlag.protoss), Race.protoss)
		self.assertIsNone(Race.from_staredit_group_flags(DATUnit.StarEditGroupFlag.men))
