
from .utils import PyPALTestCase, make_event

from ...FileFormats.Palette import Palette
from ...Utilities import UIKit as UI
from ...Utilities.CheckSaved import CheckSaved

import re
from unittest import mock


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

	def test_paste_normalizes_clipboard_hex_casing(self) -> None:
		gui = self.with_new_palette()
		gui.selected = 2
		with mock.patch.object(gui, 'selection_get', return_value='#0a141e'):
			gui.paste()
		self.pump(gui)
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette[2], (10, 20, 30))
		# The swatch is filled from the parsed color, not the raw clipboard text.
		self.assertEqual(gui.canvas.itemcget(3, 'fill'), '#0A141E')

	def test_paste_reads_clipboard_once(self) -> None:
		gui = self.with_new_palette()
		gui.selected = 2
		with mock.patch.object(gui, 'selection_get', return_value='#0A141E') as selection_get:
			gui.paste()
		selection_get.assert_called_once()

	def test_paste_ignores_non_color_clipboard(self) -> None:
		gui = self.with_new_palette()
		gui.selected = 2
		assert gui.palette is not None
		with mock.patch.object(gui, 'selection_get', return_value='garbage'):
			gui.paste()
		self.assertEqual(gui.palette.palette[2], (0, 0, 0))
		self.assertFalse(gui.edited)


class Test_PyPAL_keyboard_shortcuts(PyPALTestCase):
	def test_ctrl_p_pastes_clipboard_color(self) -> None:
		# `Ctrl+P` belongs to the palette menu's Paste command: it applies the
		# clipboard color to the selected swatch and never opens a save dialog.
		gui = self.with_new_palette()
		self.show(gui)
		gui.selected = 2
		with mock.patch.object(gui, 'selection_get', return_value='#0A141E'), \
				mock.patch.object(gui, 'saveas', return_value=CheckSaved.saved) as saveas:
			self.shortcut(gui, UI.Ctrl.p)
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette[2], (10, 20, 30))
		saveas.assert_not_called()

	def test_ctrl_alt_p_is_bound_to_save_as_starcraft_pal(self) -> None:
		# Tk on Aqua drops synthesized Option-modified key events, so instead of
		# generating the keystroke this resolves the callback registered for the
		# shortcut's bind sequence and drives it directly.
		gui = self.with_loaded_palette()
		self.show(gui)
		script = gui.bind(UI.Ctrl.Alt.p())
		match = re.search(r'\[(\S+)', script)
		assert match is not None
		# Event substitution values: numeric fields need real integers, and %W
		# must be a real widget path for the Event to reconstruct.
		args = [str(gui) if field == '%W' else '0' for field in getattr(gui, '_subst_format')]
		with mock.patch.object(gui, 'saveas', return_value=CheckSaved.saved) as saveas:
			gui.tk.call(match.group(1), *args)
		saveas.assert_called_once_with(file_type=Palette.FileType.sc_pal)


class Test_PyPAL_popup_menu(PyPALTestCase):
	def test_popup_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		with mock.patch.object(gui.palmenu, 'post') as post:
			gui.popup(make_event(x_root=5, y_root=5), 0)
		post.assert_not_called()
		self.assertIsNone(gui.selected)

	def test_popup_selects_color_and_posts_menu(self) -> None:
		gui = self.with_new_palette()
		# `canpaste` is consulted to enable/disable the menu's Paste entry; stub it
		# truthy so that branch runs, then confirm the menu is selected and posted.
		with mock.patch.object(gui, 'canpaste', return_value=(1, 2, 3)) as canpaste, \
				mock.patch.object(gui.palmenu, 'post') as post:
			gui.popup(make_event(x_root=7, y_root=9), 3)
		self.assertEqual(gui.selected, 3)
		canpaste.assert_called_once()
		post.assert_called_once_with(7, 9)
