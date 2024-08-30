
from .Delegates import ActionDelegate

from ..FileFormats.AIBIN import AIBIN

from ..Utilities.ActionManager import Action
from ..Utilities.CodeHandlers.CodeBlock import CodeBlock

class AddScriptAction(Action):
	def __init__(self, delegate: ActionDelegate, script: AIBIN.AIScript, last_selected_script_id: str | None) -> None:
		self.delegate = delegate
		self.script = script
		self.entry_point = CodeBlock()
		self.last_selected_script_id = last_selected_script_id
		super().__init__()

	def apply(self) -> None:
		self.delegate.get_ai_bin().add_script(self.script)
		self.delegate.refresh_scripts([self.script.id])

	def undo(self) -> None:
		self.delegate.get_ai_bin().remove_script(self.script.id)
		if self.last_selected_script_id:
			self.delegate.refresh_scripts([self.last_selected_script_id])

class RemoveScriptsAction(Action):
	def __init__(self, delegate: ActionDelegate, scripts: list[AIBIN.AIScript]) -> None:
		self.delegate = delegate
		self.scripts = scripts
		super().__init__()

	def apply(self) -> None:
		for script in self.scripts:
			self.delegate.get_ai_bin().remove_script(script.id)
		self.delegate.refresh_scripts()

	def undo(self) -> None:
		for script in self.scripts:
			self.delegate.get_ai_bin().add_script(script)
		self.delegate.refresh_scripts(list(script.id for script in self.scripts))

class EditScriptAction(Action):
	def __init__(self, delegate: ActionDelegate, script: AIBIN.AIScript, new_id: str, new_flags: int, new_string_id: int) -> None:
		self.delegate = delegate
		self.script = script

		self.old_id = script.id
		self.old_flags = script.flags
		self.old_string_id = script.string_id

		self.new_id = new_id
		self.new_flags = new_flags
		self.new_string_id = new_string_id

		super().__init__()

	def apply(self) -> None:
		ai_bin = self.delegate.get_ai_bin()
		self.script.id = self.new_id
		self.script.flags = self.new_flags
		self.script.string_id = self.new_string_id
		ai_bin.remove_script(self.old_id)
		ai_bin.add_script(self.script)
		self.delegate.refresh_scripts([self.new_id])

	def undo(self) -> None:
		ai_bin = self.delegate.get_ai_bin()
		self.script.id = self.old_id
		self.script.flags = self.old_flags
		self.script.string_id = self.old_string_id
		ai_bin.remove_script(self.new_id)
		ai_bin.add_script(self.script)
		self.delegate.refresh_scripts([self.old_id])

class EditFlagsAction(Action):
	def __init__(self, delegate: ActionDelegate, script: AIBIN.AIScript, new_flags: int) -> None:
		self.delegate = delegate
		self.script = script
		self.old_flags = self.script.flags
		self.new_flags = new_flags

	def apply(self) -> None:
		self.script.flags = self.new_flags
		self.delegate.refresh_scripts()

	def undo(self) -> None:
		self.script.flags = self.old_flags
		self.delegate.refresh_scripts()
