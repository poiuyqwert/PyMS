from __future__ import annotations

from ..GraftData import ReqGraftData
from ..ScriptEditor import ScriptView

from ...FileFormats.Graft import ReqScript
from ...FileFormats.Graft.CodeHandlers import GraftParseContext, GraftSerializeContext, GraftLanguage

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The Script mode of the requirements editor, editing the selected entry's script as code (only its commands)
class ReqScriptView(ScriptView[ReqScript]):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate, graft_data.graft_type.LANGUAGE.commands())

	def decompile_entry(self, serialize_context: GraftSerializeContext, entry_id: int) -> None:
		if self.graft_data.has_script(entry_id):
			self.graft_data.graft.decompile_script(serialize_context, entry_id)

	def language(self) -> GraftLanguage:
		return self.graft_data.graft_type.LANGUAGE()

	def compile_entry(self, parse_context: GraftParseContext, entry_id: int) -> ReqScript:
		return ReqScript.compile(parse_context, entry_id, self.graft_data.graft_type.LANGUAGE)

	def apply_compiled(self, compiled: ReqScript) -> bool:
		remove = False
		if not compiled.commands:
			ask_remove = UI.MessageBox.askyesnocancel(parent=self, title='Empty Script', message=f"The script for '{self.entry_name}' is empty. Remove its script?\n\nYes removes the script, No keeps an empty script.", default=UI.MessageBox.YES)
			if ask_remove is None:
				return False
			remove = ask_remove
		if remove:
			self.graft_data.graft.remove_script(compiled.entry_id)
		else:
			self.graft_data.graft.set_script(compiled)
		self.graft_data.edited = True
		return True
