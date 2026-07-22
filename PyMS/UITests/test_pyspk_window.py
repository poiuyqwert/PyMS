
from .harness import UITestCase

from ..PySPK.PySPK import PySPK
from ..FileFormats import SPK
from ..FileFormats.Palette import Palette
from ..Utilities.CheckSaved import CheckSaved

from unittest import mock

from typing import Any

# These tests drive PySPK through its public command methods and the stars/palette
# tab widgets, asserting on both widget state and the model. Outside-world
# boundaries — file dialogs, message boxes, the layer-count dialog, and the SPK
# parser — are stubbed per test so nothing blocks or touches disk. The harness
# already neutralizes settings I/O, analytics, the update check, and the tracer.

# Patch-target paths, named where they are looked up.
ASKYESNO = 'tkinter.messagebox.askyesno'
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
LAYER_COUNT_DIALOG = 'PyMS.PySPK.PySPK.LayerCountDialog'
INTERPRET_FILE = 'PyMS.FileFormats.SPK.SPK.interpret_file'


def _image(width: int = 2, height: int = 2) -> SPK.SPKImage:
	image = SPK.SPKImage()
	image.width = width
	image.height = height
	image.pixels = [[1] * width for _ in range(height)]
	return image


def _star(image: SPK.SPKImage, x: int, y: int) -> SPK.SPKStar:
	star = SPK.SPKStar(image)
	star.x = x
	star.y = y
	return star


class PySPKTestCase(UITestCase):
	def open_pyspk(self) -> PySPK:
		gui = self.make_window(PySPK)
		# The star palette normally loads from an MPQ during `initialize()`; a
		# default (all black) palette keeps image rendering self-contained.
		gui.platform_wpe = Palette()
		return gui

	def with_layers_of_stars(self, layers: int = 1, stars_per_layer: int = 3) -> PySPK:
		gui = self.open_pyspk()
		gui.new()
		image = _image()
		assert gui.spk is not None
		gui.spk.images.append(image)
		for l in range(layers):
			gui.add_layer()
			for i in range(stars_per_layer):
				gui.spk.layers[l].stars.append(_star(image, 10 * (i + 1), 10 * (i + 1)))
		gui.update_stars()
		self.pump(gui)
		return gui


class Test_PySPK_stars_tab_move_buttons(PySPKTestCase):
	def test_move_down_button_moves_selected_star_toward_end(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		first = gui.spk.layers[0].stars[0]
		gui.selected_stars.append(first)
		gui.update_selection()
		self.invoke(gui.stars_tab.move_down_button)
		self.assertEqual(gui.spk.layers[0].stars.index(first), 1)

	def test_move_up_button_moves_selected_star_toward_start(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		second = gui.spk.layers[0].stars[1]
		gui.selected_stars.append(second)
		gui.update_selection()
		self.invoke(gui.stars_tab.move_up_button)
		self.assertEqual(gui.spk.layers[0].stars.index(second), 0)


class Test_PySPK_stars_list_rows(PySPKTestCase):
	def test_rows_only_cover_visible_unlocked_layers(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		# Hide layer 0: its stars must vanish from the list, and the remaining
		# rows must map to layer 1's stars by index.
		gui.visible.set(gui.visible.get() & ~1)
		self.pump(gui)
		rows = gui.stars_tab.get_listbox_rows()
		assert gui.spk is not None
		self.assertEqual([star for star, _ in rows], gui.spk.layers[1].stars)
		self.assertEqual([layer for _, layer in rows], [1, 1])
		self.assertEqual(gui.stars_tab.listbox.size(), 2)

	def test_selection_highlight_uses_row_index_space(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		gui.visible.set(gui.visible.get() & ~1)
		self.pump(gui)
		assert gui.spk is not None
		gui.selected_stars.append(gui.spk.layers[1].stars[0])
		gui.stars_tab.update_selection()
		self.assertEqual(gui.stars_tab.listbox.curselection(), (0,))


class Test_PySPK_move_layer(PySPKTestCase):
	def test_move_layer_above_first_is_noop(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=1)
		assert gui.spk is not None
		original = list(gui.spk.layers)
		gui.layer.set(0)
		gui.move_layer(-1)
		self.assertEqual(gui.layer.get(), 0)
		self.assertEqual(gui.spk.layers, original)

	def test_move_layer_below_last_is_noop(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=1)
		assert gui.spk is not None
		original = list(gui.spk.layers)
		gui.layer.set(1)
		gui.move_layer(1)
		self.assertEqual(gui.layer.get(), 1)
		self.assertEqual(gui.spk.layers, original)

	def test_move_layer_swaps_adjacent_layers(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=1)
		assert gui.spk is not None
		top, bottom = gui.spk.layers
		gui.layer.set(0)
		gui.move_layer(1)
		self.assertEqual(gui.layer.get(), 1)
		self.assertEqual(gui.spk.layers, [bottom, top])


class Test_PySPK_delete_stars(PySPKTestCase):
	def test_delete_removes_selected_star_from_its_layer(self) -> None:
		gui = self.with_layers_of_stars(layers=2, stars_per_layer=2)
		assert gui.spk is not None
		star = gui.spk.layers[0].stars[0]
		untouched = list(gui.spk.layers[1].stars)
		gui.selected_stars.append(star)
		gui.update_selection()
		with mock.patch(ASKYESNO, return_value=True):
			gui.delete_stars()
		self.assertNotIn(star, gui.spk.layers[0].stars)
		self.assertEqual(gui.spk.layers[1].stars, untouched)
		self.assertEqual(gui.selected_stars, [])
		self.assertNotIn(star, gui.item_map)

	def test_delete_declined_keeps_stars(self) -> None:
		gui = self.with_layers_of_stars()
		assert gui.spk is not None
		star = gui.spk.layers[0].stars[0]
		gui.selected_stars.append(star)
		gui.update_selection()
		with mock.patch(ASKYESNO, return_value=False):
			gui.delete_stars()
		self.assertIn(star, gui.spk.layers[0].stars)


class Test_PySPK_import(PySPKTestCase):
	def test_import_marks_document_edited(self) -> None:
		# A freshly imported parallax is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.open_pyspk()
		def fake_interpret(spk: SPK.SPK, _filepath: Any, _layer_count: int) -> None:
			spk.layers = [SPK.SPKLayer()]
			spk.images = [_image()]
		with mock.patch(SELECT_OPEN, return_value='stars.bmp'), \
				mock.patch(LAYER_COUNT_DIALOG) as layer_count_dialog, \
				mock.patch(INTERPRET_FILE, autospec=True, side_effect=fake_interpret):
			layer_count_dialog.return_value.result.get.return_value = 1
			gui.iimport()
		self.pump(gui)
		self.assertIsNotNone(gui.spk)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.edited)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.open_pyspk()
		with mock.patch('PyMS.FileFormats.SPK.SPK.load', return_value=None):
			gui.open(file='opened.spk')
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.spk')
		def fake_interpret(spk: SPK.SPK, _filepath: Any, _layer_count: int) -> None:
			spk.layers = [SPK.SPKLayer()]
			spk.images = [_image()]
		with mock.patch(SELECT_OPEN, return_value='stars.bmp'), \
				mock.patch(LAYER_COUNT_DIALOG) as layer_count_dialog, \
				mock.patch(INTERPRET_FILE, autospec=True, side_effect=fake_interpret):
			layer_count_dialog.return_value.result.get.return_value = 1
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.spk')
		with mock.patch('PyMS.FileFormats.SPK.SPK.save', return_value=None) as spk_save, \
				mock.patch('PyMS.PySPK.PySPK.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		spk_save.assert_called_once_with('opened.spk')


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
			gui.spk.images.append(_image(width=10, height=80))
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
			gui.spk.images.append(_image(width=10, height=80))
		gui.selected_image = gui.spk.images[0]
		canvas = gui.palette_tab.starsCanvas
		canvas.config(scrollregion=(0, 0, 150, 1000))
		with mock.patch.object(canvas, 'yview', return_value=(0.0, 0.25)), \
				mock.patch.object(canvas, 'yview_moveto') as yview_moveto:
			gui.palette_tab.update_palette_selection(scroll=True)
		yview_moveto.assert_called_once()
		# Centering the first row would want a negative top; it clamps to 0.
		self.assertEqual(yview_moveto.call_args.args[0], 0.0)
