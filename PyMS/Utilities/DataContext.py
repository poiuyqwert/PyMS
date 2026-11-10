from __future__ import annotations

from ..FileFormats.TBL import TBL, decompile_string, compile_string
from ..FileFormats.DAT import DATEntryName, DataNamesUsage, UnitsDAT, UpgradesDAT, TechDAT, OrdersDAT, WeaponsDAT, ImagesDAT, SpritesDAT, FlingyDAT, SoundsDAT

from . import Assets

class DataContext:
	# `*_name` methods return names to be used as values in code (built from the TBL strings only, and only when the name is unique), `*_display_name` methods return names to describe values (like in comments)
	NAME_EXCLUDE = '\x0A\x28\x29\x2C'

	def __init__(self, *, stat_txt_tbl: TBL | None = None, unitnames_tbl: TBL | None = None, images_tbl: TBL | None = None, sounds_tbl: TBL | None = None, units_dat: UnitsDAT | None = None, upgrades_dat: UpgradesDAT | None = None, techdata_dat: TechDAT | None = None, orders_dat: OrdersDAT | None = None, weapons_dat: WeaponsDAT | None = None, flingy_dat: FlingyDAT | None = None, sprites_dat: SpritesDAT | None = None, images_dat: ImagesDAT | None = None, sounds_dat: SoundsDAT | None = None) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self.unitnames_tbl = unitnames_tbl
		self.images_tbl = images_tbl
		self.sounds_tbl = sounds_tbl
		self.units_dat = units_dat
		self._unit_names: tuple[str | None, ...] | None = None
		self._unit_display_names: tuple[str, ...] | None = None
		self._unit_ids: dict[str, tuple[int, ...]] | None = None
		self.upgrades_dat = upgrades_dat
		self._upgrade_names: tuple[str | None, ...] | None = None
		self._upgrade_display_names: tuple[str, ...] | None = None
		self._upgrade_ids: dict[str, tuple[int, ...]] | None = None
		self.techdata_dat = techdata_dat
		self._tech_names: tuple[str | None, ...] | None = None
		self._tech_display_names: tuple[str, ...] | None = None
		self._tech_ids: dict[str, tuple[int, ...]] | None = None
		self.orders_dat = orders_dat
		self._order_names: tuple[str | None, ...] | None = None
		self._order_display_names: tuple[str, ...] | None = None
		self._order_ids: dict[str, tuple[int, ...]] | None = None
		self.weapons_dat = weapons_dat
		self._weapon_names: tuple[str | None, ...] | None = None
		self._weapon_display_names: tuple[str, ...] | None = None
		self._weapon_ids: dict[str, tuple[int, ...]] | None = None
		self.images_dat = images_dat
		self._image_names: tuple[str | None, ...] | None = None
		self._image_display_names: tuple[str, ...] | None = None
		self._image_ids: dict[str, tuple[int, ...]] | None = None
		self.sprites_dat = sprites_dat
		self._sprite_names: tuple[str | None, ...] | None = None
		self._sprite_display_names: tuple[str, ...] | None = None
		self._sprite_ids: dict[str, tuple[int, ...]] | None = None
		self.flingy_dat = flingy_dat
		self._flingy_names: tuple[str | None, ...] | None = None
		self._flingy_display_names: tuple[str, ...] | None = None
		self._flingy_ids: dict[str, tuple[int, ...]] | None = None
		self.sounds_dat = sounds_dat
		self._sound_names: tuple[str | None, ...] | None = None
		self._sound_display_names: tuple[str, ...] | None = None
		self._sound_ids: dict[str, tuple[int, ...]] | None = None

	@staticmethod
	def _build_ids(names: tuple[str | None, ...]) -> dict[str, tuple[int, ...]]:
		# Every ID with each name
		ids: dict[str, list[int]] = {}
		for entry_id, name in enumerate(names):
			if name is not None:
				ids.setdefault(name, []).append(entry_id)
		return {name: tuple(entry_ids) for name, entry_ids in ids.items()}

	@staticmethod
	def _label_name(label: int, tbl: TBL | None) -> str | None:
		# Labels are 1-based (0 is no string)
		if tbl is None:
			return None
		string_id = label - 1
		if string_id < 0 or string_id >= len(tbl.strings):
			return None
		return decompile_string(tbl.strings[string_id].split('\x00')[0], exclude=DataContext.NAME_EXCLUDE).strip()

	@staticmethod
	def _label_path(label: int, tbl: TBL | None) -> str | None:
		# Labels are 1-based (0 is no string)
		if tbl is None:
			return None
		string_id = label - 1
		if string_id < 0 or string_id >= len(tbl.strings):
			return None
		return tbl.strings[string_id][:-1]

	# stat_txt.tbl

	def set_stat_txt_tbl(self, stat_txt_tbl: TBL | None) -> None:
		self.stat_txt_tbl = stat_txt_tbl
		self._clear_unit_names()
		self._clear_upgrade_names()
		self._clear_tech_names()
		self._clear_order_names()
		self._clear_weapon_names()

	def stat_txt_string(self, string_id: int) -> str | None:
		# 0-based index into stat_txt.tbl
		if not self.stat_txt_tbl:
			return None
		if string_id < 0 or string_id >= len(self.stat_txt_tbl.strings):
			return None
		return decompile_string(self.stat_txt_tbl.strings[string_id][:-1])

	def stat_txt_strings(self) -> list[str] | None:
		if not self.stat_txt_tbl:
			return None
		return [decompile_string(string[:-1]) for string in self.stat_txt_tbl.strings]

	def stat_txt_id(self, string: str) -> int | None:
		if not self.stat_txt_tbl:
			return None
		string = compile_string(string)
		if not string.endswith('\x00'):
			string += '\x00'
		try:
			return self.stat_txt_tbl.strings.index(string)
		except ValueError:
			return None

	# Units

	def set_unitnames_tbl(self, unitnames_tbl: TBL | None) -> None:
		self.unitnames_tbl = unitnames_tbl
		self._clear_unit_names()

	def set_units_dat(self, units_dat: UnitsDAT | None) -> None:
		self.units_dat = units_dat
		self._clear_unit_names()

	def _clear_unit_names(self) -> None:
		self._unit_names = None
		self._unit_display_names = None
		self._unit_ids = None

	@property
	def unit_entry_count(self) -> int:
		entry_count = self.units_dat.entry_count() if self.units_dat else UnitsDAT.FORMAT.entries
		if self.unitnames_tbl:
			entry_count = min(entry_count, len(self.unitnames_tbl.strings))
		return entry_count

	@staticmethod
	def _unit_name(raw_string: str) -> str:
		components = raw_string.split('\x00')
		if len(components) > 1 and components[1] != '*':
			name = '\x00'.join(components[:2])
		else:
			name = components[0]
		return decompile_string(name, exclude=DataContext.NAME_EXCLUDE).strip()

	def _get_unit_names(self) -> tuple[str | None, ...]:
		if self._unit_names is None:
			strings: list[str] = []
			if self.unitnames_tbl:
				strings = self.unitnames_tbl.strings
			elif self.stat_txt_tbl:
				strings = self.stat_txt_tbl.strings[:UnitsDAT.FORMAT.entries]
			self._unit_names = tuple(DataContext._unit_name(strings[unit_id]) if unit_id < len(strings) else None for unit_id in range(self.unit_entry_count))
		return self._unit_names

	def _get_unit_display_names(self) -> tuple[str, ...]:
		if self._unit_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Units)
			self._unit_display_names = tuple(DATEntryName.unit(unit_id, data_names=data_names, stat_txt=self.stat_txt_tbl, unitnamestbl=self.unitnames_tbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False).strip() for unit_id in range(self.unit_entry_count))
		return self._unit_display_names

	def _get_unit_ids(self) -> dict[str, tuple[int, ...]]:
		if self._unit_ids is None:
			self._unit_ids = DataContext._build_ids(self._get_unit_names())
		return self._unit_ids

	def unit_name(self, unit_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `unit_id`
		unit_names = self._get_unit_names()
		if not 0 <= unit_id < len(unit_names):
			return None
		name = unit_names[unit_id]
		if name is None or self.unit_ids(name) != (unit_id,):
			return None
		return name

	def unit_ids(self, unit_name: str) -> tuple[int, ...]:
		return self._get_unit_ids().get(unit_name, ())

	def unit_display_name(self, unit_id: int) -> str | None:
		unit_display_names = self._get_unit_display_names()
		if not 0 <= unit_id < len(unit_display_names):
			return None
		return unit_display_names[unit_id]

	def unit_display_names(self) -> tuple[str, ...]:
		return self._get_unit_display_names()

	# Upgrades

	def set_upgrades_dat(self, upgrades_dat: UpgradesDAT | None) -> None:
		self.upgrades_dat = upgrades_dat
		self._clear_upgrade_names()

	def _clear_upgrade_names(self) -> None:
		self._upgrade_names = None
		self._upgrade_display_names = None
		self._upgrade_ids = None

	@property
	def upgrade_entry_count(self) -> int:
		return self.upgrades_dat.entry_count() if self.upgrades_dat else UpgradesDAT.FORMAT.entries

	def _get_upgrade_names(self) -> tuple[str | None, ...]:
		if self._upgrade_names is None:
			upgrades_dat = self.upgrades_dat
			if upgrades_dat is None:
				self._upgrade_names = (None,) * self.upgrade_entry_count
			else:
				self._upgrade_names = tuple(DataContext._label_name(upgrades_dat.get_entry(upgrade_id).label, self.stat_txt_tbl) for upgrade_id in range(self.upgrade_entry_count))
		return self._upgrade_names

	def _get_upgrade_display_names(self) -> tuple[str, ...]:
		if self._upgrade_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Upgrades)
			self._upgrade_display_names = tuple(DATEntryName.upgrade(upgrade_id, data_names=data_names, upgradesdat=self.upgrades_dat, stat_txt=self.stat_txt_tbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False).strip() for upgrade_id in range(self.upgrade_entry_count))
		return self._upgrade_display_names

	def _get_upgrade_ids(self) -> dict[str, tuple[int, ...]]:
		if self._upgrade_ids is None:
			self._upgrade_ids = DataContext._build_ids(self._get_upgrade_names())
		return self._upgrade_ids

	def upgrade_name(self, upgrade_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `upgrade_id`
		upgrade_names = self._get_upgrade_names()
		if not 0 <= upgrade_id < len(upgrade_names):
			return None
		name = upgrade_names[upgrade_id]
		if name is None or self.upgrade_ids(name) != (upgrade_id,):
			return None
		return name

	def upgrade_ids(self, upgrade_name: str) -> tuple[int, ...]:
		return self._get_upgrade_ids().get(upgrade_name, ())

	def upgrade_display_name(self, upgrade_id: int) -> str | None:
		upgrade_display_names = self._get_upgrade_display_names()
		if not 0 <= upgrade_id < len(upgrade_display_names):
			return None
		return upgrade_display_names[upgrade_id]

	def upgrade_display_names(self) -> tuple[str, ...]:
		return self._get_upgrade_display_names()

	# Techs

	def set_techdata_dat(self, techdata_dat: TechDAT | None) -> None:
		self.techdata_dat = techdata_dat
		self._clear_tech_names()

	def _clear_tech_names(self) -> None:
		self._tech_names = None
		self._tech_display_names = None
		self._tech_ids = None

	@property
	def tech_entry_count(self) -> int:
		return self.techdata_dat.entry_count() if self.techdata_dat else TechDAT.FORMAT.entries

	def _get_tech_names(self) -> tuple[str | None, ...]:
		if self._tech_names is None:
			techdata_dat = self.techdata_dat
			if techdata_dat is None:
				self._tech_names = (None,) * self.tech_entry_count
			else:
				self._tech_names = tuple(DataContext._label_name(techdata_dat.get_entry(tech_id).label, self.stat_txt_tbl) for tech_id in range(self.tech_entry_count))
		return self._tech_names

	def _get_tech_display_names(self) -> tuple[str, ...]:
		if self._tech_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Techdata)
			self._tech_display_names = tuple(DATEntryName.tech(tech_id, data_names=data_names, techdatadat=self.techdata_dat, stat_txt=self.stat_txt_tbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False).strip() for tech_id in range(self.tech_entry_count))
		return self._tech_display_names

	def _get_tech_ids(self) -> dict[str, tuple[int, ...]]:
		if self._tech_ids is None:
			self._tech_ids = DataContext._build_ids(self._get_tech_names())
		return self._tech_ids

	def tech_name(self, tech_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `tech_id`
		tech_names = self._get_tech_names()
		if not 0 <= tech_id < len(tech_names):
			return None
		name = tech_names[tech_id]
		if name is None or self.tech_ids(name) != (tech_id,):
			return None
		return name

	def tech_ids(self, tech_name: str) -> tuple[int, ...]:
		return self._get_tech_ids().get(tech_name, ())

	def tech_display_name(self, tech_id: int) -> str | None:
		tech_display_names = self._get_tech_display_names()
		if not 0 <= tech_id < len(tech_display_names):
			return None
		return tech_display_names[tech_id]

	def tech_display_names(self) -> tuple[str, ...]:
		return self._get_tech_display_names()

	# Orders

	def set_orders_dat(self, orders_dat: OrdersDAT | None) -> None:
		self.orders_dat = orders_dat
		self._clear_order_names()

	def _clear_order_names(self) -> None:
		self._order_names = None
		self._order_display_names = None
		self._order_ids = None

	@property
	def order_entry_count(self) -> int:
		return self.orders_dat.entry_count() if self.orders_dat else OrdersDAT.FORMAT.entries

	def _get_order_names(self) -> tuple[str | None, ...]:
		if self._order_names is None:
			orders_dat = self.orders_dat
			if orders_dat is None:
				self._order_names = (None,) * self.order_entry_count
			else:
				self._order_names = tuple(DataContext._label_name(orders_dat.get_entry(order_id).label, self.stat_txt_tbl) for order_id in range(self.order_entry_count))
		return self._order_names

	def _get_order_display_names(self) -> tuple[str, ...]:
		if self._order_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Orders)
			self._order_display_names = tuple(DATEntryName.order(order_id, data_names=data_names, ordersdat=self.orders_dat, stat_txt=self.stat_txt_tbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False).strip() for order_id in range(self.order_entry_count))
		return self._order_display_names

	def _get_order_ids(self) -> dict[str, tuple[int, ...]]:
		if self._order_ids is None:
			self._order_ids = DataContext._build_ids(self._get_order_names())
		return self._order_ids

	def order_name(self, order_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `order_id`
		order_names = self._get_order_names()
		if not 0 <= order_id < len(order_names):
			return None
		name = order_names[order_id]
		if name is None or self.order_ids(name) != (order_id,):
			return None
		return name

	def order_ids(self, order_name: str) -> tuple[int, ...]:
		return self._get_order_ids().get(order_name, ())

	def order_display_name(self, order_id: int) -> str | None:
		order_display_names = self._get_order_display_names()
		if not 0 <= order_id < len(order_display_names):
			return None
		return order_display_names[order_id]

	def order_display_names(self) -> tuple[str, ...]:
		return self._get_order_display_names()

	# Weapons

	def set_weapons_dat(self, weapons_dat: WeaponsDAT | None) -> None:
		self.weapons_dat = weapons_dat
		self._clear_weapon_names()

	def _clear_weapon_names(self) -> None:
		self._weapon_names = None
		self._weapon_display_names = None
		self._weapon_ids = None

	@property
	def weapon_entry_count(self) -> int:
		return self.weapons_dat.entry_count() if self.weapons_dat else WeaponsDAT.FORMAT.entries

	def _get_weapon_names(self) -> tuple[str | None, ...]:
		if self._weapon_names is None:
			weapons_dat = self.weapons_dat
			if weapons_dat is None:
				self._weapon_names = (None,) * self.weapon_entry_count
			else:
				self._weapon_names = tuple(DataContext._label_name(weapons_dat.get_entry(weapon_id).label, self.stat_txt_tbl) for weapon_id in range(self.weapon_entry_count))
		return self._weapon_names

	def _get_weapon_display_names(self) -> tuple[str, ...]:
		if self._weapon_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Weapons)
			self._weapon_display_names = tuple(DATEntryName.weapon(weapon_id, data_names=data_names, weaponsdat=self.weapons_dat, stat_txt=self.stat_txt_tbl, data_names_usage=DataNamesUsage.combine, tbl_raw_string=False).strip() for weapon_id in range(self.weapon_entry_count))
		return self._weapon_display_names

	def _get_weapon_ids(self) -> dict[str, tuple[int, ...]]:
		if self._weapon_ids is None:
			self._weapon_ids = DataContext._build_ids(self._get_weapon_names())
		return self._weapon_ids

	def weapon_name(self, weapon_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `weapon_id`
		weapon_names = self._get_weapon_names()
		if not 0 <= weapon_id < len(weapon_names):
			return None
		name = weapon_names[weapon_id]
		if name is None or self.weapon_ids(name) != (weapon_id,):
			return None
		return name

	def weapon_ids(self, weapon_name: str) -> tuple[int, ...]:
		return self._get_weapon_ids().get(weapon_name, ())

	def weapon_display_name(self, weapon_id: int) -> str | None:
		weapon_display_names = self._get_weapon_display_names()
		if not 0 <= weapon_id < len(weapon_display_names):
			return None
		return weapon_display_names[weapon_id]

	def weapon_display_names(self) -> tuple[str, ...]:
		return self._get_weapon_display_names()

	# Images

	def set_images_tbl(self, images_tbl: TBL | None) -> None:
		self.images_tbl = images_tbl
		self._clear_image_names()
		self._clear_sprite_names()
		self._clear_flingy_names()

	def set_images_dat(self, images_dat: ImagesDAT | None) -> None:
		self.images_dat = images_dat
		self._clear_image_names()
		self._clear_sprite_names()
		self._clear_flingy_names()

	def _clear_image_names(self) -> None:
		self._image_names = None
		self._image_display_names = None
		self._image_ids = None

	@property
	def image_entry_count(self) -> int:
		return self.images_dat.entry_count() if self.images_dat else ImagesDAT.FORMAT.entries

	def _get_image_names(self) -> tuple[str | None, ...]:
		if self._image_names is None:
			images_dat = self.images_dat
			if images_dat is None:
				self._image_names = (None,) * self.image_entry_count
			else:
				self._image_names = tuple(DataContext._label_name(images_dat.get_entry(image_id).grp_file, self.images_tbl) for image_id in range(self.image_entry_count))
		return self._image_names

	def _get_image_display_names(self) -> tuple[str, ...]:
		if self._image_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Images)
			self._image_display_names = tuple(DATEntryName.image(image_id, data_names=data_names, imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine) for image_id in range(self.image_entry_count))
		return self._image_display_names

	def _get_image_ids(self) -> dict[str, tuple[int, ...]]:
		if self._image_ids is None:
			self._image_ids = DataContext._build_ids(self._get_image_names())
		return self._image_ids

	def image_name(self, image_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `image_id`
		image_names = self._get_image_names()
		if not 0 <= image_id < len(image_names):
			return None
		name = image_names[image_id]
		if name is None or self.image_ids(name) != (image_id,):
			return None
		return name

	def image_ids(self, image_name: str) -> tuple[int, ...]:
		return self._get_image_ids().get(image_name, ())

	def image_display_name(self, image_id: int) -> str | None:
		image_display_names = self._get_image_display_names()
		if not 0 <= image_id < len(image_display_names):
			return None
		return image_display_names[image_id]

	def image_display_names(self) -> tuple[str, ...]:
		return self._get_image_display_names()

	def image_path(self, image_id: int) -> str | None:
		if self.images_dat is None or not 0 <= image_id < self.image_entry_count:
			return None
		return DataContext._label_path(self.images_dat.get_entry(image_id).grp_file, self.images_tbl)

	# Sprites

	def set_sprites_dat(self, sprites_dat: SpritesDAT | None) -> None:
		self.sprites_dat = sprites_dat
		self._clear_sprite_names()
		self._clear_flingy_names()

	def _clear_sprite_names(self) -> None:
		self._sprite_names = None
		self._sprite_display_names = None
		self._sprite_ids = None

	@property
	def sprite_entry_count(self) -> int:
		return self.sprites_dat.entry_count() if self.sprites_dat else SpritesDAT.FORMAT.entries

	def _get_sprite_names(self) -> tuple[str | None, ...]:
		if self._sprite_names is None:
			sprites_dat = self.sprites_dat
			if sprites_dat is None:
				self._sprite_names = (None,) * self.sprite_entry_count
			else:
				image_names = self._get_image_names()
				self._sprite_names = tuple(image_names[image_id] if 0 <= (image_id := sprites_dat.get_entry(sprite_id).image) < len(image_names) else None for sprite_id in range(self.sprite_entry_count))
		return self._sprite_names

	def _get_sprite_display_names(self) -> tuple[str, ...]:
		if self._sprite_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Sprites)
			self._sprite_display_names = tuple(DATEntryName.sprite(sprite_id, data_names=data_names, spritesdat=self.sprites_dat, imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine) for sprite_id in range(self.sprite_entry_count))
		return self._sprite_display_names

	def _get_sprite_ids(self) -> dict[str, tuple[int, ...]]:
		if self._sprite_ids is None:
			self._sprite_ids = DataContext._build_ids(self._get_sprite_names())
		return self._sprite_ids

	def sprite_name(self, sprite_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `sprite_id`
		sprite_names = self._get_sprite_names()
		if not 0 <= sprite_id < len(sprite_names):
			return None
		name = sprite_names[sprite_id]
		if name is None or self.sprite_ids(name) != (sprite_id,):
			return None
		return name

	def sprite_ids(self, sprite_name: str) -> tuple[int, ...]:
		return self._get_sprite_ids().get(sprite_name, ())

	def sprite_display_name(self, sprite_id: int) -> str | None:
		sprite_display_names = self._get_sprite_display_names()
		if not 0 <= sprite_id < len(sprite_display_names):
			return None
		return sprite_display_names[sprite_id]

	def sprite_display_names(self) -> tuple[str, ...]:
		return self._get_sprite_display_names()

	# Flingy

	def set_flingy_dat(self, flingy_dat: FlingyDAT | None) -> None:
		self.flingy_dat = flingy_dat
		self._clear_flingy_names()

	def _clear_flingy_names(self) -> None:
		self._flingy_names = None
		self._flingy_display_names = None
		self._flingy_ids = None

	@property
	def flingy_entry_count(self) -> int:
		return self.flingy_dat.entry_count() if self.flingy_dat else FlingyDAT.FORMAT.entries

	def _get_flingy_names(self) -> tuple[str | None, ...]:
		if self._flingy_names is None:
			flingy_dat = self.flingy_dat
			if flingy_dat is None:
				self._flingy_names = (None,) * self.flingy_entry_count
			else:
				sprite_names = self._get_sprite_names()
				self._flingy_names = tuple(sprite_names[sprite_id] if 0 <= (sprite_id := flingy_dat.get_entry(flingy_id).sprite) < len(sprite_names) else None for flingy_id in range(self.flingy_entry_count))
		return self._flingy_names

	def _get_flingy_display_names(self) -> tuple[str, ...]:
		if self._flingy_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Flingy)
			self._flingy_display_names = tuple(DATEntryName.flingy(flingy_id, data_names=data_names, flingydat=self.flingy_dat, spritesdat=self.sprites_dat, imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine) for flingy_id in range(self.flingy_entry_count))
		return self._flingy_display_names

	def _get_flingy_ids(self) -> dict[str, tuple[int, ...]]:
		if self._flingy_ids is None:
			self._flingy_ids = DataContext._build_ids(self._get_flingy_names())
		return self._flingy_ids

	def flingy_name(self, flingy_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `flingy_id`
		flingy_names = self._get_flingy_names()
		if not 0 <= flingy_id < len(flingy_names):
			return None
		name = flingy_names[flingy_id]
		if name is None or self.flingy_ids(name) != (flingy_id,):
			return None
		return name

	def flingy_ids(self, flingy_name: str) -> tuple[int, ...]:
		return self._get_flingy_ids().get(flingy_name, ())

	def flingy_display_name(self, flingy_id: int) -> str | None:
		flingy_display_names = self._get_flingy_display_names()
		if not 0 <= flingy_id < len(flingy_display_names):
			return None
		return flingy_display_names[flingy_id]

	def flingy_display_names(self) -> tuple[str, ...]:
		return self._get_flingy_display_names()

	# Sounds

	def set_sounds_tbl(self, sounds_tbl: TBL | None) -> None:
		self.sounds_tbl = sounds_tbl
		self._clear_sound_names()

	def set_sounds_dat(self, sounds_dat: SoundsDAT | None) -> None:
		self.sounds_dat = sounds_dat
		self._clear_sound_names()

	def _clear_sound_names(self) -> None:
		self._sound_names = None
		self._sound_display_names = None
		self._sound_ids = None

	@property
	def sound_entry_count(self) -> int:
		return self.sounds_dat.entry_count() if self.sounds_dat else SoundsDAT.FORMAT.entries

	def _get_sound_names(self) -> tuple[str | None, ...]:
		if self._sound_names is None:
			sounds_dat = self.sounds_dat
			if sounds_dat is None:
				self._sound_names = (None,) * self.sound_entry_count
			else:
				self._sound_names = tuple(DataContext._label_name(sounds_dat.get_entry(sound_id).sound_file, self.sounds_tbl) for sound_id in range(self.sound_entry_count))
		return self._sound_names

	def _get_sound_display_names(self) -> tuple[str, ...]:
		if self._sound_display_names is None:
			data_names = Assets.data_cache(Assets.DataReference.Sfxdata)
			self._sound_display_names = tuple(DATEntryName.sound(sound_id, data_names=data_names, sfxdatadat=self.sounds_dat, sfxdatatbl=self.sounds_tbl, data_names_usage=DataNamesUsage.combine) for sound_id in range(self.sound_entry_count))
		return self._sound_display_names

	def _get_sound_ids(self) -> dict[str, tuple[int, ...]]:
		if self._sound_ids is None:
			self._sound_ids = DataContext._build_ids(self._get_sound_names())
		return self._sound_ids

	def sound_name(self, sound_id: int) -> str | None:
		# The name is only returned if it can be parsed back into only `sound_id`
		sound_names = self._get_sound_names()
		if not 0 <= sound_id < len(sound_names):
			return None
		name = sound_names[sound_id]
		if name is None or self.sound_ids(name) != (sound_id,):
			return None
		return name

	def sound_ids(self, sound_name: str) -> tuple[int, ...]:
		return self._get_sound_ids().get(sound_name, ())

	def sound_display_name(self, sound_id: int) -> str | None:
		sound_display_names = self._get_sound_display_names()
		if not 0 <= sound_id < len(sound_display_names):
			return None
		return sound_display_names[sound_id]

	def sound_display_names(self) -> tuple[str, ...]:
		return self._get_sound_display_names()

	def sound_path(self, sound_id: int) -> str | None:
		if self.sounds_dat is None or not 0 <= sound_id < self.sound_entry_count:
			return None
		return DataContext._label_path(self.sounds_dat.get_entry(sound_id).sound_file, self.sounds_tbl)

	# Other data names

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

	def button_card_name(self, card_id: int) -> str | None:
		# Button cards are the units, followed by the special button cards
		# Imported here, the Graft package imports this module
		from ..FileFormats.Graft.ButtonsGraft import ButtonsGraft # pylint: disable=cyclic-import
		if card_id < ButtonsGraft.SPECIAL_BUTTON_CARDS_START:
			return self.unit_display_name(card_id)
		names = Assets.data_cache(Assets.DataReference.ButtonCards)
		if card_id - ButtonsGraft.SPECIAL_BUTTON_CARDS_START < len(names):
			return names[card_id - ButtonsGraft.SPECIAL_BUTTON_CARDS_START]
		return None
