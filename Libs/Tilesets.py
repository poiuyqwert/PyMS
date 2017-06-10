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

import struct, re

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

class Tileset:
	def __init__(self):
		self.cv5 = None
		self.vf4 = None
		self.vx4 = None
		self.vr4 = None
		self.dddata = None
		self.wpe = None

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

	def save_file(self, cv5, vf4=None, vx4=None, vr4=None, dddata=None, wpe=None):
		path = os.path.dirname(cv5)
		name = os.path.basename(cv5)
		if name.endswith(os.extsep + 'cv5'):
			name = name[:-4]
		if vf4 == None:
			vf4 = os.path.join(path, '%s%svf4' % (name,os.extsep))
		if vx4 == None:
			vx4 = os.path.join(path, '%s%svx4' % (name,os.extsep))
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

	# type: 0 = group, 1 = megatile, 2 = minitile, 3 = doodad
	def decompile(self, bmpfile, type=0, id=0, settingfile=None):
		if settingfile:
			f = AtomicWriter(settingfile, 'w')
		try:
			b = BMP.BMP()
			b.palette = list(self.wpe.palette)
			if type == 0:
				b.image = [[] for _ in range(32)]
				b.width = 512
				b.height = 32
				g = self.cv5.groups[id]
				megas = []
				minis = []
				if settingfile:
					data = (id,) + tuple(g[:13])
					if id < 1024:
						f.write("""\
Group %s:
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
						f.write("""\
DoodadGroup %s:
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

					f.write('	MegaTiles:         	%s\n\n' % ' '.join([str(i) for i in g[13]]))
					# if id > 1023:
						# f.write('DDData %s:\n' % data[10])
						# for y in range(data[12]):
							# x = y * data[11]
							# f.write('\t%s\n' % ' '.join(['%s%s' % (n,' ' * (3 - len(str(n)))) for n in self.dddata.doodads[data[10]][x:x+data[11]]]))
						# f.write('\n')
				for t,mega in enumerate(g[13]):
					if settingfile and not mega in megas:
						f.write("""\
MegaTile %s:
	MiniTiles:         	%s
	MiniTileFlags:     	%s
	FlippedStates:     	%s

""" % (mega,' '.join([str(mini[0]) for mini in self.vx4.graphics[mega]]),' '.join([flags(mini,16) for mini in self.vf4.flags[mega]]),' '.join([str(mini[1]) for mini in self.vx4.graphics[mega]])))
						megas.append(mega)
					for m,mini in enumerate(self.vx4.graphics[mega]):
						for y,p in enumerate(self.vr4.images[mini[0]]):
							if mini[1]:
								p = p[::-1]
							b.image[y + (m/4)*8].extend(p)
			elif type == 1:
				b.image = [[] for _ in range(32)]
				b.width = 32
				b.height = 32
				if settingfile:
					f.write("""\
MegaTile %s:
	MiniTiles:         	%s
	MiniTileFlags:     	%s
	FlippedStates      	%s""" % (id,' '.join([str(mini[0]) for mini in self.vx4.graphics[id]]),' '.join([flags(mini,16) for mini in self.vf4.flags[id]]),' '.join([str(mini[1]) for mini in self.vx4.graphics[id]])))
				for m,mini in enumerate(self.vx4.graphics[id]):
					for y,p in enumerate(self.vr4.images[mini[0]]):
						if mini[1]:
							p = p[::-1]
						b.image[y + (m/4)*8].extend(p)
			elif type == 2:
				b.image = []
				b.width = 8
				b.height = 8
				for y,p in enumerate(self.vr4.images[id]):
					b.image.append(p)
			elif type == 3:
				ty = -1
				for n,g in enumerate(self.tileset.cv5.groups[1024:]):
					if g[9] == id and ty == -1:
						w,h,ty = g[10],g[11],g[11]
						if n + h > len(self.tileset.cv5.groups):
							h = len(self.tileset.cv5.groups) - n
							ty = h
						b.image = [[] for _ in range(32 * h)]
					if ty > 0:
						for x in range(w):
							c = self.tileset.dddata.doodads[id][x + (h-ty) * w]
							
			b.save_file(bmpfile)
		except:
			raise
		finally:
			if settingfile:
				f.close()

	# options.minitiles_find_duplicates_old - Attempt to find and reuse existing minitile images (default: True)
	# options.minitiles_find_duplicates_new - Attempt to find and reuse duplicate imported minitile images (default: True)
	# options.minitiles_find_duplicates_flipped - Check flipped versions of tiles for duplicates (default: True)
	# options.megatiles_find_duplicates_old - Attempt to find and reuse existing minitile images (default: True)
	# options.megatiles_find_duplicates_new - Attempt to find and reuse duplicate imported minitile images (default: True)
	def iimport(self, tiletype, bmpfile, ids=None, options={}):
		if ids:
			ids = list(ids)
		else:
			ids = []
		new_ids = []
		bmp = BMP.BMP()
		bmp.load_file(bmpfile)
		if tiletype == TILETYPE_GROUP and (bmp.width != 512 or bmp.height % 32):
			raise PyMSError('Interpreting','The image is not the correct size for a tile group (got %sx%s, expected width to be 512 and height to be a multiple of 32)' % (bmp.width,bmp.height))
		elif tiletype == TILETYPE_MEGA and (bmp.width % 32 or bmp.height % 32):
			raise PyMSError('Interpreting','The image is not the correct size for megatiles (got %sx%s, expected width and height to be multiples of 32)' % (bmp.width,bmp.height))
		elif tiletype == TILETYPE_MINI and (bmp.width % 8 or bmp.height % 8):
			raise PyMSError('Interpreting','The image is not the correct size for minitiles (got %sx%s, expected width and height to be multiples of 8)' % (bmp.width,bmp.height))
		new_images = []
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
		mini_lookup = {}
		i = 0
		minitiles_find_duplicates_old = options.get('minitiles_find_duplicates_old', True)
		minitiles_find_duplicates_new = options.get('minitiles_find_duplicates_new', True)
		minitiles_find_duplicates_flipped = options.get('minitiles_find_duplicates_flipped', True)
		while i < len(new_images):
			image_hash = hash(new_images[i])
			found = False
			if tiletype != TILETYPE_MINI or not len(ids):
				flipped_hash = None
				if minitiles_find_duplicates_flipped:
					flipped_hash = hash(tuple(tuple(reversed(r)) for r in image))
				if minitiles_find_duplicates_old:
					not_flipped = image_hash in self.vr4.lookup
				 	if not_flipped or (flipped_hash != None and flipped_hash in self.vr4.lookup):
				 		found = True
						del new_images[i]
						image_details.append((self.vr4.lookup[image_hash if not_flipped else flipped_hash][0],int(not not_flipped)))
				if minitiles_find_duplicates_new and not found:
					not_flipped = image_hash in mini_lookup
				 	if not_flipped or (flipped_hash != None and flipped_hash in mini_lookup):
				 		found = True
						del new_images[i]
						image_details.append((mini_lookup[image_hash if not_flipped else flipped_hash][0],int(not not_flipped)))
			if not found:
				id = new_id
				if tiletype == TILETYPE_MINI and len(ids):
					id = ids[0]
					del ids[0]
					self.vr4.set_image(id, new_images[i])
					del new_images[i]
				else:
					if tiletype == TILETYPE_MINI:
						new_ids.append(new_id)
					new_id += 1
				image_details.append((id,0))
				if image_hash in mini_lookup:
					mini_lookup[image_hash].append(id)
				else:
					mini_lookup[image_hash] = [id]
		self.vr4.images.extend(new_images)
		for image_hash in mini_lookup:
			if image_hash in self.vr4.images.lookup:
				self.vr4.images.lookup[image_hash].extend(mini_lookup[image_hash])
			else:
				self.vr4.images.lookup[image_hash] = mini_lookup[image_hash]
		if tiletype == TILETYPE_GROUP or tiletype == TILETYPE_MEGA:
			new_megatiles = []
			megas_w = minis_w / 4
			megas_h = minis_h / 4
			for y in xrange(megas_h):
				for x in xrange(megas_w):
					minitiles = []
					for oy in xrange(4):
						o = (y+oy)*minis_w + x*4
						minitiles.extend(image_details[o:o+4])
					new_megatiles.append(tuple(minitiles))
			megatile_ids = []
			new_id = len(self.vx4.graphics)
			mega_lookup = {}
			i = 0
			megatiles_find_duplicates_old = options.get('megatiles_find_duplicates_old', True)
			megatiles_find_duplicates_new = options.get('megatiles_find_duplicates_new', True)
			while i < len(new_megatiles):
				tile_hash = hash(new_megatiles[i])
				found = False
				if tiletype != TILETYPE_MEGA or not len(ids):
					if megatiles_find_duplicates_old and tile_hash in self.vx4.lookup:
						del new_megatiles[i]
						megatile_ids.append(self.vx4.lookup[tile_hash][0])
						found = True
					elif megatiles_find_duplicates_new and tile_hash in mega_lookup:
						del new_megatiles[i]
						megatile_ids.append(mega_lookup[tile_hash][0])
						found = True
				if not found:
					id = new_id
					if tiletype == TILETYPE_MEGA and len(ids):
						id = ids[0]
						del ids[0]
						self.vx4.set_tile(id, new_megatiles[i])
						del new_megatiles[i]
					else:
						if tiletype == TILETYPE_MEGA:
							new_ids.append(new_id)
						new_id += 1
					megatile_ids.append(id)
					if tile_hash in mega_lookup:
						mega_lookup[tile_hash] = [id]
					else:
						mega_lookup[tile_hash].append(id)
			self.vx4.graphics.extend(new_megatiles)
			for tile_hash in mega_lookup:
				if tile_hash in self.vx4.graphics.lookup:
					self.vx4.graphics.lookup[tile_hash].extend(mega_lookup[tile_hash])
				else:
					self.vx4.graphics.lookup[tile_hash] = mega_lookup[tile_hash]
			if tiletype == TILETYPE_GROUP:
				for n in xrange(megas_h):
					group = megatile_ids[n*16:(n+1)*16]
					if len(ids):
						id = ids[0]
						del ids[0]
						self.cv5.groups[id][13] = group
					else:
						if tiletype == TILETYPE_GROUP:
							new_ids.append(len(self.cv5.groups))
						self.cv5.groups.append([0]*13 + [group])
		return new_ids

	def interpret(self, bmpfile, type=0, settingfile=None):
		b = BMP.BMP()
		try:
			b.load_file(bmpfile)
		except:
			raise
		if type == 0 and b.width != 512:
			raise PyMSError('Interpreting','The image is not the correct size for a tile group (got a width of %s, expected 512)' % b.width)
		elif type == 1 and b.width != 32:
			raise PyMSError('Interpreting','The image is not the correct size for megatiles (got a width of %s, expected 32)' % b.width)
		elif type == 2 and b.width != 8:
			raise PyMSError('Interpreting','The image is not the correct size for minitiles (got a width of %s, expected 8)' % b.width)
		needmega = []
		if type != 2 and settingfile:
			def getset(on, line, n, doodad):
				if doodad:
					name = ['Index','Buildable','Unknown1','OverlayFlags','GroundHeight','OverlayID','Unknown6','DoodadGroupString','Unknown8','DDDataID','DoodadWidth','DoodadHeight','Unknown12'][on-1]
				else:
					name = ['Index','Buildable','Flags','Buildable2','GroundHeight','EdgeLeft','EdgeUp','EdgeRight','EdgeDown','Unknown9','HasUp','Unknown11','HasDown'][on-1]
				m = re.match('^%s:\\s+(\\d+)$' % name, line)
				if not m:
					raise PyMSError('Interpreting', "Unknown line format (expected '%s' specifier)" % name, n,line)
				ma = [65535,15][on in range(2,6)]
				if int(m.group(1)) > ma:
					raise PyMSError('Interpreting', "Invalid '%s' value '%s' (must be a number from 0 to %s)" % (m.group(1), ma), n,line)
				return int(m.group(1))
			try:
				if isstr(settingfile):
					f = open(settingfile,'r')
					set = f.readlines()
					f.close()
				else:
					set = settingfile.readlines()
			except:
				raise PyMSError('Interpreter',"Could not load file '%s'" % settingfile)
			data,groups = [],{}
			omega,megas = [],{}
			on = 0
			group = 0
			megatile = 0
			doodad = False
			for n,l in enumerate(set):
				if l:
					line = l.split('#',1)[0].strip()
					if line:
						if on == 0:
							valid = False
							if type == 0:
								m = re.match('^(Doodad)?Group (\\d+):\\s*(?:#.*)?$', line)
								if m:
									group = int(m.group(2))
									if group > 4095:
										raise PyMSError('Interpreting', "Invalid group id '%s' (must be a number from 0 to 4095)" % group, n,line)
									if group in groups:
										raise PyMSError('Interpreting', "Duplicate Tile Group id '%s'" % group,n,line)
									if m.group(1):
										doodad = True
									groups[group] = len(data)
									data.append([])
									on += 1
									valid = True
							if type < 2:
								m = re.match('^MegaTile (\\d+):\\s*(?:#.*)?$', line)
								if m:
									megatile = int(m.group(1))
									if megatile > 65535:
										raise PyMSError('Interpreting', "Invalid megatile id '%s' (must be a number from 0 to 65535)" % group, n,line)
									if megatile in megas:
										raise PyMSError('Interpreting', "Duplicate megatile id '%s'" % megatile,n,line)
									megas[megatile] = len(omega)
									omega.append([])
									needmega.remove(megatile)
									on = 15
									valid = True
							if not valid:
								e = ''
								if type == 0:
									e = 'Group/DoodadGroup or '
								raise PyMSError('Interpreting', 'Uknown line format, expected a %sMegaTile header.',b,line)
						elif on < 14:
							data[-1].append(getset(on, line, n, doodad))
							on += 1
						elif on == 14:
							m = re.match('^MegaTiles:\\s+(%s\\d+)$' % ('\\d+\\s+' * 15), line)
							if not m:
								raise PyMSError('Interpreting', "Invalid MegaTiles list (expected a list of 16 megatiles)", n,line)
							g = list(int(n) for n in re.split('\\s+',m.group(1)))
							for i in g:
								if i > 65535:
									raise PyMSError('Interpreting', "Invalid MegaTile id '%s' (must be a number from 0 to 65535)" % i, n,line)
								if not i in megas.keys()+needmega:
									needmega.append(i)
							data[-1].append(g)
							on = 0
						elif on == 15:
							m = re.match('^MiniTiles:\\s+(%s\\d+)$' % ('\\d+\\s+' * 15), line)
							if not m:
								raise PyMSError('Interpreting', "Invalid MiniTiles list (expected a list of 16 minitiles)", n,line)
							g = list(int(n) for n in re.split('\\s+',m.group(1)))
							for i in g:
								if i > 65535:
									raise PyMSError('Interpreting', "Invalid MiniTile id '%s' (must be a number from 0 to 65535)" % i, n,line)
							omega[-1].append(g)
							on += 1
						elif on == 16:
							m = re.match('^MiniTileFlags:\\s+(%s[01]{16})$' % ('[01]{16}\\s+' * 15), line)
							if not m:
								raise PyMSError('Interpreting', "Invalid MiniTileFlags list (expected 16 flags for each of the 16 minitiles)", n,line)
							omega[-1].append(list(flags(n,16) for n in re.split('\\s+',m.group(1))))
							on += 1
						elif on == 17:
							m = re.match('^FlippedStates:\\s+(%s[01])$' % ('[01]\\s+' * 15), line)
							if not m:
								raise PyMSError('Interpreting', "Invalid FlippedStates list (expected 1 flag for each of the 16 minitiles)", n,line)
							omega[-1].append(list(int(n) for n in re.split('\\s+',m.group(1))))
							on = 0
		elif type == 0:
			mini = 0
			data,omega,megas = [],[],{}
			for g in range(b.height / 32):
				data.append([0]*13 + [range(g*16,g*16+16)])
				for m in data[-1][13]:
					megas[m] = len(omega)
					omega.append([range(mini,mini+16)] + [[0]*16,[0]*16])
					mini += 16
		elif type == 1:
			omega = [[range(m*16,m*16+16),[0]*16,[0]*16] for m in range(b.height / 32)]
		if type == 0:
			if needmega:
				raise PyMSError('Interpreting', "Missing MegaTile definition for megatile id '%s" % needmega[0])
			if b.height != 32 * len(data):
				raise PyMSError('Interpreting','The image is not the correct size for %s tile groups (got a height of %s, expected %s)' % (len(data),b.height,32*len(data)))
			minitiles = {}
			curmegas,curminis = len(self.vf4.flags),len(self.vr4.images)
			for g,dat in enumerate(data):
				self.cv5.groups.append(dat[:13] + [[]])
				for x,mega in enumerate(dat[13]):
					m = omega[megas[mega]]
					self.cv5.groups[-1][13].append(curmegas + megas[mega])
					self.vf4.flags.append(m[1])
					self.vx4.graphics.append([])
					for y,mini in enumerate(m[0]):
						if not mini in minitiles:
							minitiles[mini] = len(self.vr4.images)
							self.vr4.images.append([])
							for o in range(8):
								cx = x*32+(y%4)*8
								self.vr4.images[-1].append(b.image[g*32+(y/4)*8+o][cx:cx+8])
						self.vx4.graphics[-1].append([minitiles[mini],m[2][y]])
		elif type == 1:
			if b.height != 32 * len(omega):
				raise PyMSError('Interpreting','The image is not the correct size for %s tile groups (got a height of %s, expected %s)' % (len(omega),b.height,32*len(omega)))
			minitiles = {}
			for x,mega in enumerate(omegas):
				self.vf4.flags.append(mega[1])
				self.vx4.graphics.append([])
				for y,mini in enumerate(mega[0]):
					if not mini in minitiles:
						minitiles[mini] = len(self.vr4.images)
						self.vr4.images.append([])
						for o in range(8):
							cx = (y%4)*8
							self.vr4.images[-1].append(b.image[m*32+(y/4)*8+o][cx:cx+8])
					self.vx4.graphics[-1].append([minitiles[mini],mega[2][y]])
		elif type == 2:
			if b.height % 8:
				raise PyMSError('Interpreting','The image is not the correct size for minitiles (height must be a multiple of 8, got a height of %s)' % (b.height))
			for y in range(b.height / 8):
				self.vr4.images.append([])
				for o in range(8):
					self.vr4.images[-1].append(b.image[y*8+o])

class CV5:
	def __init__(self):
		self.groups = []

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
		try:
			f.write(data)
		except:
			raise
		finally:
			f.close()

class VF4:
	def __init__(self):
		self.flags = []

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
		try:
			f.write(data)
		except:
			raise
		finally:
			f.close()

class VX4:
	def __init__(self):
		self.graphics = []
		self.lookup = {}

	def find_tile(self, tile):
		tile = tuple(tuple(r) for r in tile)
		tile_hash = hash(tile)
		if tile_hash in self.lookup:
			return self.lookup[tile_hash]
		return None

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

	def load_file(self, file):
		data = load_file(file, 'VX4')
		if data and len(data) % 32:
			raise PyMSError('Load',"'%s' is an invalid VX4 file" % file)
		graphics = []
		lookup = {}
		try:
			for id in xrange(len(data) / 32):
				graphics.append(tuple(((d & 65534)/2,d & 1) for d in struct.unpack('<16H', data[id*32:(id+1)*32])))
				tile_hash = hash(graphics[-1])
				if not tile_hash in lookup:
					lookup[tile_hash] = []
				lookup[tile_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported VX4 file '%s', could possibly be corrupt" % file)
		self.graphics = graphics
		self.lookup = lookup

	def save_file(self, file):
		data = ''
		for d in self.graphics:
			data += struct.pack('<16H', *[g*2 + h for g,h in d])
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VX4 to '%s'" % file)
		else:
			f = file
		try:
			f.write(data)
		except:
			raise
		finally:
			f.close()

class VR4:
	def __init__(self):
		self.images = []
		self.lookup = {}

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
		try:
			f.write(data)
		except:
			raise
		finally:
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
		try:
			f.write(data)
		except:
			raise
		finally:
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