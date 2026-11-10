from __future__ import annotations

from .BuilderView import ButtonSetBuilderView
from .ScriptView import ButtonSetScriptView
from ..GraftData import ButtonsGraftData

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The editor of a button set. Each mode is a tab, and a mode with unapplied changes asks before it's left.
class ButtonSetEditor(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		super().__init__(parent)
		self.entry_id: int | None = None
		self.entry_name = ''

		self.notebook = UI.Notebook(self)
		self.builder_view = ButtonSetBuilderView(self.notebook)
		self.script_view = ButtonSetScriptView(self.notebook, delegate, graft_data)
		self.notebook.add_tab(self.builder_view, 'Builder')
		self.notebook.add_tab(self.script_view, 'Script')
		self.notebook.display('Script')
		self.notebook.bind(UI.WidgetEvent.Notebook.TabActivated(), lambda _: self.load_active())
		self.notebook.pack(fill=UI.BOTH, expand=1)

	def active_view(self) -> ButtonSetBuilderView | ButtonSetScriptView:
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
