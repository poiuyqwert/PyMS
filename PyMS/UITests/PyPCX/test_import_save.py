
from .utils import PyPCXTestCase, SELECT_OPEN, ASK_SAVE, PALETTE

from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved

from unittest import mock

from typing import Any

SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
PCX_SAVE = 'PyMS.FileFormats.PCX.PCX.save'
PALETTE_LOAD = 'PyMS.FileFormats.Palette.Palette.load'

def _fake_palette_load(palette: Any, _file: Any) -> None:
	palette.palette = list(reversed(PALETTE))


class Test_PyPCX_import(PyPCXTestCase):
	def test_import_marks_content_edited(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_import_without_open_file_leaves_no_path(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		self.assertIsNone(gui.file)
		self.assertIn('(Untitled.pcx)', gui.title())

	def test_save_after_import_prompts_for_path(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		with mock.patch(SELECT_SAVE, return_value='chosen.pcx') as select_save, \
				mock.patch(PCX_SAVE) as pcx_save:
			result = gui.save()
		select_save.assert_called_once()
		pcx_save.assert_called_once_with('chosen.pcx')
		self.assertEqual(result, CheckSaved.saved)
		self.assertEqual(gui.file, 'chosen.pcx')

	def test_save_after_import_cancelled_prompt_saves_nothing(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		with mock.patch(SELECT_SAVE, return_value=None), \
				mock.patch(PCX_SAVE) as pcx_save:
			result = gui.save()
		pcx_save.assert_not_called()
		self.assertEqual(result, CheckSaved.cancelled)
		self.assertIsNone(gui.file)

	def test_close_after_import_prompts_to_save(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		with mock.patch(ASK_SAVE, return_value=False) as ask:
			gui.close()
		ask.assert_called_once()
		self.assertIsNone(gui.pcx)

	def test_import_into_open_file_marks_edited(self) -> None:
		gui = self.open_pypcx()
		self.open_pcx_file(gui)
		self.assertFalse(gui.edited)
		self.import_bmp(gui)
		self.assertTrue(gui.edited)
		self.assertEqual(gui.file, 'opened.pcx')


class Test_PyPCX_loadpal(PyPCXTestCase):
	def test_palette_import_marks_edited(self) -> None:
		gui = self.open_pypcx()
		self.open_pcx_file(gui)
		with mock.patch(SELECT_OPEN, return_value='colors.pal'), \
				mock.patch(PALETTE_LOAD, new=_fake_palette_load):
			gui.loadpal()
		self.pump(gui)
		assert gui.pcx is not None
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)
		self.assertEqual(gui.pcx.palette[0], (255, 255, 255))


class Test_PyPCX_saveas(PyPCXTestCase):
	def test_save_records_path_and_clears_edited(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		with mock.patch(SELECT_SAVE, return_value='chosen.pcx'), \
				mock.patch(PCX_SAVE):
			gui.saveas()
		self.pump(gui)
		self.assertEqual(gui.file, 'chosen.pcx')
		self.assertIn('(chosen.pcx)', gui.title())
		self.assertFalse(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.DISABLED)
