
from ...PyGRAFT.GraftData import ReqGraftData, UnitsGraftData, UpgradesGraftData, ResearchGraftData, TechGraftData, OrdersGraftData, ButtonsGraftData, AnyGraftData
from ...FileFormats.Graft import ReqScript, ButtonsGraft, FGP
from ...Utilities.DataContext import DataContext
from ...Utilities.PyMSError import PyMSError

from ..Graft.utils import vanilla_data_context

import io
import unittest

from typing import Callable

REQ_GRAFT_DATA_TYPES: tuple[Callable[[], ReqGraftData], ...] = (UnitsGraftData, UpgradesGraftData, ResearchGraftData, TechGraftData, OrdersGraftData)

def all_graft_data() -> list[AnyGraftData]:
	return [graft_data_type() for graft_data_type in REQ_GRAFT_DATA_TYPES] + [ButtonsGraftData()]

def vanilla_bytes(graft_data: AnyGraftData) -> bytes:
	if isinstance(graft_data, ReqGraftData):
		path = graft_data.graft_type.default_path()
	else:
		path = ButtonsGraft.default_path()
	with open(path, 'rb') as f:
		return f.read()

class Test_GraftData(unittest.TestCase):
	def test_new_is_vanilla_and_unedited(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				graft_data.edited = True
				graft_data.file_path = 'somewhere.graft'
				graft_data.new()
				self.assertEqual(graft_data.save_bytes(), vanilla_bytes(graft_data))
				self.assertFalse(graft_data.edited)
				self.assertIsNone(graft_data.file_path)
				self.assertEqual(graft_data.display_name, graft_data.file_name)

	def test_load_bytes_round_trips_without_file_path(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				data = vanilla_bytes(graft_data)
				graft_data.edited = True
				self.assertEqual(graft_data.load(data), [])
				self.assertEqual(graft_data.save_bytes(), data)
				self.assertFalse(graft_data.edited)
				self.assertIsNone(graft_data.file_path)

	def test_load_path_records_file_path(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				path = graft_data.graft_type.default_path() if isinstance(graft_data, ReqGraftData) else ButtonsGraft.default_path()
				graft_data.load(path)
				self.assertEqual(graft_data.file_path, path)
				self.assertEqual(graft_data.display_name, path)

	def test_failed_load_keeps_open_file(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				graft_data.new()
				graft = graft_data.graft
				with self.assertRaises(PyMSError) as cm:
					graft_data.load(b'\x00')
				self.assertIn(f'Unsupported {graft_data.file_name} file', cm.exception.error)
				self.assertIs(graft_data.graft, graft)

	def test_text_round_trip_marks_edited_and_keeps_file_path(self) -> None:
		data_context = vanilla_data_context()
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				graft_data.new()
				graft_data.file_path = 'target.graft'
				output = io.StringIO()
				graft_data.export_text(output, data_context)
				graft_data.import_text(output.getvalue(), data_context)
				self.assertTrue(graft_data.edited)
				self.assertEqual(graft_data.file_path, 'target.graft')
				self.assertEqual(graft_data.save_bytes(), vanilla_bytes(graft_data))

	def test_failed_text_import_leaves_file_unedited(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				graft_data.new()
				with self.assertRaises(PyMSError) as cm:
					graft_data.import_text('not_a_command', vanilla_data_context())
				self.assertIn('not_a_command', cm.exception.error)
				self.assertFalse(graft_data.edited)
				self.assertEqual(graft_data.save_bytes(), vanilla_bytes(graft_data))

	def test_empty_fgp_import_does_not_mark_edited(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				graft_data.new()
				self.assertEqual(graft_data.import_fgp(FGP()), [])
				self.assertFalse(graft_data.edited)

	def test_req_entry_ids_are_every_dat_entry(self) -> None:
		expected_counts: dict[Callable[[], ReqGraftData], int] = {UnitsGraftData: 228, UpgradesGraftData: 61, ResearchGraftData: 44, TechGraftData: 44, OrdersGraftData: 189}
		for graft_data_type in REQ_GRAFT_DATA_TYPES:
			graft_data = graft_data_type()
			with self.subTest(file=graft_data.file_name):
				graft_data.new()
				self.assertEqual(graft_data.entry_count(vanilla_data_context()), expected_counts[graft_data_type])
				self.assertEqual(graft_data.entry_ids(vanilla_data_context()), list(range(expected_counts[graft_data_type])))
				self.assertEqual(graft_data.entry_count(DataContext()), expected_counts[graft_data_type])

	def test_req_entry_ids_include_scripts_past_the_dat(self) -> None:
		graft_data = OrdersGraftData()
		graft_data.new()
		graft_data.graft.set_script(ReqScript(300, []))
		entry_ids = graft_data.entry_ids(vanilla_data_context())
		self.assertEqual(entry_ids, [*range(189), 300])

	def test_req_has_script(self) -> None:
		graft_data = OrdersGraftData()
		graft_data.new()
		script_ids = set(graft_data.graft.list_ids())
		for entry_id in graft_data.entry_ids(vanilla_data_context()):
			self.assertEqual(graft_data.has_script(entry_id), entry_id in script_ids)
		self.assertTrue(script_ids)
		self.assertLess(len(script_ids), 189)

	def test_req_entry_name(self) -> None:
		graft_data = UnitsGraftData()
		self.assertEqual(graft_data.entry_name(vanilla_data_context(), 0), 'Terran Marine')

	def test_mpq_paths(self) -> None:
		for graft_data in all_graft_data():
			with self.subTest(file=graft_data.file_name):
				self.assertEqual(graft_data.mpq_path, 'datreq\\' + graft_data.file_name)
