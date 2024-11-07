
from .Images import Pixels, RawPalette

from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct, math

from typing import BinaryIO

def getPadding(value: int, alignment: int) -> int:
	return int(math.ceil(value/float(alignment)))*alignment - value

class RLE:
	ABSOLUTE_MODE = 0
	ABSOLUTE_EOL = 0
	ABSOLUTE_EOF = 1
	ABSOLUTE_DELTA = 2

	@staticmethod
	def decompress(data: bytes, width: int, height: int) -> Pixels:
		image: Pixels = [[]]
		offset = 0
		while True:
			if data[offset] == RLE.ABSOLUTE_MODE:
				if data[offset+1] <= RLE.ABSOLUTE_DELTA:
					if data[offset+1] == RLE.ABSOLUTE_DELTA:
						xoffset, yoffset = data[offset+2], data[offset+3]
						if not image[-1]:
							image.pop()
						elif len(image[-1]) < width and yoffset > 0:
							image[-1].extend([0] * (width - len(image[-1])))
						image.extend([[0] * width] * yoffset + [[0] * xoffset])
						offset += 2
					else:
						if len(image[-1]) < width:
							image[-1].extend([0] * (width - len(image[-1])))
						if data[offset+1] == RLE.ABSOLUTE_EOF:
							if len(image) < height:
								image.extend([[0] * width] * (height - len(image)))
							break
						image.append([])
				else:
					n = data[offset+1]
					image[-1].extend(data[offset+2:offset+2+n])
					offset += n + getPadding(n,2)
			else:
				image[-1].extend([data[offset+1]] * data[offset])
			offset += 2
		image.reverse()
		for y in range(len(image)):
			if len(image[y]) > width:
				del image[y][width:]
		return image

class BMP:
	def __init__(self, palette: RawPalette = []) -> None:
		self.width = 0
		self.height = 0
		self.palette = palette
		self.image: Pixels = []

	def load_file(self, file: str | BinaryIO, issize: tuple[int, int] | None = None) -> None:
		data = load_file(file, 'BMP')
		self.load_data(data, issize=issize)

	def load_data(self, data: bytes, issize: tuple[int, int] | None = None) -> None:
		if data[:2] != b'BM':
			raise PyMSError('Load',"Invalid BMP file (no BMP header)")
		try:
			pixels_offset, dib_header_size, width, height, bitcount, compression, colors_used = \
				tuple(int(v) for v in struct.unpack('<4LxxHL12xL',data[10:50]))
			if issize and width != issize[0] and height != issize[1]:
				raise PyMSError('Load', "Invalid dimensions (Expected %sx%s, got %sx%s)" % (issize[0],issize[1],width,height))
			if bitcount != 8 or not compression in [0,1]:
				raise PyMSError('Load',"The BMP is not in the correct form. It must be 256 color (8 bit), with RLE compression or no compression at all.")
			if not colors_used:
				colors_used = 256
			palette: RawPalette = []
			for x in range(0,4 * colors_used,4):
				b,g,r = tuple(int(c) for c in struct.unpack('<3B',data[14+dib_header_size+x:17+dib_header_size+x]))
				palette.append((r,g,b))
			palette.extend([(0,0,0)] * (256-colors_used))
			if not compression:
				image: Pixels = []
				pad = getPadding(width,4)
				for y in range(height):
					x = pixels_offset+(width+pad)*y
					image.append(list(int(v) for v in struct.unpack('%sB%s' % (width, 'x' * pad),data[x:x+width+pad])))
				image.reverse()
				for y in range(len(image)):
					if len(image[y]) > width:
						del image[y][width:]
			else:
				image = RLE.decompress(data[pixels_offset:], width, height)
		except PyMSError:
			raise
		except:
			raise PyMSError('Load',"Unsupported BMP file, could possibly be corrupt")
		self.width = width
		self.height = height
		self.palette = palette
		self.image = image

	def set_pixels(self, image: Pixels, palette: RawPalette | None = None) -> None:
		self.height = len(image)
		self.width = len(image[0])
		if palette:
			self.palette = list(palette)
		self.image = [list(y) for y in image]

	def save_file(self, file: str) -> None:
		try:
			f = AtomicWriter(file,'wb')
		except:
			raise PyMSError('Save',"Could not save BMP to file '%s'" % file)
		data = b''
		pad = getPadding(self.width,4)
		for y in self.image:
			data = struct.pack('<%sB%s' % (self.width, 'x' * pad), *y) + data
		palette = list(self.palette)
		if len(palette) < 256:
			palette.extend([(0,0,0)] * (256-len(palette)))
		palette.reverse()
		for c in list(palette):
			t = list(c)
			t.reverse()
			data = struct.pack('<3Bx', t[0], t[1], t[2]) + data
		data = struct.pack('<HH4LHH6L', 0, 0, 1078, 40, self.width, self.height, 1, 8, 0, len(data) - 1024, 0, 0, 0, 0) + data
		f.write(b'BM' + struct.pack('<L',len(data) + 6) + data)
		f.close()
