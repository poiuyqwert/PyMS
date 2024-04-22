
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

from .CV5 import CV5, CV5Group
from .VF4 import VF4, VF4Megatile
from .VX4 import VX4, VX4Megatile, VX4Minitile
from .VR4 import VR4, VR4Image
from .DDDataBIN import DDDataBIN
from .Serialize import TileGroupField, TileGroupDef, DoodadGroupField, DoodadGroupDef, MegatileField, MegatileDef

from ..Palette import Palette
from ..BMP import BMP

from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter
from ...Utilities import Serialize
from ...Utilities import IO

import os, math
from dataclasses import dataclass
from enum import Enum

from typing import Callable, cast, Sequence


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
class ImportSettingsOptions:
	repeater: Serialize.Repeater = Serialize.repeater_ignore

class Tileset(object):
	cv5: CV5
	cv5_path: str | None
	vf4: VF4
	vf4_path: str | None
	vx4: VX4
	vx4_path: str | None
	vr4: VR4
	vr4_path: str | None
	dddata: DDDataBIN
	dddata_path: str | None
	wpe: Palette
	wpe_path: str | None

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
		self.cv5_path = None
		if vf4:
			self.vf4 = vf4
		else:
			self.vf4 = VF4()
		self.vf4_path = None
		if vx4:
			self.vx4 = vx4
		else:
			self.vx4 = VX4()
		self.vx4_path = None
		if vr4:
			self.vr4 = vr4
		else:
			self.vr4 = VR4()
		self.vr4_path = None
		if dddata:
			self.dddata = dddata
		else:
			self.dddata = DDDataBIN()
		self.dddata_path = None
		if wpe:
			self.wpe = wpe
		else:
			self.wpe = Palette()
		self.wpe_path = None

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
				raise PyMSError('Importing','Import aborted because it exceeded the maximum megatile count (%d + %d > %d)' % (self.vf4.megatile_count(),len(new_megatiles),VF4.MAX_ID+1))
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
			self.vf4.add_megatile(VF4Megatile())
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
			tile_width,tile_height = 8,8
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
			for mini_n,mini_id in enumerate(ids):
				mini_y = (mini_n // tiles_wide) * tile_height
				image = self.vr4.get_image(mini_id)
				for row_y,row in enumerate(image):
					bmp.image[mini_y+row_y].extend(row)
		bmp.save_file(path)

	def export_group_settings(self, output: IO.AnyOutputText, ids: Sequence[int], fields: Serialize.Fields | None = None) -> None:
		with IO.OutputText(output) as file:
			if self.cv5_path is not None:
				file.write("# Exported from %s\n" % self.cv5_path)
			groups = list((self.cv5.get_group(id), id) for id in ids)
			def get_definition(group: object) -> (Serialize.Definition | None):
				if not isinstance(group, CV5Group):
					return None
				if group.type == CV5Group.TYPE_DOODAD:
					return DoodadGroupDef
				return TileGroupDef
			file.write(Serialize.encode_texts(groups, get_definition, fields))

	def import_group_settings(self, input: IO.AnyInputText, ids: list[int], options: ImportSettingsOptions = ImportSettingsOptions()) -> None:
		with IO.InputText(input) as file:
			text = file.read()

		def get_group(n: int, definition: Serialize.Definition) -> CV5Group:
			if n >= len(ids):
				raise PyMSError('Internal', f'Attempted to import on group {n} with only {len(ids)} being imported')
			id = ids[n]
			group = self.cv5.get_group(id)
			if definition == TileGroupDef and group.type == CV5Group.TYPE_DOODAD:
				raise PyMSError('Import', f'Attempting to import TileGroup onto DoodadGroup {id}')
			elif definition == DoodadGroupDef and group.type != CV5Group.TYPE_DOODAD:
				raise PyMSError('Import', f'Attempting to import DoodadGroup onto TileGroup {id}')
			return group
		Serialize.decode_text(text, [TileGroupDef, DoodadGroupDef], get_group, len(ids), options.repeater)

	def export_megatile_settings(self, output: IO.AnyOutputText, ids: list[int], fields: Serialize.Fields | None = None) -> None:
		with IO.OutputText(output) as file:
			if self.vf4_path is not None:
				file.write("# Exported from %s\n" % self.vf4_path)
			megatiles = list((self.vf4.get_megatile(id), id) for id in ids)
			file.write(Serialize.encode_texts(megatiles, lambda _: MegatileDef, fields))

	def import_megatile_settings(self, input: IO.AnyInputText, ids: list[int], options: ImportSettingsOptions = ImportSettingsOptions()) -> None:
		with IO.InputText(input) as file:
			text = file.read()

		def get_megatile(n: int, definition: Serialize.Definition) -> VF4Megatile:
			if n >= len(ids):
				raise PyMSError('Internal', f'Attempted to import on group {n} with only {len(ids)} being imported')
			return self.vf4.get_megatile(ids[n])
		Serialize.decode_text(text, [MegatileDef], get_megatile, len(ids), options.repeater)
