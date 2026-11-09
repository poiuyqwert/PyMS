
from __future__ import annotations

from .GraftTab import GraftTab
from ..GraftData import ReqGraftData
from ..RequirementsEditor import RequirementsEditor

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# Tab for a requirements .graft file, listing every entry of its dat file (entries without a script are dimmed)
class ReqGraftTab(GraftTab):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate)

	def build_editor(self) -> None:
		self.editor = RequirementsEditor(self, self.delegate, self.graft_data)
		self.editor.pack(fill=UI.BOTH, expand=1)

	def activate(self) -> None:
		# The code colors are shared by every requirements tab, and may have been changed in another
		self.editor.update_highlight_styles()

	def get_graft_data(self) -> ReqGraftData[Any]:
		return self.graft_data

	def entry_ids(self) -> list[int]:
		return self.graft_data.entry_ids(self.delegate.data_context)

	def entry_names(self) -> list[str]:
		entry_ids = self.entry_ids()
		if not entry_ids:
			return []
		max_id = max(entry_ids)
		keyword = self.graft_data.graft_type.HEADER_KEYWORD
		return [GraftTab.format_entry(entry_id, max_id, self.graft_data.entry_name(self.delegate.data_context, entry_id) or f'{keyword} {entry_id}') for entry_id in entry_ids]

	def dimmed_entries(self) -> set[int]:
		return {index for index, entry_id in enumerate(self.entry_ids()) if not self.graft_data.has_script(entry_id)}

	def selected_entry_id(self) -> int | None:
		entry_ids = self.entry_ids()
		if 0 <= self.selected < len(entry_ids):
			return entry_ids[self.selected]
		return None

	def load_selected(self) -> None:
		entry_id = self.selected_entry_id()
		entry_name = ''
		if entry_id is not None:
			entry_name = self.entry_names()[self.selected].strip()
		self.editor.load(entry_id, entry_name)

	def confirm_leave(self) -> bool:
		return self.editor.confirm_leave()

	def confirm_apply_before_save(self) -> bool:
		return self.editor.confirm_apply_before_save()
