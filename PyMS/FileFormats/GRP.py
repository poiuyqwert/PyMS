
try:
	from tkinter import Image
	from PIL import Image as PILImage
	from PIL import ImageTk
except:
	from ..Utilities import Assets
	from ..Utilities.DependencyError import DependencyError
	import sys, os
	e = DependencyError('PyMS','PIL is missing. Consult the Source Installation section of the Documentation.', (('Documentation','file:///%s' % Assets.readme_file_path),))
	e.startup()
	sys.exit()
	
from .Images import Pixels, RawPalette, RGBA, RGB, Bounds

from ..Utilities.fileutils import load_file
from ..Utilities.PyMSError import PyMSError
from ..Utilities.AtomicWriter import AtomicWriter

import struct
from copy import deepcopy
from enum import Enum

from typing import TYPE_CHECKING, Callable, TypeVar, cast, BinaryIO, Sequence
if TYPE_CHECKING:
	from .BMP import BMP
	from .PCX import PCX

T = TypeVar('T')
RLEFunc = Callable[[RawPalette, int, T], RGBA]

def rle_normal(pal, index, player_colors=None): # type: (RawPalette, int, list[RGB] | None) -> RGBA
	rgb = pal[index]
	if player_colors is not None and len(player_colors) >= 8 and 8 <= index <= 15:
		rgb = player_colors[index - 8]
	return (rgb[0],rgb[1],rgb[2], 255)

def rle_shadow(pal, index, color=None): # type: (RawPalette, int, RGBA | None) -> RGBA
	return color or (0,0,0,255)

class Outline(Enum):
	enemy = 0
	self = 1
	ally = 2
def rle_outline(pal, index, ally_status=Outline.self): # type: (RawPalette, int, Outline) -> RGBA
	rgb = pal[index]
	if 1 <= index <= 9:
		if ally_status == Outline.enemy:
			rgb = (155,21,23)
		elif ally_status == Outline.self:
			rgb = (36,152,36)
		else:
			rgb = (220,220,60)
	return (rgb[0],rgb[1],rgb[2], 255)

def image_bounds(image, transindex=0): # type: (Pixels, int) -> Bounds
	width = len(image[0])
	bounds = [-1,-1,-1,-1]
	found_pixels = False
	for y,yd in enumerate(image):
		if yd.count(transindex) != width:
			found_pixels = True
			if bounds[1] == -1:
				bounds[1] = y
			bounds[3] = y + 1
			line = yd
			for x,xd in enumerate(line):
				if xd != transindex:
					if bounds[0] == -1 or x < bounds[0]:
						bounds[0] = x
					if x + 1 > bounds[2]:
						bounds[2] = x + 1
	if not found_pixels:
		return (0,0,0,0)
	return (bounds[0], bounds[1], bounds[2], bounds[3])

# transindex=None for no transparency
def image_to_pil(image, palette, transindex=0, image_bounds=None, flipHor=False, draw_function=rle_normal, draw_info=None): # type: (Pixels, RawPalette, int, Bounds | None, bool, RLEFunc, T | None) -> PILImage.Image
	if image_bounds:
		x_min,y_min,x_max,y_max = image_bounds
		image = list(line[x_min:x_max+1] for line in image[y_min:y_max+1])
	width = len(image[0])
	height = len(image)
	i = PILImage.new('RGBA', (width,height))
	pal = [draw_function(palette,i,draw_info) for i in range(len(palette))]
	if transindex is not None:
		pal[transindex] = (0,0,0,0)
	pixels = [] # type: list[int]
	if flipHor:
		for row in image:
			pixels.extend(reversed(row))
	else:
		for row in image:
			pixels.extend(row)
	data = list(map(pal.__getitem__, pixels))
	i.putdata(data) # type: ignore[arg-type]
	return i

def image_to_tk(image, palette, transindex=0, image_bounds=None, flipHor=False, draw_function=rle_normal, draw_info=None): # type: (Pixels, RawPalette, int, Bounds | None, bool, RLEFunc, T | None) -> Image
	pil = image_to_pil(image, palette, transindex, image_bounds, flipHor, draw_function, draw_info)
	return cast(Image, ImageTk.PhotoImage(pil))

ImageWithBounds = tuple[Image, int, int, int, int]

def frame_to_photo(p, g, f=None, buffered=False, size=True, trans=True, transindex=0, flipHor=False, draw_function=rle_normal, draw_info=None): # type: (RawPalette, GRP | CacheGRP | BMP | PCX | Pixels, int | None, bool, bool, bool, int, bool, RLEFunc, T | None) -> (Image | ImageWithBounds)
	if isinstance(g, CacheGRP):
		d = g[f or 0]
	elif isinstance(g, GRP):
		d = g.images[f or 0]
		transindex = g.transindex
	elif isinstance(g, BMP):
		d = g.image
	elif isinstance(g, PCX):
		d = g.image
	else:
		d = g
	if not size:
		return image_to_tk(d, p, transindex, flipHor=flipHor, draw_function=draw_function, draw_info=draw_info)
	width = len(d[0])
	height = len(d)
	i = PILImage.new('RGBA', (width,height))
	data = [] # type: list[RGBA]
	pal = list(draw_function(p,i,draw_info) for i in range(len(p)))
	pal[transindex] = (0,0,0,0)
	bounds = [-1,-1,-1,-1]
	for y,yd in enumerate(d):
		if yd.count(transindex) != width:
			if bounds[2] == -1:
				bounds[2] = y
			bounds[3] = y + 1
			line = yd
			if flipHor:
				line = list(reversed(line))
			for x,xd in enumerate(line):
				if xd != transindex:
					if bounds[0] == -1 or x < bounds[0]:
						bounds[0] = x
					if x >= bounds[1]:
						bounds[1] = x + 1
				data.append(pal[xd])
		else:
			data.extend([(0,0,0,0) for _ in range(width)])
	i.putdata(data) # type: ignore[arg-type]
	image = cast(Image, ImageTk.PhotoImage(i))
	return (image, bounds[0], bounds[1], bounds[2], bounds[3])

class RLE:
	TRANSPARENT_FLAG = (1 << 7)
	TRANSPARENT_MAX_LENGTH = TRANSPARENT_FLAG - 1
	REPEAT_FLAG = (1 << 6)
	REPEAT_MAX_LENGTH = REPEAT_FLAG - 1
	STATIC_MAX_LENGTH = REPEAT_FLAG - 1

	@staticmethod
	def encode_transparent(count): # type: (int) -> bytes
		encoded = b''
		while count > 0:
			encoded += struct.pack('<B', RLE.TRANSPARENT_FLAG | min(RLE.TRANSPARENT_MAX_LENGTH, count))
			count -= RLE.TRANSPARENT_MAX_LENGTH
		return encoded

	@staticmethod
	def encode_repeat(index, count): # type: (int, int) -> bytes
		encoded = b''
		while count > 0:
			encoded += struct.pack('<BB', RLE.REPEAT_FLAG | min(RLE.REPEAT_MAX_LENGTH, count), index)
			count -= RLE.REPEAT_MAX_LENGTH
		return encoded

	@staticmethod
	def encode_static(line): # type: (Sequence[int]) -> bytes
		encoded = b''
		for x in range(0, len(line), RLE.STATIC_MAX_LENGTH):
			run = line[x:x+RLE.STATIC_MAX_LENGTH]
			encoded += struct.pack('<%dB' % (1 + len(run)), len(run), *run)
		return encoded

	@staticmethod
	def compress_line(line, transparent_index): # type: (Sequence[int], int) -> bytes
		last_index = line[0]
		repeat_count = 0
		static_len = 0
		compressed = b''
		for (x,index) in enumerate(line):
			if index == last_index:
				repeat_count += 1
			else:
				if last_index == transparent_index:
					compressed += RLE.encode_transparent(repeat_count)
				elif repeat_count > 1 and static_len < 2:
					compressed += RLE.encode_repeat(last_index, repeat_count)
				repeat_count =  1
			if repeat_count > 2 or index == transparent_index:
				if static_len > repeat_count-1:
					compressed += RLE.encode_static(line[x-static_len:x-repeat_count+1])
				static_len = 0
			else:
				static_len += 1
			last_index = index
		if last_index == transparent_index:
			compressed += RLE.encode_transparent(repeat_count)
		elif static_len and static_len > repeat_count:
			compressed += RLE.encode_static(line[-static_len:])
		elif repeat_count:
			compressed += RLE.encode_repeat(last_index, repeat_count)
		return compressed

	@staticmethod
	def decompress_line(data, width, transparent_index=0): # type: (bytes, int, int) -> list[int]
		line = [] # type: list[int]
		offset = 0
		while len(line) < width:
			byte = data[offset]
			offset += 1
			if byte & RLE.TRANSPARENT_FLAG:
				line.extend([transparent_index] * (byte - RLE.TRANSPARENT_FLAG))
			elif byte & RLE.REPEAT_FLAG:
				line.extend([data[offset]] * (byte - RLE.REPEAT_FLAG))
				offset += 1
			else:
				line.extend(data[offset:offset+byte])
				offset += byte
		if len(line) > width:
			line = line[:width]
		return line

class CacheGRP:
	def __init__(self, palette=[(0,0,0)]*256): # type: (RawPalette) -> None
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette
		self.imagebuffer = [] # type: list[tuple[Bounds, tuple[int, ...]]]
		self.images = {} # type: dict[int, Pixels]
		self.image_bounds = {} # type: dict[int, Bounds]
		self.databuffer = b''
		self.uncompressed = None # type: bool | None

	def load_file(self, file, palette=None, restrict=None, uncompressed=None): # type: (str | BinaryIO, RawPalette | None, int | None, bool | None) -> None
		data = load_file(file, 'GRP')
		try:
			frames, width, height = struct.unpack('<3H',data[:6])
			if frames < 1 or frames > 2400 or width < 1 or width > 256 or height < 1 or height > 256:
				raise Exception()
			if restrict:
				frames = restrict
			images = [] # type: list[tuple[Bounds, tuple[int, ...]]]
			for frame in range(frames):
				xoffset, yoffset, linewidth, lines, framedata = tuple(int(v) for v in struct.unpack('<4BL', data[6+8*frame:14+8*frame]))
				line_offsets = [] # type: list[int]
				for line in range(lines):
					line_offsets.append(framedata+struct.unpack('<H',data[framedata+2*line:framedata+2+2*line])[0])
				images.append(((xoffset, yoffset, linewidth, lines), tuple(line_offsets)))
		except:
			raise PyMSError('Load',"Unsupported GRP file '%s', could possibly be corrupt or an uncompressed GRP" % file, capture_exception=True)
		self.frames = frames
		self.width = width
		self.height = height
		if palette:
			self.palette = list(palette)
		self.imagebuffer = images
		self.images = {}
		self.databuffer = data
		self.uncompressed = uncompressed

	def save_data(self): # type: () -> bytes
		return self.databuffer

	def __getitem__(self, frame): # type: (int) -> Pixels
		if frame in self.images:
			return self.images[frame]
		image = [] # type: list[list[int]]
		(xoffset, yoffset, linewidth, lines), offsets = self.imagebuffer[frame]
		if xoffset + linewidth > self.width:
			linewidth = self.width - xoffset
		if yoffset + lines > self.height:
			lines = self.height - yoffset
		image.extend([[0] * self.width for _ in range(yoffset)])
		if not self.uncompressed:
			try:
				for offset in offsets:
					image.append([0] * xoffset + RLE.decompress_line(self.databuffer[offset:], linewidth) + [0] * (self.width-linewidth-xoffset))
				if self.uncompressed is None:
					self.uncompressed = False
			except:
				if self.uncompressed is None:
					self.uncompressed = True
				else:
					raise PyMSError('Decompile','Could not decompile frame %s, GRP could be corrupt.' % frame)
		if self.uncompressed:
			try:
				for offset in offsets:
					linedata = []
					if xoffset > 0:
						linedata = [0] * xoffset
					linedata.extend(self.databuffer[offset:offset+linewidth])
					image.append(linedata + [0] * (self.width-linewidth-xoffset))
			except:
				raise PyMSError('Decompile','Could not decompile frame %s, GRP could be corrupt.' % frame)
		if len(image) < self.height:
			image.extend([[0] * self.width for _ in range(self.height - len(image))])
		self.images[frame] = image[:self.height]
		self.image_bounds[frame] = (xoffset,yoffset,linewidth,lines)
		return self.images[frame]

class GRP:
	def __init__(self, palette=[(0,0,0)]*256, uncompressed=None, transindex=0): # type: (RawPalette, bool | None, int) -> None
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette
		self.images = [] # type: list[Pixels]
		self.images_bounds = [] # type: list[Bounds]
		self.uncompressed = uncompressed
		self.transindex = transindex

	def load_file(self, file, palette=None, transindex=0, uncompressed=None): # type: (str | BinaryIO, RawPalette | None, int, bool | None) -> None
		data = load_file(file, 'GRP')
		try:
			frames, width, height = tuple(int(v) for v in struct.unpack('<3H',data[:6]))
			if frames < 1 or frames > 2400 or width < 1 or width > 256 or height < 1 or height > 256:
				raise Exception()
			retries = 2
			while retries:
				retries -= 1
				images = [] # type: list[Pixels]
				images_bounds = [] # type: list[Bounds]
				for frame in range(frames):
					image = [] # type: list[list[int]]
					xoffset, yoffset, linewidth, lines, framedata = tuple(int(v) for v in struct.unpack('<4BL', data[6+8*frame:14+8*frame]))
					# ignore extra bytes
					if xoffset + linewidth > width:
						linewidth = width - xoffset
					if yoffset + lines > height:
						lines = height - yoffset
					# print(frames,width,height,xoffset,yoffset,linewidth,lines,framedata)
					image.extend([[0] * width for _ in range(yoffset)])
					if uncompressed:
						for line in range(lines):
							linedata = []
							if xoffset > 0:
								linedata = [transindex] * xoffset
							linedata.extend(data[framedata:framedata+linewidth])
							image.append(linedata + [transindex] * (width-linewidth-xoffset))
							framedata += linewidth
					else:
						try:
							for line in range(lines):
								offset = framedata+int(struct.unpack('<H',data[framedata+2*line:framedata+2+2*line])[0])
								image.append([transindex] * xoffset + RLE.decompress_line(data[offset:], linewidth, transindex) + [transindex] * (width-linewidth-xoffset))
						except:
							if uncompressed is None:
								uncompressed = True
								break
							raise
					if len(image) < height:
						image.extend([[transindex] * width for _ in range(height - len(image))])
					images.append(image[:height])
					images_bounds.append((xoffset,yoffset,xoffset+linewidth,yoffset+lines))
		except:
			raise PyMSError('Load',"Unsupported GRP file '%s', could possibly be corrupt" % file, capture_exception=True)
		self.frames = frames
		self.width = width
		self.height = height
		self.uncompressed = uncompressed
		if palette:
			self.palette = list(palette)
		self.images = images
		self.images_bounds = images_bounds
		self.transindex = transindex

	def load_data(self, frames, palette=None, transindex=0, validate=True): # type: (list[Pixels], RawPalette | None, int, bool) -> None
		if not frames:
			raise PyMSError('GRP', 'Attempting to load GRP data with no frames')
		self.frames = len(frames)
		height = len(frames[0])
		width = len(frames[0][0])
		if validate:
			for (n, frame) in enumerate(frames, 1):
				frame_height = len(frame)
				if frame_height != height:
					raise PyMSError('GRP', 'Frame %d has unexpected height (got %d, expected %d)' % (n, frame_height, height))
				for (y, line) in enumerate(frame):
					line_width = len(line)
					if line_width != width:
						raise PyMSError('GRP', 'Frame %d line %d has unexpected width (got %d, expected %d)' % (n, y, line_width, width))
		self.height = height
		self.width = width
		if palette:
			self.palette = list(palette)
		self.images = deepcopy(frames)
		self.images_bounds = [image_bounds(frame, transindex) for frame in frames]
		self.transindex = transindex

	def save_data(self, uncompressed=None): # type: (bool | None) -> bytes
		if uncompressed is None:
			uncompressed = self.uncompressed
		header_data = struct.pack('<3H', self.frames, self.width, self.height)
		image_data = b''
		offset = 6 + 8 * self.frames
		frame_history = {} # type: dict[bytes | tuple[int, int, int, int, tuple[tuple[int, ...], ...]], bytes]
		for z,frame in enumerate(self.images):
			x_min, y_min, x_max, y_max = self.images_bounds[z]
			if uncompressed:
				data = bytes(p for row in frame[y_min:y_max] for p in row[x_min:x_max])
				if data in frame_history:
					header_data += frame_history[data]
				else:
					frame_data = struct.pack('<4BL', x_min, y_min, x_max - x_min, y_max - y_min, offset)
					header_data += frame_data
					frame_history[data] = frame_data
					image_data += data
					offset += len(data)
			else:
				frame_hash = (x_min, x_max, y_min, y_max, tuple(tuple(l[x_min:x_max]) for l in frame[y_min:y_max]))
				# If there is a duplicate frame, just point to it
				if frame_hash in frame_history:
					header_data += frame_history[frame_hash]
				else:
					frame_data = struct.pack('<4BL', x_min, y_min, x_max - x_min, y_max - y_min, offset)
					frame_history[frame_hash] = frame_data
					header_data += frame_data
					line_data = b''
					line_offset = 2 * (y_max - y_min)
					line_offsets = [] # type: list[bytes]
					line_history = {} # type: dict[tuple[int, ...], bytes]
					for _y,line in enumerate(frame[y_min:y_max]):
						line_hash = tuple(line)
						# If there is a duplicate line is this frame, just point to it
						if line_hash in line_history:
							line_offsets.append(line_history[line_hash])
						else:
							data = RLE.compress_line(line[x_min:x_max], self.transindex)
							line_data += data
							if line_offset > 65535:
								raise PyMSError('Save','The image has too much pixel data to compile')
							line_offsets.append(struct.pack('<H', line_offset))
							line_history[line_hash] = line_offsets[-1]
							line_offset += len(data)
					line_data = b''.join(line_offsets) + line_data
					image_data += line_data
					offset += len(line_data)
		return header_data + image_data

	def save_file(self, file, uncompressed=None): # type: (str | BinaryIO, bool | None) -> None
		image_data = self.save_data()
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(image_data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the GRP to '%s'" % file)
		else:
			file.write(image_data)
