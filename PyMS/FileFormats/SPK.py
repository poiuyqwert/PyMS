
from . import BMP

from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct

class SPKLayer:
	def __init__(self):
		self.stars = []

class SPKStar:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.image = None

class SPKImage:
	def __init__(self):
		self.width = 0
		self.height = 0
		self.pixels = None

class SPK:
	LAYER_ORIGIN = (-8, -8)
	LAYER_SIZE = (648, 488)
	PARALLAX_RATIOS = [16/256.0, 21/256.0, 26/256.0, 31/256.0, 36/256.0]

	def __init__(self):
		self.layers = []
		self.images = []

	def load_file(self, file):
		data = load_file(file, 'SPK')
		try:
			self.load_data(data)
		except PyMSError as e:
			raise e
		except:
			raise PyMSError('Load',"Unsupported SPK file '%s', could possibly be corrupt" % file)

	def load_data(self, data):
		layer_count = struct.unpack('<H', data[:2])[0]
		star_counts = []
		o = 2
		for _ in range(layer_count):
			star_counts.append(struct.unpack('<H', data[o:o+2])[0])
			o += 2
		layers = []
		images = {}
		maxx,maxy = 0,0
		for count in star_counts:
			layer = SPKLayer()
			layers.append(layer)
			for _ in range(count):
				star = SPKStar()
				star.x,star.y,offset = struct.unpack('<HHL', data[o:o+8])
				maxx = max(star.x,maxx)
				maxy = max(star.y,maxy)
				o += 8
				if not offset in images:
					image = SPKImage()
					image.width,image.height = struct.unpack('<HH', data[offset:offset+4])
					image.pixels = []
					p = offset + 4
					for _ in range(image.height):
						image.pixels.append([ord(c) for c in data[p:p+image.width]])
						p += image.width
					images[offset] = image
				star.image = images[offset]
				layer.stars.append(star)
		self.layers = layers
		self.images = images.values()

	def interpret_file(self, filepath, layer_count):
		bmp = BMP.BMP()
		try:
			bmp.load_file(filepath)
		except:
			raise PyMSError('Interpreting',"Could not load file '%s'" % filepath)
		height = int(bmp.height / float(layer_count))
		if bmp.height % height:
			raise PyMSError('Interpreting',"Image is not the correct height to fit %d layers" % layer_count)
		layers = list(SPKLayer() for _ in range(layer_count))
		runs_by_row = []
		for row in bmp.image:
			runs = []
			runs_by_row.append(runs)
			run = []
			for x,i in enumerate(row):
				if i and not run:
					run = [x,x]
					runs.append(run)
				elif not i and run:
					run[1] = x-1
					run = None
			if run:
				run[1] = len(row)
		images = {}
		for y,row in enumerate(runs_by_row):
			for x1,x2 in row:
				sx1,sy1,sx2,sy2 = x1,y,x2,y
				runs = [[x1,x2]]
				found = True
				ny = y+1
				lx1,lx2 = x1,x2
				while ny < len(runs_by_row) and found:
					found = False
					i = 0
					while i < len(runs_by_row[ny]):
						nx1,nx2 = runs_by_row[ny][i]
						if lx1 <= nx1 <= lx2 or lx1 <= nx2 <= lx2 or (nx1 <= lx1 and lx2 <= nx2):
							runs.append([nx1,nx2])
							found = True
							sx1 = min(sx1,nx1)
							sx2 = max(sx2,nx2)
							lx1 = nx1
							lx2 = nx2
							sy2 = ny
							del runs_by_row[ny][i]
							break
						elif nx1 > sx2:
							break
						i += 1
					ny += 1
				w = (sx2-sx1)+1
				h = (sy2-sy1)+1
				pixels = list([0] * w for _ in range(h))
				for iy,(ix1,ix2) in enumerate(runs):
					pixels[iy][ix1-sx1:ix2-sx1+1] = bmp.image[sy1+iy][ix1:ix2+1]
				check = tuple(tuple(r) for r in pixels)
				if check in images:
					image = images[check]
				else:
					image = SPKImage()
					image.width = w
					image.height = h
					image.pixels = pixels
					images[check] = image
				l = sy1 / height
				star = SPKStar()
				star.x = sx1
				star.y = sy1 - height * l
				star.image = image
				layers[l].stars.append(star)
		self.layers = layers
		self.images = images.values()

	def save_file(self, file):
		data = self.save_data()
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Save',"Could not save SPK to file '%s'" % file)
		f.write(data)
		f.close()

	def save_data(self):
		headers = struct.pack('<H', len(self.layers))
		pixels = ''
		pixels_offset = 2
		for layer in self.layers:
			stars = len(layer.stars)
			headers += struct.pack('<H', stars)
			pixels_offset += 2+8*stars
		images = {}
		for layer in self.layers:
			for star in layer.stars:
				lookup = tuple(tuple(row) for row in star.image.pixels)
				if not lookup in images:
					images[lookup] = pixels_offset
					pixels += struct.pack('<HH', star.image.width, star.image.height)
					pixels_offset += 4
					for row in star.image.pixels:
						pixels += struct.pack('<%dB' % star.image.width, *row)
					pixels_offset += star.image.width * star.image.height
				headers += struct.pack('<HHL', star.x, star.y, images[lookup])
		return headers + pixels

	def decompile_file(self, filepath, palette):
		width = 0
		height = 0
		for layer in self.layers:
			for star in layer.stars:
				width = max(width,star.x+star.image.width)
				height = max(height,star.y+star.image.height)
		full_height = height * len(self.layers)
		image = list([0] * width for _ in range(full_height))
		for l,layer in enumerate(self.layers):
			ly = height * l
			for star in layer.stars:
				for y in range(star.image.height):
					for x in range(star.image.width):
						if not image[star.y+y+ly][star.x+x] and star.image.pixels[y][x]:
							image[star.y+y+ly][star.x+x] = star.image.pixels[y][x]
		bmp = BMP.BMP()
		bmp.set_pixels(image, palette.palette)
		bmp.save_file(filepath)

# import PAL, BMP
# if __name__ == '__main__':
# 	spk = SPK()
# 	# spk.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/SC/parallax/star.spk')
# 	# spk.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/SC/parallax/test.spk')
# 	# raise
# 	spk.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/SC/parallax/test.spk')
# 	pal = PAL.Palette()
# 	pal.load_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/WORKING/SC/tileset/platform.wpe')
# # 	bmp = BMP.BMP()
# # 	bmp.palette = pal.palette
# # 	for n,image in enumerate(spk.images):
# # 		bmp.image = image.pixels
# # 		bmp.width = image.width
# # 		bmp.height = image.height
# # 		bmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/star%d.bmp' % n)
# # 	bmp.width = 648
# # 	bmp.height = 488
# 	allbmp = BMP.BMP()
# 	allbmp.palette = pal.palette
# 	allbmp.width = 648
# 	allbmp.height = 488
# 	allbmp.image = list([0] * allbmp.width for _ in range(allbmp.height))
# 	for n,layer in enumerate(spk.layers):
# 		# bmp.image = list([0] * bmp.width for _ in range(bmp.height))
# 		for star in layer.stars:
# 			for y in range(star.image.height):
# 				for x in range(star.image.width):
# # 					if not bmp.image[star.y+y][star.x+x] and star.image.pixels[y][x]:
# # 						bmp.image[star.y+y][star.x+x] = star.image.pixels[y][x]
# 					if not allbmp.image[star.y+y][star.x+x] and star.image.pixels[y][x]:
# 						allbmp.image[star.y+y][star.x+x] = star.image.pixels[y][x]
# # 		bmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/layer%d.bmp' % n)
# 	allbmp.save_file('/Users/zachzahos/Documents/Projects/PyMS/Libs/full.bmp')
