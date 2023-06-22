
from ..Utilities.UIKit import CodeText

from typing import Protocol

class FindDelegate(Protocol):
    def get_text(self) -> CodeText:
        ...
