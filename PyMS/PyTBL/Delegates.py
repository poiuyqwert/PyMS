
from .Config import PyTBLConfig

from ..FileFormats import TBL
from ..FileFormats import Palette
from ..FileFormats import GRP
from ..FileFormats import FNT
from ..FileFormats import PCX

# from ..Utilities import Config
from ..Utilities.UIKit import Text, ScrolledListbox

from typing import Protocol

class MainDelegate(Protocol):
    tbl: TBL.TBL | None
    config_: PyTBLConfig
    unitpal: Palette.Palette
    icons: GRP.GRP
    font8: FNT.FNT
    font10: FNT.FNT
    tfontgam: PCX.PCX

    text: Text
    listbox: ScrolledListbox

    def update(self) -> None:
        ...
