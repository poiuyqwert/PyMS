
from ...FileFormats.Tileset.DDDataBIN import DDDataBIN
from ...Utilities.PyMSError import PyMSError
from .utils import save_to_bytes

import io
import struct
import unittest

DDDATA_SIZE = 262144  # 512 doodads * 256 entries * 2 bytes


class Test_DDDataBIN(unittest.TestCase):
	def test_default_has_512_empty_doodads(self) -> None:
		ddd = DDDataBIN()
		self.assertEqual(ddd.doodad_count(), 512)
		self.assertEqual(ddd.get_doodad(0), [0] * 256)

	def test_add_doodad(self) -> None:
		ddd = DDDataBIN()
		doodad_id = ddd.add_doodad([7] * 256)
		self.assertEqual(doodad_id, 512)
		self.assertEqual(ddd.doodad_count(), 513)
		self.assertEqual(ddd.get_doodad(512), [7] * 256)

	def test_add_doodad_wrong_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			DDDataBIN().add_doodad([0] * 255)

	def test_load_file(self) -> None:
		ddd = DDDataBIN()
		ddd.load_file(io.BytesIO(b'\x00' * DDDATA_SIZE))
		self.assertEqual(ddd.doodad_count(), 512)
		self.assertEqual(ddd.get_doodad(0), [0] * 256)

	def test_load_file_reads_values(self) -> None:
		first = struct.pack('<256H', *range(256))
		ddd = DDDataBIN()
		ddd.load_file(io.BytesIO(first + b'\x00' * (DDDATA_SIZE - len(first))))
		self.assertEqual(ddd.get_doodad(0), list(range(256)))

	def test_load_file_wrong_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			DDDataBIN().load_file(io.BytesIO(b'\x00' * 100))

	def test_save_file_byte_length(self) -> None:
		self.assertEqual(len(save_to_bytes(DDDataBIN())), DDDATA_SIZE)

	def test_save_load_round_trip(self) -> None:
		ddd = DDDataBIN()
		ddd.get_doodad(5)[0] = 0x1234
		ddd.get_doodad(5)[255] = 0xFFFF
		loaded = DDDataBIN()
		loaded.load_file(io.BytesIO(save_to_bytes(ddd)))
		self.assertEqual(loaded.doodad_count(), 512)
		self.assertEqual(loaded.get_doodad(5), ddd.get_doodad(5))
		self.assertEqual(loaded.get_doodad(0), [0] * 256)
