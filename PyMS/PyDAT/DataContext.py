
from .DATData import DATData, UnitsDATData, WeaponsDATData, FlingyDATData, SpritesDATData, ImagesDATData, UpgradesDATData, TechDATData, SoundsDATData, PortraitsDATData, CampaignDATData, OrdersDATData
from .TBLData import TBLData
from .IconData import IconData
from .DataID import DATID, DataID

from ..FileFormats.DAT import *
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo, CacheGRP, RLEFunc, rle_normal, rle_outline, rle_shadow, Outline, ImageWithBounds
from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats.IScriptBIN import IScriptBIN
from ..FileFormats.Images import RawPalette

from ..Utilities import Assets
from ..Utilities.Settings import Settings
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.Callback import Callback

import os, re

from typing import cast, Any

class TicksPerSecond:
	fastest = 24
	faster  = 21
	fast    = 18
	normal  = 15
	slow    = 12
	slower  = 9
	slowest = 6

class DataContext(object):
	mpqhandler: MPQHandler
	iscriptbin: IScriptBIN

	def __init__(self): # type: () -> None
		self.settings = Settings('PyDAT', '1')
		self.settings.settings.set_defaults({
			'customlabels': False,
			'simple_labels': False
		})

		self.update_cb = Callback()

		self.stat_txt = TBLData(self, DataID.stat_txt, 'stat_txt', 'rez\\stat_txt.tbl')
		self.stat_txt.update_cb += self.update_cb
		self.unitnamestbl = TBLData(self, DataID.unitnamestbl, 'unitnamestbl', 'rez\\unitnames.tbl') # Expanded unit names
		self.unitnamestbl.update_cb += self.update_cb
		self.imagestbl = TBLData(self, DataID.imagestbl, 'imagestbl', 'arr\\images.tbl')
		self.imagestbl.update_cb += self.update_cb
		self.sfxdatatbl = TBLData(self, DataID.sfxdatatbl, 'sfxdatatbl', 'arr\\sfxdata.tbl')
		self.sfxdatatbl.update_cb += self.update_cb
		self.portdatatbl = TBLData(self, DataID.portdatatbl, 'portdatatbl', 'arr\\portdata.tbl')
		self.portdatatbl.update_cb += self.update_cb
		self.mapdatatbl = TBLData(self, DataID.mapdatatbl, 'mapdatatbl', 'arr\\mapdata.tbl')
		self.mapdatatbl.update_cb += self.update_cb

		self.cmdicons = IconData(self)
		self.cmdicons.update_cb += self.update_cb

		self.units = UnitsDATData(self)
		self.units.update_cb += self.update_cb
		self.weapons = WeaponsDATData(self)
		self.weapons.update_cb += self.update_cb
		self.flingy = FlingyDATData(self)
		self.flingy.update_cb += self.update_cb
		self.sprites = SpritesDATData(self)
		self.sprites.update_cb += self.update_cb
		self.images = ImagesDATData(self)
		self.images.update_cb += self.update_cb
		self.upgrades = UpgradesDATData(self)
		self.upgrades.update_cb += self.update_cb
		self.technology = TechDATData(self)
		self.technology.update_cb += self.update_cb
		self.sounds = SoundsDATData(self)
		self.sounds.update_cb += self.update_cb
		self.portraits = PortraitsDATData(self)
		self.portraits.update_cb += self.update_cb
		self.campaign = CampaignDATData(self)
		self.campaign.update_cb += self.update_cb
		self.orders = OrdersDATData(self)
		self.orders.update_cb += self.update_cb

		self.palettes = {} # type: dict[str, RawPalette]
		self.grp_cache = {} # type: dict[str, dict[str, dict[int, ImageWithBounds]]]
		self.hints = {} # type: dict[str, str]

		# TODO: Make adjustable (which will also need the FloatVar limits to be adjusted in the tabs)
		self.ticks_per_second = TicksPerSecond.fastest

		self.load_hints()

	def load_hints(self): # type: () -> None
		with open(Assets.data_file_path('Hints.txt'),'r') as hints:
			for l in hints:
				m = re.match('(\\S+)=(.+)\n?', l)
				if m:
					self.hints[m.group(1)] = m.group(2)

	def load_palettes(self): # type: () -> None
		self.palettes = {}
		pal = Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.settings.settings.files.get(p, Assets.palette_file_path('%s%spal' % (p,os.extsep))))
			except:
				continue
			self.palettes[p] = pal.palette

	def load_mpqs(self): # type: () -> None
		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpq_paths()) and self.mpqhandler.add_defaults():
			self.settings.settings.mpqs = self.mpqhandler.mpq_paths()

	# @overload
	# def dat_data(self, datid: Literal[DATID.units]) -> UnitsDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.weapons]) -> WeaponsDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.flingy]) -> FlingyDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.sprites]) -> SpritesDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.images]) -> ImagesDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.upgrades]) -> UpgradesDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.techdata]) -> TechDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.sfxdata]) -> SoundsDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.portdata]) -> PortraitsDATData: ...
	# @overload
	# def dat_data(self, datid: Literal[DATID.mapdata]) -> CampaignDATData: ...

	def dat_data(self, datid): # type: (DATID) -> DATData
		match datid:
			case DATID.units:
				return self.units
			case DATID.weapons:
				return self.weapons
			case DATID.flingy:
				return self.flingy
			case DATID.sprites:
				return self.sprites
			case DATID.images:
				return self.images
			case DATID.upgrades:
				return self.upgrades
			case DATID.techdata:
				return self.technology
			case DATID.sfxdata:
				return self.sounds
			case DATID.portdata:
				return self.portraits
			case DATID.mapdata:
				return self.campaign
			case DATID.orders:
				return self.orders

	def data_data(self, dataid): # type: (DataID) -> (TBLData | IconData | IScriptBIN)
		match dataid:
			case DataID.stat_txt:
				return self.stat_txt
			case DataID.unitnamestbl:
				return self.unitnamestbl
			case DataID.imagestbl:
				return self.imagestbl
			case DataID.sfxdatatbl:
				return self.sfxdatatbl
			case DataID.portdatatbl:
				return self.portdatatbl
			case DataID.mapdatatbl:
				return self.mapdatatbl
			case DataID.cmdicons:
				return self.cmdicons
			case DataID.iscriptbin:
				return self.iscriptbin

	def load_additional_files(self): # type: () -> None
		self.mpqhandler.open_mpqs()
		try:
			self.unitnamestbl.load_strings()
		except:
			pass
		try:
			self.stat_txt.load_strings()
			self.imagestbl.load_strings()
			self.sfxdatatbl.load_strings()
			self.portdatatbl.load_strings()
			self.mapdatatbl.load_strings()
			iscriptbin = IScriptBIN()
			iscriptbin.load_file(self.mpqhandler.load_file(self.settings.settings.files.get('iscriptbin', 'MPQ:scripts\\iscript.bin')))
			self.update_cb(DataID.iscriptbin)
		except:
			raise
		finally:
			self.mpqhandler.close_mpqs()
		self.load_palettes()
		self.cmdicons.load_grp()
		self.cmdicons.load_ticon_pcx()
		self.iscriptbin = iscriptbin
		self.units.update_names()
		self.weapons.update_names()
		self.flingy.update_names()
		self.sprites.update_names()
		self.images.update_names()
		self.upgrades.update_names()
		self.technology.update_names()
		self.sounds.update_names()
		self.portraits.update_names()
		self.campaign.update_names()
		self.orders.update_names()

	def load_dat_files(self): # type: () -> None
		defaultmpqs = MPQHandler()
		defaultmpqs.add_defaults()
		defaultmpqs.open_mpqs()
		self.units.load_defaults(defaultmpqs)
		self.weapons.load_defaults(defaultmpqs)
		self.flingy.load_defaults(defaultmpqs)
		self.sprites.load_defaults(defaultmpqs)
		self.images.load_defaults(defaultmpqs)
		self.upgrades.load_defaults(defaultmpqs)
		self.technology.load_defaults(defaultmpqs)
		self.sounds.load_defaults(defaultmpqs)
		self.portraits.load_defaults(defaultmpqs)
		self.campaign.load_defaults(defaultmpqs)
		self.orders.load_defaults(defaultmpqs)
		defaultmpqs.close_mpqs()

	def get_cmdicon(self, index, highlighted=False): # type: (int, bool) -> (ImageWithBounds | None)
		if not 'Icons' in self.palettes or not self.cmdicons.grp or index >= self.cmdicons.grp.frames:
			return None
		if highlighted in self.cmdicons.images and index in self.cmdicons.images[highlighted]:
			return self.cmdicons.images[highlighted][index]
		palette = self.palettes['Icons']
		if highlighted and self.cmdicons.ticon_pcx:
			palette = list(palette)
			for i in range(16):
				palette[i] = palette[self.cmdicons.ticon_pcx.image[0][32+i]]
		image = cast(ImageWithBounds, frame_to_photo(palette, self.cmdicons.grp, index, True))
		if not highlighted in self.cmdicons.images:
			self.cmdicons.images[highlighted] = {}
		self.cmdicons.images[highlighted][index] = image
		return image

	def get_grp_frame(self, path, draw_function=None, remapping=None, draw_info=None, palette=None, frame=0, is_full_path=False): # type: (str, int | None, int | None, Any, str | None, int | None, bool) -> (ImageWithBounds | None)
		if palette is None:
			if path.startswith('thingy\\tileset\\'):
				palette = 'Terrain'
			elif draw_function == DATImage.DrawFunction.use_remapping and remapping is not None and remapping >= DATImage.Remapping.ofire and remapping <= DATImage.Remapping.bfire:
				palette = ('o','g','b')[remapping-1] + 'fire'
			else:
				palette = 'Units'
		if not MPQ.supported() or not palette in self.palettes:
			return None
		if not is_full_path:
			path = 'unit\\' + path
		if not draw_function in (DATImage.DrawFunction.selection_circle, DATImage.DrawFunction.shadow):
			draw_function = DATImage.DrawFunction.normal
		if not path in self.grp_cache or not palette in self.grp_cache[path] or not draw_function in self.grp_cache[path][palette]:
			try:
				grp = CacheGRP()
				grp.load_file(self.mpqhandler.load_file('MPQ:' + path),restrict=1)
			except PyMSError:
				return None
			if not path in self.grp_cache:
				self.grp_cache[path] = {}
			if not palette in self.grp_cache[path]:
				self.grp_cache[path][palette] = {}
			rle_function: RLEFunc
			if draw_function == DATImage.DrawFunction.selection_circle:
				rle_function = rle_outline
				if draw_info is None:
					draw_info = Outline.self
			elif draw_function == DATImage.DrawFunction.shadow:
				rle_function = rle_shadow
				if draw_info is None:
					draw_info = (50,50,50, 255)
			else:
				rle_function = rle_normal
			self.grp_cache[path][palette][draw_function] = cast(ImageWithBounds, frame_to_photo(self.palettes[palette], grp, frame, True, draw_function=rle_function, draw_info=draw_info))
		return self.grp_cache[path][palette][draw_function]

	def get_image_frame(self, image_id, draw_function=None, remapping=None, draw_info=None, palette=None, frame=0): # type: (int, int | None, int | None, Any, str | None, int) -> (ImageWithBounds | None)
		if not self.images.dat:
			return None
		image_entry = self.images.dat.get_entry(image_id)
		tbl_index = image_entry.grp_file
		if not tbl_index:
			return None
		grp_path = self.imagestbl.strings[tbl_index - 1]
		if grp_path.endswith('<0>'):
			grp_path = grp_path[:-3]
		if draw_function is None:
			draw_function = image_entry.draw_function
			if draw_function == DATImage.DrawFunction.use_remapping and remapping is None:
				remapping = image_entry.remapping
		return self.get_grp_frame(grp_path, draw_function, remapping, draw_info, palette, frame)
