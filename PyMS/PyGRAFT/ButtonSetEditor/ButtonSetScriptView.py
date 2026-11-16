from __future__ import annotations

from ..GraftData import ButtonsGraftData
from ..ScriptEditor import ScriptView

from ...FileFormats.Graft import ButtonSet
from ...FileFormats.Graft.CodeHandlers import GraftParseContext, GraftSerializeContext, GraftLanguage, ButtonsLanguage, ButtonCodeCommands

from ...Utilities import UIKit as UI

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The Script mode of the button set editor, editing the selected button set as code (only its `button` blocks)
class ButtonSetScriptView(ScriptView[ButtonSet]):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		self.graft_data = graft_data
		super().__init__(parent, delegate, ButtonCodeCommands.button_commands, (ButtonCodeCommands.ButtonBlock.keyword,))

	def decompile_entry(self, serialize_context: GraftSerializeContext, entry_id: int) -> None:
		self.graft_data.graft.decompile_button_set(serialize_context, entry_id)

	def language(self) -> GraftLanguage:
		return ButtonsLanguage()

	def compile_entry(self, parse_context: GraftParseContext, entry_id: int) -> ButtonSet:
		return ButtonSet.compile(parse_context, entry_id)

	def apply_compiled(self, compiled: ButtonSet) -> bool:
		# An empty button set is valid (it has no buttons), so there's nothing to ask
		assert self.entry_id is not None
		self.graft_data.graft.set_button_set(self.entry_id, compiled)
		self.graft_data.edited = True
		return True
