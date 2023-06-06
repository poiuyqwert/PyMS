
try:
	from tkinter import Image
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	from ...Utilities import Assets
	from ...Utilities.DependencyError import DependencyError
	import sys, os
	e = DependencyError('PyMS', 'Pillow is missing. Consult the Source Installation section of the README.', (('README','file:///%s' % Assets.readme_file_path),))
	e.startup()
	sys.exit()

from .CV5 import CV5, CV5Group, CV5Flag
from .VF4 import VF4
from .VX4 import VX4, VX4Megatile, VX4Minitile
from .VR4 import VR4, VR4Image
from .DDDataBIN import DDDataBIN

from ..Palette import Palette
from ..BMP import BMP

from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import os, re, math
from dataclasses import dataclass
from enum import Enum

from typing import Callable, cast


def megatile_to_photo(tileset, megatile_id): # type: (Tileset, int) -> Image
	megatile = tileset.vx4.get_megatile(megatile_id)
	pi = PILImage.new('P', (32,32))
	pal = [] # type: list[int]
	for c in tileset.wpe.palette:
		pal.extend(c)
	pi.putpalette(pal)
	image = [[] for _ in range(32)] # type: list[list[int]]
	for m,minitile in enumerate(megatile.minitiles):
		for y,p in enumerate(tileset.vr4.get_image(minitile.image_id)):
			if minitile.flipped:
				p = p[::-1]
			image[(m // 4)*8+y].extend(p)
	put = [] # type: list[int]
	for row in image:
		put.extend(row)
	pi.putdata(put)
	return cast(Image, ImageTk.PhotoImage(pi))

def minitile_to_photo(tileset, minitile): # type: (Tileset, VX4Minitile) -> Image
	image = tileset.vr4.get_image(minitile.image_id)
	pi = PILImage.new('P', (24,24))
	pal = [] # type: list[int]
	for c in tileset.wpe.palette:
		pal.extend(c)
	pi.putpalette(pal)
	put = [] # type: list[int]
	for _y,p in enumerate(image):
		if minitile.flipped:
			p = p[::-1]
		for x in p * 3:
			put.extend((x,x,x))
	pi.putdata(put)
	return cast(Image, ImageTk.PhotoImage(pi))

class TileType(Enum):
	group = 0
	mega = 1
	mini = 2

# HEIGHT_LOW  = 0
# HEIGHT_MID  = (1 << 1)
# HEIGHT_HIGH = (1 << 2)

@dataclass
class ImportGraphicsOptions:
	groups_ignore_extra: bool = False # Ignore extra groups (Boolean, default: False)
	megatiles_ignore_extra: bool = False # Ignore extra megatiles (Boolean, default: False)
	megatiles_reuse_duplicates_old: bool = False # Attempt to find and reuse existing minitile images (Boolean, default: False)
	megatiles_reuse_duplicates_new: bool = False # Attempt to find and reuse duplicate imported minitile images (Boolean, default: False)
	megatiles_reuse_null_with_id: int | None = 0 # Reuse "null" megatile with id even if find duplicates is off (None or int, default: 0)
	minitiles_ignore_extra: bool = False # Ignore extra minitiles (Boolean, default: False)
	minitiles_reuse_duplicates_old: bool = True # Attempt to find and reuse existing minitile images (Boolean, default: True)
	minitiles_reuse_duplicates_new: bool = True # Attempt to find and reuse duplicate imported minitile images (Boolean, default: True)
	minitiles_reuse_null_with_id: int | None = 0 # Reuse "null" minitile with id even if find duplicates is off (None or int, default: 0)
	minitiles_reuse_duplicates_flipped: bool = True # Check flipped versions of tiles for duplicates (Boolean, default: True)
	minitiles_expand_allowed: bool | Callable[[], bool] = False # Whether importing too many minitiles will expand VX4 or not (True, False, or callback, default: False)

@dataclass
class ExportSettingsOptions:
	groups_type: bool = True
	groups_flags: bool = True

	groups_basic_edge_left: bool = True
	groups_basic_edge_up: bool = True
	groups_basic_edge_right: bool = True
	groups_basic_edge_down: bool = True
	groups_basic_piece_left: bool = True
	groups_basic_piece_up: bool = True
	groups_basic_piece_right: bool = True
	groups_basic_piece_down: bool = True

	groups_doodad_overlay_id: bool = True
	groups_doodad_scr: bool = True
	groups_doodad_string_id: bool = True
	groups_doodad_unknown4: bool = True
	groups_doodad_dddata_id: bool = True
	groups_doodad_width: bool = True
	groups_doodad_height: bool = True
	groups_doodad_unknown8: bool = True

	megatiles_export_height: bool = True
	megatiles_export_walkability: bool = True
	megatiles_export_block_sight: bool = True
	megatiles_export_ramp: bool = True

def setting_import_extras_ignore(setting_count, tile_n, tile_count): # type: (int, int, int) -> (int | None)
	if tile_n == setting_count:
		return None
	return tile_n

def setting_import_extras_repeat_all(setting_count, tile_n, tile_count): # type: (int, int, int) -> (int | None)
	return tile_n % setting_count

def setting_import_extras_repeat_last(setting_count, tile_n, tile_count): # type: (int, int, int) -> (int | None)
	return min(tile_n, setting_count-1)

@dataclass
class ImportSettingsOptions:
	repeater: Callable[[int, int, int], int | None] = setting_import_extras_ignore
	# options.repeater (Func, default: setting_import_extras_ignore)

class Tileset(object):
	cv5: CV5
	cv5_path: str
	vf4: VF4
	vf4_path: str
	vx4: VX4
	vx4_path: str
	vr4: VR4
	vr4_path: str
	dddata: DDDataBIN
	dddata_path: str
	wpe: Palette
	wpe_path: str

	# def __init__(self):
	# 	self.cv5 = None
	# 	self.cv5_path = None
	# 	self.vf4 = None
	# 	self.vf4_path = None
	# 	self.vx4 = None
	# 	self.vx4_path = None
	# 	self.vr4 = None
	# 	self.vr4_path = None
	# 	self.dddata = None
	# 	self.dddata_path = None
	# 	self.wpe = None
	# 	self.wpe_path = None

	def groups_max(self): # type: () -> int
		return CV5.MAX_ID+1
	def groups_remaining(self): # type: () -> int
		return self.cv5.groups_remaining()

	def megatiles_max(self): # type: () -> int
		return VX4.MAX_ID+1
	def megatiles_remaining(self): # type: () -> int
		return self.vx4.megatiles_remaining()

	def minitiles_max(self): # type: () -> int
		return VR4.max_id(self.vx4.is_expanded())+1
	def minitiles_remaining(self): # type: () -> int
		return self.vr4.images_remaining(expanded_vx4=self.vx4.is_expanded())

	def new_file(self, cv5=None, vf4=None, vx4=None, vr4=None, dddata=None, wpe=None): # type: (CV5 | None, VF4 | None, VX4 | None, VR4 | None, DDDataBIN | None, Palette | None) -> None
		if cv5:
			self.cv5 = cv5
		else:
			self.cv5 = CV5()
		if vf4:
			self.vf4 = vf4
		else:
			self.vf4 = VF4()
		if vx4:
			self.vx4 = vx4
		else:
			self.vx4 = VX4()
		if vr4:
			self.vr4 = vr4
		else:
			self.vr4 = VR4()
		if dddata:
			self.dddata = dddata
		else:
			self.dddata = DDDataBIN()
		if wpe:
			self.wpe = wpe
		else:
			self.wpe = Palette()

	def load_file(self, cv5_path, vf4_path=None, vx4_path=None, vr4_path=None, dddata_path=None, wpe_path=None): # type: (str, str | None, str | None, str | None, str | None, str | None) -> None
		path = os.path.dirname(cv5_path)
		name = os.path.basename(cv5_path)
		if name.split(os.extsep)[-1].lower() == 'cv5':
			name = name[:-4]
		if not vf4_path:
			vf4_path = os.path.join(path, '%s%svf4' % (name,os.extsep))
		if not vx4_path:
			vx4_path = os.path.join(path, '%s%svx4ex' % (name,os.extsep))
			# Check for and prefer expanded vx4 files
			if not os.path.exists(vx4_path):
				vx4_path = os.path.join(path, '%s%svx4' % (name,os.extsep))
		if not vr4_path:
			vr4_path = os.path.join(path, '%s%svr4' % (name,os.extsep))
		if not dddata_path:
			dddata_path = os.path.join(path, name, 'dddata%sbin' % os.extsep)
		if not wpe_path:
			wpe_path = os.path.join(path, '%s%swpe' % (name,os.extsep))
		self.cv5 = CV5()
		self.cv5.load_file(cv5_path)
		self.vf4 = VF4()
		self.vf4.load_file(vf4_path)
		self.vx4 = VX4()
		self.vx4.load_file(vx4_path)
		self.vr4 = VR4()
		self.vr4.load_file(vr4_path)
		self.dddata = DDDataBIN()
		self.dddata.load_file(dddata_path)
		self.wpe = Palette()
		self.wpe.load_file(wpe_path)
		self.cv5_path = cv5_path
		self.vf4_path = vf4_path
		self.vx4_path = vx4_path
		self.vr4_path = vr4_path
		self.dddata_path = dddata_path
		self.wpe_path = wpe_path

	def save_file(self, cv5_path, vf4_path=None, vx4_path=None, vr4_path=None, dddata_path=None, wpe_path=None): # type: (str, str | None, str | None, str | None, str | None, str | None) -> None
		path = os.path.dirname(cv5_path)
		name = os.path.basename(cv5_path)
		if name.endswith(os.extsep + 'cv5'):
			name = name[:-4]
		if vf4_path is None:
			vf4_path = os.path.join(path, '%s%svf4' % (name,os.extsep))
		if vx4_path is None:
			expanded = 'ex' if self.vx4.is_expanded() else ''
			vx4_path = os.path.join(path, '%s%svx4%s' % (name,os.extsep,expanded))
		if vr4_path is None:
			vr4_path = os.path.join(path, '%s%svr4' % (name,os.extsep))
		dddir = os.path.join(path, name)
		if dddata_path is None:
			dddata_path = os.path.join(dddir, 'dddata%sbin' % os.extsep)
		if wpe_path is None:
			wpe_path = os.path.join(path, '%s%swpe' % (name,os.extsep))
		self.cv5.save_file(cv5_path)
		self.vf4.save_file(vf4_path)
		self.vx4.save_file(vx4_path)
		self.vr4.save_file(vr4_path)
		if not os.path.exists(dddir):
			os.mkdir(dddir)
		self.dddata.save_file(dddata_path)
		self.wpe.save_sc_wpe(wpe_path)

	def import_graphics(self, tiletype, bmpfiles, ids=None, options=ImportGraphicsOptions()): # type: (TileType, list[str], list[int] | None, ImportGraphicsOptions) -> list[int]
		if ids:
			ids = list(ids)
		else:
			ids = []
		new_ids = [] # type: list[int]
		pixels = [] # type: list[list[int]]
		for path in bmpfiles:
			bmp = BMP()
			bmp.load_file(path)
			if tiletype == TileType.group and (bmp.width != 512 or bmp.height % 32):
				raise PyMSError('Interpreting','The image is not the correct size for tile groups (got %sx%s, expected width to be 512 and height to be a multiple of 32)' % (bmp.width,bmp.height))
			elif tiletype == TileType.mega and (bmp.width % 32 or bmp.height % 32):
				raise PyMSError('Interpreting','The image is not the correct size for megatiles (got %sx%s, expected width and height to be multiples of 32)' % (bmp.width,bmp.height))
			elif tiletype == TileType.mini and (bmp.width % 8 or bmp.height % 8):
				raise PyMSError('Interpreting','The image is not the correct size for minitiles (got %sx%s, expected width and height to be multiples of 8)' % (bmp.width,bmp.height))
			pixels.extend(bmp.image)

		new_images = [] # type: list[VR4Image]
		image_lookup = {} # type: dict[int, list[int]]
		update_images = [] # type: list[tuple[int, VR4Image]]

		new_megatiles = [] # type: list[VX4Megatile]
		mega_lookup = {} # type: dict[int, list[int]]
		update_megatiles = [] # type: list[tuple[int, VX4Megatile]]

		new_groups = [] # type: list[list[int]]
		update_groups = [] # # type: list[tuple[int, list[int]]]

		minis_w = len(pixels[0]) // 8
		minis_h = len(pixels) // 8
		for iy in range(minis_h):
			py = iy * 8
			for ix in range(minis_w):
				px = ix * 8
				image = tuple(tuple(pixels[py+oy][px:px+8]) for oy in range(8))
				new_images.append(image)
		minitile_details = [] # type: list[VX4Minitile]
		new_id = self.vr4.image_count()
		i = 0
		if tiletype == TileType.mini and options.minitiles_ignore_extra and len(new_images) > len(ids):
			new_images = new_images[:len(ids)]
		while i < len(new_images):
			image = new_images[i]
			image_hash = VR4.image_hash(image)
			found = False
			if tiletype != TileType.mini or not len(ids):
				existing_normal_ids, existing_flipped_ids = self.vr4.find_image_ids(image)
				existing_all_ids = existing_normal_ids + existing_flipped_ids
				if len(existing_all_ids) and (options.minitiles_reuse_duplicates_old or options.minitiles_reuse_null_with_id in existing_all_ids):
					flipped = not len(existing_normal_ids)
					if not flipped or options.minitiles_reuse_duplicates_flipped:
						found = True
						del new_images[i]
						minitile_details.append(VX4Minitile(existing_all_ids[0], flipped))
				if not found:
					existing_normal_ids = image_lookup.get(image_hash,[])
					flipped_hash = VR4.image_hash(image, True)
					existing_flipped_ids = image_lookup.get(flipped_hash,[])
					existing_all_ids = existing_normal_ids + existing_flipped_ids
					if len(existing_all_ids) and (options.minitiles_reuse_duplicates_new or options.minitiles_reuse_null_with_id in existing_all_ids):
						flipped = not len(existing_normal_ids)
						if not flipped or options.minitiles_reuse_duplicates_flipped:
							found = True
							del new_images[i]
							minitile_details.append(VX4Minitile(existing_all_ids[0], flipped))
			if not found:
				id = new_id
				if tiletype == TileType.mini and len(ids):
					id = ids[0]
					del ids[0]
					update_images.append((id, new_images[i]))
					del new_images[i]
				else:
					if tiletype == TileType.mini:
						new_ids.append(new_id)
					new_id += 1
					i += 1
				minitile_details.append(VX4Minitile(id, False))
				if image_hash in image_lookup:
					image_lookup[image_hash].append(id)
				else:
					image_lookup[image_hash] = [id]
		if len(new_images) > self.minitiles_remaining():
			if self.vx4.is_expanded() or not options.minitiles_expand_allowed or (callable(options.minitiles_expand_allowed) and not options.minitiles_expand_allowed()):
				raise PyMSError('Importing','Import aborted because it exceeded the maximum minitile image count (%d + %d > %d)' % (self.vr4.image_count(),len(new_images),VR4.MAX_ID+1))
			self.vx4.expand()
		if tiletype == TileType.group or tiletype == TileType.mega:
			megas_w = minis_w // 4
			megas_h = minis_h // 4
			for y in range(megas_h):
				for x in range(megas_w):
					minitiles = [] # type: list[VX4Minitile]
					for oy in range(4):
						o = (y*4+oy)*minis_w + x*4
						minitiles.extend(minitile_details[o:o+4])
					new_megatiles.append(VX4Megatile(minitiles))
			megatile_ids = [] # type: list[int]
			new_id = self.vx4.megatile_count()
			i = 0
			if tiletype == TileType.mega and options.megatiles_ignore_extra and len(new_megatiles) > len(ids):
				new_megatiles = new_megatiles[:len(ids)]
			while i < len(new_megatiles):
				tile_hash = hash(new_megatiles[i])
				found = False
				if tiletype != TileType.mega or not len(ids):
					existing_ids = self.vx4.find_megatile_ids(new_megatiles[i])
					if len(existing_ids) and (options.megatiles_reuse_duplicates_old or options.megatiles_reuse_null_with_id in existing_ids):
						del new_megatiles[i]
						megatile_ids.append(existing_ids[0])
						found = True
					if not found:
						existing_ids = mega_lookup.get(tile_hash,[])
						if existing_ids and (options.megatiles_reuse_duplicates_new or options.megatiles_reuse_null_with_id in existing_ids):
							del new_megatiles[i]
							megatile_ids.append(existing_ids[0])
							found = True
				if not found:
					id = new_id
					if tiletype == TileType.mega and len(ids):
						id = ids[0]
						del ids[0]
						update_megatiles.append((id, new_megatiles[i]))
						del new_megatiles[i]
					else:
						if tiletype == TileType.mega:
							new_ids.append(new_id)
						new_id += 1
						i += 1
					megatile_ids.append(id)
					if tile_hash in mega_lookup:
						mega_lookup[tile_hash].append(id)
					else:
						mega_lookup[tile_hash] = [id]
			if len(new_megatiles) > self.megatiles_remaining():
				raise PyMSError('Importing','Import aborted because it exceeded the maximum megatile count (%d + %d > %d)' % (self.vf4.flag_count(),len(new_megatiles),VF4.MAX_ID+1))
			if tiletype == TileType.group:
				groups = megas_h
				if tiletype == TileType.group and options.groups_ignore_extra and groups > len(ids):
					groups = len(ids)
				for n in range(groups):
					megatile_ids = megatile_ids[n*16:(n+1)*16]
					if len(ids):
						id = ids[0]
						del ids[0]
						update_groups.append((id,megatile_ids))
					else:
						if tiletype == TileType.group:
							new_ids.append(self.cv5.group_count() + len(new_groups))
						new_groups.append(megatile_ids)
				if len(new_groups) > self.groups_remaining():
					raise PyMSError('Importing','Import aborted because it exceeded the maximum megatile group count (%d + %d > %d)' % (self.cv5.group_count(),len(new_groups),CV5.MAX_ID+1))
		# Update minitiles
		for new_image in new_images:
			self.vr4.add_image(new_image)
		for id,image in update_images:
			self.vr4.set_image(id, image)
		# Update megatiles
		for megatile in new_megatiles:
			self.vx4.add_megatile(megatile)
		for _ in range(len(new_megatiles)):
			self.vf4.add_flags([0]*16)
		for id,tile in update_megatiles:
			self.vx4.set_megatile(id, tile)
		# Update megatile groups
		for megatile_ids in new_groups:
			group = CV5Group()
			group.megatile_ids = megatile_ids
			self.cv5.add_group(group)
		for id,megatile_ids in update_groups:
			self.cv5.get_group(id).megatile_ids = megatile_ids
		return new_ids

	def export_graphics(self, tiletype, path, ids): # type: (TileType, str, list[int]) -> None
		bmp = BMP()
		bmp.palette = list(self.wpe.palette)
		tiles_wide = 0
		tile_width = 0
		tiles_high = 0
		tile_height = 0
		def calc_dims(tiles):
			for f in range(int(math.sqrt(tiles)),0,-1):
				if not tiles % f:
					return (tiles // f, f)
			return (tiles,1)
		if tiletype == TileType.group:
			tiles_wide,tiles_high = 16,len(ids)
			tile_width,tile_height = 32,32
			tiletype = TileType.mega
			groups = ids
			ids = []
			for id in groups:
				ids.extend(self.cv5.get_group(id).megatile_ids)
		elif tiletype == TileType.mega:
			tiles_wide,tiles_high = calc_dims(len(ids))
			tile_width,tile_height = 32,32
		elif tiletype == TileType.mini:
			tiles_wide,tiles_high = calc_dims(len(ids))
		bmp.width = tile_width * tiles_wide
		bmp.height = tile_height * tiles_high
		bmp.image = [[] for _ in range(bmp.height)]
		if tiletype == TileType.mega:
			for mega_n,mega_id in enumerate(ids):
				mega_y = (mega_n // tiles_wide) * tile_height
				for mini_n in range(16):
					mini_y = (mini_n // 4) * 8
					minitile = self.vx4.get_megatile(mega_id).minitiles[mini_n]
					image = self.vr4.get_image(minitile.image_id)
					for row_y,row in enumerate(image):
						if minitile.flipped:
							row = tuple(reversed(row))
						bmp.image[mega_y+mini_y+row_y].extend(row)
		elif tiletype == TileType.mini:
			for mini_y,mini_id in enumerate(ids):
				image = self.vr4.get_image(mini_id)
				for row_y,row in enumerate(image):
					bmp.image[mini_y+row_y].extend(row)
		bmp.save_file(path)

	def export_settings(self, tiletype, path_or_file, ids, options=ExportSettingsOptions()): # type: (TileType, str, list[int], ExportSettingsOptions) -> None
		if tiletype == TileType.mini:
			raise PyMSError('Export', "Can't export settings for minitiles")
		if isinstance(path_or_file, str):
			close = True
			file = AtomicWriter(path_or_file, 'w')
		else:
			close = False
			file = path_or_file
		if tiletype == TileType.group and self.cv5_path is not None:
			file.write("# Exported from %s\n" % self.cv5_path)
		elif tiletype == TileType.mega and self.vf4_path is not None:
			file.write("# Exported from %s\n" % self.vf4_path)
		for id in ids:
			if tiletype == TileType.group:
				group = self.cv5.get_group(id)
				def write_int(name, value, export):
					if not export:
						return
					file.write("\n\t%s:%s%d" % (name, ' ' * (23-len(name)), value))
				def write_flag(name, value, flag, export):
					if not export:
						return
					file.write("\n\tflag.%s:%s%s" % (name, ' ' * (18-len(name)), '1' if value & flag else '0'))
				file.write("""\
# Export of MegaTile Group %s
%sGroup:""" % (id, 'Tile' if group.type != CV5Group.TYPE_DOODAD else 'Doodad'))
				write_int('type', group.type, options.groups_type)
				write_flag('walkable', group.flags, CV5Flag.walkable, options.groups_flags)
				write_flag('walkable', group.flags, CV5Flag.walkable, options.groups_flags)
				write_flag('unknown_0002', group.flags, CV5Flag.unknown_0002, options.groups_flags)
				write_flag('unwalkable', group.flags, CV5Flag.unwalkable, options.groups_flags)
				write_flag('unknown_0008', group.flags, CV5Flag.unknown_0008, options.groups_flags)
				write_flag('has_doodad_cover', group.flags, CV5Flag.has_doodad_cover, options.groups_flags)
				write_flag('unknown_0020', group.flags, CV5Flag.unknown_0020, options.groups_flags)
				write_flag('creep', group.flags, CV5Flag.creep, options.groups_flags)
				write_flag('unbuildable', group.flags, CV5Flag.unbuildable, options.groups_flags)
				write_flag('blocks_view', group.flags, CV5Flag.blocks_view, options.groups_flags)
				write_flag('mid_ground', group.flags, CV5Flag.mid_ground, options.groups_flags)
				write_flag('high_ground', group.flags, CV5Flag.high_ground, options.groups_flags)
				write_flag('occupied', group.flags, CV5Flag.occupied, options.groups_flags)
				write_flag('creep_receding', group.flags, CV5Flag.creep_receding, options.groups_flags)
				write_flag('cliff_edge', group.flags, CV5Flag.cliff_edge, options.groups_flags)
				write_flag('creep_temp', group.flags, CV5Flag.creep_temp, options.groups_flags)
				write_flag('special_placeable', group.flags, CV5Flag.special_placeable, options.groups_flags)
				if group.type != CV5Group.TYPE_DOODAD:
					write_int('edge_left', group.basic_edge_left, options.groups_basic_edge_left)
					write_int('edge_up', group.basic_edge_up, options.groups_basic_edge_up)
					write_int('edge_right', group.basic_edge_right, options.groups_basic_edge_right)
					write_int('edge_down', group.basic_edge_down, options.groups_basic_edge_down)
					write_int('piece_left', group.basic_piece_left, options.groups_basic_piece_left)
					write_int('piece_up', group.basic_piece_up, options.groups_basic_piece_up)
					write_int('piece_right', group.basic_piece_right, options.groups_basic_piece_right)
					write_int('piece_down', group.basic_piece_down, options.groups_basic_piece_down)
				else:
					write_int('overlay_id', group.doodad_overlay_id, options.groups_doodad_overlay_id)
					write_int('scr', group.doodad_scr, options.groups_doodad_scr)
					write_int('string_id', group.doodad_string_id, options.groups_doodad_string_id)
					write_int('unknown4', group.doodad_unknown4, options.groups_doodad_unknown4)
					write_int('dddata_id', group.doodad_dddata_id, options.groups_doodad_dddata_id)
					write_int('width', group.doodad_width, options.groups_doodad_width)
					write_int('height', group.doodad_height, options.groups_doodad_height)
					write_int('unknown8', group.doodad_unknown8, options.groups_doodad_unknown8)
			elif tiletype == TileType.mega:
				def write_flags(id, name, mask_values, else_value): # type: (int, str, tuple[tuple[int, str], ...], str) -> None
					file.write('\n\t%s:' % name)
					for n in range(16):
						if not n % 4:
							file.write('\n\t\t')
						flags = self.vf4.get_flags(id)[n]
						for mask,value in mask_values:
							if (flags & mask) == mask:
								file.write(value)
								break
						else:
							file.write(else_value)
				file.write("""\
# Export of MegaTile %s
MegaTile:""" % id)
				layers = [] # type: list[tuple[str, tuple[tuple[int, str], ...], str]]
				if options.megatiles_export_height:
					layers.append(('Height', ((2,'H'),(1,'M')), 'L'))
				if options.megatiles_export_walkability:
					layers.append(('Walkability', ((1,'1'),), '0'))
				if options.megatiles_export_block_sight:
					layers.append(('Block Sight', ((8,'1'),), '0'))
				if options.megatiles_export_ramp:
					layers.append(('Ramp', ((16,'1'),), '0'))
				for layer in layers:
					write_flags(id, *layer)
				file.write('\n\n')
		if close:
			file.close()

	_line_re = re.compile(r'^\s*(.*?)\s*(?:#.*)?\s*$')
	_group_re = re.compile(r'^\s*(Tile|Doodad)Group:\s*$')
	# TODO: Re-write import settings
	def import_settings(self, tiletype, path_or_text, ids, options=ImportSettingsOptions()): # type: (TileType, str, list[int], ImportSettingsOptions) -> None
		raise PyMSError('Internal', 'Need to re-write settings import')
		# if tiletype == TileType.mini:
		# 	raise PyMSError('Import', "Can't import settings for minitiles")
		# if '\r' in path_or_text or '\n' in path_or_text:
		# 	lines = list(str(l) for l in re.split('[\r\n]+', path_or_text))
		# else:
		# 	try:
		# 		with open(path_or_text,'r') as settings_file:
		# 			lines = settings_file.readlines()
		# 	except:
		# 		raise PyMSError('Importing',"Could not load file '%s'" % path_or_text)
		# importing_groups = [] # type: list[tuple[bool, int, list[int | None]]]
		# importing_megas = [] # type: list[list[list[int | None] | None]]
		# group_fields = [
		# 	# TileGroup
		# 	[
		# 		'Index',
		# 		'Buildable',
		# 		'Flags',
		# 		'Buildable2',
		# 		'GroundHeight',
		# 		'EdgeLeft',
		# 		'EdgeUp',
		# 		'EdgeRight',
		# 		'EdgeDown',
		# 		'Unknown9',
		# 		'HasUp',
		# 		'Unknown11',
		# 		'HasDown'
		# 	],
		# 	# DoodadGroup
		# 	[
		# 		'Index',
		# 		'Buildable',
		# 		'Unknown1',
		# 		'OverlayFlags',
		# 		'GroundHeight',
		# 		'OverlayID',
		# 		'Unknown6',
		# 		'DoodadGroupString',
		# 		'Unknown8',
		# 		'DDDataID',
		# 		'DoodadWidth',
		# 		'DoodadHeight',
		# 		'Unknown12'
		# 	]
		# ]
		# setting_re = re.compile(r'^\s*([a-zA-Z0-9]+):\s*(\d+)\s*$')
		# height_re = re.compile(r'^\s*[LMH?]{4}\s*$')
		# height_flags = {
		# 	'L': HEIGHT_LOW,
		# 	'M': HEIGHT_MID,
		# 	'H': HEIGHT_HIGH,
		# 	'?': None
		# }
		# bool_re = re.compile(r'^\s*[01?]{4}\s*$')
		# bool_flags = {
		# 	'0': False,
		# 	'1': True,
		# 	'?': None
		# }
		# last_line = len(lines)-1
		# def get_line(inside=None, validate_re=None, validate_msg=None): # type: (str | None, re.Pattern | None, str | None) -> str
		# 	while len(lines):
		# 		line = Tileset._line_re.sub('\\1', lines.pop(0))
		# 		if not line:
		# 			continue
		# 		if validate_re and not validate_re.match(line):
		# 			message = 'Unknown line format'
		# 			if validate_msg:
		# 				message += ', expected ' + validate_msg
		# 			raise PyMSError('Importing', message, last_line-len(lines), line)
		# 		return line
		# 	if inside:
		# 		raise PyMSError('Importing', 'Unexpected end of file inside ' + inside)
		# 	return ''
		# while lines:
		# 	line = get_line()
		# 	if not line:
		# 		continue
		# 	if tiletype == TileType.group:
		# 		m = Tileset._group_re.match(line)
		# 		if m:
		# 			importing_groups.append(((m.group(1) == 'Doodad'),last_line-len(lines),[None] * 13))
		# 			continue
		# 		if not importing_groups:
		# 			raise PyMSError('Importing', 'Unknown line format, expected a TileGroup or DoodadGroup header.', last_line-len(lines), line)
		# 		m = setting_re.match(line)
		# 		if not m or not m.group(1) in group_fields[importing_groups[-1][0]]:
		# 			raise PyMSError('Importing', 'Unknown line format, expected a group setting (Index, Buildable, etc.)', last_line-len(lines), line)
		# 		index = group_fields[importing_groups[-1][0]].index(m.group(1))
		# 		importing_groups[-1][2][index] = int(m.group(2)) # TODO: storage limits
		# 	elif tiletype == TileType.mega:
		# 		if line == 'MegaTile:':
		# 			if len(importing_megas) and all(flag is None for flag in importing_megas[-1]):
		# 				raise PyMSError('Importing', 'Previous MegaTile is empty.', last_line-len(lines), line)
		# 			importing_megas.append([None]*4)
		# 			continue
		# 		if not importing_megas:
		# 			raise PyMSError('Importing', 'Unknown line format, expected a MegaTile header.', last_line-len(lines), line)
		# 		mega_flags = [] # type: list[int | None]
		# 		if line == 'Height:':
		# 			for _ in range(4):
		# 				mega_flags.extend(height_flags[f] for f in get_line('Height settings', height_re, ' 4 height flags (flags = L, M, H, or ?)'))
		# 			importing_megas[-1][0] = mega_flags
		# 		elif line == 'Walkability:':
		# 			for _ in range(4):
		# 				mega_flags.extend(bool_flags[f] for f in get_line('Walkability settings', bool_re, ' 4 walkability flags (1 = Walkable, 0 = Not, or ?)'))
		# 			importing_megas[-1][1] = mega_flags
		# 		elif line == 'Block Sight:':
		# 			for _ in range(4):
		# 				mega_flags.extend(bool_flags[f] for f in get_line('Block Sight settings', bool_re, ' 4 block sight flags (1 = Blocked, 0 = Not, or ?)'))
		# 			importing_megas[-1][2] = mega_flags
		# 		elif line == 'Ramp:':
		# 			for _ in range(4):
		# 				mega_flags.extend(bool_flags[f] for f in get_line('Ramp settings', bool_re, ' 4 ramp flags (1 = Ramp(?), 0 = Not)'))
		# 			importing_megas[-1][3] = mega_flags
		# 		else:
		# 			raise PyMSError('Importing', 'Unknown line format, expected a setting header (Height, Walkability, Block Sight, or Ramp).', last_line-len(lines), line)
		# if not len(importing_groups) and not len(importing_megas):
		# 	raise PyMSError('Importing', 'Nothing to import.')
		# if len(importing_megas) and all(flag is None for flag in importing_megas[-1]):
		# 	raise PyMSError('Importing', 'Last %s is empty.' % (''))
		# repeater = options.repeater
		# if tiletype == TileType.group:
		# 	setting_count = len(importing_groups)
		# elif tiletype == TileType.mega:
		# 	setting_count = len(importing_megas)
		# tile_count = len(ids)
		# for tile_n,id in enumerate(ids):
		# 	settings_n = repeater(setting_count, tile_n, tile_count)
		# 	if settings_n is None:
		# 		break
		# 	if tiletype == TileType.group:
		# 		_,_,group_data = importing_groups[settings_n]
		# 		group = CV5Group()
		# 		group.type = group_data[0] or 0
		# 		group.flags = group_data[1] or 0
		# 		group._edge_left_or_overlay_id = group_data[3] or 0
		# 		group._edge_up_or_scr = group_data[3] or 0
		# 		group._edge_right_or_string_id = group_data[4] or 0
		# 		group._edge_down_or_unknown4 = group_data[5] or 0
		# 		group._piece_left_or_dddata_id = group_data[6] or 0
		# 		group._piece_up_or_width = group_data[7] or 0
		# 		group._piece_right_or_height = group_data[8] or 0
		# 		group._piece_down_or_unknown8 = group_data[9] or 0
		# 		self.cv5.get_group(id).update_settings(group)
		# 	else:
		# 		mega_data = importing_megas[settings_n]
		# 		for mini_n in range(16):
		# 			flags = self.vf4.get_flags(id)[mini_n]
		# 			if mega_data[0] is not None and mega_data[0][mini_n] is not None:
		# 				flags &= ~(HEIGHT_MID | HEIGHT_HIGH)
		# 				flags |= mega_data[0][mini_n] or 0
		# 			if mega_data[1] is not None and mega_data[1][mini_n] is not None:
		# 				if mega_data[1][mini_n]:
		# 					flags |= 1
		# 				else:
		# 					flags &= ~1
		# 			if mega_data[2] is not None and mega_data[2][mini_n] is not None:
		# 				if mega_data[2][mini_n]:
		# 					flags |= 8
		# 				else:
		# 					flags &= ~8
		# 			if mega_data[3] is not None and mega_data[3][mini_n] is not None:
		# 				if mega_data[3][mini_n]:
		# 					flags |= 16
		# 				else:
		# 					flags &= ~16
		# 			self.vf4.get_flags(id)[mini_n] = flags
