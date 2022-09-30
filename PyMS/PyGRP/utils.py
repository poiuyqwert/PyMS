
from ..FileFormats import GRP
from ..FileFormats import BMP

from ..Utilities.utils import isstr
from ..Utilities.PyMSError import PyMSError

import os, re
from math import ceil

def grptobmp(path, pal, uncompressed, onebmp, grp, bmp='', frames=None, mute=False):
	if isstr(grp):
		inp = GRP.GRP(pal.palette, uncompressed)
		if not mute:
			print("Reading GRP '%s'..." % grp)
		inp.load_file(grp)
		if not mute:
			print(" - '%s' read successfully" % grp)
	else:
		inp = grp
	if bmp:
		bmpname = bmp
	else:
		bmpname = os.path.join(path,os.extsep.join(os.path.basename(grp).split(os.extsep)[:-1]))
	out = BMP.BMP(pal.palette)
	if frames == None:
		frames = range(inp.frames)
	n = 0
	for f,frame in enumerate(inp.images):
		if f in frames:
			if onebmp == 1:
				if not n % 17:
					out.image.extend([list(y) for y in frame])
				else:
					for y,d in enumerate(frame):
						out.image[(n / 17) * inp.height + y].extend(d)
			elif onebmp == 2:
				out.image.extend([list(y) for y in frame])
			else:
				name = '%s %s%sbmp' % (bmpname, str(n).zfill(3), os.extsep)
				if not mute:
					print("Writing BMP '%s'..." % name)
				out.set_pixels(frame)
				out.save_file(os.path.join(path,name))
				if not mute:
					print(" - '%s' written succesfully" % name)
			n += 1
	if onebmp:
		if onebmp == 1 and len(frames) % 17 and len(frames) / 17:
			for y in range(inp.height):
				out.image[-y-1].extend([inp.transindex] * inp.width * (17 - len(frames) % 17))
		out.height = len(out.image)
		out.width = len(out.image[0])
		name = '%s%sbmp' % (bmpname, os.extsep)
		out.save_file(os.path.join(path,name))
		if not mute:
			print(" - '%s' written succesfully" % name)

def bmptogrp(path, pal, uncompressed, frames, bmp, grp='', issize=None, ret=False, mute=False, vertical=False, transindex=0):
	out = GRP.GRP(pal.palette, uncompressed, transindex)
	inp = BMP.BMP()
	try:
		if frames:
			fullfile = os.path.join(path,bmp)
			if not mute:
				print("Reading BMP '%s'..." % fullfile)
			inp.load_file(fullfile)
			out.frames = frames
			if vertical:
				out.width = inp.width
				out.height = inp.height / frames
			else:
				out.width = inp.width / min(frames,17)
				out.height = inp.height / int(ceil(frames / 17.0))
			if out.width > 256 or out.height > 256:
				raise PyMSError('Load', "Invalid dimensions in the BMP '%s' (Frames have a maximum size of 256x256, got %sx%s)" % (fullfile,out.width,out.height))
			if issize and out.width != issize[0] and out.height != issize[1]:
				raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],out.width,out.height))
			for n in range(frames):
				out.images.append([])
				for y in range(out.height):
					if vertical:
						out.images[-1].append(inp.image[n * out.height + y])
					else:
						x = (n % 17) * out.width
						out.images[-1].append(inp.image[(n / 17) * out.height + y][x:x+out.width])
				out.images_bounds.append(GRP.image_bounds(out.images[-1]))
			if not mute:
				print(" - '%s' read successfully" % fullfile)
			if ret:
				return out
		else:
			if isinstance(bmp, tuple) or isinstance(bmp, list):
				files = bmp
				found = 2
				single = False
			else:
				file = os.path.basename(bmp)
				t = os.extsep.join(file.split(os.extsep)[:-1])
				m = re.match('(.+) (.+?)',t)
				single = not m
				if single:
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
							print("Reading BMP '%s'..." % fullfile)
						inp.load_file(fullfile)
						if found % 2:
							if issize and inp.width != issize[0] and inp.height != issize[1]:
								raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],inp.width,inp.height))
							if inp.width != out.width or inp.height != out.height:
								raise PyMSError('Input',"Incorrect frame dimensions in BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,out.width,out.height,inp.width,inp.height))
							out.frames += 1
							out.images.append(inp.image)
							out.images_bounds.append(GRP.image_bounds(out.images[-1]))
						else:
							if issize and inp.width != issize[0] and inp.height != issize[1]:
								raise PyMSError('Load',"Invalid dimensions in the BMP '%s' (Expected %sx%s, got %sx%s)" % (fullfile,issize[0],issize[1],inp.width,inp.height))
							if inp.width > 256 or inp.height > 256:
								raise PyMSError('Load', "Invalid dimensions in the BMP '%s' (Frames have a maximum size of 256x256, got %sx%s)" % (fullfile,inp.width,inp.height))
							out.load_data([inp.image])
							found += 1
						if not mute:
							print(" - '%s' read successfully" % fullfile)
						if single:
							break
					else:
						break
			if not found:
				raise PyMSError('Input',"Could not find files matching format '%s <frame>.bmp'" % name)
			if ret:
				return out
	except PyMSError:
		raise
	else:
		if grp:
			fullfile = os.path.join(path,grp)
		else:
			fullfile = os.path.join(path,'%s%sgrp' % (name, os.extsep))
		if not mute:
			print("Writing GRP '%s'..." % fullfile)
		out.save_file(fullfile)
		if not mute:
			print(" - '%s' written successfully" % fullfile)
