
from .utils import PyFNTTestCase, SELECT_OPEN, INFO_DIALOG, info_dialog_stub, make_font

from ...PyFNT.InfoDialog import FontInfo
from ...Utilities.PyMSError import PyMSError

from unittest import mock

SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
FNT_TO_BMP = 'PyMS.PyFNT.PyFNT.fnttobmp'
BMP_TO_FNT = 'PyMS.PyFNT.PyFNT.bmptofnt'
BMP_CLASS = 'PyMS.PyFNT.PyFNT.BMP'
ERROR_DIALOG = 'PyMS.PyFNT.PyFNT.ErrorDialog'


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
				mock.patch(INFO_DIALOG, return_value=info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, return_value=make_font()):
			gui.imports()
		self.pump(gui)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.edited)
		self.assertEqual(gui.status.get(), 'Font imported successfully!')

	def test_import_cancelled_dialog_aborts(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=info_dialog_stub(None)), \
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
				mock.patch(INFO_DIALOG, return_value=info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, return_value=make_font()), \
				mock.patch.object(gui, 'update_idletasks', side_effect=record_paint):
			gui.imports()
		self.assertIn('Importing FNT, please wait...', painted)

	def test_import_error_does_not_leave_wait_status(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(SELECT_OPEN, return_value='font.bmp'), \
				mock.patch(INFO_DIALOG, return_value=info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))), \
				mock.patch(BMP_CLASS), \
				mock.patch(BMP_TO_FNT, side_effect=PyMSError('Import', 'boom')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.imports()
		error_dialog.assert_called_once()
		self.assertEqual(gui.status.get(), 'Failed to import font.')
		self.assertIsNone(gui.fnt)
