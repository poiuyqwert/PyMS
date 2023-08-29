
from ..FileFormats import SPK

from ..Utilities.UIKit import IntVar, Image
from ..Utilities import Config

from typing import Protocol

class MainDelegate(Protocol):
    spk: SPK.SPK | None
    settings: Settings
    tool: IntVar
    visible: IntVar
    locked: IntVar
    selected_stars: list[SPK.SPKStar]

    def is_file_open(self) -> bool:
        ...

    def are_stars_selected(self) -> bool:
        ...

    def update_selection(self) -> None:
        ...

    def get_image(self, spkimage: SPK.SPKImage) -> (Image | None):
        ...
