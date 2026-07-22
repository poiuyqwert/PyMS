
from unittest import mock

from .harness import UITestCase

from ..PyGOT.PyGOT import PyGOT
from ..FileFormats import GOT
from ..Utilities import UIKit as UI
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.PyMSError import PyMSError

# These tests drive PyGOT through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; file dialogs and the GOT
# format's file I/O are mocked so no disk access happens.


class PyGOTTestCase(UITestCase):
	def make_pygot(self) -> PyGOT:
		return self.make_window(PyGOT)


class Test_PyGOT_edited_tracking(PyGOTTestCase):
	def test_new_document_starts_unedited(self) -> None:
		gui = self.make_pygot()
		gui.new()
		self.assertFalse(gui.edited)

	def test_league_id_change_marks_edited(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.mark_edited(False)
		gui.league_id.set(5)
		self.assertTrue(gui.edited)


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


class Test_PyGOT_value_entry_states(PyGOTTestCase):
	def test_value_entry_follows_dropdown_selection(self) -> None:
		gui = self.make_pygot()
		gui.new()
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		gui.victory_condition.set(GOT.VictoryCondition.resources.value)
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.NORMAL)
		gui.victory_condition.set(GOT.VictoryCondition.map_default.value)
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		gui.resources.set(GOT.Resources.fixed_value.value)
		self.assertEqual(str(gui.resources_entry['state']), UI.NORMAL)

	def test_value_entries_disabled_after_close(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.victory_condition.set(GOT.VictoryCondition.resources.value)
		gui.resources.set(GOT.Resources.income.value)
		with mock.patch('tkinter.messagebox.askyesnocancel', return_value=False):
			gui.close()
		self.assertEqual(str(gui.victory_condition_entry['state']), UI.DISABLED)
		self.assertEqual(str(gui.resources_entry['state']), UI.DISABLED)


class Test_PyGOT_save_name_validation(PyGOTTestCase):
	def test_name_over_32_utf8_bytes_shows_error_without_prompting(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.name.set('é' * 17) # 17 characters, 34 bytes encoded
		with mock.patch('PyMS.PyGOT.PyGOT.ErrorDialog') as error_dialog, \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_save') as select_save, \
				mock.patch('PyMS.FileFormats.GOT.GOT.save', return_value=None) as got_save:
			result = gui.saveas()
		self.assertEqual(result, CheckSaved.cancelled)
		error_dialog.assert_called_once()
		error = error_dialog.call_args.args[1]
		self.assertIsInstance(error, PyMSError)
		self.assertIn('too long', str(error))
		select_save.assert_not_called()
		got_save.assert_not_called()

	def test_variation_name_over_32_utf8_bytes_shows_error(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.subtype_name.set('é' * 17)
		with mock.patch('PyMS.PyGOT.PyGOT.ErrorDialog') as error_dialog, \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_save'), \
				mock.patch('PyMS.FileFormats.GOT.GOT.save', return_value=None) as got_save:
			result = gui.saveas()
		self.assertEqual(result, CheckSaved.cancelled)
		error_dialog.assert_called_once()
		got_save.assert_not_called()

	def test_name_at_32_ascii_characters_saves(self) -> None:
		gui = self.make_pygot()
		gui.new()
		gui.name.set('a' * 32)
		with mock.patch('PyMS.PyGOT.PyGOT.check_allow_overwrite_internal_file', return_value=True), \
				mock.patch('PyMS.FileFormats.GOT.GOT.save', return_value=None) as got_save:
			result = gui.saveas(file_path='out.got')
		self.assertEqual(result, CheckSaved.saved)
		got_save.assert_called_once_with('out.got')
		self.assertFalse(gui.edited)


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


class Test_PyGOT_file_open_state(PyGOTTestCase):
	def test_file_open_reflects_document_presence(self) -> None:
		gui = self.make_pygot()
		self.assertFalse(gui.is_file_open())
		gui.new()
		self.assertTrue(gui.is_file_open())
