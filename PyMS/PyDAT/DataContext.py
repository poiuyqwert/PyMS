
from ..FileFormats.DAT.ImagesDAT import Image
from ..FileFormats.Palette import Palette
from ..FileFormats.GRP import frame_to_photo, CacheGRP
from ..FileFormats.TBL import TBL
from ..FileFormats.MPQ.SFmpq import SFMPQ_LOADED
from ..FileFormats.IScriptBIN import IScriptBIN

from ..Utilities.utils import BASE_DIR
from ..Utilities.Settings import Settings
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.PyMSError import PyMSError

import os, re

class DataContext(object):
	def __init__(self):
		self.settings = Settings('PyDAT', '1')

		self.mpqhandler = None

		self.stat_txt = None
		self.imagestbl = None
		self.sfxdatatbl = None
		self.portdatatbl = None
		self.mapdatatbl = None
		self.cmdicon = None
		self.iscriptbin = None

		self.palettes = {}
		self.grp_cache = {}
		self.icon_cache = {}
		self.hints = {}

		self.load_hints()

	def load_hints(self):
		with open(os.path.join(BASE_DIR,'PyMS','Data','Hints.txt'),'r') as hints:
			for l in hints:
				m = re.match('(\\S+)=(.+)\n?', l)
				if m:
					self.hints[m.group(1)] = m.group(2)

	def load_palettes(self):
		pal = Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.settings.settings.palettes.get(p, os.path.join(BASE_DIR, 'Palettes', '%s%spal' % (p,os.extsep))))
			except:
				continue
			self.palettes[p] = pal.palette

	def load_mpqs(self):
		self.mpqhandler = MPQHandler(self.settings.settings.get('mpqs',[]))
		if not len(self.mpqhandler.mpqs) and self.mpqhandler.add_defaults():
			self.settings.settings.mpqs = self.mpqhandler.mpqs

	def load_additional_files(self):
		self.mpqhandler.open_mpqs()
		try:
			stat_txt = TBL()
			stat_txt.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('stat_txt', 'MPQ:rez\\stat_txt.tbl')))
			imagestbl = TBL()
			imagestbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('imagestbl', 'MPQ:arr\\images.tbl')))
			sfxdatatbl = TBL()
			sfxdatatbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('sfxdatatbl', 'MPQ:arr\\sfxdata.tbl')))
			portdatatbl = TBL()
			portdatatbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('portdatatbl', 'MPQ:arr\\portdata.tbl')))
			mapdatatbl = TBL()
			mapdatatbl.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('mapdatatbl', 'MPQ:arr\\mapdata.tbl')))
			cmdicon = CacheGRP()
			cmdicon.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('cmdicons', 'MPQ:unit\\cmdbtns\\cmdicons.grp')))
			iscriptbin = IScriptBIN()
			iscriptbin.load_file(self.mpqhandler.get_file(self.settings.settings.files.get('iscriptbin', 'MPQ:scripts\\iscript.bin')))
		except:
			self.mpqhandler.close_mpqs()
			raise
		else:
			self.mpqhandler.close_mpqs()
		self.stat_txt = stat_txt
		self.imagestbl = imagestbl
		self.sfxdatatbl = sfxdatatbl
		self.portdatatbl = portdatatbl
		self.mapdatatbl = mapdatatbl
		self.cmdicon = cmdicon
		self.iscriptbin = iscriptbin


	def get_cmdicon(self, index):
		if not 'Icons' in self.palettes or not self.cmdicon or index >= self.cmdicon.frames:
			return None
		if index in self.icon_cache:
			return self.icon_cache[index]
		image = frame_to_photo(self.palettes['Icons'], self.cmdicon, index, True)
		self.icon_cache[index] = image
		return image

	def get_grp_frame(self, path, draw_function=None, remapping=None, draw_info=None, palette=None, frame=0, is_full_path=False):
		if palette == None:
			if path.startswith('thingy\\tileset\\'):
				palette = 'Terrain'
			elif draw_function == Image.DrawFunction.use_remapping and remapping >= Image.Remapping.ofire and remapping <= Image.Remapping.bfire:
				palette = ('o','g','b')[remapping-1] + 'fire'
			else:
				palette = 'Units'
		if not SFMPQ_LOADED or not palette in self.palettes:
			return None
		if not is_full_path:
			path = 'unit\\' + path
		if not path in self.grp_cache or not palette in self.grp_cache[path]:
			p = self.mpqhandler.get_file('MPQ:' + path)
			try:
				grp = CacheGRP()
				grp.load_file(p,restrict=1)
			except PyMSError:
				return None
			if not path in self.grp_cache:
				self.grp_cache[path] = {}
			self.grp_cache[path][palette] = frame_to_photo(self.palettes[palette], grp, frame, True, draw_function=draw_function, draw_info=draw_info)
		return self.grp_cache[path][palette]

	# def get_image_frame(self, image_id):
	# 	image_entry = self.images.get_entry(image_id)
	# 	tbl_index = image_entry.grp_file
	# 	if tbl_index:
	# 		grp_path = self.imagestbl.strings[tbl_index - 1][:-1]
	# 		return self.get_grp_frame(grp_path)
