
from ...TBL import TBL
from ...DAT import DATEntryName, DataNamesUsage, ImagesDAT, SpritesDAT, FlingyDAT, SoundsDAT, WeaponsDAT

from ....Utilities import Assets

class DataContext:
	def __init__(self, images_tbl: TBL | None = None, images_dat: ImagesDAT | None = None, sprites_dat: SpritesDAT | None = None, flingy_dat: FlingyDAT | None = None, sounds_tbl: TBL | None = None, sounds_dat: SoundsDAT | None = None, stat_txt_tbl: TBL | None = None, weapons_dat: WeaponsDAT | None = None):
		self.images_tbl = images_tbl
		self.images_dat = images_dat
		self._image_names: list[str] | None = None
		self.sprites_dat = sprites_dat
		self._sprite_names: list[str] | None = None
		self.flingy_dat = flingy_dat
		self._flingy_names: list[str] | None = None
		self.sounds_tbl = sounds_tbl
		self.sounds_dat = sounds_dat
		self._sound_names: list[str] | None = None
		self.stat_txt_tbl = stat_txt_tbl
		self.weapons_dat = weapons_dat
		self._weapon_names: list[str] | None = None

	def set_images_tbl(self, images_tbl: TBL | None):
		self.images_tbl = images_tbl
		self._image_names = None
		self._sprite_names = None
		self._flingy_names = None

	def set_images_dat(self, images_dat: ImagesDAT | None):
		self.images_dat = images_dat
		self._image_names = None

	@property
	def images_entry_count(self) -> int:
		return self.images_dat.entry_count() if self.images_dat else ImagesDAT.FORMAT.entries

	def _get_image_names(self) -> list[str] | None:
		if self._image_names is not None:
			return self._image_names
		self._image_names = []
		for image_id in range(0, self.images_entry_count):
			self._image_names.append(DATEntryName.image(image_id, data_names=Assets.data_cache(Assets.DataReference.Images), imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine))
		return self._image_names

	def image_name(self, image_id: int) -> str | None:
		image_names = self._get_image_names()
		if not image_names:
			return None
		if image_id >= len(image_names):
			return None
		return image_names[image_id]

	def set_sprites_dat(self, sprites_dat: SpritesDAT | None):
		self.sprites_dat = sprites_dat
		self._sprite_names = None

	@property
	def sprites_entry_count(self) -> int:
		return self.sprites_dat.entry_count() if self.sprites_dat else SpritesDAT.FORMAT.entries

	def _get_sprite_names(self) -> list[str] | None:
		if self._sprite_names is not None:
			return self._sprite_names
		self._sprite_names = []
		for sprite_id in range(0, self.sprites_entry_count):
			self._sprite_names.append(DATEntryName.sprite(sprite_id, data_names=Assets.data_cache(Assets.DataReference.Sprites), spritesdat=self.sprites_dat, imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine))
		return self._sprite_names

	def sprite_name(self, sprite_id: int) -> str | None:
		sprite_names = self._get_sprite_names()
		if not sprite_names:
			return None
		if sprite_id >= len(sprite_names):
			return None
		return sprite_names[sprite_id]

	def set_flingy_dat(self, flingy_dat: FlingyDAT | None):
		self.flingy_dat = flingy_dat
		self._flingy_names = None

	@property
	def flingy_entry_count(self) -> int:
		return self.flingy_dat.entry_count() if self.flingy_dat else FlingyDAT.FORMAT.entries

	def _get_flingy_names(self) -> list[str] | None:
		if self._flingy_names is not None:
			return self._flingy_names
		self._flingy_names = []
		for flingy_id in range(0, self.flingy_entry_count):
			self._flingy_names.append(DATEntryName.flingy(flingy_id, data_names=Assets.data_cache(Assets.DataReference.Flingy), flingydat=self.flingy_dat, spritesdat=self.sprites_dat, imagesdat=self.images_dat, imagestbl=self.images_tbl, data_names_usage=DataNamesUsage.combine))
		return self._flingy_names

	def flingy_name(self, flingy_id: int) -> str | None:
		flingy_names = self._get_flingy_names()
		if not flingy_names:
			return None
		if flingy_id >= len(flingy_names):
			return None
		return flingy_names[flingy_id]

	def set_sounds_tbl(self, sounds_tbl: TBL | None):
		self.sounds_tbl = sounds_tbl
		self._sound_names = None

	def set_sounds_dat(self, sounds_dat: SoundsDAT | None):
		self.sounds_dat = sounds_dat
		self._sound_names = None

	@property
	def sounds_entry_count(self) -> int:
		return self.sounds_dat.entry_count() if self.sounds_dat else SoundsDAT.FORMAT.entries

	def _get_sound_names(self) -> list[str] | None:
		if self._sound_names is not None:
			return self._sound_names
		self._sound_names = []
		for sound_id in range(0, self.sounds_entry_count):
			self._sound_names.append(DATEntryName.sound(sound_id, data_names=Assets.data_cache(Assets.DataReference.Sfxdata), sfxdatadat=self.sounds_dat, sfxdatatbl=self.sounds_tbl, data_names_usage=DataNamesUsage.combine))
		return self._sound_names

	def sound_name(self, sound_id: int) -> str | None:
		sound_names = self._get_sound_names()
		if not sound_names:
			return None
		if sound_id >= len(sound_names):
			return None
		return sound_names[sound_id]

	def set_stat_txt_tbl(self, stat_txt_tbl: TBL | None):
		self.stat_txt_tbl = stat_txt_tbl
		self._weapon_names = None

	def set_weapons_dat(self, weapons_dat: WeaponsDAT | None):
		self.weapons_dat = weapons_dat
		self._weapon_names = None

	@property
	def weapons_entry_count(self) -> int:
		return self.weapons_dat.entry_count() if self.weapons_dat else WeaponsDAT.FORMAT.entries

	def _get_weapon_names(self) -> list[str] | None:
		if self._weapon_names is not None:
			return self._weapon_names
		self._weapon_names = []
		for weapon_id in range(0, self.weapons_entry_count):
			self._weapon_names.append(DATEntryName.weapon(weapon_id, data_names=Assets.data_cache(Assets.DataReference.Weapons), weaponsdat=self.weapons_dat, stat_txt=self.stat_txt_tbl, data_names_usage=DataNamesUsage.combine))
		return self._weapon_names

	def weapon_name(self, weapon_id: int) -> str | None:
		weapon_names = self._get_weapon_names()
		if not weapon_names:
			return None
		if weapon_id >= len(weapon_names):
			return None
		return weapon_names[weapon_id]
