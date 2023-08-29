
from ..FileFormats.DialogBIN import DialogBIN
from ..FileFormats.FNT import FNT
from ..FileFormats.PCX import PCX
from ..Utilities import Config
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.UIKit import PILImage, ImageTk, Anchor, Canvas

from typing import Protocol

class MainDelegate(Protocol):
	def get_bin(self) -> (DialogBIN | None):
		...

	def get_settings(self) -> Settings:
		...

	def get_mpqhandler(self) -> MPQHandler:
		...

	def get_scr_enabled(self) -> bool:
		...

	def mark_edited(self) -> None:
		...

	def refresh_preview(self) -> None:
		...

	def refresh_smks(self) -> None:
		...

	def refresh_nodes(self) -> None:
		...

class NodeDelegate(Protocol):
	def get_mpqhandler(self) -> MPQHandler:
		...

	def get_dialog_asset(self, asset_id: int) -> (PILImage.Image | None):
		...

	def get_dialog_frame(self, id: int) -> (PILImage.Image | None):
		...

	def get_show_hidden(self) -> bool:
		...

	def get_show_dialog(self) -> bool:
		...

	def get_show_smks(self) -> bool:
		...

	def get_show_animated(self) -> bool:
		...

	def get_show_images(self) -> bool:
		...

	def get_show_text(self) -> bool:
		...

	def get_show_bounds_widget(self) -> bool:
		...

	def get_show_bounds_group(self) -> bool:
		...

	def get_show_bounds_text(self) -> bool:
		...

	def get_show_bounds_responsive(self) -> bool:
		...

	def get_font(self, flags: int) -> FNT:
		...

	def get_tfontgam(self) -> PCX:
		...

	def get_tfont(self) -> (PCX | None):
		...

	def node_render_image_create(self, x: int, y: int, image: ImageTk.PhotoImage, anchor: Anchor) -> Canvas.Item: # type: ignore[name-defined]
		...

	def node_render_image_update(self, item: Canvas.Item, x: int, y: int, image: ImageTk.PhotoImage | None) -> None: # type: ignore[name-defined]
		...

	def node_render_rect_create(self, x1: int, y1: int, x2: int, y2: int, color: str) -> Canvas.Item: # type: ignore[name-defined]
		...

	def node_render_rect_update(self, item: Canvas.Item, x1: int, y1: int, x2: int, y2: int) -> None: # type: ignore[name-defined]
		...

	def node_render_lift(self, item: Canvas.Item) -> None: # type: ignore[name-defined]
		...

	def node_render_delete(self, item: Canvas.Item) -> None: # type: ignore[name-defined]
		...

	def capture_exception(self) -> None:
		...
