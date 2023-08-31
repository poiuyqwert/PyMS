
from __future__ import annotations

from .MegaEditorMode import MegaEditorMode

from ..FileFormats.Tileset.Tileset import Tileset, TileType
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import Image, Misc

from typing import Protocol

class MainDelegate(Protocol):
	def get_tileset(self) -> (Tileset | None):
		...

	def get_tile(self, id: int | VX4Minitile) -> Image:
		...

	def mark_edited(self) -> None:
		...

class TilePaletteDelegate(MainDelegate, Protocol):
	def change(self, tile_type: TileType, id: int) -> None:
		...

	def megaload(self) -> None:
		...

	def update_ranges(self) -> None:
		...

class TilePaletteViewDelegate(MainDelegate, Protocol):
	def tile_palette_binding_widget(self) -> Misc:
		...

	def tile_palette_bind_updown(self) -> bool:
		...

	def tile_palette_selection_changed(self) -> None:
		...

	def tile_palette_double_clicked(self, id: int) -> None:
		...

class MegaEditorDelegate(MainDelegate, Protocol):
	def megaload(self) -> None:
		...

	def draw_tiles(self, force: bool) -> None:
		...

class MegaEditorViewDelegate(MainDelegate, Protocol):
	def mega_edit_mode_updated(self, mode: MegaEditorMode) -> None:
		...

	def draw_group(self) -> None:
		...

class MiniEditorDelegate(MainDelegate, Protocol):
	def draw_tiles(self, force: bool) -> None:
		...

class GraphicsImporterDelegate(MainDelegate, Protocol):
	def imported_graphics(self, ids: list[int]) -> None:
		...
