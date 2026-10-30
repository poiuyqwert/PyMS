
from .utils import PyBINTestCase

from ...Utilities import IO
from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved

from unittest import mock


class Test_PyBIN_import(PyBINTestCase):
	def test_import_marks_document_edited(self) -> None:
		# A freshly imported dialog is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.make_pybin()
		assert gui.bin is not None
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_save_target_so_save_prompts(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		# IO.InputText treats a string that isn't an existing path as raw
		# content, so returning decompiled text from the file dialog keeps the
		# import entirely in-memory.
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertIsNone(gui.file)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='') as select_save:
			result = gui.save()
		select_save.assert_called_once()
		self.assertEqual(result, CheckSaved.cancelled)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pybin()
		assert gui.bin is not None
		dialog_text = IO.output_to_text(gui.bin.decompile)
		with mock.patch('PyMS.FileFormats.DialogBIN.DialogBIN.DialogBIN.load', return_value=None):
			gui.open(file='opened.bin')
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.bin')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value=dialog_text):
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.bin')
		with mock.patch('PyMS.FileFormats.DialogBIN.DialogBIN.DialogBIN.save', return_value=None) as bin_save, \
				mock.patch('PyMS.PyBIN.PyBIN.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		bin_save.assert_called_once_with('opened.bin')
