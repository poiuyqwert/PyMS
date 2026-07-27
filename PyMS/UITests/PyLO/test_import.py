
from .utils import PyLOTestCase

from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.PyMSError import PyMSError

from unittest import mock


class Test_PyLO_import(PyLOTestCase):
	def test_import_interprets_text_into_model(self) -> None:
		gui = self.make_pylo()
		text = 'Frame:\n    (1, 2)\n'
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data=text)):
			gui.iimport()
		assert gui.lo is not None
		self.assertEqual(gui.lo.frames, [[[1, 2]]])
		self.assertEqual(gui.text.get('1.0', UI.END).rstrip('\n'), 'Frame:\n    (1, 2)')

	def test_import_marks_document_edited(self) -> None:
		# A freshly imported overlay is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.make_pylo()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Frame:\n    (1, 2)\n')):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited_state.is_edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_save_target_so_save_prompts(self) -> None:
		gui = self.make_pylo()
		text = 'Frame:\n    (1, 2)\n'
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data=text)):
			gui.iimport()
		self.assertIsNone(gui.file)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='') as select_save:
			result = gui.save()
		select_save.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.FileFormats.LO.LO.load', return_value=None):
			gui.open(file='opened.loa')
		self.assertEqual(gui.file, 'opened.loa')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Frame:\n    (3, 4)\n')):
			gui.iimport()
		self.assertEqual(gui.file, 'opened.loa')
		with mock.patch('PyMS.FileFormats.LO.LO.save', return_value=None) as lo_save, \
				mock.patch('PyMS.PyLO.PyLO.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		lo_save.assert_called_once_with('opened.loa')

	def test_import_with_uncompilable_text_shows_error_and_aborts(self) -> None:
		gui = self.make_pylo()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='garbage\n')), \
				mock.patch('PyMS.PyLO.PyLO.ErrorDialog') as error_dialog:
			gui.iimport()
		error_dialog.assert_called_once()
		error = error_dialog.call_args.args[1]
		self.assertIsInstance(error, PyMSError)
		self.assertIn('Unknown line format', str(error))
		self.assertFalse(gui.is_file_open())
		self.assertEqual(gui.text.get('1.0', UI.END).rstrip('\n'), '')
