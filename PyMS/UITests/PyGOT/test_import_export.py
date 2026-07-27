
from .utils import PyGOTTestCase

from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved

from unittest import mock


class Test_PyGOT_import(PyGOTTestCase):
	def test_import_marks_document_edited(self) -> None:
		# A freshly imported template is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.make_pygot()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='template.txt'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.interpret', return_value=None):
			gui.iimport()
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_does_not_adopt_text_path_as_save_target(self) -> None:
		gui = self.make_pygot()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='template.txt'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.interpret', return_value=None):
			gui.iimport()
		self.assertIsNotNone(gui.got)
		self.assertIsNone(gui.file)

	def test_save_after_import_prompts_for_got_path(self) -> None:
		gui = self.make_pygot()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='template.txt'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.interpret', return_value=None):
			gui.iimport()
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='saved.got') as select_save, \
				mock.patch('PyMS.FileFormats.GOT.GOT.save', return_value=None) as got_save:
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		select_save.assert_called_once()
		got_save.assert_called_once_with('saved.got')
		self.assertEqual(gui.file, 'saved.got')

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.make_pygot()
		with mock.patch('PyMS.FileFormats.GOT.GOT.load', return_value=None):
			gui.open(file='opened.got')
		self.assertEqual(gui.file, 'opened.got')
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='template.txt'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.interpret', return_value=None):
			gui.iimport()
		self.assertEqual(gui.file, 'opened.got')
		with mock.patch('PyMS.FileFormats.GOT.GOT.save', return_value=None) as got_save, \
				mock.patch('PyMS.PyGOT.PyGOT.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		got_save.assert_called_once_with('opened.got')


class Test_PyGOT_export(PyGOTTestCase):
	def test_export_includes_unsaved_field_edits(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.gametype_id.set(5)
		with mock.patch('PyMS.Utilities.Config.SelectFile.select_save', return_value='export.txt'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.decompile', return_value=None) as decompile:
			gui.export()
		decompile.assert_called_once_with('export.txt')
		assert gui.got is not None
		self.assertEqual(gui.got.gametype_id, 5)
		self.assertEqual(gui.status.get(), 'Export Successful!')
