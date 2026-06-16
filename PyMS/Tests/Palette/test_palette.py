
from ...FileFormats.Palette import Palette
from ...Utilities.UIKit.FileType import FileType
from ...Utilities.PyMSError import PyMSError
from ...Utilities import IO

import io
import unittest

PALETTE = [(i, (i * 2) % 256, (i * 3) % 256) for i in range(256)]
Format = Palette.Format


def _capture(method_name: str) -> bytes:
	pal = Palette()
	pal.palette = list(PALETTE)
	return IO.output_to_bytes(getattr(pal, method_name))


class Test_format_round_trips(unittest.TestCase):
	def test_riff(self) -> None:
		data = _capture('save_riff_pal')
		self.assertEqual(len(data), 1048)
		self.assertEqual(Palette().load_riff_pal(data), PALETTE)

	def test_jasc(self) -> None:
		data = _capture('save_jasc_pal')
		self.assertEqual(Palette().load_jasc_pal(data), PALETTE)

	def test_sc_wpe(self) -> None:
		data = _capture('save_sc_wpe')
		self.assertEqual(len(data), 1024)  # 256 * RGBA
		self.assertEqual(Palette().load_sc_wpe(data), PALETTE)

	def test_sc_pal(self) -> None:
		data = _capture('save_sc_pal')
		self.assertEqual(len(data), 768)  # 256 * RGB
		self.assertEqual(Palette().load_sc_pal(data), PALETTE)


class Test_parser_validation(unittest.TestCase):
	def test_riff_wrong_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Palette().load_riff_pal(b'RIFF\x00\x00\x00\x00PAL data' + b'\x00' * 10)

	def test_riff_bad_header_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Palette().load_riff_pal(b'XXXX' + b'\x00' * 1044)

	def test_jasc_bad_header_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Palette().load_jasc_pal(b'NOT-JASC\r\n0100\r\n256\r\n')

	def test_sc_pal_wrong_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Palette().load_sc_pal(b'\x00' * 100)


class Test_load(unittest.TestCase):
	def _detect(self, method_name: str) -> Palette:
		data = _capture(method_name)
		palette = Palette()
		palette.load(io.BytesIO(data))
		return palette

	def test_detects_riff(self) -> None:
		palette = self._detect('save_riff_pal')
		self.assertEqual(palette.format, Format.riff)
		self.assertEqual(palette.palette, PALETTE)

	def test_detects_jasc(self) -> None:
		palette = self._detect('save_jasc_pal')
		self.assertEqual(palette.format, Format.jasc)
		self.assertEqual(palette.palette, PALETTE)

	def test_detects_wpe_as_raw_rgba(self) -> None:
		palette = self._detect('save_sc_wpe')
		self.assertEqual(palette.format, Format.raw_rgba)
		self.assertEqual(palette.palette, PALETTE)

	def test_detects_pal_as_raw_rgb(self) -> None:
		palette = self._detect('save_sc_pal')
		self.assertEqual(palette.format, Format.raw_rgb)
		self.assertEqual(palette.palette, PALETTE)

	def test_unrecognized_data_raises(self) -> None:
		with self.assertRaises(PyMSError):
			Palette().load(io.BytesIO(b'not a palette'))


class Test_save_types(unittest.TestCase):
	def test_riff(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.riff, None), (FileType.pal_riff(),))

	def test_jasc(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.jasc, None), (FileType.pal_jasc(),))

	def test_raw_rgb_default(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.raw_rgb, None), (FileType.pal_sc(), FileType.act()))

	def test_raw_rgb_pal_extension(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.raw_rgb, 'pal'), (FileType.pal_sc(),))

	def test_raw_rgb_act_extension(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.raw_rgb, 'act'), (FileType.act(),))

	def test_raw_rgba(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.raw_rgba, None), (FileType.wpe(),))

	def test_unknown_extension_falls_back_to_default(self) -> None:
		self.assertEqual(Palette.FileType.save_types(Format.raw_rgb, 'zzz'), (FileType.pal_sc(), FileType.act()))
