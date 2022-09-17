
from .DATData import *
from .TBLData import TBLData
from .IconData import IconData
from .DataID import DATID, DataID

from ..FileFormats.DAT import *
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo, CacheGRP, rle_normal, rle_outline, rle_shadow, OUTLINE_SELF
from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats.IScriptBIN import IScriptBIN

from ..Utilities import Assets
from ..Utilities.Settings import Settings
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError
from ..Utilities.Callback import Callback

import os, re

class TicksPerSecond:
	fastest = 24
	faster  = 21
	fast    = 18
	normal  = 15
	slow    = 12
	slower  = 9
	slowest = 6

class DataContext(object):
	def __init__(self):
		self.settings = Settings('PyDAT', '1')
		self.settings.settings.set_defaults({
			'customlabels': False,
			'simple_labels': False
		})

		self.mpqhandler = None

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
		self.iscriptbin = None

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

		self.palettes = {}
		self.grp_cache = {}
		self.hints = {}

		# TODO: Make adjustable (which will also need the FloatVar limits to be adjusted in the tabs)
		self.ticks_per_second = TicksPerSecond.fastest

		self.load_hints()

	def load_hints(self):
		with open(Assets.data_file_path('Hints.txt'),'r') as hints:
			for l in hints:
				m = re.match('(\\S+)=(.+)\n?', l)
				if m:
					self.hints[m.group(1)] = m.group(2)

	def load_palettes(self):
		self.palettes = {}
		pal = Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.settings.settings.files.get(p, Assets.palette_file_path('%s%spal' % (p,os.extsep))))
			except:
				continue
			self.palettes[p] = pal.palette

	def load_mpqs(self):
		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpq_paths()) and self.mpqhandler.add_defaults():
			self.settings.settings.mpqs = self.mpqhandler.mpq_paths()

	def dat_data(self, datid):
		if datid == DATID.units:
			return self.units
		elif datid == DATID.weapons:
			return self.weapons
		elif datid == DATID.flingy:
			return self.flingy
		elif datid == DATID.sprites:
			return self.sprites
		elif datid == DATID.images:
			return self.images
		elif datid == DATID.upgrades:
			return self.upgrades
		elif datid == DATID.techdata:
			return self.technology
		elif datid == DATID.sfxdata:
			return self.sounds
		elif datid == DATID.portdata:
			return self.portraits
		elif datid == DATID.mapdata:
			return self.campaign
		elif datid == DATID.orders:
			return self.orders

	def data_data(self, dataid):
		if dataid == DataID.stat_txt:
			return self.stat_txt
		elif dataid == DataID.unitnamestbl:
			return self.unitnamestbl
		elif dataid == DataID.imagestbl:
			return self.imagestbl
		elif dataid == DataID.sfxdatatbl:
			return self.sfxdatatbl
		elif dataid == DataID.portdatatbl:
			return self.portdatatbl
		elif dataid == DataID.mapdatatbl:
			return self.mapdatatbl
		elif dataid == DataID.cmdicons:
			return self.cmdicons
		elif dataid == DataID.iscriptbin:
			return self.iscriptbin

	def load_additional_files(self):
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
			iscriptbin.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('iscriptbin', 'MPQ:scripts\\iscript.bin')))
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

	def load_dat_files(self):
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

	def get_cmdicon(self, index, highlighted=False):
		if not 'Icons' in self.palettes or not self.cmdicons.grp or index >= self.cmdicons.grp.frames:
			return None
		if highlighted in self.cmdicons.images and index in self.cmdicons.images[highlighted]:
			return self.cmdicons.images[highlighted][index]
		palette = self.palettes['Icons']
		if highlighted and self.cmdicons.ticon_pcx:
			palette = list(palette)
			for i in range(16):
				palette[i] = palette[self.cmdicons.ticon_pcx.image[0][32+i]]
		image = frame_to_photo(palette, self.cmdicons.grp, index, True)
		if not highlighted in self.cmdicons.images:
			self.cmdicons.images[highlighted] = {}
		self.cmdicons.images[highlighted][index] = image
		return image

	def get_grp_frame(self, path, draw_function=None, remapping=None, draw_info=None, palette=None, frame=0, is_full_path=False):
		if palette == None:
			if path.startswith('thingy\\tileset\\'):
				palette = 'Terrain'
			elif draw_function == Image.DrawFunction.use_remapping and remapping >= Image.Remapping.ofire and remapping <= Image.Remapping.bfire:
				palette = ('o','g','b')[remapping-1] + 'fire'
			else:
				palette = 'Units'
		if not MPQ.supported() or not palette in self.palettes:
			return None
		if not is_full_path:
			path = 'unit\\' + path
		if not draw_function in (Image.DrawFunction.selection_circle, Image.DrawFunction.shadow):
			draw_function = Image.DrawFunction.normal
		if not path in self.grp_cache or not palette in self.grp_cache[path] or not draw_function in self.grp_cache[path][palette]:
			p = self.mpqhandler.get_file('MPQ:' + path)
			try:
				grp = CacheGRP()
				grp.load_file(p,restrict=1)
			except PyMSError:
				return None
			if not path in self.grp_cache:
				self.grp_cache[path] = {}
			if not palette in self.grp_cache[path]:
				self.grp_cache[path][palette] = {}
			if draw_function == Image.DrawFunction.selection_circle:
				rle_function = rle_outline
				if draw_info == None:
					draw_info = OUTLINE_SELF
			elif draw_function == Image.DrawFunction.shadow:
				rle_function = rle_shadow
				if draw_info == None:
					draw_info = (50,50,50, 255)
			else:
				rle_function = rle_normal
			self.grp_cache[path][palette][draw_function] = frame_to_photo(self.palettes[palette], grp, frame, True, draw_function=rle_function, draw_info=draw_info)
		return self.grp_cache[path][palette][draw_function]

	def get_image_frame(self, image_id, draw_function=None, remapping=None, draw_info=None, palette=None, frame=0):
		if not self.images.dat:
			return None
		image_entry = self.images.dat.get_entry(image_id)
		tbl_index = image_entry.grp_file
		if not tbl_index:
			return None
		grp_path = self.imagestbl.strings[tbl_index - 1]
		if grp_path.endswith('<0>'):
			grp_path = grp_path[:-3]
		if draw_function == None:
			draw_function = image_entry.draw_function
			if draw_function == Image.DrawFunction.use_remapping and remapping == None:
				remapping = image_entry.remapping
		return self.get_grp_frame(grp_path, draw_function, remapping, draw_info, palette, frame)
