from ...FileFormats.DAT import UnitsDAT, UpgradesDAT, TechDAT, DATUnit
from ...FileFormats.FNT import FNT
from ...FileFormats.PCX import PCX
from ...FileFormats.TBL import end_at_null
from ...Utilities.DataContext import DataContext, Race
from ...Utilities.TextPreview.HotkeyString import HotkeyString, TooltipCosts, TooltipKind
from ...Utilities.TextPreview.Layout import GlyphItem
from ...Utilities.TextPreview.TextDrawing import TextDrawing
from ...Utilities import Assets

import unittest

def _data_context() -> DataContext:
	units_dat = UnitsDAT()
	units_dat.new_file()
	marine = units_dat.get_entry(0)
	marine.mineral_cost = 50
	marine.vespene_cost = 0
	marine.supply_required.whole = 1
	marine.supply_required.half = False
	marine.staredit_group_flags = DATUnit.StarEditGroupFlag.terran
	zergling = units_dat.get_entry(37)
	zergling.mineral_cost = 50
	zergling.supply_required.whole = 0
	zergling.supply_required.half = True
	zergling.staredit_group_flags = DATUnit.StarEditGroupFlag.zerg
	zergling.special_ability_flags = DATUnit.SpecialAbilityFlag.two_units_in_one_egg
	hydralisk = units_dat.get_entry(38)
	hydralisk.mineral_cost = 75
	hydralisk.vespene_cost = 25
	hydralisk.supply_required.whole = 1
	hydralisk.supply_required.half = True
	hydralisk.staredit_group_flags = DATUnit.StarEditGroupFlag.zerg
	barracks = units_dat.get_entry(111)
	barracks.mineral_cost = 150
	barracks.staredit_group_flags = DATUnit.StarEditGroupFlag.terran | DATUnit.StarEditGroupFlag.building
	critter = units_dat.get_entry(89)
	critter.mineral_cost = 1
	critter.supply_required.whole = 1
	critter.staredit_group_flags = DATUnit.StarEditGroupFlag.neutral
	templar = units_dat.get_entry(67)
	templar.staredit_group_flags = DATUnit.StarEditGroupFlag.protoss
	techdata_dat = TechDAT()
	techdata_dat.new_file()
	stim = techdata_dat.get_entry(0)
	stim.mineral_cost = 100
	stim.vespene_cost = 100
	stim.energy_required = 10
	upgrades_dat = UpgradesDAT()
	upgrades_dat.new_file()
	armor = upgrades_dat.get_entry(0)
	armor.mineral_cost_base = 100
	armor.vespene_cost_base = 75
	armor.mineral_cost_factor = 75
	armor.max_repeats = 3
	once = upgrades_dat.get_entry(1)
	once.mineral_cost_base = 150
	once.vespene_cost_base = 150
	once.max_repeats = 1
	return DataContext(units_dat=units_dat, techdata_dat=techdata_dat, upgrades_dat=upgrades_dat)

class Test_ForKind(unittest.TestCase):
	def test_unit_costs_and_race(self) -> None:
		costs = TooltipCosts.for_kind(TooltipKind.unit, 0, _data_context())
		self.assertEqual(costs, TooltipCosts(minerals=50, gas=0, supply=1, race=Race.terran))

	def test_supply_is_of_the_units_made_at_once_rounded_down(self) -> None:
		data_context = _data_context()
		# 2 Zerglings of half a supply each
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.unit, 37, data_context), TooltipCosts(minerals=50, gas=0, supply=1, race=Race.zerg))
		# 1.5 supply
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.unit, 38, data_context), TooltipCosts(minerals=75, gas=25, supply=1, race=Race.zerg))

	def test_no_supply_for_a_unit_without_a_race(self) -> None:
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.unit, 89, _data_context()), TooltipCosts(minerals=1, gas=0))

	def test_unit_resources_have_no_supply(self) -> None:
		costs = TooltipCosts.for_kind(TooltipKind.unit_resources, 0, _data_context())
		self.assertEqual(costs, TooltipCosts(minerals=50, gas=0, race=Race.terran))

	def test_building_has_no_supply(self) -> None:
		costs = TooltipCosts.for_kind(TooltipKind.unit, 111, _data_context())
		self.assertEqual(costs, TooltipCosts(minerals=150, gas=0, supply=0, race=Race.terran))

	def test_research_uses_the_tech_costs(self) -> None:
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.tech, 0, _data_context()), TooltipCosts(minerals=100, gas=100))

	def test_upgrade_uses_the_first_level_costs(self) -> None:
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.upgrade, 0, _data_context()), TooltipCosts(minerals=100, gas=75, next_level=1))

	def test_no_next_level_for_an_upgrade_with_one_level(self) -> None:
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.upgrade, 1, _data_context()), TooltipCosts(minerals=150, gas=150))

	def test_spell_energy_has_the_race_of_the_unit_showing_it(self) -> None:
		data_context = _data_context()
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.spell, 0, data_context, 67), TooltipCosts(energy=10, race=Race.protoss))
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.spell, 0, data_context), TooltipCosts(energy=10))

	def test_no_spell_energy_for_a_unit_without_a_race(self) -> None:
		self.assertEqual(TooltipCosts.for_kind(TooltipKind.spell, 0, _data_context(), 89), TooltipCosts())

	def test_no_costs_for_other_kinds_missing_dats_or_invalid_entries(self) -> None:
		data_context = _data_context()
		self.assertIsNone(TooltipCosts.for_kind(TooltipKind.none, 0, data_context))
		self.assertIsNone(TooltipCosts.for_kind(TooltipKind.unit, 0xFFFF, data_context))
		self.assertIsNone(TooltipCosts.for_kind(TooltipKind.unit, 0, DataContext()))

class Test_TooltipDrawing(unittest.TestCase):
	def _data_context(self) -> DataContext:
		data_context = _data_context()
		font8 = FNT()
		font8.load(Assets.mpq_file_path('font', 'font8.fnt'))
		data_context.set_font8_fnt(font8)
		data_context.set_tfontgam_pcx(PCX())
		return data_context

	def _letters(self, drawing: TextDrawing | None) -> list[GlyphItem]:
		assert drawing is not None
		return [item for item in drawing.layout.items if isinstance(item, GlyphItem)]

	def test_no_drawing_without_the_font_or_its_colors(self) -> None:
		data_context = self._data_context()
		data_context.set_font8_fnt(None)
		self.assertIsNone(TextDrawing.tooltip('Move', data_context))
		data_context = self._data_context()
		data_context.set_tfontgam_pcx(None)
		self.assertIsNone(TextDrawing.tooltip('Move', data_context))

	def test_hotkey_string_is_drawn_with_its_cost_line(self) -> None:
		data_context = self._data_context()
		hotkey_string = HotkeyString.parse('m\x01Train Marine\x00')
		assert hotkey_string is not None
		costs = TooltipCosts.for_kind(hotkey_string.kind, 0, data_context)
		drawing = TextDrawing.tooltip(hotkey_string.tooltip_runs(costs, data_context), data_context)
		assert drawing is not None
		font = data_context.font8_fnt
		assert font is not None
		# The hotkey and type aren't drawn, and the cost line is under the text
		self.assertEqual(self._letters(drawing)[0].letter_index, ord('T') - font.start)
		self.assertEqual(drawing.height, font.height * 2)

	def test_plain_text_has_no_cost_line(self) -> None:
		data_context = self._data_context()
		drawing = TextDrawing.tooltip(end_at_null('Stim Packs:\n   Research at Academy\x00'), data_context)
		assert drawing is not None
		font = data_context.font8_fnt
		assert font is not None
		self.assertEqual(self._letters(drawing)[0].letter_index, ord('S') - font.start)
		self.assertEqual(drawing.height, font.height * 2)
		self.assertTrue(all(isinstance(item, GlyphItem) for item in drawing.layout.items))
