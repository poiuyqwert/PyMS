
from .utils import PyTRGTestCase

from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.PyMSError import PyMSError

import os
from unittest import mock


class Test_PyTRG_import(PyTRGTestCase):
	def test_import_marks_document_edited(self) -> None:
		# Freshly imported triggers are unsaved work: they must be flagged
		# edited so closing without saving prompts instead of silently
		# discarding them.
		gui = self.make_pytrg()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Trigger():\n')):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited_state.is_edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_save_target_so_save_prompts(self) -> None:
		gui = self.make_pytrg()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Trigger():\n')):
			gui.iimport()
		self.assertIsNone(gui.file)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='') as select_save:
			result = gui.save()
		select_save.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pytrg()
		with mock.patch('PyMS.FileFormats.TRG.TRG.TRG.load', return_value=None):
			gui.open(file='opened.trg')
		self.assertEqual(gui.file, 'opened.trg')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='fake.txt'), \
				mock.patch('builtins.open', mock.mock_open(read_data='Trigger():\n')):
			gui.iimport()
		self.assertEqual(gui.file, 'opened.trg')
		with mock.patch('PyMS.FileFormats.TRG.TRG.TRG.compile', return_value=None), \
				mock.patch('PyMS.FileFormats.TRG.TRG.TRG.save', return_value=[]) as trg_save, \
				mock.patch('PyMS.PyTRG.PyTRG.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		trg_save.assert_called_once_with('opened.trg')


class Test_PyTRG_export(PyTRGTestCase):
	def test_unwritable_path_shows_error_instead_of_raising(self) -> None:
		gui = self.make_pytrg()
		gui.new()
		unwritable = os.path.join(os.path.dirname(__file__), 'does-not-exist', 'export.txt')
		with mock.patch('PyMS.PyTRG.PyTRG.ErrorDialog') as error_dialog, \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value=unwritable):
			gui.export()
		error_dialog.assert_called_once()
		error = error_dialog.call_args.args[1]
		self.assertIsInstance(error, PyMSError)
		self.assertNotEqual(gui.status.get(), 'Export Successful!')
