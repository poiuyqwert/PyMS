from ..harness import UITestCase

from ...FileFormats.FNT import FNT, COLOR_CODES_INGAME
from ...FileFormats.PCX import PCX
from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.DataContext import DataContext
from ...Utilities.TextPreview.Layout import TextStyle, InlineImage, TextLayout
from ...Utilities.TextPreview.TextDrawing import TextDrawing

import tkinter

class _Host(UI.MainWindow):
	pass

class Test_TextDrawing(UITestCase):
	def setUp(self) -> None:
		super().setUp()
		self.window = self.make_window(_Host)
		self.canvas = UI.Canvas(self.window, width=200, height=100)
		self.canvas.pack()
		font = FNT()
		font.load(Assets.mpq_file_path('font', 'font8.fnt'))
		tfontgam = PCX()
		tfontgam.load(Assets.mpq_file_path('game', 'tfontgam.pcx'))
		self.data_context = DataContext(font8_fnt=font, tfontgam_pcx=tfontgam)
		self.style = TextStyle(font, tfontgam, COLOR_CODES_INGAME)

	def coords(self) -> list[tuple[int, int]]:
		return [(int(x), int(y)) for x, y in (tkinter.Canvas.coords(self.canvas, item.item_id) for item in self.canvas.find_all())]

	def test_draws_each_letter_into_the_canvas(self) -> None:
		layout = TextLayout.from_runs('AB', self.style)
		drawing = TextDrawing(layout, self.data_context)
		drawing.draw(self.canvas, 5, 7, tags='text')
		self.assertTrue(drawing.is_drawn())
		self.assertEqual(len(drawing.items), 2)
		self.assertEqual(self.coords(), [(5 + item.x, 7 + item.y) for item in layout.items])
		self.assertEqual(self.canvas.find_withtag('text'), self.canvas.find_all())

	def test_move_and_delete(self) -> None:
		layout = TextLayout.from_runs('AB', self.style)
		drawing = TextDrawing(layout, self.data_context)
		drawing.draw(self.canvas, 0, 0)
		drawing.move(10, 20)
		self.assertEqual(self.coords(), [(10 + item.x, 20 + item.y) for item in layout.items])
		drawing.delete()
		self.assertFalse(drawing.is_drawn())
		self.assertFalse(self.canvas.find_all())

	def test_drawing_again_replaces_the_items(self) -> None:
		drawing = TextDrawing(TextLayout.from_runs('AB', self.style), self.data_context)
		drawing.draw(self.canvas, 0, 0)
		drawing.draw(self.canvas, 0, 0)
		self.assertEqual(len(self.canvas.find_all()), 2)

	def test_images_stay_alive_when_the_glyphs_are_cleared(self) -> None:
		drawing = TextDrawing(TextLayout.from_runs('A', self.style), self.data_context)
		drawing.draw(self.canvas, 0, 0)
		image = drawing.images[0]
		self.data_context.set_font8_fnt(None)
		self.assertIs(drawing.images[0], image)
		self.assertEqual(self.canvas.itemcget(self.canvas.find_all()[0], 'image'), str(image))

	def test_inline_images_are_drawn_at_their_offset(self) -> None:
		photo = UI.PhotoImage(width=4, height=4)
		layout = TextLayout.from_runs([InlineImage(photo, width=4, height=4, x_offset=2), 'A'], self.style)
		drawing = TextDrawing(layout, self.data_context)
		drawing.draw(self.canvas, 10, 10)
		self.assertEqual(self.coords()[0], (8, 10))
