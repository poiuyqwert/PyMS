from ..harness import UITestCase

from ...FileFormats.FNT import FNT
from ...FileFormats.PCX import PCX
from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.DataContext import DataContext
from ...Utilities.TextPreview.TextDrawing import TextDrawing
from ...Utilities.TextPreview.TextPreviewTooltip import TextPreviewTooltip

class _Host(UI.MainWindow):
	pass

class Test_TextPreviewTooltip(UITestCase):
	def setUp(self) -> None:
		super().setUp()
		self.window = self.make_window(_Host)
		self.parent = UI.Canvas(self.window, width=50, height=50)
		self.parent.pack()
		font = FNT()
		font.load(Assets.mpq_file_path('font', 'font8.fnt'))
		tfontgam = PCX()
		tfontgam.load(Assets.mpq_file_path('game', 'tfontgam.pcx'))
		self.data_context = DataContext(font8_fnt=font, tfontgam_pcx=tfontgam)
		self.text: str | None = 'Short'
		self.tooltip = TextPreviewTooltip(self.parent, self.drawing)
		self.show(self.window)

	def drawing(self) -> TextDrawing | None:
		if self.text is None:
			return None
		return TextDrawing.tooltip(self.text, self.data_context)

	def tip_size(self) -> tuple[int, int]:
		assert self.tooltip.canvas is not None
		return (int(self.tooltip.canvas.cget('width')), int(self.tooltip.canvas.cget('height')))

	def test_refresh_shows_a_hidden_tip_right_away(self) -> None:
		self.tooltip.enter()
		self.assertIsNotNone(self.tooltip.id)
		self.tooltip.refresh()
		self.assertIsNone(self.tooltip.id)
		self.assertIsNotNone(self.tooltip.tip)
		self.tooltip.hidetip()

	def test_refresh_redraws_a_shown_tip_in_its_window(self) -> None:
		self.tooltip.showtip()
		tip = self.tooltip.tip
		short_size = self.tip_size()
		self.text = 'A much longer tooltip text'
		self.tooltip.refresh()
		self.pump(self.window)
		self.assertIs(self.tooltip.tip, tip)
		assert self.tooltip.drawing is not None
		padding = TextPreviewTooltip.PADDING
		self.assertEqual(self.tip_size(), (self.tooltip.drawing.width + padding * 2, self.tooltip.drawing.height + padding * 2))
		self.assertGreater(self.tip_size()[0], short_size[0])
		# Only the new drawing is in the window
		self.assertEqual(len(self.tooltip.drawing.items), len(self.tooltip.canvas.find_all()) if self.tooltip.canvas else -1)
		self.tooltip.hidetip()

	def test_refresh_hides_the_tip_without_a_drawing(self) -> None:
		self.tooltip.showtip()
		self.text = None
		self.tooltip.refresh()
		self.assertIsNone(self.tooltip.tip)
		self.assertIsNone(self.tooltip.drawing)
