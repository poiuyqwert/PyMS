
from ..FileFormats.Tileset.Tileset import Tileset, TileType
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import Image, Misc

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .MegaEditorView import MegaEditorView

class MainDelegate(Protocol):
	def get_tileset(self): # type: () -> (Tileset | None)
		...

	def get_tile(self, id): # type: (int | VX4Minitile) -> Image
		...

	def mark_edited(self): # type: () -> None
		...

class TilePaletteDelegate(MainDelegate, Protocol):
	def change(self, tile_type, id): # type: (TileType, int) -> None
		...

	def megaload(self): # type: () -> None
		...

	def update_ranges(self): # type: () -> None
		...

class TilePaletteViewDelegate(MainDelegate, Protocol):
	def tile_palette_binding_widget(self): # type: () -> Misc
		...

	def tile_palette_bind_updown(self): # type: () -> bool
		...

	def tile_palette_selection_changed(self): # type: () -> None
		...

	def tile_palette_double_clicked(self, id): # type: (int) -> None
		...

class MegaEditorDelegate(MainDelegate, Protocol):
	def megaload(self): # type: () -> None
		...

	def draw_tiles(self, force): # type: (bool) -> None
		...

class MegaEditorViewDelegate(MainDelegate, Protocol):
	def mega_edit_mode_updated(self, mode): # type: (MegaEditorView.Mode) -> None
		...

	def draw_group(self): # type: () -> None
		...

class MiniEditorDelegate(MainDelegate, Protocol):
	def draw_tiles(self, force): # type: (bool) -> None
		...

class GraphicsImporterDelegate(MainDelegate, Protocol):
	def imported_graphics(self, ids: list[int]) -> None:
		...
