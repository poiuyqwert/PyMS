
from .harness import UITestCase

from ..PyFNT.PyFNT import PyFNT
from ..PyFNT.InfoDialog import InfoDialog, FontInfo
from ..FileFormats.FNT import FNT
from ..FileFormats.PCX import PCX
from ..Utilities import UIKit as UI
from ..Utilities.PyMSError import PyMSError

from unittest import mock

from typing import Any

# These tests drive PyFNT through its public command methods, asserting on both
# widget state and the model. Outside-world boundaries — the file dialogs, the
# FNT specifications dialog, the BMP/FNT converters, and the error dialog — are
# stubbed per test so nothing blocks or touches disk. The special palette is
# seeded in-memory since the harness never runs `initialize()`/`open_files()`.

# Patch-target paths, named where they are looked up.
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
INFO_DIALOG = 'PyMS.PyFNT.PyFNT.InfoDialog'
FNT_TO_BMP = 'PyMS.PyFNT.PyFNT.fnttobmp'
BMP_TO_FNT = 'PyMS.PyFNT.PyFNT.bmptofnt'
BMP_CLASS = 'PyMS.PyFNT.PyFNT.BMP'
ERROR_DIALOG = 'PyMS.PyFNT.PyFNT.ErrorDialog'


def _special_palette() -> PCX:
	# A recognizable special palette: pixel value c maps through `image[0]` to
	# palette index c, whose color is the distinct grayscale (c, c, c).
	pcx = PCX([(i, i, i) for i in range(256)])
	pcx.image = [list(range(256))]
	return pcx


def _info_dialog_stub(result: FontInfo | None) -> mock.Mock:
	stub = mock.Mock()
	stub.result = result
	return stub


def _font(width: int = 4, height: int = 3, start: int = 32, letters: int = 5) -> FNT:
	fnt = FNT()
	fnt.width, fnt.height, fnt.start = width, height, start
	fnt.letters = [[[0] * width for _ in range(height)] for __ in range(letters)]
	return fnt


class PyFNTTestCase(UITestCase):
	def open_pyfnt(self) -> PyFNT:
		gui = self.make_window(PyFNT)
		gui.palette = _special_palette()
		return gui

	def with_new_font(self) -> PyFNT:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))):
			gui.new()
		self.pump(gui)
		return gui


class Test_InfoDialog_result(PyFNTTestCase):
	def _open_dialog(self, gui: PyFNT, need_size: bool = False) -> InfoDialog:
		# `grab_wait` blocks on `wait_window` until the dialog closes; neutralize
		# it so the constructor returns with the dialog still open.
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			return InfoDialog(gui, need_size)

	def test_dialog_starts_with_no_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui)
		self.assertIsNone(dialog.result)
		dialog.cancel()

	def test_ok_captures_entered_values_as_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui, need_size=True)
		dialog.lowi.set(33)
		dialog.letters.set(6)
		dialog.width.set(5)
		dialog.height.set(7)
		dialog.ok()
		self.assertEqual(dialog.result, FontInfo(lowi=33, letters=6, width=5, height=7))

	def test_cancel_leaves_no_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui)
		dialog.cancel()
		self.assertIsNone(dialog.result)

	def test_size_prompts_ask_for_width_and_height(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui, need_size=True)
		labels = [str(child.cget('text')) for child in dialog.winfo_children() if isinstance(child, UI.Label)]
		self.assertTrue(any('max width' in label for label in labels))
		self.assertTrue(any('max height' in label for label in labels))
		dialog.cancel()


class Test_PyFNT_new(PyFNTTestCase):
	def test_new_cancelled_dialog_aborts(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(None)):
			gui.new()
		self.assertIsNone(gui.fnt)
		self.assertFalse(gui.is_file_open())

	def test_new_cancelled_dialog_keeps_current_font(self) -> None:
		gui = self.with_new_font()
		original = gui.fnt
		with mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(None)):
			gui.new()
		self.assertIs(gui.fnt, original)

	def test_new_accepted_dialog_builds_font(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(FontInfo(lowi=33, letters=6, width=5, height=7))):
			gui.new()
		self.pump(gui)
		assert gui.fnt is not None
		self.assertEqual((gui.fnt.width, gui.fnt.height, gui.fnt.start), (5, 7, 33))
		self.assertEqual(len(gui.fnt.letters), 6)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.is_file_open())
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))
		self.assertIn('(Untitled.fnt)', gui.title())


class Test_PyFNT_open(PyFNTTestCase):
	def test_open_in_memory_font_clears_stale_file(self) -> None:
		# Opening a font object (the Import path) must not leave the previous
		# document's path behind, or a later Save would silently overwrite it.
		gui = self.with_new_font()
		gui.file = 'previous.fnt'
		gui.open(file=_font())
		self.assertIsNone(gui.file)
		self.assertIn('(Untitled.fnt)', gui.title())

	def test_open_from_path_records_file(self) -> None:
		gui = self.open_pyfnt()
		loaded = _font()
		def fake_load(fnt: FNT, _file: Any) -> None:
			fnt.width, fnt.height, fnt.start = loaded.width, loaded.height, loaded.start
			fnt.letters = loaded.letters
		with mock.patch(SELECT_OPEN, return_value='opened.fnt'), \
				mock.patch('PyMS.FileFormats.FNT.FNT.load', new=fake_load):
			gui.open()
		self.assertEqual(gui.file, 'opened.fnt')
		self.assertIn('(opened.fnt)', gui.title())


class Test_PyFNT_exports(PyFNTTestCase):
	def test_export_success_reports_success(self) -> None:
		gui = self.with_new_font()
		with mock.patch(SELECT_SAVE, return_value='out.bmp'), \
				mock.patch(FNT_TO_BMP) as fnttobmp:
			gui.exports()
		fnttobmp.assert_called_once()
		self.assertEqual(gui.status.get(), 'Font exported successfully!')

	def test_export_error_does_not_report_success(self) -> None:
		gui = self.with_new_font()
		with mock.patch(SELECT_SAVE, return_value='out.bmp'), \
				mock.patch(FNT_TO_BMP, side_effect=PyMSError('Export', 'boom')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.exports()
		error_dialog.assert_called_once()
		self.assertEqual(gui.status.get(), 'Failed to export font.')


class Test_PyFNT_imports(PyFNTTestCase):
	def test_import_loads_font_and_clears_file(self) -> None:
		gui = self.with_new_font()
		gui.file = 'previous.fnt'
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, return_value=_font()):
			gui.imports()
		self.pump(gui)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.edited)
		self.assertEqual(gui.status.get(), 'Font imported successfully!')

	def test_import_cancelled_dialog_aborts(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(None)), \
				mock.patch(BMP_TO_FNT) as bmptofnt:
			gui.imports()
		bmptofnt.assert_not_called()
		self.assertIsNone(gui.fnt)

	def test_import_paints_wait_status_before_work(self) -> None:
		gui = self.open_pyfnt()
		painted: list[str] = []
		def record_paint() -> None:
			painted.append(gui.status.get())
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, return_value=_font()), \
				mock.patch.object(gui, 'update_idletasks', side_effect=record_paint):
			gui.imports()
		self.assertIn('Importing FNT, please wait...', painted)

	def test_import_error_does_not_leave_wait_status(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=_info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, side_effect=PyMSError('Import', 'boom')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.imports()
		error_dialog.assert_called_once()
		self.assertEqual(gui.status.get(), 'Failed to import font.')
		self.assertIsNone(gui.fnt)


class Test_PyFNT_preview(PyFNTTestCase):
	def test_resize_builds_a_cell_per_pixel(self) -> None:
		gui = self.with_new_font()
		assert gui.fnt is not None
		self.assertEqual(len(gui.cells), gui.fnt.height)
		for row in gui.cells:
			self.assertEqual(len(row), gui.fnt.width)

	def test_preview_paints_letter_pixels(self) -> None:
		gui = self.with_new_font()
		assert gui.fnt is not None
		# Give the selected letter one recognizable pixel: value 7 maps to the
		# grayscale color (7, 7, 7) through the seeded special palette.
		gui.fnt.letters[0][1][2] = 7
		gui.preview()
		self.pump(gui)
		self.assertEqual(gui.canvas.itemcget(gui.cells[1][2].item_id, 'fill'), UI.Colors.to_html((7, 7, 7)))
		self.assertEqual(gui.canvas.itemcget(gui.cells[0][0].item_id, 'fill'), UI.Colors.to_html((0, 0, 0)))

	def test_close_clears_cells(self) -> None:
		gui = self.with_new_font()
		gui.close()
		self.assertEqual(gui.cells, [])
		self.assertIsNone(gui.fnt)
