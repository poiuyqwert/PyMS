from __future__ import annotations

from ..GraftData import ReqGraftData
from ..ScriptEditor import ScriptView

from ...FileFormats.Graft import ReqScript
from ...FileFormats.Graft.CodeHandlers import GraftParseContext, GraftSerializeContext, GraftLanguage

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from ..Delegates import MainDelegate, ReqEditorDelegate

# The Script mode of the requirements editor, editing the selected entry's script as code (only its commands)
class ReqScriptView(ScriptView[ReqScript]):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, editor_delegate: ReqEditorDelegate, graft_data: ReqGraftData[Any]) -> None:
		self.editor_delegate = editor_delegate
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
		return self.editor_delegate.apply_script(compiled)
