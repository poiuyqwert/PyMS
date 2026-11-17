from __future__ import annotations

from .Layout import InlineImage

from ..DataContext import DataContext, IconFrame, Race

from ...FileFormats.DAT import DATUnit
from ...FileFormats.TBL import end_at_null

from dataclasses import dataclass

from typing import ClassVar

class TooltipKind:
	# The second character of a hotkey string, which chooses the cost line shown under the text
	none = 0
	unit = 1 # The minerals, gas, and supply of a unit
	upgrade = 2 # The next level, then the minerals and gas of an upgrade
	spell = 3 # The energy of a technology
	tech = 4 # The minerals and gas of a technology
	unit_resources = 5 # The minerals and gas of a unit, without its supply (like a building)

	MAX = 5

@dataclass(frozen=True)
class TooltipCosts:
	# The values of a tooltip's cost line (missing and 0 values aren't shown)
	minerals: int | None = None
	gas: int | None = None
	supply: int | None = None
	energy: int | None = None
	next_level: int | None = None
	# Chooses the gas/supply/energy icons (the Zerg icons when it's `None`)
	race: Race | None = None

	@staticmethod
	def placeholder(kind: int) -> TooltipCosts:
		# Sample values for previewing a string without knowing what it's for
		if kind == TooltipKind.unit:
			return TooltipCosts(minerals=200, gas=100, supply=2)
		if kind == TooltipKind.upgrade:
			return TooltipCosts(minerals=100, gas=100, next_level=1)
		if kind == TooltipKind.spell:
			return TooltipCosts(energy=75)
		if kind in (TooltipKind.tech, TooltipKind.unit_resources):
			return TooltipCosts(minerals=150, gas=50)
		return TooltipCosts()

	@classmethod
	def for_kind(cls, kind: int, entry_id: int, data_context: DataContext, owner_unit_id: int | None = None) -> TooltipCosts | None:
		# The costs shown in a tooltip: like the game, the hotkey type of its string chooses which `.dat` the entry (a button's action parameter) is in.
		# `owner_unit_id` is the unit whose command card shows the button (its race is used for spell energy).
		# `None` when the hotkey type has no costs, or the entry isn't found.
		if kind == TooltipKind.unit:
			return cls.for_unit(entry_id, data_context, with_supply=True)
		if kind == TooltipKind.unit_resources:
			return cls.for_unit(entry_id, data_context, with_supply=False)
		if kind == TooltipKind.upgrade:
			return cls.for_upgrade(entry_id, data_context)
		if kind == TooltipKind.spell:
			return cls.for_tech_energy(entry_id, data_context, owner_unit_id)
		if kind == TooltipKind.tech:
			return cls.for_tech_research(entry_id, data_context)
		return None

	@classmethod
	def for_unit(cls, unit_id: int, data_context: DataContext, *, with_supply: bool) -> TooltipCosts | None:
		units_dat = data_context.units_dat
		if units_dat is None or not 0 <= unit_id < units_dat.entry_count():
			return None
		unit = units_dat.get_entry(unit_id)
		race = Race.from_staredit_group_flags(unit.staredit_group_flags)
		supply = None
		# Like the game, a unit without a race has no supply shown
		if with_supply and race is not None:
			# Supply is stored in halves, and is shown for the units made at once (2 Zerglings from 1 egg), rounded down
			halves = unit.supply_required.whole * 2 + (1 if unit.supply_required.half else 0)
			count = 2 if unit.special_ability_flags & DATUnit.SpecialAbilityFlag.two_units_in_one_egg else 1
			supply = halves * count // 2
		return cls(minerals=unit.mineral_cost, gas=unit.vespene_cost, supply=supply, race=race)

	@classmethod
	def for_tech_research(cls, tech_id: int, data_context: DataContext) -> TooltipCosts | None:
		techdata_dat = data_context.techdata_dat
		if techdata_dat is None or not 0 <= tech_id < techdata_dat.entry_count():
			return None
		tech = techdata_dat.get_entry(tech_id)
		return cls(minerals=tech.mineral_cost, gas=tech.vespene_cost)

	@classmethod
	def for_tech_energy(cls, tech_id: int, data_context: DataContext, owner_unit_id: int | None) -> TooltipCosts | None:
		techdata_dat = data_context.techdata_dat
		if techdata_dat is None or not 0 <= tech_id < techdata_dat.entry_count():
			return None
		energy = techdata_dat.get_entry(tech_id).energy_required
		units_dat = data_context.units_dat
		if owner_unit_id is None or units_dat is None or not 0 <= owner_unit_id < units_dat.entry_count():
			# The unit isn't known, so neither is its race
			return cls(energy=energy)
		race = Race.from_staredit_group_flags(units_dat.get_entry(owner_unit_id).staredit_group_flags)
		# Like the game, the energy is shown with the race of the unit, and isn't shown for a unit without a race
		if race is None:
			return cls()
		return cls(energy=energy, race=race)

	@classmethod
	def for_upgrade(cls, upgrade_id: int, data_context: DataContext) -> TooltipCosts | None:
		upgrades_dat = data_context.upgrades_dat
		if upgrades_dat is None or not 0 <= upgrade_id < upgrades_dat.entry_count():
			return None
		upgrade = upgrades_dat.get_entry(upgrade_id)
		# The costs of the first level, which is only shown when there's more than one level
		next_level = 1 if upgrade.max_repeats > 1 else None
		return cls(minerals=upgrade.mineral_cost_base, gas=upgrade.vespene_cost_base, next_level=next_level)

@dataclass(frozen=True)
class HotkeyString:
	# A string of a button (`stat_txt.tbl`): its hotkey, the kind of cost line of its tooltip, and its text
	hotkey: str
	kind: int
	text: str

	# The stat_txt.tbl string (0-based) shown before the level of an upgrade
	NEXT_LEVEL_STRING: ClassVar[int] = 794
	NEXT_LEVEL_DEFAULT: ClassVar[str] = 'Next Level:'

	@staticmethod
	def parse(raw: str, *, stop_at_null: bool = True) -> HotkeyString | None:
		# `None` when the string isn't a hotkey string (too short, or an unknown kind)
		if len(raw) < 2 or ord(raw[1]) > TooltipKind.MAX:
			return None
		text = raw[2:]
		if stop_at_null:
			text = end_at_null(text)
		return HotkeyString(raw[0], ord(raw[1]), text)

	@staticmethod
	def _next_level_label(data_context: DataContext) -> str:
		raw = data_context.stat_txt_raw_string(HotkeyString.NEXT_LEVEL_STRING)
		if raw is None:
			return HotkeyString.NEXT_LEVEL_DEFAULT
		return end_at_null(raw)

	@staticmethod
	def _icon_image(data_context: DataContext, frame: IconFrame) -> InlineImage | None:
		icon = data_context.get_icon(frame)
		if icon is None:
			return None
		image, bounds = icon
		return InlineImage(image, bounds.x_max + 1, bounds.y_max)

	def tooltip_runs(self, costs: TooltipCosts | None, data_context: DataContext) -> list[str | InlineImage]:
		# The text of the hotkey string, followed by its cost line (with the icons of `data_context`, which are left out when they aren't loaded).
		# Like the game, only the costs that aren't 0 are shown, and there's no cost line when they all are.
		runs: list[str | InlineImage] = [self.text]
		kind = self.kind
		if not TooltipKind.unit <= kind <= TooltipKind.MAX:
			return runs
		if costs is None:
			costs = TooltipCosts.placeholder(kind)

		# The level of an upgrade is added to its text (when it can be upgraded more than once)
		if costs.next_level:
			runs.append(f'\n{HotkeyString._next_level_label(data_context)} {costs.next_level}')

		# The costs in the order the game shows them
		all_values = (
			(IconFrame.minerals, costs.minerals),
			(IconFrame.gas(costs.race), costs.gas),
			(IconFrame.energy(costs.race), costs.energy),
			(IconFrame.supply(costs.race), costs.supply),
		)
		values = [(frame, value) for frame, value in all_values if value]
		if not values:
			return runs
		# The cost line is in the default color (unless a color that can't be changed is used)
		runs.append('\n\x02')
		for index, (frame, value) in enumerate(values):
			if image := HotkeyString._icon_image(data_context, frame):
				runs.append(image)
			runs.append(str(value) + ('' if index == len(values) - 1 else ' '))
		return runs
