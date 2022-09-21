
from ..FileFormats.PCX import PCX
from ..FileFormats.BMP import BMP

from ..Utilities.PyMSError import PyMSError
from ..Utilities.fileutils import load_file
from ..Utilities.AtomicWriter import AtomicWriter
from ..Utilities.FileType import FileType

import struct

class Palette:
	class Format:
		riff     = "riff"
		jasc     = "jasc"
		raw_rgb  = "raw_rgb" # SC .pal, .act
		raw_rgba = "raw_rgba" # .wpe

	class FileType:
		# Values intialized at end of file (need to refer to Palette type)
		riff = None
		jasc = None
		sc_pal = None
		wpe = None
		act = None

		@staticmethod
		def load_types():
			load_types = [
				FileType.pal(),
				FileType.wpe(),
				FileType.act(),
				FileType.pcx(),
				FileType.bmp()
			]
			return tuple(load_types)

		@staticmethod
		def save_types(format, ext):
			save_types_lookup = {
				Palette.Format.riff: {
					None: [FileType.pal_riff()]
				},
				Palette.Format.jasc: {
					None: [FileType.pal_jasc()]
				},
				Palette.Format.raw_rgb: {
					None: [FileType.pal_sc(),FileType.act()],
					Palette.FileType.sc_pal.ext: [FileType.pal_sc()],
					Palette.FileType.act.ext: [FileType.act()]
				},
				Palette.Format.raw_rgba: {
					None: [FileType.wpe()]
				}
			}
			save_types_format = save_types_lookup.get(format)
			if not save_types_format:
				raise PyMSError('Palette',"Unsupported save format '%s'" % format)
			save_types = save_types_format.get(ext, save_types_format.get(None))
			return tuple(save_types)

		def __init__(self, format, ext):
			self.format = format
			self.ext = ext

	def __init__(self):
		self.palette = [[0,0,0] for _ in range(256)]
		self.format = None

	def load_riff_pal(self, data):
		# TODO: Better parsing, specs here: https://worms2d.info/Palette_file
		if len(data) != 1048 or not data.startswith('RIFF\x00\x00\x00\x00PAL data'):
			raise PyMSError('Palette',"Unsupported RIFF palette file, could possibly be corrupt")
		return self.load_sc_pal(data[24:], 4)

	def load_jasc_pal(self, data):
		data = data.split('\r\n')
		if not data[-1]:
			data.pop()
		if len(data) != 259 or data[0] != 'JASC-PAL' or data[1] != '0100' or data[2] != '256':
			raise PyMSError('Palette',"Unsupported JASC palette file, could possibly be corrupt")
		return [[int(c) for c in line.split(' ')] for line in data[3:]]

	def load_zsoft_pcx(self, data):
		pcx = PCX()
		try:
			pcx.load_data(data)
		except:
			raise PyMSError('Palette',"Unsupported PCX palette file, could possibly be corrupt")
		return pcx.palette

	def load_bmp(self, data):
		bmp = BMP()
		try:
			bmp.load_data(data)
		except:
			raise PyMSError('Palette',"Unsupported BMP palette file, could possibly be corrupt")
		return bmp.palette

	def load_sc_wpe(self, data):
		return self.load_sc_pal(data, 4)

	def load_sc_pal(self, data, components=3):
		size = 256 * components
		if len(data) != size:
			raise PyMSError('Palette',"Unsupported PAL palette file, could possibly be corrupt")
		palette = []
		for x in range(0,size,components):
			palette.append(list(struct.unpack('3B', data[x:x + 3])))
		return palette

	def load_file(self, path):
		data = load_file(path, 'palette')
		formats = (
			(Palette.Format.riff, self.load_riff_pal),
			(Palette.Format.jasc, self.load_jasc_pal),
			(None, self.load_zsoft_pcx),
			(None, self.load_bmp),
			# Need to try raw formats last as they have no identifying parts other than their data length
			(Palette.Format.raw_rgba, self.load_sc_wpe),
			(Palette.Format.raw_rgb, self.load_sc_pal)
		)
		for format,load_method in formats:
			try:
				palette = load_method(data)
				if len(palette) == 256:
					self.format = format
					break
			except:
				pass
		else:
			raise PyMSError('Palette',"Unsupported palette file '%s', could possibly be corrupt" % path)
		self.palette = palette

	def load_data(self, palette):
		self.palette = palette

	def save_riff_pal(self, path):
		try:
			f = AtomicWriter(path,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % path)
		f.write('RIFF\x00\x00\x00\x00PAL data\x04\x04\x00\x00\x00\x03\x00\x01')
		for c in self.palette:
			f.write(struct.pack('3Bx',*c))
		f.close()

	def save_jasc_pal(self, path):
		try:
			f = AtomicWriter(path,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % path)
		f.write('JASC-PAL\r\n0100\r\n256\r\n')
		for color in self.palette:
			f.write(' '.join(str(c) for c in color) + '\r\n')
		f.close()

	def save_sc_wpe(self, path):
		try:
			f = AtomicWriter(path,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % path)
		for c in self.palette:
			f.write(struct.pack('3Bx',*c))
		f.close()

	def save_sc_pal(self, path):
		try:
			f = AtomicWriter(path,'wb')
		except:
			raise PyMSError('Palette',"Could not save palette to file '%s'" % path)
		for c in self.palette:
			f.write(struct.pack('3B',*c))
		f.close()

	def save(self, path, format):
		formats = {
			Palette.Format.riff: self.save_riff_pal,
			Palette.Format.jasc: self.save_jasc_pal,
			Palette.Format.raw_rgba: self.save_sc_wpe,
			Palette.Format.raw_rgb: self.save_sc_pal
		}
		save_method = formats.get(format)
		if not save_method:
			raise PyMSError('Palette',"Unsupported save format '%s'" % format)
		save_method(path)

Palette.FileType.riff = Palette.FileType(Palette.Format.riff, 'pal')
Palette.FileType.jasc = Palette.FileType(Palette.Format.jasc, 'pal')
Palette.FileType.sc_pal = Palette.FileType(Palette.Format.raw_rgb, 'pal')
Palette.FileType.wpe = Palette.FileType(Palette.Format.raw_rgba, 'wpe')
Palette.FileType.act = Palette.FileType(Palette.Format.raw_rgb, 'act')