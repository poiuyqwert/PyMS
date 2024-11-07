
from ..FileFormats.TRG import TRG

from typing import Protocol

class MainDelegate(Protocol):
    def get_trg(self) -> TRG.TRG: ...
