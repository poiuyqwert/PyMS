
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
if TYPE_CHECKING:
	from .Config import PyGRAFTConfig
	from ..Utilities.DataContext import DataContext
	from ..FileFormats.Graft import ReqScript

class MainDelegate(Protocol):
	config_: PyGRAFTConfig
	data_context: DataContext

	def update_status_bar(self) -> None:
		...

	def refresh(self) -> None:
		...

class ReqEditorDelegate(Protocol):
	def apply_script(self, script: ReqScript) -> bool:
		...
