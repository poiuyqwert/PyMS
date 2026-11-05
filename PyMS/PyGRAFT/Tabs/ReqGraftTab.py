
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ReqGraftData

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for a requirements .graft file, listing the IDs that have a script
class ReqGraftTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate)

	def get_graft_data(self) -> ReqGraftData[Any]:
		return self.graft_data

	def entry_ids(self) -> list[int]:
		return self.graft_data.entry_ids()

	def entry_names(self) -> list[str]:
		entry_ids = self.entry_ids()
		if not entry_ids:
			return []
		max_id = max(entry_ids)
		keyword = self.graft_data.graft_type.HEADER_KEYWORD
		return [GraftTab.format_entry(entry_id, max_id, self.graft_data.entry_name(self.delegate.data_context, entry_id) or f'{keyword} {entry_id}') for entry_id in entry_ids]

	def selected_entry_id(self) -> int | None:
		entry_ids = self.entry_ids()
		if 0 <= self.selected < len(entry_ids):
			return entry_ids[self.selected]
		return None
