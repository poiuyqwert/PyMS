
from ...PyDAT.TBLData import TBLData
from ...PyDAT.DataID import DataID
from ...PyDAT.DataContext import DataContext
from ...FileFormats.TBL import TBL, compile_string
from ...Utilities import IO

import io
import unittest
from unittest.mock import Mock
from typing import cast


def _tbl_bytes(strings: list[str]) -> bytes:
	tbl = TBL()
	tbl.strings = [compile_string(s) for s in strings]
	return IO.output_to_bytes(tbl.save)


def _context_with_file(data: bytes | None) -> DataContext:
	mock = Mock()
	mock.mpq_handler.get_file.return_value = io.BytesIO(data) if data is not None else None
	return cast(DataContext, mock)


class Test_load_strings(unittest.TestCase):
	def test_loads_and_decompiles_strings(self) -> None:
		data = _tbl_bytes(['Hello', 'Beta'])
		tbl_data = TBLData(_context_with_file(data), DataID.stat_txt, Mock())
		fired: list[DataID] = []
		tbl_data.update_cb += fired.append
		tbl_data.load_strings()
		self.assertEqual(tbl_data.strings, ('Hello<0>', 'Beta<0>'))
		self.assertEqual(fired, [DataID.stat_txt])

	def test_missing_file_yields_empty_and_fires_callback(self) -> None:
		tbl_data = TBLData(_context_with_file(None), DataID.stat_txt, Mock())
		fired: list[DataID] = []
		tbl_data.update_cb += fired.append
		tbl_data.load_strings()
		self.assertEqual(tbl_data.strings, ())
		self.assertEqual(fired, [DataID.stat_txt])


class Test_save_data(unittest.TestCase):
	def test_compiles_strings_to_tbl_bytes(self) -> None:
		tbl_data = TBLData(cast(DataContext, Mock()), DataID.stat_txt, Mock())
		tbl_data.strings = ('Alpha', 'Beta')
		self.assertEqual(tbl_data.save_data(), _tbl_bytes(['Alpha', 'Beta']))

	def test_empty_strings(self) -> None:
		tbl_data = TBLData(cast(DataContext, Mock()), DataID.stat_txt, Mock())
		self.assertEqual(tbl_data.save_data(), _tbl_bytes([]))

	def test_load_then_save_is_byte_identical(self) -> None:
		data = _tbl_bytes(['Hello', 'Wor<0>ld', 'Gamma'])
		tbl_data = TBLData(_context_with_file(data), DataID.stat_txt, Mock())
		tbl_data.load_strings()
		self.assertEqual(tbl_data.save_data(), data)
