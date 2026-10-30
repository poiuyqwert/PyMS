
from .utils import PySPKTestCase, make_image

from unittest import mock


class Test_PySPK_palette_autoscroll(PySPKTestCase):
	def test_scroll_to_selection_passes_clamped_fraction(self) -> None:
		# Ten 80px images pad out to 100px rows (1000px total). With a viewport
		# showing 25% of that, centering the last image's row wants its center
		# (949) minus half the visible span (125) as the top: 0.824 — clamped to
		# the furthest reachable scroll position, 1 - 0.25 = 0.75.
		gui = self.open_pyspk()
		gui.new()
		assert gui.spk is not None
		for _ in range(10):
			gui.spk.images.append(make_image(width=10, height=80))
		gui.selected_image = gui.spk.images[-1]
		canvas = gui.palette_tab.starsCanvas
		canvas.config(scrollregion=(0, 0, 150, 1000))
		with mock.patch.object(canvas, 'yview', return_value=(0.0, 0.25)), \
				mock.patch.object(canvas, 'yview_moveto') as yview_moveto:
			gui.palette_tab.update_palette_selection(scroll=True)
		yview_moveto.assert_called_once()
		self.assertAlmostEqual(yview_moveto.call_args.args[0], 0.75)

	def test_scroll_to_early_selection_stays_at_top(self) -> None:
		gui = self.open_pyspk()
		gui.new()
		assert gui.spk is not None
		for _ in range(10):
			gui.spk.images.append(make_image(width=10, height=80))
		gui.selected_image = gui.spk.images[0]
		canvas = gui.palette_tab.starsCanvas
		canvas.config(scrollregion=(0, 0, 150, 1000))
		with mock.patch.object(canvas, 'yview', return_value=(0.0, 0.25)), \
				mock.patch.object(canvas, 'yview_moveto') as yview_moveto:
			gui.palette_tab.update_palette_selection(scroll=True)
		yview_moveto.assert_called_once()
		# Centering the first row would want a negative top; it clamps to 0.
		self.assertEqual(yview_moveto.call_args.args[0], 0.0)
