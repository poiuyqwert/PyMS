
from __future__ import annotations

from ..FileFormats import GRP
from ..FileFormats import BMP
from ..FileFormats import Palette

from ..Utilities.PyMSError import PyMSError

import os, re
from math import ceil
from enum import Enum

from typing import Sequence

class BMPStyle(Enum):
	bmp_per_frame = 'bmp_per_frame'
	single_bmp_framesets = 'single_bmp_framesets'
	single_bmp_vertical = 'single_bmp_vertical'

	@staticmethod
	def ALL() -> tuple[BMPStyle, ...]:
		return (
			BMPStyle.bmp_per_frame,
			BMPStyle.single_bmp_framesets,
			BMPStyle.single_bmp_vertical
		)

	@property
	def display_name(self) -> str:
		match self:
			case BMPStyle.bmp_per_frame:
				return 'One BMP per Frame'
			case BMPStyle.single_bmp_framesets:
				return 'Single BMP (Framesets)'
			case BMPStyle.single_bmp_vertical:
				return 'Single BMP (Vertical/SFGrpConv)'

	@property
	def index(self) -> int:
		match self:
			case BMPStyle.bmp_per_frame:
				return 0
			case BMPStyle.single_bmp_framesets:
				return 1
			case BMPStyle.single_bmp_vertical:
				return 2

	@staticmethod
	def from_index(index: int) -> BMPStyle:
		if index == 0:
			return BMPStyle.bmp_per_frame
		elif index == 2:
			return BMPStyle.single_bmp_vertical
		return BMPStyle.single_bmp_framesets

	@property
	def is_vertical(self) -> bool:
		match self:
			case BMPStyle.bmp_per_frame:
				return False
			case BMPStyle.single_bmp_framesets:
				return True
			case BMPStyle.single_bmp_vertical:
				return True

# TODO: Improve
def grptobmp(path: str, pal: Palette.Palette, uncompressed: bool, bmp_style: BMPStyle, grp: str | GRP.GRP, bmp: str | None = None, frames: Sequence[int] | None = None, mute: bool = False) -> None:
	if isinstance(grp, str):
		inp = GRP.GRP(pal.palette, uncompressed)
		if not mute:
			print(f"Reading GRP '{grp}'...")
		inp.load_file(grp)
		if not mute:
			print(f" - '{grp}' read successfully")
	else:
		inp = grp
	if bmp:
		bmpname = bmp
	elif isinstance(grp, str):
		bmpname = os.path.join(path,os.extsep.join(os.path.basename(grp).split(os.extsep)[:-1]))
	else:
		raise PyMSError('Internal', 'No bmp name provided')
	out = BMP.BMP(pal.palette)
	if frames is None:
		frames = list(range(inp.frames))
	n = 0
	for f,frame in enumerate(inp.images):
		if f in frames:
			if bmp_style == BMPStyle.single_bmp_framesets:
				if not n % 17:
					out.image.extend([list(y) for y in frame])
				else:
					for y,d in enumerate(frame):
						out.image[(n // 17) * inp.height + y].extend(d)
			elif bmp_style == BMPStyle.single_bmp_vertical:
				out.image.extend([list(y) for y in frame])
			else:
				name = f'{bmpname} {str(n).zfill(3)}{os.extsep}bmp'
				if not mute:
					print(f"Writing BMP '{name}'...")
				out.set_pixels(frame)
				out.save_file(os.path.join(path,name))
				if not mute:
					print(f" - '{name}' written succesfully")
			n += 1
	if bmp_style != BMPStyle.bmp_per_frame:
		if bmp_style == BMPStyle.single_bmp_framesets and len(frames) % 17 and len(frames) // 17:
			for y in range(inp.height):
				out.image[-y-1].extend([inp.transindex] * inp.width * (17 - len(frames) % 17))
		out.height = len(out.image)
		out.width = len(out.image[0])
		name = f'{bmpname}{os.extsep}bmp'
		out.save_file(os.path.join(path,name))
		if not mute:
			print(f" - '{name}' written succesfully")

# TODO: Improve
def bmptogrp(path: str, pal: Palette.Palette, uncompressed: bool, frames: int, bmp: str | list[str], grp: str | None = None, issize: tuple[int,int] | None = None, ret=False, mute=False, vertical=False, transindex=0) -> (GRP.GRP | None):
	out = GRP.GRP(pal.palette, uncompressed, transindex)
	inp = BMP.BMP()
	if frames:
		assert isinstance(bmp, str)
		fullfile = os.path.join(path,bmp)
		if not mute:
			print(f"Reading BMP '{fullfile}'...")
		inp.load_file(fullfile)
		if vertical:
			out.width = inp.width
			out.height = inp.height // frames
		else:
			out.width = inp.width // min(frames,17)
			out.height = inp.height // int(ceil(frames / 17.0))
		if out.width > 256 or out.height > 256:
			raise PyMSError('Load', f"Invalid dimensions in the BMP '{fullfile}' (Frames have a maximum size of 256x256, got {out.width}x{out.height})")
		if issize and out.width != issize[0] and out.height != issize[1]:
			raise PyMSError('Load', f"Invalid dimensions in the BMP '{fullfile}' (Expected {issize[0]}x{issize[1]}, got {out.width}x{out.height})")
		image = []
		for n in range(frames):
			for y in range(out.height):
				if vertical:
					image.append(inp.image[n * out.height + y])
				else:
					x = (n % 17) * out.width
					image.append(inp.image[(n // 17) * out.height + y][x:x+out.width])
		out.add_frame(image)
		if not mute:
			print(f" - '{fullfile}' read successfully")
		if ret:
			return out
	else:
		if isinstance(bmp, (tuple, list)):
			files = bmp
			found = 2
			single = False
		else:
			file = os.path.basename(bmp)
			t = os.extsep.join(file.split(os.extsep)[:-1])
			m = re.match('(.+) (.+?)',t)
			single = not m
			if not m:
				name = t
			else:
				name = m.group(1)
			found = 0
			files = os.listdir(path)
			files.sort()
		for f in files:
			if found or f == file:
				if found > 1 or (f.startswith(name) and len(f) > len(name)+2):
					fullfile = os.path.join(path,f)
					if not mute:
						print(f"Reading BMP '{fullfile}'...")
					inp.load_file(fullfile)
					if found % 2:
						if issize and inp.width != issize[0] and inp.height != issize[1]:
							raise PyMSError('Load', f"Invalid dimensions in the BMP '{fullfile}' (Expected {issize[0]}x{issize[1]}, got {inp.width}x{inp.height})")
						if inp.width != out.width or inp.height != out.height:
							raise PyMSError('Input', f"Incorrect frame dimensions in BMP '{fullfile}' (Expected {out.width}x{out.height}, got {inp.width}x{inp.height})")
						out.add_frame(inp.image)
					else:
						if issize and inp.width != issize[0] and inp.height != issize[1]:
							raise PyMSError('Load', f"Invalid dimensions in the BMP '{fullfile}' (Expected {issize[0]}x{issize[1]}, got {inp.width}x{inp.height})")
						if inp.width > 256 or inp.height > 256:
							raise PyMSError('Load', f"Invalid dimensions in the BMP '{fullfile}' (Frames have a maximum size of 256x256, got {inp.width}x{inp.height})")
						out.load_data([inp.image])
						found += 1
					if not mute:
						print(f" - '{fullfile}' read successfully")
					if single:
						break
				else:
					break
		if not found:
			raise PyMSError('Input', f"Could not find files matching format '{name} <frame>.bmp'")
		if ret:
			return out
	if grp:
		fullfile = os.path.join(path,grp)
	else:
		fullfile = os.path.join(path, f'{name}{os.extsep}grp')
	if not mute:
		print(f"Writing GRP '{fullfile}'...")
	out.save_file(fullfile)
	if not mute:
		print(f" - '{fullfile}' written successfully")
	return None
