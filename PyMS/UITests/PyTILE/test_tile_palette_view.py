
import tkinter

from ..harness import UITestCase

from ...PyTILE.TilePaletteView import TilePaletteView

from ...FileFormats.Tileset.Tileset import Tileset, TileType
from ...FileFormats.Tileset.VX4 import VX4Megatile, VX4Minitile

from ...Utilities import UIKit as UI


class _Delegate:
	def __init__(self, window: UI.MainWindow, tileset: Tileset | None = None) -> None:
		self.window = window
		self.tileset = tileset
		self.selection_changes = 0

	def get_tileset(self) -> Tileset | None:
		return self.tileset

	def get_tile(self, _tile_id: int | VX4Minitile) -> UI.AnyPhotoImage:
		return tkinter.PhotoImage(master=self.window, width=32, height=32)

	def mark_edited(self) -> None:
		pass

	def tile_palette_binding_widget(self) -> UI.Misc:
		return self.window

	def tile_palette_bind_updown(self) -> bool:
		return False

	def tile_palette_selection_changed(self) -> None:
		self.selection_changes += 1

	def tile_palette_double_clicked(self, tile_id: int) -> None:
		pass


class Test_Multiselect(UITestCase):
	def _view(self) -> tuple[TilePaletteView, _Delegate]:
		window = self.make_window(UI.MainWindow)
		delegate = _Delegate(window)
		view = TilePaletteView(parent=window, delegate=delegate)
		view.pack(fill=UI.BOTH, expand=1)
		self.pump(window)
		return (view, delegate)

	def test_shift_select_with_no_anchor_toggles_the_tile(self) -> None:
		# The very first interaction being a Shift+Click must behave like a
		# Ctrl+Click toggle instead of failing on a missing anchor.
		view, delegate = self._view()
		view.select(3, modifier='shift')
		self.assertEqual(view.selected, [3])
		self.assertEqual(delegate.selection_changes, 1)

	def test_shift_select_extends_from_anchor(self) -> None:
		view, _ = self._view()
		view.select(2, modifier='set')
		view.select(5, modifier='shift')
		self.assertEqual(view.selected, [2, 3, 4, 5])

	def test_set_selection_clears_the_anchor(self) -> None:
		view, _ = self._view()
		view.select(2, modifier='set')
		view.set_selection([4])
		view.select(6, modifier='shift')
		self.assertEqual(view.selected, [4, 6])


class Test_Scroll_To_Selection(UITestCase):
	def test_scrolls_to_a_tile_below_the_viewport(self) -> None:
		window = self.make_window(UI.MainWindow)
		tileset = Tileset()
		tileset.new_file()
		for _ in range(200):
			tileset.vx4.add_megatile(VX4Megatile())
		delegate = _Delegate(window, tileset)
		view = TilePaletteView(parent=window, delegate=delegate, tiletype=TileType.mega, multiselect=False)
		view.pack(fill=UI.BOTH, expand=1)
		self.pump(window)
		self.assertEqual(view.canvas.yview()[0], 0.0)
		view.select(199)
		view.scroll_to_selection()
		self.pump(window)
		self.assertGreater(view.canvas.yview()[0], 0.0)
