
from ..FileFormats.Tileset.Tileset import Tileset, TileType
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import Image, Misc

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .MegaEditorView import MegaEditorView

class TilePaletteDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def set_selecting(self, selecting): # type: (bool | None) -> None
		...

	def change(self, tile_type, id): # type: (TileType, int) -> None
		...

	def megaload(self): # type: () -> None
		...

	def mark_edited(self): # type: () -> None
		...

	def update_ranges(self): # type: () -> None
		...

class TilePaletteViewDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def tile_palette_binding_widget(self): # type: () -> Misc
		...

	def tile_palette_bind_updown(self): # type: () -> bool
		...

	def tile_palette_selection_changed(self): # type: () -> None
		...

	def tile_palette_double_clicked(self, id): # type: (int) -> None
		...

class MegaEditorDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def megaload(self): # type: () -> None
		...

	def draw_tiles(self, force): # type: (bool) -> None
		...

	def mark_edited(self): # type: () -> None
		...

class MegaEditorViewDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def mega_edit_mode_updated(self, mode): # type: (MegaEditorView.Mode) -> None
		...

	def draw_group(self): # type: () -> None
		...

	def mark_edited(self): # type: () -> None
		...

class MiniEditorDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def mark_edited(self): # type: () -> None
		...

	def draw_tiles(self, force): # type: (bool) -> None
		...

class PlaceabilityDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def mark_edited(self): # type: () -> None
		...
