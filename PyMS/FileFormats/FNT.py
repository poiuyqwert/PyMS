
try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	try:
		import ImageTk
	except:
		from ..Utilities import Assets
		from ..Utilities.DependencyError import DependencyError
		import sys, os
		e = DependencyError('PyMS','PIL is missing. Consult the Source Installation section of the Documentation.', (('Documentation','file:///%s' % Assets.doc_path('intro.html')),))
		e.startup()
		sys.exit()

from . import BMP

from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct

# Maps the color characters to special palette index
COLOR_CODES_INGAME = {
	1:2, # This is technically "default" color, but its usually the same as 2 so I remap it there by default
	2:(0,0),
	3:(0,1),
	4:(0,2),
	5:(0,3),
	6:(0,4),
	7:(0,5),
	8:(1,0),
	11:(0,6),
	14:(1,1),
	15:(1,2),
	16:(1,3),
	17:(1,4),
	20:(0,7),
	21:(1,5),
	22:(1,6),
	23:(1,7),
	24:(2,0),
	25:(2,1),
	26:(0,0),
	27:(2,2),
	28:(2,3),
	29:(2,4),
	30:(2,5),
	31:(2,7)
}
COLOR_CODES_GLUE = {
	1:2, # This is technically "default" color, but its usually the same as 2 so I remap it there by default
	2:(0,0),
	3:(0,1),
	4:(0,2),
	5:(0,3),
	6:(0,4),
	13:(0,0),
	26:(0,0),
}
COLOR_CODES_TITLE = {
	1:2, # This is technically "default" color, but its usually the same as 2 so I remap it there by default
	2:(0,0),
	3:(0,1),
	4:(0,2),
	5:(0,3),
	6:(0,4),
	13:(0,0),
	26:(0,0),
}
# Any color codes after these will do nothing
COLOR_OVERPOWER = [5,11,20]

def letter_to_photo(palette, letter, color, remap=None, remap_palette=None):
	i = PILImage.new('RGBA', (len(letter[0]),len(letter)))
	if remap == None:
		remap = COLOR_CODES_INGAME
	if remap_palette:
		palette = remap_palette
	color_map = remap[color]
	while isinstance(color_map, int):
		color_map = remap[color_map]
	data = []
	for y in letter:
		data.extend(y)
	pal = []
	for n,c in enumerate(palette.palette):
		alpha = 0
		if n != palette.image[color_map[0]][color_map[1] * 8] and c != [255,0,255]:
			alpha = 255
		pal.append((c[0],c[1],c[2],alpha))
	i.putdata([pal[palette.image[color_map[0]][color_map[1]*8+i]] for i in data])
	return ImageTk.PhotoImage(i)

def fnttobmp(fnt,pal,file=None):
	b = BMP.BMP()
	b.set_pixels(fnt.letters[0],pal)
	for l in fnt.letters[1:]:
		for y,yd in enumerate(l):
			b.image[y].extend(yd)
	b.width = len(b.image[0])
	if file == None:
		return b
	b.save_file(file)

def bmptofnt(bmp,lowi,letters,file=None):
	f = FNT()
	f.start,f.width,f.height = lowi,bmp.width / letters,bmp.height
	for l in range(letters):
		f.letters.append([])
		for y in bmp.image:
			f.letters[-1].append(y[f.width * l:f.width * (l+1)])
	if file == None:
		return f
	f.save_file(file)

class FNT:
	def __init__(self):
		self.width = 0
		self.height = 0
		self.start = 0
		self.letters = []
		self.sizes = []

	def load_file(self, file):
		data = load_file(file, 'FNT')
		if data[:4] != 'FONT':
			raise PyMSError('Load',"Invalid FNT file '%s' (invalid header)" % file)
		try:
			lowi,highi,maxw,maxh = struct.unpack('<4B',data[4:8])
			letters = []
			sizes = []
			for l in range(highi-lowi+1):
				o = 8+4*l
				o = struct.unpack('<L',data[o:o+4])[0]
				if o:
					width,height,xoffset,yoffset = struct.unpack('4B', data[o:o+4])
					pxls = [[]]
					o += 4
					while len(pxls) < height or (len(pxls) == height and len(pxls[-1]) < width):
						c = data[o]
						co,col = (c & 248) >> 3,c & 7
						if len(pxls[-1])+co > width:
							e = width-len(pxls[-1])
							pxls[-1].extend([0] * e)
							pxls.extend([[0] * width for _ in range(min((co-e)/width,height-len(pxls)))])
							if (co-e)%width and len(pxls) < height:
								pxls.append([0] * ((co-e)%width))
						elif co:
							pxls[-1].extend([0] * co)
						if len(pxls) < height and len(pxls[-1]) == width:
							pxls.append([])
						if len(pxls) < height or len(pxls[-1]) < width:
							pxls[-1].append(col)
						o += 1
					for y,d in enumerate(pxls):
						pxls[y] = [0]*xoffset + d + [0]*(maxw-width-xoffset)
					pxls = [[0]*maxw for _ in range(yoffset)] + pxls + [[0]*maxw for _ in range(maxh-height-yoffset)]
					sizes.append([width,height,xoffset,yoffset])
				else:
					pxls = [[0]*maxw for _ in range(maxh)]
					sizes.append([0,0,0,0])
				letters.append(pxls)
			self.width,self.height = maxw,maxh
			self.start = lowi
			self.letters = letters
			self.sizes = sizes
		except:
			raise PyMSError('Load',"Unsupported FNT file '%s', could possibly be corrupt" % file)

	def save_file(self, file):
		try:
			f = AtomicWriter(file, 'wb')
		except:
			raise PyMSError('Compile',"Could not load file '%s'" % file)
		header = 'FONT%c%c%c%c' % (self.start,self.start+len(self.letters)-1,self.width,self.height)
		o = 8+4*len(self.letters)
		data = ''
		hist = {}
		for d in self.letters:
			ldata = ''
			maxw = len(d[0])
			w,h,xo,yo = 0,0,999,-1
			for y,yd in enumerate(d):
				if yd.count(0) < maxw:
					if yo < 0:
						yo = y
					h = y + 1
					for x,xd in enumerate(yd):
						if xd:
							if xo < 0 or x < xo:
								xo = x
							if x >= w:
								w = x + 1
			if w + h == 0:
				header += '\x00'*4
			else:
				w -= xo
				h -= yo
				ldata += '%c%c%c%c' % (w,h,xo,yo)
				skip = 0
				for y in d[yo:yo+h]:
					for x in y[xo:xo+w]:
						if not x and skip < 31:
							skip += 1
						else:
							ldata += chr((skip << 3) + x)
							skip = 0
				if skip:
					ldata += chr(skip << 3)
				if ldata in hist:
					header += struct.pack('<L',hist[ldata])
				else:
					header += struct.pack('<L',o)
					hist[ldata] = o
					data += ldata
					o += len(ldata)
		f.write(header + data)
		f.close()

# from BMP import *
# import sys
# sys.stdout = open('stdieo.txt','w')
# f = FNT()
# f.load_file('test.fnt')
# b = BMP()
# for y in f.letters[0][-1]:
	# for x in y:
		# print(FONT_COLORS[x],)
	# print('')
# b.load_data(f.letters[0],FONT_COLORS)
# for d in f.letters[1:]:
	# for y,yd in enumerate(d):
		# b.image[y].extend(yd)
# b.width = len(b.image[0])
# b.save_file('ex.bmp')
#f.save_file('test.fnt')