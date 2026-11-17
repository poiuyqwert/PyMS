
from .Config import PyTBLConfig

from ..FileFormats import TBL

from ..Utilities import UIKit as UI
from ..Utilities.DataContext import DataContext

from typing import Protocol

class MainDelegate(Protocol):
	tbl: TBL.TBL | None
	config_: PyTBLConfig
	data_context: DataContext

	text: UI.Text
	listbox: UI.ScrolledListbox

	def update(self) -> None:
		...
