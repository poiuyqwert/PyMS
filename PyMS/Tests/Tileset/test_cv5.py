
from ...FileFormats.Tileset.CV5 import CV5, CV5Group
from ...Utilities.PyMSError import PyMSError
from .utils import group_inc, group_full
from ...Utilities import IO

import io
import struct
import unittest


class Test_CV5Group(unittest.TestCase):
	def test_load_data(self) -> None:
		header = list(range(10))
		megatile_ids = list(range(100, 116))
		group = CV5Group()
		group.load_data(struct.pack('<26H', *(header + megatile_ids)))
		self.assertEqual(group.type, 0)
		self.assertEqual(group.flags, 1)
		self.assertEqual(group.megatile_ids, megatile_ids)

	def test_save_data_round_trip(self) -> None:
		group = group_inc()
		group.megatile_ids = list(range(16))
		reloaded = CV5Group()
		reloaded.load_data(group.save_data())
		self.assertEqual(reloaded, group)

	def test_basic_and_doodad_properties_alias(self) -> None:
		group = CV5Group()
		group.basic_edge_left = 42
		self.assertEqual(group.doodad_overlay_id, 42)
		group.doodad_dddata_id = 7
		self.assertEqual(group.basic_piece_left, 7)

	def test_update_settings_copies_fields_not_megatiles(self) -> None:
		source = group_full()
		source.megatile_ids = list(range(16))
		target = CV5Group()
		target.megatile_ids = [0] * 16
		target.update_settings(source)
		self.assertEqual(target.flags, source.flags)
		self.assertEqual(target.basic_edge_left, source.basic_edge_left)
		self.assertEqual(target.megatile_ids, [0] * 16)

	def test_equality(self) -> None:
		self.assertEqual(group_inc(), group_inc())
		self.assertNotEqual(group_inc(), group_full())


class Test_CV5(unittest.TestCase):
	def test_defaults(self) -> None:
		cv5 = CV5()
		self.assertEqual(cv5.group_count(), 0)
		self.assertEqual(cv5.groups_remaining(), CV5.MAX_ID + 1)

	def test_add_group(self) -> None:
		cv5 = CV5()
		group = group_inc()
		group_id = cv5.add_group(group)
		self.assertEqual(group_id, 0)
		self.assertEqual(cv5.group_count(), 1)
		self.assertIs(cv5.get_group(0), group)

	def test_save_load_round_trip(self) -> None:
		# `save_data` packs the 16 megatile ids, so they must be populated.
		def with_megatiles(group: CV5Group) -> CV5Group:
			group.megatile_ids = list(range(16))
			return group
		cv5 = CV5()
		cv5.add_group(with_megatiles(group_inc()))
		cv5.add_group(with_megatiles(group_full()))
		loaded = CV5()
		loaded.load(io.BytesIO(IO.output_to_bytes(cv5.save)))
		self.assertEqual(loaded.group_count(), 2)
		self.assertEqual(loaded.get_group(0), with_megatiles(group_inc()))
		self.assertEqual(loaded.get_group(1), with_megatiles(group_full()))

	def test_load_invalid_size_raises(self) -> None:
		with self.assertRaises(PyMSError):
			CV5().load(io.BytesIO(b'\x00' * 51))
