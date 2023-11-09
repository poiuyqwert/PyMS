
from ..FileFormats.AIBIN import AIBIN

from ..Utilities.ActionManager import Action
from ..Utilities.CodeHandlers.CodeBlock import CodeBlock

from typing import Protocol

class ActionDelegate(Protocol):
	def get_ai_bin(self) -> AIBIN.AIBIN:
		...

	def refresh_scripts(self, select_script_ids: list[str] | None = None) -> None:
		...

class AddScriptAction(Action):
	def __init__(self, delegate: ActionDelegate, header: AIBIN.AIScriptHeader, last_selected_script_id: str | None) -> None:
		self.delegate = delegate
		self.header = header
		self.entry_point = CodeBlock()
		self.last_selected_script_id = last_selected_script_id
		super().__init__()

	def apply(self) -> None:
		self.delegate.get_ai_bin().add_script(self.header, self.entry_point)
		self.delegate.refresh_scripts([self.header.id])

	def undo(self) -> None:
		self.delegate.get_ai_bin().remove_script(self.header.id)
		if self.last_selected_script_id:
			self.delegate.refresh_scripts([self.last_selected_script_id])

class RemoveScriptsAction(Action):
	def __init__(self, delegate: ActionDelegate, scripts: list[tuple[AIBIN.AIScriptHeader, CodeBlock]]) -> None:
		self.delegate = delegate
		self.scripts = scripts
		super().__init__()

	def apply(self) -> None:
		for header,_ in self.scripts:
			self.delegate.get_ai_bin().remove_script(header.id)
		self.delegate.refresh_scripts()

	def undo(self) -> None:
		for header,entry_point in self.scripts:
			self.delegate.get_ai_bin().add_script(header, entry_point)
		self.delegate.refresh_scripts(list(header.id for header,_ in self.scripts))

class EditScriptAction(Action):
	def __init__(self, delegate: ActionDelegate, header: AIBIN.AIScriptHeader, entry_point: CodeBlock, new_id: str, new_flags: int, new_string_id: int) -> None:
		self.delegate = delegate
		self.header = header
		self.entry_point = entry_point

		self.old_id = header.id
		self.old_flags = header.flags
		self.old_string_id = header.string_id

		self.new_id = new_id
		self.new_flags = new_flags
		self.new_string_id = new_string_id

		super().__init__()

	def apply(self) -> None:
		ai_bin = self.delegate.get_ai_bin()
		self.header.id = self.new_id
		self.header.flags = self.new_flags
		self.header.string_id = self.new_string_id
		ai_bin.remove_script(self.old_id)
		ai_bin.add_script(self.header, self.entry_point)
		self.delegate.refresh_scripts([self.new_id])

	def undo(self) -> None:
		ai_bin = self.delegate.get_ai_bin()
		self.header.id = self.old_id
		self.header.flags = self.old_flags
		self.header.string_id = self.old_string_id
		ai_bin.remove_script(self.new_id)
		ai_bin.add_script(self.header, self.entry_point)
		self.delegate.refresh_scripts([self.old_id])

class EditFlagsAction(Action):
	def __init__(self, delegate: ActionDelegate, header: AIBIN.AIScriptHeader, new_flags: int) -> None:
		self.delegate = delegate
		self.header = header
		self.old_flags = self.header.flags
		self.new_flags = new_flags

	def apply(self) -> None:
		self.header.flags = self.new_flags
		self.delegate.refresh_scripts()

	def undo(self) -> None:
		self.header.flags = self.old_flags
		self.delegate.refresh_scripts()
