
from .utils import PyPALTestCase, ASKYESNOCANCEL, ERROR_DIALOG

from ...FileFormats.Palette import Palette
from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.PyMSError import PyMSError

import tkinter
from unittest import mock

SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
PALETTE_SAVE = 'PyMS.FileFormats.Palette.Palette.save'
ALLOW_OVERWRITE = 'PyMS.PyPAL.PyPAL.check_allow_overwrite_internal_file'


class Test_PyPAL_save(PyPALTestCase):
	def test_save_delegates_to_saveas_with_current_file_and_format(self) -> None:
		gui = self.with_new_palette()
		gui.file = 'current.pal'
		gui.format = Palette.Format.riff
		with mock.patch.object(gui, 'saveas', return_value=CheckSaved.saved) as saveas:
			self.assertEqual(gui.save(), CheckSaved.saved)
		saveas.assert_called_once_with(file_path='current.pal', file_format=Palette.Format.riff)

	def test_saveas_without_palette_is_saved_noop(self) -> None:
		gui = self.open_pypal()
		with mock.patch(PALETTE_SAVE) as palette_save:
			self.assertEqual(gui.saveas(file_path='x.pal'), CheckSaved.saved)
		palette_save.assert_not_called()

	def test_saveas_with_path_writes_and_updates_state(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ALLOW_OVERWRITE, return_value=True), \
				mock.patch(PALETTE_SAVE) as palette_save:
			result = gui.saveas(file_path='out.pal', file_format=Palette.Format.raw_rgb)
		self.assertEqual(result, CheckSaved.saved)
		palette_save.assert_called_once_with('out.pal', Palette.Format.raw_rgb)
		self.assertEqual(gui.file, 'out.pal')
		self.assertEqual(gui.format, Palette.Format.raw_rgb)
		self.assertFalse(gui.edited)
		self.assertEqual(gui.status.get(), 'Save Successful!')
		self.assertTrue(gui.toolbar.tag_is_enabled('format_known'))

	def test_saveas_via_dialog_uses_chosen_path(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(SELECT_SAVE, return_value='picked.pal'), \
				mock.patch(PALETTE_SAVE) as palette_save:
			result = gui.saveas(file_format=Palette.Format.raw_rgb)
		self.assertEqual(result, CheckSaved.saved)
		palette_save.assert_called_once_with('picked.pal', Palette.Format.raw_rgb)
		self.assertEqual(gui.file, 'picked.pal')

	def test_saveas_cancelled_dialog_is_cancelled(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(SELECT_SAVE, return_value=None), \
				mock.patch(PALETTE_SAVE) as palette_save:
			self.assertEqual(gui.saveas(), CheckSaved.cancelled)
		palette_save.assert_not_called()

	def test_saveas_blocked_overwrite_of_internal_file_is_cancelled(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ALLOW_OVERWRITE, return_value=False), \
				mock.patch(PALETTE_SAVE) as palette_save:
			self.assertEqual(gui.saveas(file_path='internal.pal'), CheckSaved.cancelled)
		palette_save.assert_not_called()

	def test_saveas_defaults_format_from_file_type(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ALLOW_OVERWRITE, return_value=True), \
				mock.patch(PALETTE_SAVE):
			gui.saveas(file_path='out.pal', file_type=Palette.FileType.sc_pal)
		self.assertEqual(gui.format, Palette.FileType.sc_pal.format)

	def test_saveas_dialog_filter_matches_chosen_file_type(self) -> None:
		gui = self.with_new_palette()
		for file_type in (Palette.FileType.riff, Palette.FileType.jasc, Palette.FileType.sc_pal, Palette.FileType.wpe, Palette.FileType.act):
			with self.subTest(pal_format=file_type.format, ext=file_type.ext):
				with mock.patch(SELECT_SAVE, return_value=None) as select_save:
					gui.saveas(file_type=file_type)
				select_save.assert_called_once()
				expected = list(Palette.FileType.save_types(file_type.format, file_type.ext))
				self.assertEqual(select_save.call_args.kwargs['filetypes'], expected)

	def test_saveas_write_error_shows_error_dialog(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ALLOW_OVERWRITE, return_value=True), \
				mock.patch(PALETTE_SAVE, side_effect=PyMSError('Save', 'boom')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			result = gui.saveas(file_path='out.pal', file_format=Palette.Format.raw_rgb)
		self.assertEqual(result, CheckSaved.cancelled)
		error_dialog.assert_called_once()


class Test_PyPAL_close(PyPALTestCase):
	def test_close_without_open_file_is_noop(self) -> None:
		gui = self.open_pypal()
		gui.close()
		self.assertIsNone(gui.palette)

	def test_close_clears_document_and_disables_actions(self) -> None:
		gui = self.with_loaded_palette()
		gui.close()
		self.pump(gui)
		self.assertIsNone(gui.palette)
		self.assertIsNone(gui.file)
		self.assertIsNone(gui.selected)
		self.assertFalse(gui.toolbar.tag_is_enabled('file_open'))
		self.assertEqual(gui.status.get(), 'Load or create a palette.')
		# The selection rectangle collapses to zero area (hidden).
		coords = tkinter.Canvas.coords(gui.canvas, gui.sel.item_id)
		self.assertEqual(coords[0], coords[2])
		self.assertEqual(coords[1], coords[3])

	def test_close_cancelled_when_unsaved_changes_kept(self) -> None:
		gui = self.with_loaded_palette()
		gui.mark_edited(True)
		original = gui.palette
		with mock.patch(ASKYESNOCANCEL, return_value=None):
			gui.close()
		self.assertIs(gui.palette, original)


class Test_PyPAL_exit(PyPALTestCase):
	def test_exit_cancelled_keeps_window_open(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		with mock.patch(ASKYESNOCANCEL, return_value=None), \
				mock.patch.object(gui.config_, 'save') as config_save:
			gui.exit()
		self.assertTrue(gui.winfo_exists())
		config_save.assert_not_called()

	def test_exit_saves_settings_and_destroys_window(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui.config_, 'save') as config_save, \
				mock.patch.object(gui, 'destroy') as destroy:
			gui.exit()
		config_save.assert_called_once()
		destroy.assert_called_once()
