from utils import *

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
	PARALLAX_RATIOS = [1/(64/4.0), 1/(128/10.0), 1/(320/20.0), 1/(192/23.0), 1/(320/45.0)] # Estimates

	def __init__(self):
		self.layers = []
		self.images = []

	def load_file(self, file):
		try:
			if isstr(file):
				f = open(file,'rb')
				data = f.read()
				f.close()
			else:
				data = file.read()
		except:
			raise PyMSError('Load',"Could not load SPK file '%s'" % file)
		try:
			self.load_data(data)
		except PyMSError, e:
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
		for count in star_counts:
			layer = SPKLayer()
			layers.append(layer)
			for _ in range(count):
				star = SPKStar()
				star.x,star.y,offset = struct.unpack('<HHL', data[o:o+8])
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

	def save_file(self, file):
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise
		f.write(self.save_data())
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
