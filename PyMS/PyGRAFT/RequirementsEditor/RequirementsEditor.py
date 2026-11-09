
from __future__ import annotations

from .BuilderView import ReqBuilderView
from .ScriptView import ReqScriptView
from ..GraftData import ReqGraftData

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The editor of a requirement script, shared by every requirements .graft file (only the commands available differ).
# Each mode is a tab, and a mode with unapplied changes asks before it's left.
class RequirementsEditor(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		super().__init__(parent)
		self.entry_id: int | None = None
		self.entry_name = ''

		self.notebook = UI.Notebook(self)
		self.builder_view = ReqBuilderView(self.notebook)
		self.script_view = ReqScriptView(self.notebook, delegate, graft_data)
		self.notebook.add_tab(self.builder_view, 'Builder')
		self.notebook.add_tab(self.script_view, 'Script')
		self.notebook.display('Script')
		self.notebook.bind(UI.WidgetEvent.Notebook.TabActivated(), lambda _: self.load_active())
		self.notebook.pack(fill=UI.BOTH, expand=1)

	def active_view(self) -> ReqBuilderView | ReqScriptView:
		if self.notebook.active is self.builder_view:
			return self.builder_view
		return self.script_view

	def load(self, entry_id: int | None, entry_name: str) -> None:
		self.entry_id = entry_id
		self.entry_name = entry_name
		self.load_active()

	def load_active(self) -> None:
		self.active_view().load(self.entry_id, self.entry_name)

	def confirm_leave(self) -> bool:
		return self.active_view().confirm_leave()

	def confirm_apply_before_save(self) -> bool:
		return self.active_view().confirm_apply_before_save()

	def update_highlight_styles(self) -> None:
		self.script_view.update_highlight_styles()
