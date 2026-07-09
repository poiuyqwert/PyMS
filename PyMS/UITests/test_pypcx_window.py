
from .harness import UITestCase

from ..PyPCX.PyPCX import PyPCX
from ..FileFormats.PCX import PCX
from ..Utilities import UIKit as UI
from ..Utilities.CheckSaved import CheckSaved

from unittest import mock

from typing import Any

# These tests drive PyPCX through its public command methods, asserting on both
# widget state and the model. Outside-world boundaries — the file dialogs, the
# PCX/BMP/Palette loaders and savers, and the unsaved-changes prompt — are
# stubbed per test so nothing blocks or touches disk.

# Patch-target paths, named where they are looked up.
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
PCX_LOAD = 'PyMS.FileFormats.PCX.PCX.load'
PCX_SAVE = 'PyMS.FileFormats.PCX.PCX.save'
BMP_LOAD = 'PyMS.FileFormats.BMP.BMP.load'
PALETTE_LOAD = 'PyMS.FileFormats.Palette.Palette.load'
ASK_SAVE = 'tkinter.messagebox.askyesnocancel'

_PALETTE = [(i, i, i) for i in range(256)]

def _fake_bmp_load(bmp: Any, _file: Any) -> None:
	bmp.set_pixels([[0, 1], [2, 3]], _PALETTE)

def _fake_pcx_load(pcx: PCX, _file: Any) -> None:
	pcx.load_pixels([[0, 1], [2, 3]], _PALETTE)

def _fake_palette_load(palette: Any, _file: Any) -> None:
	palette.palette = list(reversed(_PALETTE))


class PyPCXTestCase(UITestCase):
	def open_pypcx(self) -> PyPCX:
		return self.make_window(PyPCX)

	def open_pcx_file(self, gui: PyPCX, file: str = 'opened.pcx') -> None:
		with mock.patch(SELECT_OPEN, return_value=file), \
				mock.patch(PCX_LOAD, new=_fake_pcx_load):
			gui.open()
		self.pump(gui)

	def import_bmp(self, gui: PyPCX) -> None:
		# Discard unsaved changes if prompted, so a repeat import can't block on
		# a real message box now that importing marks the content edited.
		with mock.patch(SELECT_OPEN, return_value='image.bmp'), \
				mock.patch(BMP_LOAD, new=_fake_bmp_load), \
				mock.patch(ASK_SAVE, return_value=False):
			gui.iimport()
		self.pump(gui)


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


class Test_PyPCX_preview(PyPCXTestCase):
	def test_preview_reuses_single_canvas_image(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		items = gui.canvas.find_all()
		self.assertEqual(len(items), 1)
		self.import_bmp(gui)
		gui.preview()
		self.pump(gui)
		self.assertEqual(gui.canvas.find_all(), items)
		assert gui.canvas_image is not None
		self.assertEqual(gui.canvas_image.cget('image'), str(gui.image))

	def test_close_hides_canvas_and_preview_restores_it(self) -> None:
		gui = self.open_pypcx()
		self.import_bmp(gui)
		self.assertEqual(gui.canvas.winfo_manager(), 'pack')
		with mock.patch(ASK_SAVE, return_value=False):
			gui.close()
		self.pump(gui)
		self.assertEqual(gui.canvas.winfo_manager(), '')
		self.assertEqual(gui.canvas.find_all(), [])
		self.import_bmp(gui)
		self.assertEqual(gui.canvas.winfo_manager(), 'pack')


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
