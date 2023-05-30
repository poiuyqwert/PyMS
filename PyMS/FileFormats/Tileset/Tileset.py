
try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	from ...Utilities import Assets
	from ...Utilities.DependencyError import DependencyError
	import sys, os
	e = DependencyError('PyMS', 'Pillow is missing. Consult the Source Installation section of the README.', (('README','file:///%s' % Assets.readme_file_path),))
	e.startup()
	sys.exit()

from .CV5 import CV5
from .VF4 import VF4
from .VX4 import VX4
from .VR4 import VR4
from .DDDataBIN import DDDataBIN

from ..Palette import Palette
from ..BMP import BMP

from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import os, re, math

# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
	

def megatile_to_photo(tileset, megatile_id): # type: (Tileset, int) -> (ImageTk.PhotoImage | None)
	try:
		megatile = tileset.vx4.megatiles[megatile_id]
	except:
		return None
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
			image[int(m/4)*8+y].extend(p)
	put = [] # type: list[int]
	for row in image:
		put.extend(row)
	pi.putdata(put)
	return ImageTk.PhotoImage(pi)

def minitile_to_photo(tileset, minitile): # type: (Tileset, tuple[int, bool]) -> ImageTk.PhotoImage
	image = tileset.vr4.get_image(minitile[0])
	flip = minitile[1]
	pi = PILImage.new('P', (24,24))
	pal = [] # type: list[int]
	for c in tileset.wpe.palette:
		pal.extend(c)
	pi.putpalette(pal)
	put = [] # type: list[int]
	for _y,p in enumerate(image):
		if flip:
			p = p[::-1]
		for x in p * 3:
			put.extend((x,x,x))
	pi.putdata(put)
	return ImageTk.PhotoImage(pi)

TILETYPE_GROUP = 0
TILETYPE_MEGA  = 1
TILETYPE_MINI  = 2

HEIGHT_LOW  = 0
HEIGHT_MID  = (1 << 1)
HEIGHT_HIGH = (1 << 2)

def setting_import_extras_ignore(setting_count, tile_n, tile_count): # type: (int, int, int) -> (int | None)
	if tile_n == setting_count:
		return None
	return tile_n

def setting_import_extras_repeat_all(setting_count, tile_n, tile_count): # type: (int, int, int) -> int
	return tile_n % setting_count

def setting_import_extras_repeat_last(setting_count, tile_n, tile_count): # type: (int, int, int) -> int
	return min(tile_n, setting_count-1)

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
		return self.vx4.graphics_remaining()

	def minitiles_max(self): # type: () -> int
		return self.vr4.max_id(self.vx4.expanded)+1
	def minitiles_remaining(self): # type: () -> int
		return self.vr4.images_remaining(expanded_vx4=self.vx4.expanded)

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
			expanded = 'ex' if self.vx4.expanded else ''
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

	# options.groups_ignore_extra                  - Ignore extra groups (Boolean, default: False)
	# options.megatiles_ignore_extra               - Ignore extra megatiles (Boolean, default: False)
	# options.megatiles_reuse_duplicates_old       - Attempt to find and reuse existing minitile images (Boolean, default: False)
	# options.megatiles_reuse_duplicates_new       - Attempt to find and reuse duplicate imported minitile images (Boolean, default: False)
	# options.megatiles_reuse_null_with_id         - Reuse "null" megatile with id even if find duplicates is off (None or int, default: 0)
	# options.minitiles_ignore_extra               - Ignore extra minitiles (Boolean, default: False)
	# options.minitiles_reuse_duplicates_old       - Attempt to find and reuse existing minitile images (Boolean, default: True)
	# options.minitiles_reuse_duplicates_new       - Attempt to find and reuse duplicate imported minitile images (Boolean, default: True)
	# options.minitiles_reuse_null_with_id         - Reuse "null" minitile with id even if find duplicates is off (None or int, default: 0)
	# options.minitiles_reuse_duplicates_flipped   - Check flipped versions of tiles for duplicates (Boolean, default: True)
	# options.minitiles_expand_allowed             - Whether importing too many minitiles will expand VX4 or not (True, False, or callback, default: False)
	def import_graphics(self, tiletype, bmpfiles, ids=None, options={}): # type: (int, list[str], list[int] | None, dict) -> None
		if ids:
			ids = list(ids)
		else:
			ids = []
		new_ids = [] # type: list[int]
		pixels = [] # type: list[list[int]]
		for path in bmpfiles:
			bmp = BMP()
			bmp.load_file(path)
			if tiletype == TILETYPE_GROUP and (bmp.width != 512 or bmp.height % 32):
				raise PyMSError('Interpreting','The image is not the correct size for tile groups (got %sx%s, expected width to be 512 and height to be a multiple of 32)' % (bmp.width,bmp.height))
			elif tiletype == TILETYPE_MEGA and (bmp.width % 32 or bmp.height % 32):
				raise PyMSError('Interpreting','The image is not the correct size for megatiles (got %sx%s, expected width and height to be multiples of 32)' % (bmp.width,bmp.height))
			elif tiletype == TILETYPE_MINI and (bmp.width % 8 or bmp.height % 8):
				raise PyMSError('Interpreting','The image is not the correct size for minitiles (got %sx%s, expected width and height to be multiples of 8)' % (bmp.width,bmp.height))
			pixels.extend(bmp.image)
		new_images = [] # type: list[tuple[tuple[int, ...], ...]]
		mini_lookup = {} # type: dict[int, list[int]]
		update_images = [] # type: list[tuple[int, tuple[tuple[int,...], ...]]]
		new_megatiles = [] # type: list[tuple[tuple[int, bool], ...]]
		mega_lookup = {} # type: dict[int, list[int]]
		update_megatiles = [] # type: list[tuple[int, list[tuple[int, ...]]]]
		new_groups = [] # type: list[int]
		update_groups = [] # # type: list[tuple[int, list[int]]]

		minis_w = int(len(pixels[0]) / 8)
		minis_h = int(len(pixels) / 8)
		for iy in range(minis_h):
			py = iy * 8
			for ix in range(minis_w):
				px = ix * 8
				image = tuple(tuple(pixels[py+oy][px:px+8]) for oy in range(8))
				new_images.append(image)
		image_details = [] # type: list[tuple[int, bool]]
		new_id = self.vr4.images_count()
		i = 0
		minitiles_reuse_null_with_id = int(options.get('minitiles_reuse_null_with_id', 0))
		minitiles_reuse_duplicates_old = bool(options.get('minitiles_reuse_duplicates_old', True))
		minitiles_reuse_duplicates_new = bool(options.get('minitiles_reuse_duplicates_new', True))
		# minitiles_reuse_duplicates_flipped = options.get('minitiles_reuse_duplicates_flipped', True) # TODO: Figure out why this is not used
		if tiletype == TILETYPE_MINI and options.get('minitiles_ignore_extra', False) and len(new_images) > len(ids):
			new_images = new_images[:len(ids)]
		while i < len(new_images):
			image = new_images[i]
			image_hash = VR4.image_hash(image)
			found = False
			if tiletype != TILETYPE_MINI or not len(ids):
				existing_normal_ids, existing_flipped_ids = self.vr4.find_image(image)
				existing_all_ids = existing_normal_ids + existing_flipped_ids
				if existing_all_ids and (minitiles_reuse_duplicates_old or minitiles_reuse_null_with_id in existing_all_ids):
					flipped = not len(existing_normal_ids)
					found = True
					del new_images[i]
					image_details.append((existing_all_ids[0], flipped))
				if not found:
					existing_normal_ids = mini_lookup.get(image_hash,[])
					flipped_hash = VR4.image_hash(image, True)
					existing_flipped_ids = mini_lookup.get(flipped_hash,[])
					existing_all_ids = existing_normal_ids + existing_flipped_ids
					if existing_all_ids and (minitiles_reuse_duplicates_new or minitiles_reuse_null_with_id in existing_all_ids):
						flipped = not len(existing_normal_ids)
						found = True
						del new_images[i]
						image_details.append((existing_all_ids[0], flipped))
			if not found:
				id = new_id
				if tiletype == TILETYPE_MINI and len(ids):
					id = ids[0]
					del ids[0]
					update_images.append((id, new_images[i]))
					del new_images[i]
				else:
					if tiletype == TILETYPE_MINI:
						new_ids.append(new_id)
					new_id += 1
					i += 1
				image_details.append((id,False))
				if image_hash in mini_lookup:
					mini_lookup[image_hash].append(id)
				else:
					mini_lookup[image_hash] = [id]
		minitiles_expand_allowed = options.get('minitiles_expand_allowed', False)
		if len(new_images) > self.minitiles_remaining():
			if self.vx4.expanded or not minitiles_expand_allowed or (callable(minitiles_expand_allowed) and not minitiles_expand_allowed()):
				raise PyMSError('Importing','Import aborted because it exceeded the maximum minitile image count (%d + %d > %d)' % (len(self.vr4.images),len(new_images),VR4.MAX_ID+1))
			self.vx4.expanded = True
		if tiletype == TILETYPE_GROUP or tiletype == TILETYPE_MEGA:
			megas_w = int(minis_w / 4)
			megas_h = int(minis_h / 4)
			for y in range(megas_h):
				for x in range(megas_w):
					minitiles = [] # type: list[tuple[int, bool]]
					for oy in range(4):
						o = (y*4+oy)*minis_w + x*4
						minitiles.extend(image_details[o:o+4])
					new_megatiles.append(tuple(minitiles))
			megatile_ids = []
			new_id = len(self.vx4.megatiles)
			i = 0
			megatiles_reuse_null_with_id = options.get('megatiles_reuse_null_with_id', 0)
			megatiles_reuse_duplicates_old = options.get('megatiles_reuse_duplicates_old', True)
			# megatiles_reuse_duplicates_new = options.get('megatiles_reuse_duplicates_new', True) # TODO: Figure out why this is not used
			if tiletype == TILETYPE_MEGA and options.get('megatiles_ignore_extra', False) and len(new_megatiles) > len(ids):
				new_megatiles = new_megatiles[:len(ids)]
			while i < len(new_megatiles):
				tile_hash = hash(new_megatiles[i])
				found = False
				if tiletype != TILETYPE_MEGA or not len(ids):
					existing_ids = self.vx4.lookup.get(tile_hash,[])
					if existing_ids and (megatiles_reuse_duplicates_old or megatiles_reuse_null_with_id in existing_ids):
						del new_megatiles[i]
						megatile_ids.append(existing_ids[0])
						found = True
					if not found:
						existing_ids = mega_lookup.get(tile_hash,[])
						if existing_ids and (megatiles_reuse_duplicates_old or megatiles_reuse_null_with_id in existing_ids):
							del new_megatiles[i]
							megatile_ids.append(existing_ids[0])
							found = True
				if not found:
					id = new_id
					if tiletype == TILETYPE_MEGA and len(ids):
						id = ids[0]
						del ids[0]
						update_megatiles.append((id, new_megatiles[i]))
						del new_megatiles[i]
					else:
						if tiletype == TILETYPE_MEGA:
							new_ids.append(new_id)
						new_id += 1
						i += 1
					megatile_ids.append(id)
					if tile_hash in mega_lookup:
						mega_lookup[tile_hash].append(id)
					else:
						mega_lookup[tile_hash] = [id]
			if len(new_megatiles) > self.megatiles_remaining():
				raise PyMSError('Importing','Import aborted because it exceeded the maximum megatile count (%d + %d > %d)' % (len(self.vf4.flags),len(new_megatiles),VF4.MAX_ID+1))
			if tiletype == TILETYPE_GROUP:
				groups = megas_h
				if tiletype == TILETYPE_GROUP and options.get('groups_ignore_extra', False) and groups > len(ids):
					groups = len(ids)
				for n in range(groups):
					group = megatile_ids[n*16:(n+1)*16]
					if len(ids):
						id = ids[0]
						del ids[0]
						update_groups.append((id,group))
					else:
						if tiletype == TILETYPE_GROUP:
							new_ids.append(len(self.cv5.groups) + len(new_groups))
						new_groups.append(group)
				if len(new_groups) > self.groups_remaining():
					raise PyMSError('Importing','Import aborted because it exceeded the maximum megatile group count (%d + %d > %d)' % (len(self.cv5.groups),len(new_groups),CV5.MAX_ID+1))
		# Update minitiles
		self.vr4.images.extend(new_images)
		for id,image in update_images:
			self.vr4.set_image(id, image)
		for image_hash in mini_lookup:
			if image_hash in self.vr4.lookup:
				self.vr4.lookup[image_hash].extend(mini_lookup[image_hash])
			else:
				self.vr4.lookup[image_hash] = mini_lookup[image_hash]
		# Update megatiles
		for megatile in new_megatiles:
			self.vx4.megatiles.add_tile(megatile)
		self.vf4.flags.extend([0]*16 for _ in range(len(new_megatiles)))
		for id,tile in update_megatiles:
			self.vx4.set_tile(id, tile)
		for tile_hash in mega_lookup:
			if tile_hash in self.vx4.lookup:
				self.vx4.lookup[tile_hash].extend(mega_lookup[tile_hash])
			else:
				self.vx4.lookup[tile_hash] = mega_lookup[tile_hash]
		# Update megatile groups
		for group in new_groups:
			self.cv5.groups.append([0]*13 + [group])
		for id,group in update_groups:
			self.cv5.groups[id][13] = group
		return new_ids

	def export_graphics(self, tiletype, path, ids):
		bmp = BMP()
		bmp.palette = list(self.wpe.palette)
		tiles_wide = 0
		tile_width = 0
		tiles_high = 0
		tile_height = 0
		def calc_dims(tiles):
			for f in range(int(math.sqrt(tiles)),0,-1):
				if not tiles % f:
					return (tiles / f, f)
			return (tiles,1)
		if tiletype == TILETYPE_GROUP:
			tiles_wide,tiles_high = 16,len(ids)
			tile_width,tile_height = 32,32
			tiletype = TILETYPE_MEGA
			groups = ids
			ids = []
			for id in groups:
				ids.extend(self.cv5.groups[id][13])
		elif tiletype == TILETYPE_MEGA:
			tiles_wide,tiles_high = calc_dims(len(ids))
			tile_width,tile_height = 32,32
		elif tiletype == TILETYPE_MINI:
			tiles_wide,tiles_high = calc_dims(len(ids))
		bmp.width = tile_width * tiles_wide
		bmp.height = tile_height * tiles_high
		bmp.image = [[] for _ in range(bmp.height)]
		if tiletype == TILETYPE_MEGA:
			for mega_n,mega_id in enumerate(ids):
				mega_y = (mega_n / tiles_wide) * tile_height
				for mini_n in range(16):
					mini_y = (mini_n / 4) * 8
					mini_id,flipped = self.vx4.graphics[mega_id][mini_n]
					image = self.vr4.images[mini_id]
					for row_y,row in enumerate(image):
						if flipped:
							row = reversed(row)
						bmp.image[mega_y+mini_y+row_y].extend(row)
		elif tiletype == TILETYPE_MINI:
			for mini_y,mini_id in enumerate(ids):
				image = self.vr4.images[mini_id]
				for row_y,row in enumerate(image):
					bmp.image[mini_y+row_y].extend(row)
		bmp.save_file(path)

	# options.groups_export_index
	# options.groups_export_buildable
	# options.groups_export_flags
	# options.groups_export_buildable2
	# options.groups_export_ground_height
	# options.groups_export_edge_left
	# options.groups_export_edge_up
	# options.groups_export_edge_right
	# options.groups_export_edge_down
	# options.groups_export_unknown9
	# options.groups_export_has_up
	# options.groups_export_unknown11
	# options.groups_export_has_down
	# options.groups_export_unknown1
	# options.groups_export_overlay_flags
	# options.groups_export_overlay_id
	# options.groups_export_unknown6
	# options.groups_export_doodad_group_string
	# options.groups_export_unknown8
	# options.groups_export_dddata_id
	# options.groups_export_doodad_width
	# options.groups_export_doodad_height
	# options.groups_export_unknown12
	# options.megatiles_export_height
	# options.megatiles_export_walkability
	# options.megatiles_export_block_sight
	# options.megatiles_export_ramp
	def export_settings(self, tiletype, path_or_file, ids, options={}):
		if isinstance(path_or_file, str):
			close = True
			file = AtomicWriter(path_or_file, 'w')
		else:
			close = False
			file = path_or_file
		if tiletype == TILETYPE_GROUP and self.cv5_path is not None:
			file.write("# Exported from %s\n" % self.cv5_path)
		elif tiletype == TILETYPE_MEGA and self.vf4_path is not None:
			file.write("# Exported from %s\n" % self.vf4_path)
		groups_export_index = options.get('groups_export_index',True)
		groups_export_buildable = options.get('groups_export_buildable',True)
		groups_export_flags = options.get('groups_export_flags',True)
		groups_export_buildable2 = options.get('groups_export_buildable2',True)
		groups_export_ground_height = options.get('groups_export_ground_height',True)
		groups_export_edge_left = options.get('groups_export_edge_left',True)
		groups_export_edge_up = options.get('groups_export_edge_up',True)
		groups_export_edge_right = options.get('groups_export_edge_right',True)
		groups_export_edge_down = options.get('groups_export_edge_down',True)
		groups_export_unknown9 = options.get('groups_export_unknown9',True)
		groups_export_has_up = options.get('groups_export_has_up',True)
		groups_export_unknown11 = options.get('groups_export_unknown11',True)
		groups_export_has_down = options.get('groups_export_has_down',True)
		groups_export_unknown1 = options.get('groups_export_unknown1',True)
		groups_export_overlay_flags = options.get('groups_export_overlay_flags',True)
		groups_export_overlay_id = options.get('groups_export_overlay_id',True)
		groups_export_unknown6 = options.get('groups_export_unknown6',True)
		groups_export_doodad_group_string = options.get('groups_export_doodad_group_string',True)
		groups_export_unknown8 = options.get('groups_export_unknown8',True)
		groups_export_dddata_id = options.get('groups_export_dddata_id',True)
		groups_export_doodad_width = options.get('groups_export_doodad_width',True)
		groups_export_doodad_height = options.get('groups_export_doodad_height',True)
		groups_export_unknown12 = options.get('groups_export_unknown12',True)
		megatiles_export_height = options.get('megatiles_export_height',True)
		megatiles_export_walkability = options.get('megatiles_export_walkability',True)
		megatiles_export_block_sight = options.get('megatiles_export_block_sight',True)
		megatiles_export_ramp = options.get('megatiles_export_ramp',True)
		for id in ids:
			if tiletype == TILETYPE_GROUP:
				data = self.cv5.groups[id][:13]
				if id < 1024:
					file.write("""\
# Export of MegaTile Group %s
TileGroup:""" % id)
					fields = (
						('Index',groups_export_index),
						('Buildable',groups_export_buildable),
						('Flags',groups_export_flags),
						('Buildable2',groups_export_buildable2),
						('GroundHeight',groups_export_ground_height),
						('EdgeLeft',groups_export_edge_left),
						('EdgeUp',groups_export_edge_up),
						('EdgeRight',groups_export_edge_right),
						('EdgeDown',groups_export_edge_down),
						('Unknown9',groups_export_unknown9),
						('HasUp',groups_export_has_up),
						('Unknown11',groups_export_unknown11),
						('HasDown',groups_export_has_down),
					)
				else:
					file.write("""\
# Export of MegaTile Group %s
DoodadGroup:""" % id)
					fields = (
						('Index',groups_export_index),
						('Buildable',groups_export_buildable),
						('Unknown1',groups_export_unknown1),
						('OverlayFlags',groups_export_overlay_flags),
						('GroundHeight',groups_export_ground_height),
						('OverlayID',groups_export_overlay_id),
						('Unknown6',groups_export_unknown6),
						('DoodadGroupString',groups_export_doodad_group_string),
						('Unknown8',groups_export_unknown8),
						('DDDataID',groups_export_dddata_id),
						('DoodadWidth',groups_export_doodad_width),
						('DoodadHeight',groups_export_doodad_height),
						('Unknown12',groups_export_unknown12),
					)
				for v,(name,show) in zip(data,fields):
					if show:
						file.write("\n\t%s:%s%s" % (name, ' ' * (22-len(name)), v))
			elif tiletype == TILETYPE_MEGA:
				def write_flags(id, name, mask_values, else_value):
					file.write('\n\t%s:' % name)
					for n in range(16):
						if not n % 4:
							file.write('\n\t\t')
						flags = self.vf4.flags[id][n]
						for mask,value in mask_values:
							if (flags & mask) == mask:
								file.write(value)
								break
						else:
							file.write(else_value)
				file.write("""\
# Export of MegaTile %s
MegaTile:""" % id)
				layers = []
				if megatiles_export_height:
					layers.append(('Height', ((HEIGHT_HIGH,'H'),(HEIGHT_MID,'M')), 'L'))
				if megatiles_export_walkability:
					layers.append(('Walkability', ((1,'1'),), '0'))
				if megatiles_export_block_sight:
					layers.append(('Block Sight', ((8,'1'),), '0'))
				if megatiles_export_ramp:
					layers.append(('Ramp', ((16,'1'),), '0'))
				for layer in layers:
					write_flags(id, *layer)
				file.write('\n\n')
		if close:
			file.close()

	# options.repeater (Func, default: setting_import_extras_ignore)
	def import_settings(self, tiletype, path_or_text, ids, options={}):
		if '\r' in path_or_text or '\n' in path_or_text:
			lines = re.split('[\r\n]+', path_or_text)
		else:
			try:
				with open(path_or_text,'r') as settings_file:
					lines = settings_file.readlines()
			except:
				raise PyMSError('Importing',"Could not load file '%s'" % path_or_text)
		importing = []
		line_re = re.compile(r'^\s*(.*?)\s*(?:#.*)?\s*$')
		group_re = re.compile(r'^\s*(Tile|Doodad)Group:\s*$')
		group_fields = [
			# TileGroup
			[
				'Index',
				'Buildable',
				'Flags',
				'Buildable2',
				'GroundHeight',
				'EdgeLeft',
				'EdgeUp',
				'EdgeRight',
				'EdgeDown',
				'Unknown9',
				'HasUp',
				'Unknown11',
				'HasDown'
			],
			# DoodadGroup
			[
				'Index',
				'Buildable',
				'Unknown1',
				'OverlayFlags',
				'GroundHeight',
				'OverlayID',
				'Unknown6',
				'DoodadGroupString',
				'Unknown8',
				'DDDataID',
				'DoodadWidth',
				'DoodadHeight',
				'Unknown12'
			]
		]
		setting_re = re.compile(r'^\s*([a-zA-Z0-9]+):\s*(\d+)\s*$')
		height_re = re.compile(r'^\s*[LMH?]{4}\s*$')
		height_flags = {
			'L': HEIGHT_LOW,
			'M': HEIGHT_MID,
			'H': HEIGHT_HIGH,
			'?': None
		}
		bool_re = re.compile(r'^\s*[01?]{4}\s*$')
		bool_flags = {
			'0': False,
			'1': True,
			'?': None
		}
		last_line = len(lines)-1
		def get_line(inside=None, validate_re=None, validate_msg=None):
			while len(lines):
				line = line_re.sub('\\1', lines.pop(0))
				if not line:
					continue
				if validate_re and not validate_re.match(line):
					message = 'Unknown line format'
					if validate_msg:
						message += ', expected ' + validate_msg
					raise PyMSError('Importing', message, last_line-len(lines), line)
				return line
			if inside:
				raise PyMSError('Importing', 'Unexpected end of file inside ' + inside)
		while lines:
			line = get_line()
			if not line:
				continue
			if tiletype == TILETYPE_GROUP:
				m = group_re.match(line)
				if m:
					importing.append(((m.group(1) == 'Doodad'),last_line-len(lines),[None] * 13))
					continue
				if not importing:
					raise PyMSError('Importing', 'Unknown line format, expected a TileGroup or DoodadGroup header.', last_line-len(lines), line)
				m = setting_re.match(line)
				if not m or not m.group(1) in group_fields[importing[-1][0]]:
					raise PyMSError('Importing', 'Unknown line format, expected a group setting (Index, Buildable, etc.)', last_line-len(lines), line)
				index = group_fields[importing[-1][0]].index(m.group(1))
				importing[-1][2][index] = int(m.group(2)) # TODO: storage limits
			elif tiletype == TILETYPE_MEGA:
				if line == 'MegaTile:':
					if len(importing) and all(flag is None for flag in importing[-1]):
						raise PyMSError('Importing', 'Previous MegaTile is empty.', last_line-len(lines), line)
					importing.append([None]*4)
					continue
				if not importing:
					raise PyMSError('Importing', 'Unknown line format, expected a MegaTile header.', last_line-len(lines), line)
				if line == 'Height:':
					flags = []
					for _ in range(4):
						flags.extend(height_flags[f] for f in get_line('Height settings', height_re, ' 4 height flags (flags = L, M, H, or ?)'))
					importing[-1][0] = flags
				elif line == 'Walkability:':
					flags = []
					for _ in range(4):
						flags.extend(bool_flags[f] for f in get_line('Walkability settings', bool_re, ' 4 walkability flags (1 = Walkable, 0 = Not, or ?)'))
					importing[-1][1] = flags
				elif line == 'Block Sight:':
					flags = []
					for _ in range(4):
						flags.extend(bool_flags[f] for f in get_line('Block Sight settings', bool_re, ' 4 block sight flags (1 = Blocked, 0 = Not, or ?)'))
					importing[-1][2] = flags
				elif line == 'Ramp:':
					flags = []
					for _ in range(4):
						flags.extend(bool_flags[f] for f in get_line('Ramp settings', bool_re, ' 4 ramp flags (1 = Ramp(?), 0 = Not)'))
					importing[-1][3] = flags
				else:
					raise PyMSError('Importing', 'Unknown line format, expected a setting header (Height, Walkability, Block Sight, or Ramp).', last_line-len(lines), line)
		if not len(importing):
			raise PyMSError('Importing', 'Nothing to import.')
		if len(importing) and all(flag is None for flag in importing[-1]):
			raise PyMSError('Importing', 'Last %s is empty.' % (''))
		repeater = options.get('repeater', setting_import_extras_ignore)
		setting_count = len(importing)
		tile_count = len(ids)
		if tiletype == TILETYPE_GROUP:
			for tile_n,id in enumerate(ids):
				settings_n = repeater(setting_count, tile_n, tile_count)
				if settings_n is None:
					break
				doodad,line_n,_ = importing[settings_n]
				if doodad and id < 1024:
					raise PyMSError('Importing', 'Attempting to import DoodadGroup onto TileGroup %s' % id, line_n)
				elif not doodad and id >= 1024:
					raise PyMSError('Importing', 'Attempting to import TileGroup onto DoodadGroup %s' % id, line_n)
		for tile_n,id in enumerate(ids):
			settings_n = repeater(setting_count, tile_n, tile_count)
			if settings_n is None:
				break
			data = importing[settings_n]
			if tiletype == TILETYPE_GROUP:
				_,_,data = data
				for n in range(13):
					if data[n] is not None:
						self.cv5.groups[id][n] = data[n]
			else:
				for mini_n in range(16):
					flags = self.vf4.flags[id][mini_n]
					if data[0] is not None and data[0][mini_n] is not None:
						flags &= ~(HEIGHT_MID | HEIGHT_HIGH)
						flags |= data[0][mini_n]
					if data[1] is not None and data[1][mini_n] is not None:
						if data[1][mini_n]:
							flags |= 1
						else:
							flags &= ~1
					if data[2] is not None and data[2][mini_n] is not None:
						if data[2][mini_n]:
							flags |= 8
						else:
							flags &= ~8
					if data[3] is not None and data[3][mini_n] is not None:
						if data[3][mini_n]:
							flags |= 16
						else:
							flags &= ~16
					self.vf4.flags[id][mini_n] = flags
