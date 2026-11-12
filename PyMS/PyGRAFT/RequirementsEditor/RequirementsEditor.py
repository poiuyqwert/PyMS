
from __future__ import annotations

from .BuilderView import ReqBuilderView
from .ScriptView import ReqScriptView
from ..GraftData import ReqGraftData

from ...FileFormats.Graft import ReqScript

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The editor of a requirement script, shared by every requirements .graft file (only the commands available differ).
# Each mode is a tab, and a mode with unapplied changes asks before it's left.
class RequirementsEditor(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		super().__init__(parent)
		self.graft_data = graft_data
		self.entry_id: int | None = None
		self.entry_name = ''

		self.notebook = UI.Notebook(self)
		self.builder_view = ReqBuilderView(self.notebook, delegate, self, graft_data)
		self.script_view = ReqScriptView(self.notebook, delegate, self, graft_data)
		self.notebook.add_tab(self.builder_view, 'Builder')
		self.notebook.add_tab(self.script_view, 'Script')
		self.notebook.display('Builder')
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

	# ReqEditorDelegate
	def apply_script(self, script: ReqScript) -> bool:
		# Stores the script into the file (marking it edited), asking whether an empty script removes the entry's script.
		# Returns `False` if the user cancelled.
		remove = False
		if not script.commands:
			ask_remove = UI.MessageBox.askyesnocancel(parent=self, title='Empty Script', message=f"The script for '{self.entry_name}' is empty. Remove its script?\n\nYes removes the script, No keeps an empty script.", default=UI.MessageBox.YES)
			if ask_remove is None:
				return False
			remove = ask_remove
		if remove:
			self.graft_data.graft.remove_script(script.entry_id)
		else:
			self.graft_data.graft.set_script(script)
		self.graft_data.edited = True
		return True

	def update_highlight_styles(self) -> None:
		self.script_view.update_highlight_styles()
