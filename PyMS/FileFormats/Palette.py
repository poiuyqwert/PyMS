
from __future__ import annotations

from .Images import RawPalette
from .PCX import PCX
from .BMP import BMP

from ..Utilities.PyMSError import PyMSError
from ..Utilities import IO
from ..Utilities import UIKit # TODO: Note sure I like this referring to UIKit

import struct
from enum import Enum

class Palette:
	class Format(Enum):
		riff     = "riff"
		jasc     = "jasc"
		raw_rgb  = "raw_rgb" # SC .pal, .act
		raw_rgba = "raw_rgba" # .wpe

	class FileType:
		# Values intialized at end of file (need to refer to Palette type)
		riff: Palette.FileType
		jasc: Palette.FileType
		sc_pal: Palette.FileType
		wpe: Palette.FileType
		act: Palette.FileType

		@staticmethod
		def load_types() -> tuple[UIKit.FileType, ...]:
			load_types = [
				UIKit.FileType.pal(),
				UIKit.FileType.wpe(),
				UIKit.FileType.act(),
				UIKit.FileType.pcx(),
				UIKit.FileType.bmp()
			]
			return tuple(load_types)

		@staticmethod
		def save_types(pal_format: Palette.Format, ext: str | None) -> tuple[UIKit.FileType, ...]:
			save_types_lookup: dict[Palette.Format, dict[str | None, list[UIKit.FileType]]] = {
				Palette.Format.riff: {
					None: [UIKit.FileType.pal_riff()]
				},
				Palette.Format.jasc: {
					None: [UIKit.FileType.pal_jasc()]
				},
				Palette.Format.raw_rgb: {
					None: [UIKit.FileType.pal_sc(),UIKit.FileType.act()],
					Palette.FileType.sc_pal.ext: [UIKit.FileType.pal_sc()],
					Palette.FileType.act.ext: [UIKit.FileType.act()]
				},
				Palette.Format.raw_rgba: {
					None: [UIKit.FileType.wpe()]
				}
			}
			save_types_format = save_types_lookup.get(pal_format)
			if not save_types_format:
				raise PyMSError('Palette', f"Unsupported save format '{pal_format}'")
			save_types = save_types_format.get(ext, save_types_format[None])
			return tuple(save_types)

		def __init__(self, pal_format: Palette.Format, ext: str) -> None:
			self.format = pal_format
			self.ext = ext

	def __init__(self) -> None:
		self.palette: RawPalette = [(0,0,0)] * 256
		self.format: Palette.Format | None = None

	def load_riff_pal(self, any_input: IO.AnyInputBytes) -> RawPalette:
		# TODO: Better parsing, specs here: https://worms2d.info/Palette_file
		with IO.InputBytes(any_input) as f:
			data = f.read()
		if len(data) != 1048 or not data.startswith(b'RIFF\x00\x00\x00\x00PAL data'):
			raise PyMSError('Palette', "Unsupported RIFF palette file, could possibly be corrupt")
		return self.load_sc_pal(data[24:], 4)

	def load_jasc_pal(self, any_input: IO.AnyInputBytes) -> RawPalette:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		lines = data.decode('utf-8').split('\r\n')
		if not lines[-1]:
			lines.pop()
		if len(lines) != 259 or lines[0] != 'JASC-PAL' or lines[1] != '0100' or lines[2] != '256':
			raise PyMSError('Palette', "Unsupported JASC palette file, could possibly be corrupt")
		palette: RawPalette = []
		for line in lines[3:]:
			r,g,b = line.split(' ')
			palette.append((int(r),int(g),int(b)))
		return palette

	def load_zsoft_pcx(self, any_input: IO.AnyInputBytes) -> RawPalette:
		pcx = PCX()
		try:
			pcx.load(any_input)
		except Exception as exc:
			raise PyMSError('Palette', "Unsupported PCX palette file, could possibly be corrupt") from exc
		return pcx.palette

	def load_bmp(self, any_input: IO.AnyInputBytes) -> RawPalette:
		bmp = BMP()
		try:
			bmp.load(any_input)
		except Exception as exc:
			raise PyMSError('Palette', "Unsupported BMP palette file, could possibly be corrupt") from exc
		return bmp.palette

	def load_sc_wpe(self, any_input: IO.AnyInputBytes) -> RawPalette:
		return self.load_sc_pal(any_input, 4)

	def load_sc_pal(self, any_input: IO.AnyInputBytes, components: int = 3) -> RawPalette:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		size = 256 * components
		if len(data) != size:
			raise PyMSError('Palette', "Unsupported PAL palette file, could possibly be corrupt")
		palette: RawPalette = []
		for x in range(0,size,components):
			r,g,b = tuple(int(c) for c in struct.unpack('3B', data[x:x + 3]))
			palette.append((r,g,b))
		return palette

	def load(self, any_input: IO.AnyInputBytes) -> None:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		formats = (
			(Palette.Format.riff, self.load_riff_pal),
			(Palette.Format.jasc, self.load_jasc_pal),
			(None, self.load_zsoft_pcx),
			(None, self.load_bmp),
			# Need to try raw formats last as they have no identifying parts other than their data length
			(Palette.Format.raw_rgba, self.load_sc_wpe),
			(Palette.Format.raw_rgb, self.load_sc_pal)
		)
		for pal_format,load_method in formats:
			try:
				palette = load_method(data)
				if len(palette) == 256:
					self.format = pal_format
					break
			except Exception:
				pass
		else:
			raise PyMSError('Palette', "Unsupported palette file, could possibly be corrupt")
		self.palette = palette

	def load_palette(self, palette: RawPalette) -> None:
		self.palette = list(palette)

	def save_riff_pal(self, output: IO.AnyOutputBytes) -> None:
		with IO.OutputBytes(output) as f:
			f.write(b'RIFF\x00\x00\x00\x00PAL data\x04\x04\x00\x00\x00\x03\x00\x01')
			for c in self.palette:
				f.write(struct.pack('3Bx',*c))

	def save_jasc_pal(self, output: IO.AnyOutputBytes) -> None:
		text = 'JASC-PAL\r\n0100\r\n256\r\n'
		for color in self.palette:
			text += ' '.join(str(c) for c in color) + '\r\n'
		with IO.OutputBytes(output) as f:
			f.write(text.encode('utf-8'))

	def save_sc_wpe(self, output: IO.AnyOutputBytes) -> None:
		with IO.OutputBytes(output) as f:
			for c in self.palette:
				f.write(struct.pack('3Bx',*c))

	def save_sc_pal(self, output: IO.AnyOutputBytes) -> None:
		with IO.OutputBytes(output) as f:
			for c in self.palette:
				f.write(struct.pack('3B',*c))

	def save(self, output: IO.AnyOutputBytes, pal_format: Palette.Format) -> None:
		formats = {
			Palette.Format.riff: self.save_riff_pal,
			Palette.Format.jasc: self.save_jasc_pal,
			Palette.Format.raw_rgba: self.save_sc_wpe,
			Palette.Format.raw_rgb: self.save_sc_pal
		}
		save_method = formats.get(pal_format)
		if not save_method:
			raise PyMSError('Palette', f"Unsupported save format '{pal_format}'")
		save_method(output)

Palette.FileType.riff = Palette.FileType(Palette.Format.riff, 'pal')
Palette.FileType.jasc = Palette.FileType(Palette.Format.jasc, 'pal')
Palette.FileType.sc_pal = Palette.FileType(Palette.Format.raw_rgb, 'pal')
Palette.FileType.wpe = Palette.FileType(Palette.Format.raw_rgba, 'wpe')
Palette.FileType.act = Palette.FileType(Palette.Format.raw_rgb, 'act')
