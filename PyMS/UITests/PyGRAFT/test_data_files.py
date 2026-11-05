
from .utils import PyGRAFTTestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...FileFormats.TBL import TBL
from ...Utilities import Assets
from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError

import io

from typing import BinaryIO
from unittest import mock

def vanilla_files(gui: PyGRAFT) -> dict[str, bytes]:
	# The data file settings, mapped to the bundled vanilla files
	files = gui.config_.settings.files
	paths = {
		files.stat_txt.file_path: ('rez', 'stat_txt.tbl'),
		files.dat.units.file_path: ('arr', 'units.dat'),
		files.dat.upgrades.file_path: ('arr', 'upgrades.dat'),
		files.dat.techdata.file_path: ('arr', 'techdata.dat'),
		files.dat.orders.file_path: ('arr', 'orders.dat'),
	}
	data: dict[str, bytes] = {}
	for setting_path, path_components in paths.items():
		with open(Assets.mpq_file_path(*path_components), 'rb') as f:
			data[setting_path] = f.read()
	return data

def unitnames_data(marine_name: str) -> bytes:
	stat_txt = TBL()
	stat_txt.load(Assets.mpq_file_path('rez', 'stat_txt.tbl'))
	unitnames = TBL()
	unitnames.strings = [f'{marine_name}\x00'] + stat_txt.strings[1:228]
	return IO.output_to_bytes(unitnames.save)

class Test_PyGRAFT_data_files(PyGRAFTTestCase):
	def open_files(self, gui: PyGRAFT, files: dict[str, bytes]) -> PyMSError | None:
		def get_file(path: str, *_: object) -> BinaryIO | None:
			return io.BytesIO(files[path]) if path in files else None
		def load_file(path: str, *_: object) -> BinaryIO:
			file = get_file(path)
			assert file is not None
			return file
		with mock.patch.object(gui.mpq_handler, 'open_mpqs', return_value=[]), \
				mock.patch.object(gui.mpq_handler, 'close_mpqs'), \
				mock.patch.object(gui.mpq_handler, 'get_file', side_effect=get_file), \
				mock.patch.object(gui.mpq_handler, 'load_file', side_effect=load_file):
			err = gui.open_files()
		self.pump(gui)
		return err

	def test_missing_unitnames_falls_back_to_stat_txt(self) -> None:
		gui = self.open_pygraft()
		self.assertIsNone(self.open_files(gui, vanilla_files(gui)))
		self.assertIsNone(gui.data_context.unitnames_tbl)
		self.assertIsNotNone(gui.data_context.stat_txt_tbl)
		self.display_tab(gui, 'Unit Training Reqs.')
		self.assertIn('Terran Marine', self.list_entries(gui)[0])

	def test_found_unitnames_names_units(self) -> None:
		gui = self.open_pygraft()
		gui.config_.settings.files.unitnames.file_path = 'mod/unitnames.tbl'
		files = vanilla_files(gui)
		files['mod/unitnames.tbl'] = unitnames_data('Space Marine')
		self.assertIsNone(self.open_files(gui, files))
		self.assertIsNotNone(gui.data_context.unitnames_tbl)
		self.display_tab(gui, 'Unit Training Reqs.')
		self.assertIn('Space Marine', self.list_entries(gui)[0])
		self.display_tab(gui, 'Button Cards')
		self.assertIn('Space Marine', self.list_entries(gui)[0])

	def test_invalid_unitnames_is_an_error(self) -> None:
		gui = self.open_pygraft()
		gui.config_.settings.files.unitnames.file_path = 'mod/unitnames.tbl'
		files = vanilla_files(gui)
		files['mod/unitnames.tbl'] = b'\x05'
		err = self.open_files(gui, files)
		assert err is not None
		self.assertIn('Unsupported TBL file', err.error)
		self.assertIsNone(gui.data_context.unitnames_tbl)
		self.assertIsNone(gui.data_context.stat_txt_tbl)
