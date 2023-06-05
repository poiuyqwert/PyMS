
from .Images import Pixels, RawPalette

from ..Utilities.utils import nearest_multiple
from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct, math

from typing import BinaryIO

# This class is designed for StarCraft PCX's, there is no guarantee it works with other PCX files
class PCX:
	def __init__(self, palette=[]): # type: (RawPalette) -> None
		self.width = 0
		self.height = 0
		self.palette = palette
		self.image = [] # type: Pixels

	def load_file(self, file, pal=False): # type: (str | BinaryIO, bool) -> None
		data = load_file(file, 'PCX')
		self.load_data(data, pal)

	def load_data(self, data, pal=False): # type: (bytes, bool) -> None
		if data[:4] != b'\x0A\x05\x01\x08':
			raise PyMSError('Load',"Not a PCX file (no PCX header)")
		try:
			xmin,ymin,xmax,ymax,_hdpi,_vdpi = struct.unpack('<6H',data[4:16])
			planes,_bytesperline,_palinfo,_hscreensize,_vscreensize = struct.unpack('<B4H', data[65:74])
			xmax = (xmax-xmin)+1
			ymax = (ymax-ymin)+1
			if data[-769] != b'\x0C':
				raise PyMSError('Load', "Unsupported PCX file, the palette information is missing")
			if pal and (xmax > 256 or ymax > 256 or planes != 1):
				raise PyMSError('Load', "Unsupported special palette (PCX) file")
			palette = [] # type: RawPalette
			for x in range(0,768,3):
				if x == 765:
					r,g,b = tuple(int(c) for c in struct.unpack('3B', data[-768+x:]))
				else:
					r,g,b = tuple(int(c) for c in struct.unpack('3B', data[-768+x:-765+x]))
				palette.append((r,g,b))
			image = [[]] # type: Pixels
			x = 128
			while x < len(data) - 769:
				c = data[x]
				x += 1
				if c & 192 == 192:
					image[-1].extend([data[x]] * (63 & c))
					x += 1
				else:
					image[-1].append(c)
				if len(image[-1]) > xmax:
					image.append(image[-1][xmax:])
					image[-2] = image[-2][:xmax]
				elif len(image[-1]) == xmax and len(image) < ymax:
					image.append([])
			# print("""\
# --- %s ---------------
# x min/max      : %s %s
# y min/max      : %s %s
# h/v dpi        : %s %s
# planes         : %s
# bytes/plane    : %s
# palinfo        : %s
# h/v screen size: %s %s
# palette        : %s""" % (file,xmin,xmax,ymin,ymax,hdpi,vdpi,planes,bytesperline,palinfo,hscreensize,vscreensize,palette))
			for y in image:
				if len(y) < xmax:
					y.extend([0]*(xmax-len(y)))
			self.width = xmax
			self.height = ymax
			self.palette = palette
			self.image = image
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',"Unsupported PCX file, could possibly be corrupt")

	def load_pixels(self, image, palette=None): # type: (Pixels, RawPalette | None) -> None
		self.height = len(image)
		self.width = len(image[0])
		if palette:
			self.palette = list(palette)
		self.image = [list(y) for y in image]

	def save_file(self, file): # type: (str) -> None
		try:
			f = AtomicWriter(file,'wb')
		except:
			raise PyMSError('Save',"Could not save PCX to file '%s'" % file)
		f.write(b'\x0A\x05\x01\x08' + struct.pack('<6H49xB4H54x', 0, 0, self.width-1, self.height-1, 72, 72, 1, nearest_multiple(self.width,2,math.ceil), 0, 0, 0))
		for y in self.image:
			last = y[0]
			repeat = 1
			for index in y[1:]:
				if index == last:
					if repeat == 63:
						f.write(b'\xFF')
						f.write(index.to_bytes())
						repeat = 1
					else:
						repeat += 1
				else:
					if repeat > 1:
						f.write((repeat | 0xC0).to_bytes())
					elif last >= 192:
						f.write(b'\xC1')
					f.write(last.to_bytes())
					last = index
					repeat = 1
			if repeat > 1:
				f.write((repeat | 0xC0).to_bytes())
			elif last >= 192:
				f.write(b'\xC1')
			f.write(last.to_bytes())
		f.write(b'\x0C' + b''.join(struct.pack('3B',*c) for c in self.palette))
		f.close()

# import sys
# sys.stdout = open('stdeo.txt','w')
# import BMP
# p = PCX()
#p.load_file(r'C:\Documents and Settings\Administrator\Desktop\SCScrnShot_021909_220704.pcx')
# p.load_file(r'C:\Documents and Settings\Administrator\Desktop\test.pcx')
# b = BMP.BMP()
# b.load_data(p.image, p.palette)
# b.save_file(r'C:\Documents and Settings\Administrator\Desktop\test.bmp')
# p = PCX()
# b = BMP.BMP()
# for f in ['ticon','bfire','gfire','ofire']:
	# p.load_file(f + '.pcx')
	# # for l in p.image:
	# # 	print(len(l))
	# # print('-----')
	# b.load_data(p.image, p.palette)
	# b.save_file(f + '.bmp')
