
from .utils import PyPALTestCase, PALETTE, ASKYESNOCANCEL, SELECT_OPEN, ERROR_DIALOG, raw_rgb_bytes, make_event

from ...PyPAL.PyPAL import PyPAL
from ...FileFormats.Palette import Palette
from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved
from ...Utilities.PyMSError import PyMSError

import io
import tkinter
from unittest import mock

from typing import Any

PALETTE_LOAD_FILE = 'PyMS.FileFormats.Palette.Palette.load'


class Test_PyPAL_startup(PyPALTestCase):
	def test_startup_has_no_file_and_disabled_actions(self) -> None:
		gui = self.open_pypal()
		self.assertIsNone(gui.palette)
		self.assertIsNone(gui.selected)
		self.assertFalse(gui.edited)
		self.assertFalse(gui.is_file_open())
		self.assertTrue(gui.title().startswith('PyPAL '))
		self.assertNotIn('(', gui.title())
		self.assertEqual(gui.status.get(), 'Load or create a Palette.')
		self.assertFalse(gui.toolbar.tag_is_enabled('file_open'))
		self.assertFalse(gui.toolbar.tag_is_enabled('format_known'))
		# Without a palette every swatch is painted black.
		self.assertEqual(gui.canvas.itemcget(1, 'fill'), '#000000')

	def test_guifile_argument_opens_palette_on_startup(self) -> None:
		def fake_load(palette: Palette, _file: Any) -> None:
			palette.palette = list(PALETTE)
			palette.format = Palette.Format.raw_rgb
		gui = self.open_pypal(
			factory=lambda: PyPAL('startup.pal'),
			extra_patches={PALETTE_LOAD_FILE: {'new': fake_load}},
		)
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette, PALETTE)
		self.assertEqual(gui.file, 'startup.pal')
		self.assertIn('(startup.pal)', gui.title())


class Test_PyPAL_check_saved(PyPALTestCase):
	def test_no_palette_is_saved(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(gui.check_saved(), CheckSaved.saved)

	def test_unedited_palette_is_saved(self) -> None:
		gui = self.with_new_palette()
		self.assertFalse(gui.edited)
		self.assertEqual(gui.check_saved(), CheckSaved.saved)

	def test_edited_then_cancel_prompt_is_cancelled(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		with mock.patch(ASKYESNOCANCEL, return_value=None):
			self.assertEqual(gui.check_saved(), CheckSaved.cancelled)

	def test_edited_then_discard_is_saved(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		with mock.patch(ASKYESNOCANCEL, return_value=False):
			self.assertEqual(gui.check_saved(), CheckSaved.saved)

	def test_edited_then_save_with_existing_file_delegates_to_save(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		gui.file = 'existing.pal'
		with mock.patch(ASKYESNOCANCEL, return_value=True), \
				mock.patch.object(gui, 'save', return_value=CheckSaved.saved) as save:
			self.assertEqual(gui.check_saved(), CheckSaved.saved)
		save.assert_called_once_with()

	def test_edited_then_save_without_file_delegates_to_saveas(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		with mock.patch(ASKYESNOCANCEL, return_value=True), \
				mock.patch.object(gui, 'saveas', return_value=CheckSaved.saved) as saveas:
			self.assertEqual(gui.check_saved(), CheckSaved.saved)
		saveas.assert_called_once_with()


class Test_PyPAL_new(PyPALTestCase):
	def test_new_populates_model_and_enables_file_actions(self) -> None:
		gui = self.with_new_palette()
		assert gui.palette is not None
		self.assertEqual(len(gui.palette.palette), 256)
		self.assertIsNone(gui.file)
		self.assertIsNone(gui.format)
		self.assertEqual(gui.selected, 0)
		self.assertFalse(gui.edited)
		self.assertIn('(Untitled.pal)', gui.title())
		# `new` selects index 0, so the status bar ends on that color's readout.
		self.assertTrue(gui.status.get().startswith('Index: 0'))
		# `file_open` turns on; `format_known` stays off until a format is chosen.
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))
		self.assertFalse(gui.toolbar.tag_is_enabled('format_known'))
		self.assertEqual(gui.canvas.itemcget(1, 'fill'), '#000000')

	def test_new_cancelled_when_unsaved_changes_kept(self) -> None:
		gui = self.with_new_palette()
		gui.mark_edited(True)
		original = gui.palette
		with mock.patch(ASKYESNOCANCEL, return_value=None):
			gui.new()
		self.assertIs(gui.palette, original)

	def test_new_via_keyboard_shortcut(self) -> None:
		gui = self.open_pypal()
		# The shortcut binding ignores non-viewable buttons, so show the window
		# before generating the key event.
		self.show(gui)
		self.shortcut(gui, UI.Ctrl.n)
		self.assertIsNotNone(gui.palette)
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))


class Test_PyPAL_open(PyPALTestCase):
	def test_open_via_file_dialog_loads_palette_into_canvas(self) -> None:
		gui = self.with_loaded_palette()
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette, PALETTE)
		self.assertEqual(gui.format, Palette.Format.raw_rgb)
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))
		self.assertTrue(gui.toolbar.tag_is_enabled('format_known'))
		# Swatch n shows color n: index 1 is (1, 2, 3).
		self.assertEqual(gui.canvas.itemcget(2, 'fill'), UI.Colors.to_html(PALETTE[1]))

	def test_open_cancelled_dialog_leaves_no_palette(self) -> None:
		gui = self.open_pypal()
		with mock.patch(SELECT_OPEN, return_value=None):
			gui.open()
		self.assertIsNone(gui.palette)

	def test_open_load_error_shows_error_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch(SELECT_OPEN, return_value='broken.pal'), \
				mock.patch(PALETTE_LOAD_FILE, side_effect=PyMSError('Load', 'boom')), \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.open()
		self.assertIsNone(gui.palette)
		error_dialog.assert_called_once()

	def test_open_preserves_existing_selection(self) -> None:
		gui = self.with_new_palette()
		gui.select(make_event(), 5)
		self.assertEqual(gui.selected, 5)
		with mock.patch(SELECT_OPEN, return_value=io.BytesIO(raw_rgb_bytes())):
			gui.open()
		# `open` re-applies the selection, keeping the prior index.
		self.assertEqual(gui.selected, 5)

	def test_open_restores_selection_highlight_after_close(self) -> None:
		# After `close` the selection is cleared and its rectangle collapsed;
		# loading a file must leave the highlight at a defined position again.
		gui = self.with_loaded_palette()
		gui.close()
		self.assertIsNone(gui.selected)
		with mock.patch(SELECT_OPEN, return_value=io.BytesIO(raw_rgb_bytes())):
			gui.open()
		self.assertEqual(gui.selected, 0)
		coords = tkinter.Canvas.coords(gui.canvas, gui.sel.item_id)
		self.assertEqual(coords[2] - coords[0], 17.0)
		self.assertEqual(coords[3] - coords[1], 17.0)
