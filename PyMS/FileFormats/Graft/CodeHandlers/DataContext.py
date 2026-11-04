from __future__ import annotations

from ..Definitions import SPECIAL_BUTTON_CARDS_START

from ...TBL import TBL, decompile_string
from ...DAT import DATEntryName, DataNamesUsage, UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT

from ....Utilities import Assets

class DataContext:
	def __init__(self, *, stat_txt_tbl: TBL | None = None, units_dat: UnitsDAT | None = None, upgrades_dat: UpgradesDAT | None = None, techdata_dat: TechDAT | None = None, orders_dat: OrdersDAT | None = None, data_names_usage: DataNamesUsage = DataNamesUsage.use) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self.units_dat = units_dat
		self._unit_names: tuple[str, ...] | None = None
		self._unit_ids: dict[str, tuple[int, ...]] | None = None
		self.upgrades_dat = upgrades_dat
		self._upgrade_names: tuple[str, ...] | None = None
		self._upgrade_ids: dict[str, tuple[int, ...]] | None = None
		self.techdata_dat = techdata_dat
		self._tech_names: tuple[str, ...] | None = None
		self._tech_ids: dict[str, tuple[int, ...]] | None = None
		self.orders_dat = orders_dat
		self._order_names: tuple[str, ...] | None = None
		self.data_names_usage = data_names_usage

	@staticmethod
	def _build_ids(names: tuple[str, ...]) -> dict[str, tuple[int, ...]]:
		# Every ID with each name
		ids: dict[str, list[int]] = {}
		for entry_id, name in enumerate(names):
			ids.setdefault(name, []).append(entry_id)
		return {name: tuple(entry_ids) for name, entry_ids in ids.items()}

	def set_stat_txt_tbl(self, stat_txt_tbl: TBL | None) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self._unit_names = None
		self._unit_ids = None
		self._upgrade_names = None
		self._upgrade_ids = None
		self._tech_names = None
		self._tech_ids = None
		self._order_names = None

	def set_units_dat(self, units_dat: UnitsDAT | None) -> None:
		self.units_dat = units_dat
		self._unit_names = None
		self._unit_ids = None

	def _get_unit_names(self) -> tuple[str, ...]:
		if self._unit_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Units)
			entry_count = self.units_dat.entry_count() if self.units_dat else UnitsDAT.FORMAT.entries
			self._unit_names = tuple(DATEntryName.unit(unit_id, data_names=data_names, stat_txt=self.stat_txt_tbl, data_names_usage=self.data_names_usage, tbl_raw_string=False).strip() for unit_id in range(entry_count))
		return self._unit_names

	def _get_unit_ids(self) -> dict[str, tuple[int, ...]]:
		if self._unit_ids is None:
			self._unit_ids = DataContext._build_ids(self._get_unit_names())
		return self._unit_ids

	def unit_name(self, unit_id: int, unique: bool = False) -> str | None:
		# With `unique`, the name is only returned if it can be parsed back into only `unit_id`
		unit_names = self._get_unit_names()
		if not 0 <= unit_id < len(unit_names):
			return None
		name = unit_names[unit_id]
		if unique and self.unit_ids(name) != (unit_id,):
			return None
		return name

	def unit_ids(self, unit_name: str) -> tuple[int, ...]:
		return self._get_unit_ids().get(unit_name, ())

	def set_upgrades_dat(self, upgrades_dat: UpgradesDAT | None) -> None:
		self.upgrades_dat = upgrades_dat
		self._upgrade_names = None
		self._upgrade_ids = None

	def _get_upgrade_names(self) -> tuple[str, ...]:
		if self._upgrade_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Upgrades)
			entry_count = self.upgrades_dat.entry_count() if self.upgrades_dat else UpgradesDAT.FORMAT.entries
			self._upgrade_names = tuple(DATEntryName.upgrade(upgrade_id, data_names=data_names, upgradesdat=self.upgrades_dat, stat_txt=self.stat_txt_tbl, data_names_usage=self.data_names_usage, tbl_raw_string=False).strip() for upgrade_id in range(entry_count))
		return self._upgrade_names

	def _get_upgrade_ids(self) -> dict[str, tuple[int, ...]]:
		if self._upgrade_ids is None:
			self._upgrade_ids = DataContext._build_ids(self._get_upgrade_names())
		return self._upgrade_ids

	def upgrade_name(self, upgrade_id: int, unique: bool = False) -> str | None:
		# With `unique`, the name is only returned if it can be parsed back into only `upgrade_id`
		upgrade_names = self._get_upgrade_names()
		if not 0 <= upgrade_id < len(upgrade_names):
			return None
		name = upgrade_names[upgrade_id]
		if unique and self.upgrade_ids(name) != (upgrade_id,):
			return None
		return name

	def upgrade_ids(self, upgrade_name: str) -> tuple[int, ...]:
		return self._get_upgrade_ids().get(upgrade_name, ())

	def set_techdata_dat(self, techdata_dat: TechDAT | None) -> None:
		self.techdata_dat = techdata_dat
		self._tech_names = None
		self._tech_ids = None

	def _get_tech_names(self) -> tuple[str, ...]:
		if self._tech_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Techdata)
			entry_count = self.techdata_dat.entry_count() if self.techdata_dat else TechDAT.FORMAT.entries
			self._tech_names = tuple(DATEntryName.tech(tech_id, data_names=data_names, techdatadat=self.techdata_dat, stat_txt=self.stat_txt_tbl, data_names_usage=self.data_names_usage, tbl_raw_string=False).strip() for tech_id in range(entry_count))
		return self._tech_names

	def _get_tech_ids(self) -> dict[str, tuple[int, ...]]:
		if self._tech_ids is None:
			self._tech_ids = DataContext._build_ids(self._get_tech_names())
		return self._tech_ids

	def tech_name(self, tech_id: int, unique: bool = False) -> str | None:
		# With `unique`, the name is only returned if it can be parsed back into only `tech_id`
		tech_names = self._get_tech_names()
		if not 0 <= tech_id < len(tech_names):
			return None
		name = tech_names[tech_id]
		if unique and self.tech_ids(name) != (tech_id,):
			return None
		return name

	def tech_ids(self, tech_name: str) -> tuple[int, ...]:
		return self._get_tech_ids().get(tech_name, ())

	def set_orders_dat(self, orders_dat: OrdersDAT | None) -> None:
		self.orders_dat = orders_dat
		self._order_names = None

	def _get_order_names(self) -> tuple[str, ...]:
		if self._order_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Orders)
			entry_count = self.orders_dat.entry_count() if self.orders_dat else OrdersDAT.FORMAT.entries
			self._order_names = tuple(DATEntryName.order(order_id, data_names=data_names, ordersdat=self.orders_dat, stat_txt=self.stat_txt_tbl, data_names_usage=self.data_names_usage, tbl_raw_string=False).strip() for order_id in range(entry_count))
		return self._order_names

	def order_name(self, order_id: int) -> str | None:
		order_names = self._get_order_names()
		if 0 <= order_id < len(order_names):
			return order_names[order_id]
		return None

	def icon_name(self, icon_id: int) -> str | None:
		icons = Assets.data_cache(Assets.DataReference.Icons)
		if 0 <= icon_id < len(icons):
			return icons[icon_id]
		return None

	def button_set_name(self, button_set_id: int) -> str | None:
		names = Assets.data_cache(Assets.DataReference.ButtonSets)
		if 0 <= button_set_id < len(names):
			return names[button_set_id]
		return None

	def special_button_card_name(self, card_id: int) -> str | None:
		names = Assets.data_cache(Assets.DataReference.ButtonCards)
		if 0 <= card_id - SPECIAL_BUTTON_CARDS_START < len(names):
			return names[card_id - SPECIAL_BUTTON_CARDS_START]
		return None

	def stat_txt_string(self, string_id: int) -> str | None:
		# Button string IDs are 1-based (0 is no string)
		if not self.stat_txt_tbl or string_id < 1 or string_id > len(self.stat_txt_tbl.strings):
			return None
		return decompile_string(self.stat_txt_tbl.strings[string_id - 1][:-1])
