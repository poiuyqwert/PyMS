
from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...FileFormats import TBL
from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved

from unittest import mock


class Test_PyTBL_open(PyTBLTestCase):
	def test_open_populates_list_and_selects_first_string(self) -> None:
		gui = self.make_pytbl(['first\x00', 'second\x00'])
		self.assertEqual(gui.listbox.size(), 2)
		self.assertEqual(self.selected_index(gui), 0)
		self.assertEqual(gui.file, 'test.tbl')
		self.assertEqual(gui.status.get(), 'Load Successful!')
		self.assertFalse(gui.edited)

	def test_import_populates_list_and_selects_first_string(self) -> None:
		gui = self.make_window(PyTBL)
		def fake_interpret(tbl: TBL.TBL, _file: str) -> None:
			tbl.strings = ['first\x00']
		with mock.patch('PyMS.FileFormats.TBL.TBL.interpret', autospec=True, side_effect=fake_interpret), \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='test.txt'):
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.listbox.size(), 1)
		self.assertEqual(self.selected_index(gui), 0)
		self.assertIsNone(gui.file)
		self.assertEqual(gui.status.get(), 'Import Successful!')

	def test_import_marks_document_edited(self) -> None:
		# Freshly imported strings are unsaved work: they must be flagged
		# edited so closing without saving prompts instead of silently
		# discarding them.
		gui = self.make_window(PyTBL)
		def fake_interpret(tbl: TBL.TBL, _file: str) -> None:
			tbl.strings = ['first\x00']
		with mock.patch('PyMS.FileFormats.TBL.TBL.interpret', autospec=True, side_effect=fake_interpret), \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='test.txt'):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pytbl(['first\x00'])
		self.assertEqual(gui.file, 'test.tbl')
		def fake_interpret(tbl: TBL.TBL, _file: str) -> None:
			tbl.strings = ['second\x00']
		with mock.patch('PyMS.FileFormats.TBL.TBL.interpret', autospec=True, side_effect=fake_interpret), \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='test.txt'):
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.file, 'test.tbl')
		with mock.patch('PyMS.FileFormats.TBL.TBL.save', return_value=None) as tbl_save, \
				mock.patch('PyMS.PyTBL.PyTBL.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		tbl_save.assert_called_once_with('test.tbl')
