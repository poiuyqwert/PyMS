
from .utils import PyPALTestCase, make_event

from ...PyPAL.PyPAL import PyPAL
from ...Utilities import UIKit as UI

import tkinter
from unittest import mock

ASKCOLOR = 'tkinter.colorchooser.askcolor'


class Test_PyPAL_selection_and_status(PyPALTestCase):
	def test_select_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		gui.select(make_event(), 5)
		self.assertIsNone(gui.selected)

	def _sel_coords(self, gui: PyPAL) -> list[float]:
		# Read raw item coords via the base Canvas — UIKit's `coords` is a setter,
		# and absolute values carry an OS-dependent coordinate adjustment, so tests
		# compare positions relatively rather than against fixed pixels.
		return tkinter.Canvas.coords(gui.canvas, gui.sel.item_id)

	def test_select_moves_selection_rectangle(self) -> None:
		gui = self.with_new_palette()
		gui.select(make_event(), 0)
		origin = self._sel_coords(gui)
		gui.select(make_event(), 17)
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
		gui.colorstatus(make_event(), 5)
		self.assertEqual(gui.status.get(), 'Load or create a Palette.')

	def test_colorstatus_reports_color_under_cursor(self) -> None:
		gui = self.with_new_palette()
		gui.colorstatus(make_event(), 5)
		self.assertEqual(gui.status.get(), 'Index: 5  RGB: (0,0,0)  Hex: #000000')

	def test_colorstatus_leaving_swatch_clears_status(self) -> None:
		gui = self.with_new_palette()
		gui.colorstatus(make_event(), 5)
		# Index -1 is the "pointer left the palette" signal; the color readout is
		# cleared so it doesn't linger once the pointer is off the swatches.
		gui.colorstatus(make_event(), -1)
		self.assertEqual(gui.status.get(), '')

	def test_colorstatus_leaving_swatch_without_palette_keeps_status(self) -> None:
		gui = self.open_pypal()
		gui.colorstatus(make_event(), -1)
		self.assertEqual(gui.status.get(), 'Load or create a Palette.')


class Test_PyPAL_change_color(PyPALTestCase):
	def test_changecolor_without_palette_is_ignored(self) -> None:
		gui = self.open_pypal()
		with mock.patch(ASKCOLOR) as askcolor:
			gui.changecolor(make_event(), 5)
		askcolor.assert_not_called()
		self.assertFalse(gui.edited)

	def test_changecolor_applies_chosen_color(self) -> None:
		gui = self.with_new_palette()
		with mock.patch(ASKCOLOR, return_value=((10, 20, 30), '#0A141E')):
			gui.changecolor(make_event(), 5)
		self.pump(gui)
		assert gui.palette is not None
		self.assertTrue(gui.edited)
		self.assertEqual(gui.palette.palette[5], (10, 20, 30))
		self.assertEqual(gui.canvas.itemcget(6, 'fill'), '#0A141E')
		# The status-bar edit icon reflects the unsaved-changes state.
		self.assertEqual(str(gui.editstatus['state']), UI.NORMAL)

	def test_changecolor_stores_integer_components(self) -> None:
		# `askcolor` can return float components on some platforms; the stored
		# palette entry must be ints so binary saves and hex formatting work.
		gui = self.with_new_palette()
		with mock.patch(ASKCOLOR, return_value=((9.6, 20.0, 29.99609375), '#0A141E')):
			gui.changecolor(make_event(), 5)
		assert gui.palette is not None
		self.assertEqual(gui.palette.palette[5], (10, 20, 30))

	def test_changecolor_cancelled_chooser_leaves_palette(self) -> None:
		gui = self.with_new_palette()
		assert gui.palette is not None
		with mock.patch(ASKCOLOR, return_value=(None, None)):
			gui.changecolor(make_event(), 5)
		self.assertEqual(gui.palette.palette[5], (0, 0, 0))
		self.assertFalse(gui.edited)


class Test_PyPAL_repaint(PyPALTestCase):
	def test_update_canvas_paints_black_without_palette(self) -> None:
		gui = self.open_pypal()
		gui.canvas.itemconfigure(1, fill='#FFFFFF')
		gui.update_canvas()
		self.assertEqual(gui.canvas.itemcget(1, 'fill'), '#000000')
