
from .utils import PyFNTTestCase

from ...Utilities import UIKit as UI


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
