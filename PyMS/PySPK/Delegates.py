
from .Config import PySPKConfig

from ..FileFormats import SPK
from ..FileFormats import Palette

from ..Utilities.UIKit import IntVar, Image

from typing import Protocol

class MainDelegate(Protocol):
	spk: SPK.SPK | None
	platform_wpe: Palette.Palette
	config_: PySPKConfig
	tool: IntVar
	visible: IntVar
	locked: IntVar
	selected_stars: list[SPK.SPKStar]
	selected_image: SPK.SPKImage | None

	def is_file_open(self) -> bool:
		...

	def is_image_selected(self) -> bool:
		...

	def are_stars_selected(self) -> bool:
		...

	def update_selection(self) -> None:
		...

	def get_image(self, spkimage: SPK.SPKImage) -> (Image | None):
		...

	def action_states(self) -> None:
		...

	def edit(self) -> None:
		...
