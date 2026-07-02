
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

FRAMESET_ROW_SIZE = 17

def frames_to_sheet(frames: Sequence[GRP.Pixels], style: BMPStyle, transindex: int) -> GRP.Pixels:
	if not frames:
		raise PyMSError('Internal', 'No frames to combine into a sheet')
	sheet: GRP.Pixels = []
	match style:
		case BMPStyle.bmp_per_frame:
			raise PyMSError('Internal', 'Frames can not be combined into a sheet for one BMP per frame')
		case BMPStyle.single_bmp_framesets:
			frame_height = len(frames[0])
			frame_width = len(frames[0][0])
			for n,frame in enumerate(frames):
				if not n % FRAMESET_ROW_SIZE:
					sheet.extend(list(row) for row in frame)
				else:
					for y,row in enumerate(frame):
						sheet[(n // FRAMESET_ROW_SIZE) * frame_height + y].extend(row)
			if len(frames) % FRAMESET_ROW_SIZE and len(frames) // FRAMESET_ROW_SIZE:
				padding = [transindex] * frame_width * (FRAMESET_ROW_SIZE - len(frames) % FRAMESET_ROW_SIZE)
				for y in range(frame_height):
					sheet[-y-1].extend(padding)
		case BMPStyle.single_bmp_vertical:
			for frame in frames:
				sheet.extend(list(row) for row in frame)
	return sheet

def sheet_frame_size(sheet_width: int, sheet_height: int, frame_count: int, style: BMPStyle) -> tuple[int, int]:
	match style:
		case BMPStyle.bmp_per_frame:
			raise PyMSError('Internal', 'A sheet can not be split into frames for one BMP per frame')
		case BMPStyle.single_bmp_framesets:
			return (sheet_width // min(frame_count, FRAMESET_ROW_SIZE), sheet_height // int(ceil(frame_count / FRAMESET_ROW_SIZE)))
		case BMPStyle.single_bmp_vertical:
			return (sheet_width, sheet_height // frame_count)

def sheet_to_frames(sheet: GRP.Pixels, frame_count: int, style: BMPStyle) -> list[GRP.Pixels]:
	frame_width,frame_height = sheet_frame_size(len(sheet[0]), len(sheet), frame_count, style)
	frames: list[GRP.Pixels] = []
	for n in range(frame_count):
		frame: GRP.Pixels = []
		for y in range(frame_height):
			if style == BMPStyle.single_bmp_vertical:
				frame.append(list(sheet[n * frame_height + y]))
			else:
				x = (n % FRAMESET_ROW_SIZE) * frame_width
				frame.append(list(sheet[(n // FRAMESET_ROW_SIZE) * frame_height + y][x:x+frame_width]))
		frames.append(frame)
	return frames

def frame_bmp_name(basename: str, frame: int) -> str:
	return f'{basename} {str(frame).zfill(3)}{os.extsep}bmp'

def grp_to_bmps(grp: GRP.GRP, palette: GRP.RawPalette, style: BMPStyle, frame_indices: Sequence[int] | None = None) -> list[BMP.BMP]:
	if frame_indices is None:
		frames = list(grp.images)
	else:
		include = frozenset(frame_indices)
		frames = [frame for f,frame in enumerate(grp.images) if f in include]
	bmps: list[BMP.BMP] = []
	if style == BMPStyle.bmp_per_frame:
		for frame in frames:
			bmp = BMP.BMP(palette)
			bmp.set_pixels(frame)
			bmps.append(bmp)
	else:
		bmp = BMP.BMP(palette)
		bmp.set_pixels(frames_to_sheet(frames, style, grp.transindex))
		bmps.append(bmp)
	return bmps

def check_frame_bmp(bmp: BMP.BMP, filename: str, expected_size: tuple[int, int] | None, issize: tuple[int, int] | None) -> None:
	if issize and (bmp.width != issize[0] or bmp.height != issize[1]):
		raise PyMSError('Load', f"Invalid dimensions in the BMP '{filename}' (Expected {issize[0]}x{issize[1]}, got {bmp.width}x{bmp.height})")
	if expected_size is None:
		if bmp.width > 256 or bmp.height > 256:
			raise PyMSError('Load', f"Invalid dimensions in the BMP '{filename}' (Frames have a maximum size of 256x256, got {bmp.width}x{bmp.height})")
	elif bmp.width != expected_size[0] or bmp.height != expected_size[1]:
		raise PyMSError('Input', f"Incorrect frame dimensions in BMP '{filename}' (Expected {expected_size[0]}x{expected_size[1]}, got {bmp.width}x{bmp.height})")

def bmp_sheet_to_frames(bmp: BMP.BMP, frame_count: int, style: BMPStyle, filename: str, issize: tuple[int, int] | None = None) -> list[GRP.Pixels]:
	frame_width,frame_height = sheet_frame_size(bmp.width, bmp.height, frame_count, style)
	if frame_width > 256 or frame_height > 256:
		raise PyMSError('Load', f"Invalid dimensions in the BMP '{filename}' (Frames have a maximum size of 256x256, got {frame_width}x{frame_height})")
	if issize and (frame_width != issize[0] or frame_height != issize[1]):
		raise PyMSError('Load', f"Invalid dimensions in the BMP '{filename}' (Expected {issize[0]}x{issize[1]}, got {frame_width}x{frame_height})")
	return sheet_to_frames(bmp.image, frame_count, style)

def frames_to_grp(frames: list[GRP.Pixels], palette: GRP.RawPalette, uncompressed: bool, transindex: int = 0) -> GRP.GRP:
	grp = GRP.GRP(palette, uncompressed, transindex)
	grp.load_frames(frames, transindex=transindex)
	return grp

def find_frame_bmps(path: str, first_file: str) -> tuple[str, list[str]]:
	file = os.path.basename(first_file)
	stem = os.extsep.join(file.split(os.extsep)[:-1])
	m = re.match('(.+) (.+?)', stem)
	single = not m
	name = m.group(1) if m else stem
	files: list[str] = []
	listing = os.listdir(path)
	listing.sort()
	started = False
	for f in listing:
		if not started:
			if f != file:
				continue
			started = True
		if not (f.startswith(name) and len(f) > len(name)+2):
			break
		files.append(f)
		if single:
			break
	return (name, files)

def grptobmp(*, path: str, pal: Palette.Palette, uncompressed: bool, bmp_style: BMPStyle, grp: str, bmp: str | None = None) -> None:
	inp = GRP.GRP(pal.palette, uncompressed)
	print(f"Reading GRP '{grp}'...")
	inp.load(grp)
	print(f" - '{grp}' read successfully")
	if bmp:
		bmpname = bmp
	else:
		bmpname = os.path.join(path,os.extsep.join(os.path.basename(grp).split(os.extsep)[:-1]))
	bmps = grp_to_bmps(inp, pal.palette, bmp_style)
	if bmp_style == BMPStyle.bmp_per_frame:
		for n,out in enumerate(bmps):
			name = frame_bmp_name(bmpname, n)
			print(f"Writing BMP '{name}'...")
			out.save(os.path.join(path,name))
			print(f" - '{name}' written succesfully")
	else:
		name = f'{bmpname}{os.extsep}bmp'
		bmps[0].save(os.path.join(path,name))
		print(f" - '{name}' written succesfully")

def bmptogrp(*, path: str, pal: Palette.Palette, uncompressed: bool, frames: int, bmp: str, grp: str | None = None) -> None:
	if frames:
		name = os.extsep.join(os.path.basename(bmp).split(os.extsep)[:-1])
		fullfile = os.path.join(path,bmp)
		print(f"Reading BMP '{fullfile}'...")
		inp = BMP.BMP()
		inp.load(fullfile)
		frame_images = bmp_sheet_to_frames(inp, frames, BMPStyle.single_bmp_framesets, fullfile)
		out = frames_to_grp(frame_images, pal.palette, uncompressed)
		print(f" - '{fullfile}' read successfully")
	else:
		name, files = find_frame_bmps(path, bmp)
		if not files:
			raise PyMSError('Input', f"Could not find files matching format '{name} <frame>.bmp'")
		frame_images = []
		expected_size: tuple[int, int] | None = None
		for f in files:
			fullfile = os.path.join(path,f)
			print(f"Reading BMP '{fullfile}'...")
			inp = BMP.BMP()
			inp.load(fullfile)
			check_frame_bmp(inp, fullfile, expected_size, None)
			if expected_size is None:
				expected_size = (inp.width, inp.height)
			frame_images.append(inp.image)
			print(f" - '{fullfile}' read successfully")
		out = frames_to_grp(frame_images, pal.palette, uncompressed)
	if grp:
		fullfile = os.path.join(path,grp)
	else:
		fullfile = os.path.join(path, f'{name}{os.extsep}grp')
	print(f"Writing GRP '{fullfile}'...")
	out.save(fullfile)
	print(f" - '{fullfile}' written successfully")
