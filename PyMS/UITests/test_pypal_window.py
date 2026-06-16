
from .harness import UITestCase

from ..PyPAL.PyPAL import PyPAL
from ..FileFormats.Palette import Palette
from ..Utilities import UIKit as UI
from ..Utilities.CheckSaved import CheckSaved
from ..Utilities.PyMSError import PyMSError

import io
import tkinter
from unittest import mock

from typing import Any, Callable

# These tests drive PyPAL through its public command methods and real widget
# seams (keyboard shortcuts, the canvas, the palette menu), asserting on both
# widget state and the model. Outside-world boundaries that a method reaches —
# file dialogs, message boxes, the color chooser, the on-disk save, and the
# secondary dialog windows — are stubbed per test so nothing blocks or touches
# disk. The harness already neutralizes settings I/O, analytics, the update
# check, and the tracer for construction.

# A recognizable 256-color palette: each entry is distinct so swatch colors and
# round-trips can be asserted precisely. Index 0 is black; index 1 is (1,2,3).
PALETTE = [(i, (i * 2) % 256, (i * 3) % 256) for i in range(256)]

# Patch-target paths, named where they are looked up.
ASKYESNOCANCEL = 'tkinter.messagebox.askyesnocancel'
ASKCOLOR = 'tkinter.colorchooser.askcolor'
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
SELECT_SAVE = 'PyMS.Utilities.Config.SelectFile.select_save'
PALETTE_SAVE = 'PyMS.FileFormats.Palette.Palette.save'
PALETTE_LOAD_FILE = 'PyMS.FileFormats.Palette.Palette.load'
ALLOW_OVERWRITE = 'PyMS.PyPAL.PyPAL.check_allow_overwrite_internal_file'
ERROR_DIALOG = 'PyMS.PyPAL.PyPAL.ErrorDialog'


def _raw_rgb_bytes() -> bytes:
	# 768-byte raw RGB dump — `Palette.load` detects this as `raw_rgb`.
	return bytes(component for color in PALETTE for component in color)


def _event(**attrs: Any) -> UI.Event:
	event: UI.Event = UI.Event()
	for name, value in attrs.items():
		setattr(event, name, value)
	return event


class PyPALTestCase(UITestCase):
	def open_pypal(self, factory: Callable[[], PyPAL] = PyPAL, extra_patches: dict[str, dict[str, Any]] | None = None) -> PyPAL:
		return self.make_window(factory, extra_patches=extra_patches)

	def with_new_palette(self) -> PyPAL:
		gui = self.open_pypal()
		gui.new()
		self.pump(gui)
		return gui

	def with_loaded_palette(self) -> PyPAL:
		# Drive the real Open flow with the file dialog stubbed to return an
		# in-memory palette stream, leaving a clean (unedited) loaded document.
		gui = self.open_pypal()
		with mock.patch(SELECT_OPEN, return_value=io.BytesIO(_raw_rgb_bytes())):
			gui.open()
		self.pump(gui)
		return gui


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
		gui.select(_event(), 5)
		self.assertEqual(gui.selected, 5)
		with mock.patch(SELECT_OPEN, return_value=io.BytesIO(_raw_rgb_bytes())):
			gui.open()
		# `open` only initializes the selection when none exists yet.
		self.assertEqual(gui.selected, 5)


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


class Test_PyPAL_selection_and_status(PyPALTestCase):
	def test_select_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		gui.select(_event(), 5)
		self.assertIsNone(gui.selected)

	def _sel_coords(self, gui: PyPAL) -> list[float]:
		# Read raw item coords via the base Canvas — UIKit's `coords` is a setter,
		# and absolute values carry an OS-dependent coordinate adjustment, so tests
		# compare positions relatively rather than against fixed pixels.
		return tkinter.Canvas.coords(gui.canvas, gui.sel.item_id)

	def test_select_moves_selection_rectangle(self) -> None:
		gui = self.with_new_palette()
		gui.select(_event(), 0)
		origin = self._sel_coords(gui)
		gui.select(_event(), 17)
		moved = self._sel_coords(gui)
		self.assertEqual(gui.selected, 17)
		# Index 17 sits one column right and one row down in the 16-wide grid of
		# 17-pixel cells, and the selection box is a 17x17 square.
		self.assertEqual(moved[0] - origin[0], 17.0)
		self.assertEqual(moved[1] - origin[1], 17.0)
		self.assertEqual(moved[2] - moved[0], 17.0)
		self.assertEqual(moved[3] - moved[1], 17.0)

	def test_colorstatus_without_palette_keeps_status(self) -> None:
		gui = self.open_pypal()
		gui.colorstatus(_event(), 5)
		self.assertEqual(gui.status.get(), 'Load or create a Palette.')

	def test_colorstatus_reports_color_under_cursor(self) -> None:
		gui = self.with_new_palette()
		gui.colorstatus(_event(), 5)
		self.assertEqual(gui.status.get(), 'Index: 5  RGB: (0,0,0)  Hex: #000000')

	def test_colorstatus_leaving_swatch_keeps_status(self) -> None:
		gui = self.with_new_palette()
		gui.status.set('sentinel')
		# Index -1 is the "pointer left the palette" signal; status is untouched.
		gui.colorstatus(_event(), -1)
		self.assertEqual(gui.status.get(), 'sentinel')


class Test_PyPAL_change_color(PyPALTestCase):
	def test_changecolor_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		with mock.patch(ASKCOLOR) as askcolor:
			gui.changecolor(_event(), 5)
		askcolor.assert_not_called()
		self.assertFalse(gui.edited)

	def test_changecolor_applies_chosen_color(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ASKCOLOR, return_value=((10, 20, 30), '#0A141E')):
			gui.changecolor(_event(), 5)
		self.pump(gui)
		assert gui.palette is not None
		self.assertTrue(gui.edited)
		self.assertEqual(gui.palette.palette[5], (10, 20, 30))
		self.assertEqual(gui.canvas.itemcget(6, 'fill'), '#0A141E')
		# The status-bar edit icon reflects the unsaved-changes state.
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_changecolor_cancelled_chooser_leaves_palette(self) -> None:
		gui = self.with_new_palette()
		assert gui.palette is not None
		with mock.patch(ASKCOLOR, return_value=(None, None)):
			gui.changecolor(_event(), 5)
		self.assertEqual(gui.palette.palette[5], (0, 0, 0))
		self.assertFalse(gui.edited)


class Test_PyPAL_clipboard(PyPALTestCase):
	def test_copy_without_selection_does_not_touch_clipboard(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui, 'clipboard_append') as clipboard_append:
			gui.copy()
		clipboard_append.assert_not_called()

	def test_copy_places_selected_color_on_clipboard(self) -> None:
		gui = self.with_new_palette()
		assert gui.palette is not None
		gui.palette.palette[1] = (1, 2, 3)
		gui.selected = 1
		gui.copy()
		self.assertEqual(gui.clipboard_get(), '#010203')

	def test_canpaste_parses_valid_hex(self) -> None:
		gui = self.open_pypal()
		self.assertEqual(gui.canpaste('#0A141E'), (10, 20, 30))

	def test_canpaste_rejects_non_color_text(self) -> None:
		gui = self.open_pypal()
		self.assertIsNone(gui.canpaste('not a color'))

	def test_canpaste_rejects_invalid_hex_digits(self) -> None:
		gui = self.open_pypal()
		self.assertIsNone(gui.canpaste('#GGGGGG'))

	def test_canpaste_reads_clipboard_when_no_argument(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui, 'selection_get', return_value='#0A141E'):
			self.assertEqual(gui.canpaste(), (10, 20, 30))

	def test_canpaste_handles_empty_clipboard(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui, 'selection_get', side_effect=Exception):
			self.assertIsNone(gui.canpaste())

	def test_paste_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui, 'selection_get', return_value='#0A141E'):
			gui.paste()
		self.assertIsNone(gui.palette)

	def test_paste_applies_clipboard_color(self) -> None:
		gui = self.with_new_palette()
		gui.selected = 2
		with mock.patch.object(gui, 'selection_get', return_value='#0A141E'):
			gui.paste()
		self.pump(gui)
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette[2], (10, 20, 30))
		self.assertEqual(gui.canvas.itemcget(3, 'fill'), '#0A141E')
		self.assertTrue(gui.edited)

	def test_paste_ignores_non_color_clipboard(self) -> None:
		gui = self.with_new_palette()
		gui.selected = 2
		assert gui.palette is not None
		with mock.patch.object(gui, 'selection_get', return_value='garbage'):
			gui.paste()
		self.assertEqual(gui.palette.palette[2], (0, 0, 0))
		self.assertFalse(gui.edited)


class Test_PyPAL_popup_menu(PyPALTestCase):
	def test_popup_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui.palmenu, 'post') as post:
			gui.popup(_event(x_root=5, y_root=5), 0)
		post.assert_not_called()
		self.assertIsNone(gui.selected)

	def test_popup_selects_color_and_posts_menu(self) -> None:
		gui = self.with_new_palette()
		# `canpaste` is consulted to enable/disable the menu's Paste entry; stub it
		# truthy so that branch runs, then confirm the menu is selected and posted.
		with mock.patch.object(gui, 'canpaste', return_value=(1, 2, 3)) as canpaste, \
				mock.patch.object(gui.palmenu, 'post') as post:
			gui.popup(_event(x_root=7, y_root=9), 3)
		self.assertEqual(gui.selected, 3)
		canpaste.assert_called_once()
		post.assert_called_once_with(7, 9)


class Test_PyPAL_update_title(PyPALTestCase):
	def test_title_without_document(self) -> None:
		gui = self.open_pypal()
		gui.file = None
		gui.palette = None
		gui.update_title()
		self.assertNotIn('(', gui.title())

	def test_title_for_unsaved_new_document(self) -> None:
		gui = self.open_pypal()
		gui.palette = Palette()
		gui.file = None
		gui.update_title()
		self.assertIn('(Untitled.pal)', gui.title())

	def test_title_for_named_file(self) -> None:
		gui = self.open_pypal()
		gui.file = 'colors.pal'
		gui.update_title()
		self.assertIn('(colors.pal)', gui.title())


class Test_PyPAL_edit_indicator(PyPALTestCase):
	def test_mark_edited_enables_indicator(self) -> None:
		gui = self.open_pypal()
		gui.mark_edited(True)
		self.assertTrue(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_mark_edited_false_disables_indicator(self) -> None:
		gui = self.open_pypal()
		gui.mark_edited(False)
		self.assertFalse(gui.edited)
		self.assertEqual(str(gui.editstatus['state']), UI.DISABLED)


class Test_PyPAL_repaint(PyPALTestCase):
	def test_update_canvas_paints_black_without_palette(self) -> None:
		gui = self.open_pypal()
		gui.canvas.itemconfigure(1, fill='#FFFFFF')
		gui.update_canvas()
		self.assertEqual(gui.canvas.itemcget(1, 'fill'), '#000000')


class Test_PyPAL_registry(PyPALTestCase):
	def test_register_registers_both_palette_extensions(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.registry.register') as register, \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.register_registry()
		self.assertEqual(register.call_count, 2)
		error_dialog.assert_not_called()

	def test_register_error_stops_and_reports(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.registry.register', side_effect=PyMSError('Registry', 'boom')) as register, \
				mock.patch(ERROR_DIALOG) as error_dialog:
			gui.register_registry()
		register.assert_called_once()
		error_dialog.assert_called_once()


class Test_PyPAL_secondary_dialogs(PyPALTestCase):
	def test_settings_opens_settings_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.SettingsDialog') as dialog:
			gui.sets()
		dialog.assert_called_once_with(gui, gui.config_)

	def test_help_opens_help_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.HelpDialog') as dialog:
			gui.help()
		dialog.assert_called_once()

	def test_about_opens_about_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.AboutDialog') as dialog:
			gui.about()
		dialog.assert_called_once()

	def test_sponsor_opens_sponsor_dialog(self) -> None:
		gui = self.open_pypal()
		with mock.patch('PyMS.PyPAL.PyPAL.SponsorDialog') as dialog:
			gui.sponsor()
		dialog.assert_called_once_with(gui)


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
