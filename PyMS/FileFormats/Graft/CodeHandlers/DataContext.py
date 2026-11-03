from __future__ import annotations

from ..Definitions import ParamKind

from ...TBL import TBL, decompile_string
from ...DAT import DATEntryName, DataNamesUsage, UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT

from ....Utilities import Assets

from typing import Callable

class DataContext:
	def __init__(self, *, stat_txt_tbl: TBL | None = None, units_dat: UnitsDAT | None = None, upgrades_dat: UpgradesDAT | None = None, techdata_dat: TechDAT | None = None, orders_dat: OrdersDAT | None = None, data_names_usage: DataNamesUsage = DataNamesUsage.use) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self.units_dat = units_dat
		self.upgrades_dat = upgrades_dat
		self.techdata_dat = techdata_dat
		self.orders_dat = orders_dat
		self.data_names_usage = data_names_usage
		self._names: dict[ParamKind, tuple[str, ...]] = {}
		self._ids: dict[ParamKind, dict[str, int]] = {}

	def _invalidate(self, *kinds: ParamKind) -> None:
		for kind in kinds:
			self._names.pop(kind, None)
			self._ids.pop(kind, None)

	def set_stat_txt_tbl(self, stat_txt_tbl: TBL | None) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self._invalidate(ParamKind.unit, ParamKind.upgrade, ParamKind.tech, ParamKind.order)

	def set_units_dat(self, units_dat: UnitsDAT | None) -> None:
		self.units_dat = units_dat
		self._invalidate(ParamKind.unit)

	def set_upgrades_dat(self, upgrades_dat: UpgradesDAT | None) -> None:
		self.upgrades_dat = upgrades_dat
		self._invalidate(ParamKind.upgrade)

	def set_techdata_dat(self, techdata_dat: TechDAT | None) -> None:
		self.techdata_dat = techdata_dat
		self._invalidate(ParamKind.tech)

	def set_orders_dat(self, orders_dat: OrdersDAT | None) -> None:
		self.orders_dat = orders_dat
		self._invalidate(ParamKind.order)

	def entry_count(self, kind: ParamKind) -> int:
		match kind:
			case ParamKind.unit:
				return self.units_dat.entry_count() if self.units_dat else UnitsDAT.FORMAT.entries
			case ParamKind.upgrade:
				return self.upgrades_dat.entry_count() if self.upgrades_dat else UpgradesDAT.FORMAT.entries
			case ParamKind.tech:
				return self.techdata_dat.entry_count() if self.techdata_dat else TechDAT.FORMAT.entries
			case ParamKind.order:
				return self.orders_dat.entry_count() if self.orders_dat else OrdersDAT.FORMAT.entries
		return 0

	def _build_name(self, kind: ParamKind) -> Callable[[int], str]:
		usage = self.data_names_usage
		match kind:
			case ParamKind.unit:
				return lambda entry_id: DATEntryName.unit(entry_id, data_names=Assets.data_cache(Assets.DataReference.Units), stat_txt=self.stat_txt_tbl, data_names_usage=usage, tbl_raw_string=False)
			case ParamKind.upgrade:
				return lambda entry_id: DATEntryName.upgrade(entry_id, data_names=Assets.data_cache(Assets.DataReference.Upgrades), upgradesdat=self.upgrades_dat, stat_txt=self.stat_txt_tbl, data_names_usage=usage, tbl_raw_string=False)
			case ParamKind.tech:
				return lambda entry_id: DATEntryName.tech(entry_id, data_names=Assets.data_cache(Assets.DataReference.Techdata), techdatadat=self.techdata_dat, stat_txt=self.stat_txt_tbl, data_names_usage=usage, tbl_raw_string=False)
			case ParamKind.order:
				return lambda entry_id: DATEntryName.order(entry_id, data_names=Assets.data_cache(Assets.DataReference.Orders), ordersdat=self.orders_dat, stat_txt=self.stat_txt_tbl, data_names_usage=usage, tbl_raw_string=False)
		raise ValueError(f'No names for {kind}')

	def get_names(self, kind: ParamKind) -> tuple[str, ...]:
		if kind == ParamKind.none:
			return ()
		names = self._names.get(kind)
		if names is None:
			build_name = self._build_name(kind)
			names = tuple(build_name(entry_id).strip() for entry_id in range(self.entry_count(kind)))
			self._names[kind] = names
		return names

	def name(self, kind: ParamKind, entry_id: int) -> str | None:
		names = self.get_names(kind)
		if 0 <= entry_id < len(names):
			return names[entry_id]
		return None

	def _get_ids(self, kind: ParamKind) -> dict[str, int]:
		ids = self._ids.get(kind)
		if ids is None:
			# Only names that identify exactly one entry can be used in place of an ID
			ids = {}
			duplicates: set[str] = set()
			for entry_id, name in enumerate(self.get_names(kind)):
				if name in ids:
					duplicates.add(name)
				else:
					ids[name] = entry_id
			for name in duplicates:
				del ids[name]
			self._ids[kind] = ids
		return ids

	def id(self, kind: ParamKind, name: str) -> int | None:
		if kind == ParamKind.none:
			return None
		return self._get_ids(kind).get(name)

	def unique_name(self, kind: ParamKind, entry_id: int) -> str | None:
		# The name of `entry_id`, if that name can be parsed back into the same ID
		name = self.name(kind, entry_id)
		if name is None or self.id(kind, name) != entry_id:
			return None
		return name

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

	def stat_txt_string(self, string_id: int) -> str | None:
		# Button string IDs are 1-based (0 is no string)
		if not self.stat_txt_tbl or string_id < 1 or string_id > len(self.stat_txt_tbl.strings):
			return None
		return decompile_string(self.stat_txt_tbl.strings[string_id - 1][:-1])
