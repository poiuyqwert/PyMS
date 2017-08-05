from utils import *
from fileutils import *

import sys,struct
try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	try:
		import ImageTk
	except:
		e = DependencyError('PyMS','PIL is missing. Consult the Source Installation section of the Documentation.', ('Documentation','file:///%s' % os.path.join(BASE_DIR, 'Docs', 'intro.html')))
		e.mainloop()
		sys.exit()

import PAL, BMP

import struct, re, math

def megatile_to_photo(t, m=None):
	if m != None:
		try:
			d = t.vx4.graphics[m]
		except:
			return
	else:
		d = t
	pi = PILImage.new('P', (32,32))
	pal = []
	for c in t.wpe.palette:
		pal.extend(c)
	pi.putpalette(pal)
	image = [[] for _ in range(32)]
	for m,mini in enumerate(d):
		for y,p in enumerate(t.vr4.images[mini[0]]):
			if mini[1]:
				p = p[::-1]
			image[(m/4)*8+y].extend(p)
	put = []
	for y in image:
		put.extend(y)
	pi.putdata(put)
	return ImageTk.PhotoImage(pi)

def minitile_to_photo(t, m=None):
	if isinstance(m, tuple) or isinstance(m, list):
		d = t.vr4.images[m[0]]
		f = m[1]
	else:
		d = t
		f = m
	pi = PILImage.new('P', (24,24))
	pal = []
	for c in t.wpe.palette:
		pal.extend(c)
	pi.putpalette(pal)
	put = []
	for y,p in enumerate(d):
		if f:
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

def setting_import_extras_ignore(setting_count, tile_n, tile_count):
	if tile_n == setting_count:
		return None
	return tile_n

def setting_import_extras_repeat_all(setting_count, tile_n, tile_count):
	return tile_n % setting_count

def setting_import_extras_repeat_last(setting_count, tile_n, tile_count):
	return min(tile_n, setting_count-1)

class Tileset:
	def __init__(self):
		self.cv5 = None
		self.cv5_path = None
		self.vf4 = None
		self.vf4_path = None
		self.vx4 = None
		self.vx4_path = None
		self.vr4 = None
		self.vr4_path = None
		self.dddata = None
		self.dddata_path = None
		self.wpe = None
		self.wpe_path = None

	def groups_max(self):
		return CV5.MAX_ID+1
	def groups_remaining(self):
		if self.cv5:
			return self.cv5.groups_remaining()

	def megatiles_max(self):
		return VX4.MAX_ID+1
	def megatiles_remaining(self):
		if self.vx4:
			return self.vx4.graphics_remaining()

	def minitiles_max(self):
		if self.vr4:
			return self.vr4.max_id(self.vx4.expanded)+1
		return VR4.MAX_ID+1
	def minitiles_remaining(self):
		if self.vr4:
			return self.vr4.images_remaining(expanded_vx4=self.vx4.expanded)

	def new_file(self, cv5=None, vf4=None, vx4=None, vr4=None, dddata=None, wpe=None):
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
			self.wpe = PAL.Palette()

	def load_file(self, cv5, vf4=None, vx4=None, vr4=None, dddata=None, wpe=None):
		path = None
		name = None
		if isstr(cv5):
			path = os.path.dirname(cv5)
			name = os.path.basename(cv5)
			if name.split(os.extsep)[-1].lower() == 'cv5':
				name = name[:-4]
		if not vf4:
			if not path or not name:
				raise
			vf4 = os.path.join(path, '%s%svf4' % (name,os.extsep))
		if not vx4:
			if not path or not name:
				raise
			vx4 = os.path.join(path, '%s%svx4ex' % (name,os.extsep))
			# Check for and prefer expanded vx4 files
			if not os.path.exists(vx4):
				vx4 = os.path.join(path, '%s%svx4' % (name,os.extsep))
		if not vr4:
			if not path or not name:
				raise
			vr4 = os.path.join(path, '%s%svr4' % (name,os.extsep))
		if not dddata:
			if not path or not name:
				raise
			dddata = os.path.join(path, name, 'dddata%sbin' % os.extsep)
		if not wpe:
			if not path or not name:
				raise
			wpe = os.path.join(path, '%s%swpe' % (name,os.extsep))
		self.cv5 = CV5()
		self.cv5.load_file(cv5)
		self.vf4 = VF4()
		self.vf4.load_file(vf4)
		self.vx4 = VX4()
		self.vx4.load_file(vx4)
		self.vr4 = VR4()
		self.vr4.load_file(vr4)
		self.dddata = DDDataBIN()
		self.dddata.load_file(dddata)
		self.wpe = PAL.Palette()
		self.wpe.load_file(wpe)
		self.cv5_path = cv5 if isstr(cv5) else None
		self.vf4_path = vf4 if isstr(vf4) else None
		self.vx4_path = vx4 if isstr(vx4) else None
		self.vr4_path = vr4 if isstr(vr4) else None
		self.dddata_path = dddata if isstr(dddata) else None
		self.wpe_path = wpe if isstr(wpe) else None

	def save_file(self, cv5, vf4=None, vx4=None, vr4=None, dddata=None, wpe=None):
		path = os.path.dirname(cv5)
		name = os.path.basename(cv5)
		if name.endswith(os.extsep + 'cv5'):
			name = name[:-4]
		if vf4 == None:
			vf4 = os.path.join(path, '%s%svf4' % (name,os.extsep))
		if vx4 == None:
			expanded = 'ex' if self.vx4.expanded else ''
			vx4 = os.path.join(path, '%s%svx4%s' % (name,os.extsep,expanded))
		if vr4 == None:
			vr4 = os.path.join(path, '%s%svr4' % (name,os.extsep))
		dddir = os.path.join(path, name)
		if dddata == None:
			dddata = os.path.join(dddir, 'dddata%sbin' % os.extsep)
		if wpe == None:
			wpe = os.path.join(path, '%s%swpe' % (name,os.extsep))
		self.cv5.save_file(cv5)
		self.vf4.save_file(vf4)
		self.vx4.save_file(vx4)
		self.vr4.save_file(vr4)
		if not os.path.exists(dddir):
			os.mkdir(dddir)
		self.dddata.save_file(dddata)
		self.wpe.save_sc_wpe(wpe)

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
	def import_graphics(self, tiletype, bmpfile, ids=None, options={}):
		if ids:
			ids = list(ids)
		else:
			ids = []
		new_ids = []
		bmp = BMP.BMP()
		bmp.load_file(bmpfile)
		if tiletype == TILETYPE_GROUP and (bmp.width != 512 or bmp.height % 32):
			raise PyMSError('Interpreting','The image is not the correct size for tile groups (got %sx%s, expected width to be 512 and height to be a multiple of 32)' % (bmp.width,bmp.height))
		elif tiletype == TILETYPE_MEGA and (bmp.width % 32 or bmp.height % 32):
			raise PyMSError('Interpreting','The image is not the correct size for megatiles (got %sx%s, expected width and height to be multiples of 32)' % (bmp.width,bmp.height))
		elif tiletype == TILETYPE_MINI and (bmp.width % 8 or bmp.height % 8):
			raise PyMSError('Interpreting','The image is not the correct size for minitiles (got %sx%s, expected width and height to be multiples of 8)' % (bmp.width,bmp.height))
		
		new_images = []
		mini_lookup = {}
		update_images = [] # (id,image)
		new_megatiles = []
		mega_lookup = {}
		update_megatiles = [] # (id,tile)
		new_groups = []
		update_groups = [] # (id,group)

		minis_w = bmp.width / 8
		minis_h = bmp.height / 8
		for iy in xrange(minis_h):
			py = iy * 8
			for ix in xrange(minis_w):
				px = ix * 8
				image = tuple(tuple(bmp.image[py+oy][px:px+8]) for oy in xrange(8))
				new_images.append(image)
		image_details = [] # (id,isFlipped)
		new_id = len(self.vr4.images)
		i = 0
		minitiles_reuse_null_with_id = options.get('minitiles_reuse_null_with_id', 0)
		minitiles_reuse_duplicates_old = options.get('minitiles_reuse_duplicates_old', True)
		minitiles_reuse_duplicates_new = options.get('minitiles_reuse_duplicates_new', True)
		minitiles_reuse_duplicates_flipped = options.get('minitiles_reuse_duplicates_flipped', True)
		if tiletype == TILETYPE_MINI and options.get('minitiles_ignore_extra', False) and len(new_images) > len(ids):
			new_images = new_images[:len(ids)]
		while i < len(new_images):
			image = new_images[i]
			image_hash = hash(image)
			found = False
			if tiletype != TILETYPE_MINI or not len(ids):
				flipped_hash = hash(tuple(tuple(reversed(r)) for r in image))
				existing_ids = self.vr4.lookup.get(image_hash,[]) + self.vr4.lookup.get(flipped_hash,[])
			 	if len(existing_ids) and (minitiles_reuse_duplicates_old or minitiles_reuse_null_with_id in existing_ids):
			 		normal_found = image_hash in self.vr4.lookup
			 		found = True
					del new_images[i]
					image_details.append((existing_ids[0],int(not normal_found)))
				if not found:
					existing_ids = mini_lookup.get(image_hash,[]) + mini_lookup.get(flipped_hash,[])
				 	if len(existing_ids) and (minitiles_reuse_duplicates_new or minitiles_reuse_null_with_id in existing_ids):
				 		normal_found = image_hash in mini_lookup
				 		found = True
						del new_images[i]
						image_details.append((existing_ids[0],int(not normal_found)))
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
				image_details.append((id,0))
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
			megas_w = minis_w / 4
			megas_h = minis_h / 4
			for y in xrange(megas_h):
				for x in xrange(megas_w):
					minitiles = []
					for oy in xrange(4):
						o = (y*4+oy)*minis_w + x*4
						minitiles.extend(image_details[o:o+4])
					new_megatiles.append(tuple(minitiles))
			megatile_ids = []
			new_id = len(self.vx4.graphics)
			i = 0
			megatiles_reuse_null_with_id = options.get('megatiles_reuse_null_with_id', 0)
			megatiles_reuse_duplicates_old = options.get('megatiles_reuse_duplicates_old', True)
			megatiles_reuse_duplicates_new = options.get('megatiles_reuse_duplicates_new', True)
			if tiletype == TILETYPE_MEGA and options.get('megatiles_ignore_extra', False) and len(new_megatiles) > len(ids):
				new_megatiles = new_megatiles[:len(ids)]
			while i < len(new_megatiles):
				tile_hash = hash(new_megatiles[i])
				found = False
				if tiletype != TILETYPE_MEGA or not len(ids):
					existing_ids = self.vx4.lookup.get(tile_hash,None)
					if existing_ids and (megatiles_reuse_duplicates_old or megatiles_reuse_null_with_id in existing_ids):
						del new_megatiles[i]
						megatile_ids.append(existing_ids[0])
						found = True
					if not found:
						existing_ids = mega_lookup.get(tile_hash,None)
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
				for n in xrange(groups):
					group = megatile_ids[n*16:(n+1)*16]
					if len(ids):
						id = ids[0]
						del ids[0]
						update_groups.append((id,group))
					else:
						if tiletype == TILETYPE_GROUP:
							new_ids.append(len(self.cv5.groups) + len(new_groups))
						new_groups.append(group)
				if len(new_images) > self.groups_remaining():
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
		self.vx4.graphics.extend(new_megatiles)
		self.vf4.flags.extend([0]*16 for _ in xrange(len(new_megatiles)))
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
		bmp = BMP.BMP()
		bmp.palette = list(self.wpe.palette)
		tiles_wide = 0
		tile_width = 0
		tiles_high = 0
		tile_height = 0
		def calc_dims(tiles):
			for f in xrange(int(math.sqrt(tiles)),0,-1):
				if not tiles % f:
					return (tiles / f, f)
			return (tiles,1)
		if tiletype == TILETYPE_GROUP:
			tiles_wide,tiles_high = 16,len(ids) % 16
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
				for mini_n in xrange(16):
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

	# options.megatiles_export_height
	# options.megatiles_export_walkability
	# options.megatiles_export_block_sight
	# options.megatiles_export_ramp
	def export_settings(self, tiletype, path, ids, options={}):
		file = AtomicWriter(path, 'w')
		if tiletype == TILETYPE_GROUP and self.cv5_path != None:
			file.write("# Exported from %s\n" % self.cv5_path)
		elif tiletype == TILETYPE_MEGA and self.vf4_path != None:
			file.write("# Exported from %s\n" % self.vf4_path)
		megatiles_export_height = options.get('megatiles_export_height',True)
		megatiles_export_walkability = options.get('megatiles_export_walkability',True)
		megatiles_export_block_sight = options.get('megatiles_export_block_sight',True)
		megatiles_export_ramp = options.get('megatiles_export_ramp',True)
		for id in ids:
			if tiletype == TILETYPE_GROUP:
				data = tuple([id] + self.cv5.groups[id][:13])
				if id < 1024:
					file.write("""\
# Export of MegaTile Group %s
TileGroup:
	Index:             	%s
	Buildable:         	%s
	Flags:             	%s
	Buildable2:        	%s
	GroundHeight:      	%s
	EdgeLeft:          	%s
	EdgeUp:            	%s
	EdgeRight:         	%s
	EdgeDown:          	%s
	Unknown9:          	%s
	HasUp:             	%s
	Unknown11:         	%s
	HasDown:            %s
""" % data)
				else:
					file.write("""\
# Export of MegaTile Group %s
DoodadGroup:
	Index:             	%s
	Buildable:         	%s
	Unknown1:          	%s
	OverlayFlags:      	%s
	GroundHeight:      	%s
	OverlayID:         	%s
	Unknown6:          	%s
	DoodadGroupString: 	%s
	Unknown8:          	%s
	DDDataID:          	%s
	DoodadWidth:       	%s
	DoodadHeight:      	%s
	Unknown12:         	%s
""" % data)
			elif tiletype == TILETYPE_MEGA:
				def write_flags(id, name, mask_values, else_value):
					file.write('\n\t%s:' % name)
					for n in xrange(16):
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
		file.close()

	# options.repeater (Func, default: setting_import_extras_ignore)
	def import_settings(self, tiletype, path, ids, options={}):
		try:
			with open(path,'r') as settings_file:
				lines = settings_file.readlines()
		except:
			raise PyMSError('Importing',"Could not load file '%s'" % path)
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
					if len(importing) and all(flag == None for flag in importing[-1]):
						raise PyMSError('Importing', 'Previous MegaTile is empty.', last_line-len(lines), line)
					importing.append([None]*4)
					continue
				if not importing:
					raise PyMSError('Importing', 'Unknown line format, expected a MegaTile header.', last_line-len(lines), line)
				if line == 'Height:':
					flags = []
					for _ in xrange(4):
						flags.extend(height_flags[f] for f in get_line('Height settings', height_re, ' 4 height flags (flags = L, M, H, or ?)'))
					importing[-1][0] = flags
				elif line == 'Walkability:':
					flags = []
					for _ in xrange(4):
						flags.extend(bool_flags[f] for f in get_line('Walkability settings', bool_re, ' 4 walkability flags (1 = Walkable, 0 = Not, or ?)'))
					importing[-1][1] = flags
				elif line == 'Block Sight:':
					flags = []
					for _ in xrange(4):
						flags.extend(bool_flags[f] for f in get_line('Block Sight settings', bool_re, ' 4 block sight flags (1 = Blocked, 0 = Not, or ?)'))
					importing[-1][2] = flags
				elif line == 'Ramp:':
					flags = []
					for _ in xrange(4):
						flags.extend(bool_flags[f] for f in get_line('Ramp settings', bool_re, ' 4 ramp flags (1 = Ramp(?), 0 = Not)'))
					importing[-1][3] = flags
				else:
					raise PyMSError('Importing', 'Unknown line format, expected a setting header (Height, Walkability, Block Sight, or Ramp).', last_line-len(lines), line)
		if not len(importing):
			raise PyMSError('Importing', 'Nothing to import.')
		if len(importing) and all(flag == None for flag in importing[-1]):
			raise PyMSError('Importing', 'Last %s is empty.' % (''))
		repeater = options.get('repeater', setting_import_extras_ignore)
		setting_count = len(importing)
		tile_count = len(ids)
		if tiletype == TILETYPE_GROUP:
			for tile_n,id in enumerate(ids):
				settings_n = repeater(setting_count, tile_n, tile_count)
				if settings_n == None:
					break
				doodad,line_n,_ = importing[settings_n]
				if doodad and id < 1024:
					raise PyMSError('Importing', 'Attempting to import DoodadGroup onto TileGroup %s' % id, line_n)
				elif not doodad and id >= 1024:
					raise PyMSError('Importing', 'Attempting to import TileGroup onto DoodadGroup %s' % id, line_n)
		for tile_n,id in enumerate(ids):
			settings_n = repeater(setting_count, tile_n, tile_count)
			if settings_n == None:
				break
			data = importing[settings_n]
			if tiletype == TILETYPE_GROUP:
				_,_,data = data
				for n in xrange(13):
					if data[n] != None:
						self.cv5.groups[id][n] = data[n]
			else:
				for mini_n in xrange(16):
					flags = self.vf4.flags[id][mini_n]
					if data[0] != None and data[0][mini_n] != None:
						flags &= ~(HEIGHT_MID | HEIGHT_HIGH)
						flags |= data[0][mini_n]
					if data[1] != None and data[1][mini_n] != None:
						if data[1][mini_n]:
							flags |= 1
						else:
							flags &= ~1
					if data[2] != None and data[2][mini_n] != None:
						if data[2][mini_n]:
							flags |= 8
						else:
							flags &= ~8
					if data[3] != None and data[3][mini_n] != None:
						if data[3][mini_n]:
							flags |= 16
						else:
							flags &= ~16
					self.vf4.flags[id][mini_n] = flags

class CV5:
	MAX_ID = 4095
	def __init__(self):
		self.groups = []

	def groups_remaining(self):
		return (CV5.MAX_ID+1) - len(self.groups)

	def load_file(self, file):
		data = load_file(file, 'CV5')
		if data and len(data) % 52:
			raise PyMSError('Load',"'%s' is an invalid CV5 file" % file)
		groups = []
		try:
			o = 0
			while o + 51 < len(data):
				d = list(struct.unpack('<HBB24H', data[o:o+52]))
				groups.append([d[0],(d[1] & 240) >> 4,d[1] & 15,(d[2] & 240) >> 4,d[2] & 15] + d[3:11] + [d[11:]])
				o += 52
		except:
			raise PyMSError('Load',"Unsupported CV5 file '%s', could possibly be corrupt" % file)
		self.groups = groups

	def save_file(self, file):
		data = ''
		for d in self.groups:
			data += struct.pack('<HBB24H', *[d[0],(d[1] << 4) + d[2],(d[3] << 4) + d[4]] + d[5:13] + d[13])
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the CV5 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()

class VF4:
	MAX_ID = 65535
	def __init__(self):
		self.flags = []

	def flags_remaining(self):
		return (VF4.MAX_ID+1) - len(self.flags)

	def load_file(self, file):
		data = load_file(file, 'VF4')
		if data and len(data) % 32:
			raise PyMSError('Load',"'%s' is an invalid VF$ file" % file)
		flags = []
		try:
			o = 0
			while o + 31 < len(data):
				flags.append(list(struct.unpack('<16H', data[o:o+32])))
				o += 32
		except:
			raise PyMSError('Load',"Unsupported VF4 file '%s', could possibly be corrupt" % file)
		self.flags = flags

	def save_file(self, file):
		data = ''
		for d in self.flags:
			data += struct.pack('<16H', *d)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VF4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()

class VX4:
	MAX_ID = 65535
	def __init__(self, expanded=False):
		self.graphics = []
		self.lookup = {}
		self.expanded = expanded

	def graphics_remaining(self):
		return (VX4.MAX_ID+1) - len(self.graphics)

	def find_tile(self, tile):
		tile = tuple(tuple(r) for r in tile)
		tile_hash = hash(tile)
		if tile_hash in self.lookup:
			return self.lookup[tile_hash]
		return None

	def add_tile(self, tile):
		correct_size = (len(tile) == 16)
		if correct_size:
			for r in tile:
				if len(r) != 2:
					correct_size = False
					break
		if not correct_size:
			raise
		id = len(self.graphics)
		self.graphics.append(tuple(tuple(r) for r in tile))
		tile_hash = hash(self.graphics[id])
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)
	def set_tile(self, id, tile):
		correct_size = (len(tile) == 16)
		if correct_size:
			for r in tile:
				if len(r) != 2:
					correct_size = False
					break
		if not correct_size:
			raise
		old_hash = hash(self.graphics[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.graphics[id] = tuple(tuple(r) for r in tile)
		tile_hash = hash(self.graphics[id])
		if not tile_hash in self.lookup:
			self.lookup[tile_hash] = []
		self.lookup[tile_hash].append(id)

	# expanded = True, False, or None (None = .vx4ex file extension detection)
	def load_file(self, file, expanded=None):
		if expanded == None and isstr(file):
			expanded = (file[-6:].lower() == '.vx4ex')
		data = load_file(file, 'VX4')
		struct_size = (64 if expanded else 32)
		file_type = 'Expanded VX4 file' if expanded else 'VX4 file'
		if data and len(data) % struct_size:
			raise PyMSError('Load',"'%s' is an invalid %s" % (file, file_type))
		graphics = []
		lookup = {}
		try:
			ref_size_max = 0xFFFFFFFE if expanded else 0xFFFE
			struct_frmt = '<16L' if expanded else '<16H'
			for id in xrange(len(data) / struct_size):
				graphics.append(tuple(((d & ref_size_max)/2,d & 1) for d in struct.unpack(struct_frmt, data[id*struct_size:(id+1)*struct_size])))
				tile_hash = hash(graphics[-1])
				if not tile_hash in lookup:
					lookup[tile_hash] = []
				lookup[tile_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported %s '%s', could possibly be corrupt" % (file_type, file))
		self.graphics = graphics
		self.lookup = lookup
		self.expanded = expanded

	def save_file(self, file):
		data = ''
		struct_frmt = '<16L' if self.expanded else '<16H'
		for d in self.graphics:
			data += struct.pack(struct_frmt, *[g*2 + h for g,h in d])
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VX4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()

class VR4:
	MAX_ID 				= 0xFFFE / 2
	MAX_ID_EXPANDED_VX4 = 0xFFFFFFFE / 2

	def __init__(self):
		self.images = []
		self.lookup = {}

	def max_id(self, expanded_vx4=False):
		return VR4.MAX_ID_EXPANDED_VX4 if expanded_vx4 else VR4.MAX_ID
	def images_remaining(self, expanded_vx4=False):
		return self.max_id(expanded_vx4)+1 - len(self.images)

	# returns ([ids],isFlipped) or None
	def find_image(self, image):
		image = tuple(tuple(r) for r in image)
		image_hash = hash(image)
		if image_hash in self.lookup:
			return (self.lookup[image_hash],False)
		flipped_hash = hash(tuple(tuple(reversed(r)) for r in image))
		if flipped_hash in self.lookup:
			return (self.lookup[flipped_hash],True)
		return None

	def add_image(self, image):
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise
		id = len(self.images)
		self.images.append(tuple(tuple(r) for r in image))
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)
	def set_image(self, id, image):
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise
		old_hash = hash(self.images[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.images[id] = tuple(tuple(r) for r in image)
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)

	def load_file(self, file):
		data = load_file(file, 'VR4')
		if data and len(data) % 64:
			raise PyMSError('Load',"'%s' is an invalid VR4 file" % file)
		images = []
		lookup = {}
		try:
			for id in xrange(len(data) / 64):
				d = struct.unpack('64B', data[id*64:(id+1)*64])
				images.append(tuple(tuple(d[y:y+8]) for y in range(0,64,8)))
				image_hash = hash(images[-1])
				if not image_hash in self.lookup:
					lookup[image_hash] = []
				lookup[image_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported VR4 file '%s', could possibly be corrupt" % file)
		self.images = images
		self.lookup = lookup

	def save_file(self, file):
		data = ''
		for d in self.images:
			i = []
			for l in d:
				i.extend(l)
			data += struct.pack('64B', *i)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VR4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()

class DDDataBIN:
	def __init__(self):
		self.doodads = [[0]*256 for _ in range(512)]

	def load_file(self, file):
		data = load_file(file, 'dddata.dat')
		if len(data) != 262144:
			raise PyMSError('Load',"'%s' is an invalid dddata.bin file" % file)
		doodads = []
		try:
			o = 0
			while o + 511 < len(data):
				doodads.append(list(struct.unpack('<256H', data[o:o+512])))
				o += 512
		except:
			raise PyMSError('Load',"Unsupported dddata.dat file '%s', could possibly be corrupt" % file)
		self.doodads = doodads

	def save_file(self, file):
		data = ''
		for d in self.doodads:
			data += struct.pack('<256H', *d)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the dddata.dat to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()

# sys.stdout = open('stdeo.txt','w')
# sys.stderr = sys.stdout
# p = "C:\\Documents and Settings\\Administrator\\Desktop\\extract\\tileset\\"
# ps = [p + 'ashworld.' + e for e in ['cv5','vf4','vx4','vr4','wpe']]
# ps = ps[:4] + [p + 'ashworld\\dddata.bin'] + ps[4:5]
# t = Tileset()
# t.load_file(*ps)
# o = Tileset()
# o.cv5 = CV5()
# o.vx4 = VX4()
# o.vf4 = VF4()
# o.vr4 = VR4()
# o.dddata = DDDataBIN()
# o.wpe = t.wpe
# try:
	# t.decompile('C:\\Documents and Settings\\Administrator\\Desktop\\PyMS\\testtiles.bmp',0,1,'C:\\Documents and Settings\\Administrator\\Desktop\\PyMS\\testtiles.txt')
	# o.interpret('C:\\Documents and Settings\\Administrator\\Desktop\\PyMS\\testtiles.bmp',0,'C:\\Documents and Settings\\Administrator\\Desktop\\PyMS\\testtiles.txt')
	# o.save_file('test.cv5','test.vf4','test.vx4','test.vr4')
# except PyMSError, e:
	# print repr(e)