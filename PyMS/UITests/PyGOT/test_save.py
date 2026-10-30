
from .utils import PyGOTTestCase

from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.PyMSError import PyMSError

from unittest import mock


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
