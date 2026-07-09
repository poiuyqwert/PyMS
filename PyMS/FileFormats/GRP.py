
from __future__ import annotations

try:
	from PIL import Image as PILImage
	from PIL import ImageTk
except Exception:
	from ..Utilities.DependencyError import DependencyError
	import sys
	e = DependencyError('PyMS','PIL is missing. Please consult the Installation section of the Readme.')
	e.startup()
	sys.exit()

from .Images import Pixels, RawPalette, RGBA, RGB, Bounds
from .BMP import BMP
from .PCX import PCX

from ..Utilities.PyMSError import PyMSError
from ..Utilities import IO

import struct, math
from copy import deepcopy
from enum import Enum

from typing import Callable, TypeVar, Sequence

T = TypeVar('T')
RLEFunc = Callable[[RawPalette, int, T], RGBA]

def rle_normal(pal: RawPalette, index: int, player_colors: list[RGB] | None = None) -> RGBA:
	rgb = pal[index]
	if player_colors is not None and len(player_colors) >= 8 and 8 <= index <= 15:
		rgb = player_colors[index - 8]
	return (rgb[0],rgb[1],rgb[2], 255)

def rle_shadow(_pal: RawPalette, _index: int, color: RGBA | None = None) -> RGBA:
	return color or (0,0,0,255)

class Outline(Enum):
	enemy = 0
	self = 1
	ally = 2
def rle_outline(pal: RawPalette, index: int, ally_status: Outline = Outline.self) -> RGBA:
	rgb = pal[index]
	if 1 <= index <= 9:
		if ally_status == Outline.enemy:
			rgb = (155,21,23)
		elif ally_status == Outline.self:
			rgb = (36,152,36)
		else:
			rgb = (220,220,60)
	return (rgb[0],rgb[1],rgb[2], 255)

def image_bounds(image: Pixels, transindex: int = 0) -> Bounds:
	width = len(image[0])
	x_min = -1
	y_min = -1
	x_max = -1
	y_max = -1
	for y,yd in enumerate(image):
		if yd.count(transindex) != width:
			if y_min == -1:
				y_min = y
			y_max = y + 1
			for x,xd in enumerate(yd):
				if xd != transindex:
					if x_min == -1 or x < x_min:
						x_min = x
					x_max = max(x_max, x + 1)
	if y_min == -1:
		return Bounds(x_min=0, y_min=0, x_max=0, y_max=0)
	return Bounds(x_min=x_min, y_min=y_min, x_max=x_max, y_max=y_max)

# transindex=None for no transparency
def image_to_pil(image: Pixels, palette: RawPalette, *, transindex: int | None = 0, bounds: Bounds | None = None, flipHor: bool = False, draw_function: RLEFunc = rle_normal, draw_info: T | None = None) -> PILImage.Image:
	if bounds:
		image = list(line[bounds.x_min:bounds.x_max] for line in image[bounds.y_min:bounds.y_max])
	width = len(image[0])
	height = len(image)
	i = PILImage.new('RGBA', (width,height))
	pal = [draw_function(palette,index,draw_info) for index in range(len(palette))]
	if transindex is not None:
		pal[transindex] = (0,0,0,0)
	pixels: list[int] = []
	if flipHor:
		for row in image:
			pixels.extend(reversed(row))
	else:
		for row in image:
			pixels.extend(row)
	data = list(map(pal.__getitem__, pixels))
	i.putdata(data) # type: ignore[arg-type]
	return i

# Returns the pixels for frame `f` of the source, and the effective
# transparent index (a GRP knows its own transindex, overriding the caller's)
def frame_pixels(g: GRP | CacheGRP | BMP | PCX | Pixels, f: int | None = None, transindex: int = 0) -> tuple[Pixels, int]:
	if isinstance(g, CacheGRP):
		return (g[f or 0], transindex)
	if isinstance(g, GRP):
		return (g.images[f or 0], g.transindex)
	if isinstance(g, (BMP, PCX)):
		return (g.image, transindex)
	return (g, transindex)

def frame_to_photo(p: RawPalette, g: GRP | CacheGRP | BMP | PCX | Pixels, f: int | None = None, *, transindex: int = 0, flipHor: bool = False, draw_function: RLEFunc = rle_normal, draw_info: T | None = None) -> ImageTk.PhotoImage:
	image, transindex = frame_pixels(g, f, transindex)
	pil = image_to_pil(image, p, transindex=transindex, flipHor=flipHor, draw_function=draw_function, draw_info=draw_info)
	return ImageTk.PhotoImage(pil)

class RLE:
	TRANSPARENT_FLAG = (1 << 7)
	TRANSPARENT_MAX_LENGTH = TRANSPARENT_FLAG - 1
	REPEAT_FLAG = (1 << 6)
	REPEAT_MAX_LENGTH = REPEAT_FLAG - 1
	STATIC_MAX_LENGTH = REPEAT_FLAG - 1

	@staticmethod
	def encode_transparent(count: int) -> bytes:
		encoded = bytearray()
		while count > 0:
			encoded += struct.pack('<B', RLE.TRANSPARENT_FLAG | min(RLE.TRANSPARENT_MAX_LENGTH, count))
			count -= RLE.TRANSPARENT_MAX_LENGTH
		return bytes(encoded)

	@staticmethod
	def encode_repeat(index: int, count: int) -> bytes:
		encoded = bytearray()
		while count > 0:
			encoded += struct.pack('<BB', RLE.REPEAT_FLAG | min(RLE.REPEAT_MAX_LENGTH, count), index)
			count -= RLE.REPEAT_MAX_LENGTH
		return bytes(encoded)

	@staticmethod
	def encode_static(line: Sequence[int]) -> bytes:
		encoded = bytearray()
		for x in range(0, len(line), RLE.STATIC_MAX_LENGTH):
			run = line[x:x+RLE.STATIC_MAX_LENGTH]
			encoded += struct.pack(f'<{1 + len(run)}B', len(run), *run)
		return bytes(encoded)

	@staticmethod
	def compress_line(line: Sequence[int], transparent_index: int) -> bytes:
		last_index = line[0]
		repeat_count = 0
		static_len = 0
		compressed = bytearray()
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
		return bytes(compressed)

	@staticmethod
	def decompress_line(data: bytes, width: int, transparent_index: int = 0) -> list[int]:
		line: list[int] = []
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
	def __init__(self, palette: RawPalette | None = None) -> None:
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette or [(0,0,0)]*256
		self.imagebuffer: list[tuple[Bounds, tuple[int, ...]]] = []
		self.images: dict[int, Pixels] = {}
		self.databuffer = b''
		self.uncompressed: bool | None = None

	def load(self, any_input: IO.AnyInputBytes, palette: RawPalette | None = None, restrict: int | None = None, uncompressed: bool | None = None) -> None:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		try:
			frames, width, height = struct.unpack('<3H',data[:6])
			if frames < 1 or frames > 2400:
				raise PyMSError('Load', f'Invalid GRP file (expected between 1 and 2400 frames, got {frames})')
			if width < 1 or width > 256 or height < 1 or height > 256:
				raise PyMSError('Load', f'Invalid GRP file (expected size to be between 1x1 and 256x256, got {width}x{height})')
			if restrict:
				frames = restrict
			images: list[tuple[Bounds, tuple[int, ...]]] = []
			for frame in range(frames):
				xoffset, yoffset, linewidth, lines, framedata = tuple(int(v) for v in struct.unpack('<4BL', data[6+8*frame:14+8*frame]))
				line_offsets: list[int] = []
				for line in range(lines):
					line_offsets.append(framedata+struct.unpack('<H',data[framedata+2*line:framedata+2+2*line])[0])
				images.append((Bounds(x_min=xoffset, y_min=yoffset, x_max=xoffset + linewidth, y_max=yoffset + lines), tuple(line_offsets)))
		except PyMSError:
			raise
		except Exception as exc:
			raise PyMSError('Load', "Unsupported GRP file, could possibly be corrupt or an uncompressed GRP") from exc
		self.frames = frames
		self.width = width
		self.height = height
		if palette:
			self.palette = list(palette)
		self.imagebuffer = images
		self.images = {}
		self.databuffer = data
		self.uncompressed = uncompressed

	def save(self, output: IO.AnyOutputBytes) -> None:
		with IO.OutputBytes(output) as f:
			f.write(self.databuffer)

	def __getitem__(self, frame: int) -> Pixels:
		if frame in self.images:
			return self.images[frame]
		image: list[list[int]] = []
		bounds, offsets = self.imagebuffer[frame]
		xoffset = bounds.x_min
		linewidth = min(bounds.x_max, self.width) - xoffset
		image.extend([[0] * self.width for _ in range(bounds.y_min)])
		if not self.uncompressed:
			try:
				compressed_rows: list[list[int]] = []
				for offset in offsets:
					compressed_rows.append([0] * xoffset + RLE.decompress_line(self.databuffer[offset:], linewidth) + [0] * (self.width-linewidth-xoffset))
				image.extend(compressed_rows)
				if self.uncompressed is None:
					self.uncompressed = False
			except Exception as exc: # pylint: disable=broad-exception-caught
				if self.uncompressed is None:
					self.uncompressed = True
				else:
					raise PyMSError('Decompile', f'Could not decompile frame {frame}, GRP could be corrupt.') from exc
		if self.uncompressed:
			try:
				for offset in offsets:
					linedata = []
					if xoffset > 0:
						linedata = [0] * xoffset
					linedata.extend(self.databuffer[offset:offset+linewidth])
					image.append(linedata + [0] * (self.width-linewidth-xoffset))
			except Exception as exc:
				raise PyMSError('Decompile', f'Could not decompile frame {frame}, GRP could be corrupt.') from exc
		if len(image) < self.height:
			image.extend([[0] * self.width for _ in range(self.height - len(image))])
		self.images[frame] = image[:self.height]
		return self.images[frame]

class GRP:
	def __init__(self, palette: RawPalette | None = None, uncompressed: bool | None = None, transindex: int = 0) -> None:
		self.frames = 0
		self.width = 0
		self.height = 0
		self.palette = palette or [(0,0,0)]*256
		self.images: list[Pixels] = []
		self.images_bounds: list[Bounds] = []
		self.uncompressed = uncompressed
		self.transindex = transindex

	def load(self, any_input: IO.AnyInputBytes, palette: RawPalette | None = None, transindex: int = 0, uncompressed: bool | None = None) -> None:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		try:
			frames, width, height = tuple(int(v) for v in struct.unpack('<3H',data[:6]))
			if frames < 1 or frames > 2400:
				raise PyMSError('Load', f'Invalid GRP file (expected between 1 and 2400 frames, got {frames})')
			if width < 1 or width > 256 or height < 1 or height > 256:
				raise PyMSError('Load', f'Invalid GRP file (expected size to be between 1x1 and 256x256, got {width}x{height})')
			retries = 2
			while retries:
				retries -= 1
				images: list[Pixels] = []
				images_bounds: list[Bounds] = []
				for frame in range(frames):
					image: list[list[int]] = []
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
						except Exception:
							if uncompressed is None:
								uncompressed = True
								break
							raise
					if len(image) < height:
						image.extend([[transindex] * width for _ in range(height - len(image))])
					images.append(image[:height])
					images_bounds.append(Bounds(x_min=xoffset, y_min=yoffset, x_max=xoffset + linewidth, y_max=yoffset + lines))
		except PyMSError:
			raise
		except Exception as exc:
			raise PyMSError('Load', "Unsupported GRP file, could possibly be corrupt") from exc
		self.frames = frames
		self.width = width
		self.height = height
		self.uncompressed = uncompressed
		if palette:
			self.palette = list(palette)
		self.images = images
		self.images_bounds = images_bounds
		self.transindex = transindex

	def load_frames(self, frames: list[Pixels], palette: RawPalette | None = None, transindex: int = 0, validate: bool = True) -> None:
		if not frames:
			raise PyMSError('GRP', 'Attempting to load GRP data with no frames')
		self.frames = len(frames)
		height = len(frames[0])
		width = len(frames[0][0])
		if validate:
			for (n, frame) in enumerate(frames, 1):
				frame_height = len(frame)
				if frame_height != height:
					raise PyMSError('GRP', f'Frame {n} has unexpected height (got {frame_height}, expected {height})')
				for (y, line) in enumerate(frame):
					line_width = len(line)
					if line_width != width:
						raise PyMSError('GRP', f'Frame {n} line {y} has unexpected width (got {line_width}, expected {width})')
		self.height = height
		self.width = width
		if palette:
			self.palette = list(palette)
		self.images = deepcopy(frames)
		self.images_bounds = [image_bounds(frame, transindex) for frame in frames]
		self.transindex = transindex

	def add_frame(self, frame: Pixels, validate: bool = True) -> None:
		if validate and self.images:
			frame_index = len(self.images)
			frame_height = len(frame)
			if frame_height != self.height:
				raise PyMSError('GRP', f'Adding frame {frame_index} has unexpected height (got {frame_height}, expected {self.height})')
			for (y, line) in enumerate(frame):
				line_width = len(line)
				if line_width != self.width:
					raise PyMSError('GRP', f'Adding frame {frame_index} line {y} has unexpected width (got {line_width}, expected {self.width})')
		self.frames += 1
		self.images.append(deepcopy(frame))
		self.images_bounds.append(image_bounds(frame, self.transindex))

	def add_frames(self, image: Pixels, frames: int, vertical: bool = True) -> None:
		if not image:
			raise PyMSError('GRP', 'Adding frames has empty buffer')
		width = len(image[0])
		height = len(image)
		if vertical:
			height //= frames
		else:
			width //= min(frames,17)
			height //= int(math.ceil(frames / 17.0))
		if width > 256 or height > 256:
			raise PyMSError('Load', f'Invalid dimensions in the image (Frames have a maximum size of 256x256, got {width}x{height})')
		if self.frames and (width != self.width or height != self.height):
			raise PyMSError('Load', f'Invalid dimensions in the image (Expected {self.width}x{self.height}, got {width}x{height})')
		for n in range(frames):
			frame = []
			for y in range(height):
				if vertical:
					frame.append(image[n * height + y])
				else:
					x = (n % 17) * width
					frame.append(image[(n // 17) * height + y][x:x+width])
			self.add_frame(frame)

	def save(self, output: IO.AnyOutputBytes, uncompressed: bool | None = None) -> None:
		if uncompressed is None:
			uncompressed = self.uncompressed
		header_data = struct.pack('<3H', self.frames, self.width, self.height)
		image_data = b''
		offset = 6 + 8 * self.frames
		frame_history: dict[bytes | tuple[Bounds, tuple[tuple[int, ...], ...]], bytes] = {}
		for z,frame in enumerate(self.images):
			bounds = self.images_bounds[z]
			if uncompressed:
				data = bytes(p for row in frame[bounds.y_min:bounds.y_max] for p in row[bounds.x_min:bounds.x_max])
				if data in frame_history:
					header_data += frame_history[data]
				else:
					frame_data = struct.pack('<4BL', bounds.x_min, bounds.y_min, bounds.width, bounds.height, offset)
					header_data += frame_data
					frame_history[data] = frame_data
					image_data += data
					offset += len(data)
			else:
				frame_hash = (bounds, tuple(tuple(l[bounds.x_min:bounds.x_max]) for l in frame[bounds.y_min:bounds.y_max]))
				# If there is a duplicate frame, just point to it
				if frame_hash in frame_history:
					header_data += frame_history[frame_hash]
				else:
					frame_data = struct.pack('<4BL', bounds.x_min, bounds.y_min, bounds.width, bounds.height, offset)
					frame_history[frame_hash] = frame_data
					header_data += frame_data
					line_data = b''
					line_offset = 2 * bounds.height
					line_offsets: list[bytes] = []
					line_history: dict[tuple[int, ...], bytes] = {}
					for _y,line in enumerate(frame[bounds.y_min:bounds.y_max]):
						line_hash = tuple(line)
						# If there is a duplicate line is this frame, just point to it
						if line_hash in line_history:
							line_offsets.append(line_history[line_hash])
						else:
							data = RLE.compress_line(line[bounds.x_min:bounds.x_max], self.transindex)
							line_data += data
							if line_offset > 65535:
								raise PyMSError('Save', 'The image has too much pixel data to compile')
							line_offsets.append(struct.pack('<H', line_offset))
							line_history[line_hash] = line_offsets[-1]
							line_offset += len(data)
					line_data = b''.join(line_offsets) + line_data
					image_data += line_data
					offset += len(line_data)
		with IO.OutputBytes(output) as f:
			f.write(header_data + image_data)
