
from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
    from .DataContext import DataContext
    from .DataID import DATID
    from .Tabs.DATTab import DATTab

class MainDelegate(Protocol):
    data_context: 'DataContext'

    def change_tab(self, dat_id: 'DATID') -> None:
        ...

    def change_id(self, entry_id: int) -> None:
        ...

    def update_status_bar(self) -> None:
        ...

    def active_tab(self) -> 'DATTab':
        ...

    def refresh(self) -> None:
        ...

class SubDelegate(Protocol):
    id: int
    edited: bool
