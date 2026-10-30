
from .utils import PySPKTestCase


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
