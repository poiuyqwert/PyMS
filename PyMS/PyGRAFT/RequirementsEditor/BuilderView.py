from __future__ import annotations

from .OpcodeEditorView import OpcodeEditorView
from ..EditorModeView import EditorModeView
from ..GraftData import ReqGraftData

from ...FileFormats.Graft import ReqScript
from ...FileFormats.Graft.CodeHandlers import RequirementCodeCommands, GraftLexer, GraftParseContext
from ...FileFormats.Graft.CodeHandlers.RequirementCodeCommands import ReqCommandDefinition
from ...FileFormats.Graft.CodeHandlers.CodeTypes import UnitCodeType, TechCodeType

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeType import IntCodeType
from ...Utilities.EditedState import EditedState
from ...Utilities.PyMSError import PyMSError
from ...Utilities.ErrorDialog import ErrorDialog

from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from ..Delegates import MainDelegate, ReqEditorDelegate

# The Builder mode of the requirements editor, editing the selected entry's script as a list of opcodes (one row each)
class ReqBuilderView(EditorModeView):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, editor_delegate: ReqEditorDelegate, graft_data: ReqGraftData[Any]) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.editor_delegate = editor_delegate
		self.graft_data = graft_data
		language = graft_data.graft_type.LANGUAGE
		self.language = language
		self.available_commands: list[ReqCommandDefinition] = []
		for cmd_def in language.commands():
			assert isinstance(cmd_def, ReqCommandDefinition)
			self.available_commands.append(cmd_def)
		# The script being edited, applied to the file only when the changes are applied
		self.commands: list[CodeCommand] = []
		self.rows: list[OpcodeEditorView] = []

		self.edited_state = EditedState()
		self.edited_state.callback += self.update_edited

		self.toolbar = UI.Toolbar(self)
		self.apply_button = self.add_button('save', self.apply_changes, 'Apply Changes', UI.Ctrl.Return)
		self.revert_button = self.add_button('reset', self.revert, 'Revert Changes')
		self.toolbar.add_gap()
		self.test_button = self.add_button('test', self.test, 'Test Script', UI.Ctrl.t)
		self.toolbar.add_section()
		self.add_opcode_button = self.add_button('add', self.add_opcode, 'Add Opcode')
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)

		# The entry is selected in the main window's list, so the status bar only shows the edited state
		statusbar = UI.StatusBar(self)
		statusbar.add_spacer(weight=0.5)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_spacer()
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.scroll_view = UI.ScrollView(self)
		self.scroll_view.pack(fill=UI.BOTH, expand=1, padx=1, pady=1)

		self.update_edited(False)
		self.update_read_only()

	def add_button(self, icon: str, callback: Callable[[], Any], tooltip: str, shortcut: UI.EventPattern | None = None) -> UI.Button:
		button = self.toolbar.add_button(Assets.get_image(icon), callback, tooltip, shortcut, bind_shortcut=False)
		if shortcut:
			# Every requirements tab has a Builder, so the shortcuts are added to the window (not replacing the others), and only the visible Builder runs them.
			# The Script mode's shortcuts are bound on its text and stop there, so they don't reach these.
			def triggered(_event: UI.Event) -> None:
				if button['state'] != UI.DISABLED and button.winfo_viewable():
					callback()
			self.winfo_toplevel().bind(shortcut(), triggered, True)
		return button

	# Edited state

	def is_edited(self) -> bool:
		return self.edited_state.is_edited

	def update_edited(self, edited: bool) -> None:
		state = UI.NORMAL if edited else UI.DISABLED
		self.apply_button['state'] = state
		self.revert_button['state'] = state
		self.editstatus['state'] = state

	def update_read_only(self) -> None:
		# Without a selected entry there is nothing to edit
		state = UI.DISABLED if self.entry_id is None else UI.NORMAL
		self.test_button['state'] = state
		self.add_opcode_button['state'] = state

	def mark_edited(self) -> None:
		self.sync_rows()
		self.edited_state.mark_edited()

	# Loading

	def load(self, entry_id: int | None, entry_name: str) -> None:
		self.entry_id = entry_id
		self.entry_name = entry_name
		self.commands = []
		if entry_id is not None and (script := self.graft_data.graft.get_script(entry_id)):
			self.commands = [CodeCommand(command.definition, list(command.params)) for command in script.commands]
		# The unit/tech names may have changed since the rows were made
		for row in self.rows:
			row.refresh_param_entries()
		self.sync_rows()
		self.update_read_only()
		self.edited_state.mark_edited(False)

	@staticmethod
	def indents(commands: list[CodeCommand]) -> list[int]:
		# Each command's indent, like the code: the commands after an upgrade level (up to and including its `end_level_requirements`) are indented, and `level_3_requires` indents the rest of the script
		indents: list[int] = []
		in_sublist = False
		for command in commands:
			indents.append(1 if in_sublist else 0)
			if (command.definition in RequirementCodeCommands.sublist_commands or command.definition is RequirementCodeCommands.Level3Requires) and not in_sublist:
				in_sublist = True
			elif command.definition is RequirementCodeCommands.EndLevelRequirements and in_sublist:
				in_sublist = False
		return indents

	def sync_rows(self) -> None:
		# Shows the commands in the rows (reusing the rows already made), clearing any error highlight.
		# New rows are only shown once they're loaded, so they all appear at once with their opcodes.
		while len(self.rows) > len(self.commands):
			self.rows.pop().destroy()
		new_rows: list[OpcodeEditorView] = []
		while len(self.rows) < len(self.commands):
			row = OpcodeEditorView(self.scroll_view.content_view, self, self.available_commands)
			self.rows.append(row)
			new_rows.append(row)
		indents = ReqBuilderView.indents(self.commands)
		for index, (row, command, indent) in enumerate(zip(self.rows, self.commands, indents)):
			definition = command.definition
			assert isinstance(definition, ReqCommandDefinition)
			row.set_command(index, definition, command.params, indent=indent, is_last=index == len(self.commands) - 1)
			row.set_error(False)
		for row in new_rows:
			row.pack(side=UI.TOP, fill=UI.X)

	# OpcodeEditorDelegate

	def opcode_changed(self, index: int, cmd_def: ReqCommandDefinition, params: list[int]) -> None:
		self.commands[index] = CodeCommand(cmd_def, list(params))
		self.mark_edited()

	def move_opcode(self, index: int, delta: int) -> None:
		other = index + delta
		if not 0 <= other < len(self.commands):
			return
		self.commands[index], self.commands[other] = self.commands[other], self.commands[index]
		self.mark_edited()

	def delete_opcode(self, index: int) -> None:
		del self.commands[index]
		self.mark_edited()

	def add_opcode_after(self, index: int) -> None:
		self.insert_opcode(index + 1)

	def param_limits(self, param_type: IntCodeType) -> tuple[int, int]:
		return param_type.get_limits(GraftParseContext(GraftLexer(''), self.delegate.data_context, self.language()))

	def param_entries(self, param_type: IntCodeType) -> list[tuple[str, int | None]]:
		names: tuple[str, ...] = ()
		if isinstance(param_type, UnitCodeType):
			names = self.delegate.data_context.unit_display_names()
		elif isinstance(param_type, TechCodeType):
			names = self.delegate.data_context.tech_display_names()
		min_value, max_value = self.param_limits(param_type)
		# Any ID can be entered, so IDs without a name show the catch-all entry
		return [*((name, entry_id) for entry_id, name in enumerate(names) if min_value <= entry_id <= max_value), ('Unknown', None)]

	# Actions

	def add_opcode(self) -> None:
		self.insert_opcode(len(self.commands))

	def insert_opcode(self, index: int) -> None:
		if self.entry_id is None:
			return
		self.commands.insert(index, CodeCommand(RequirementCodeCommands.HasCompleted, [0]))
		self.mark_edited()
		self.scroll_to_row(index)

	def scroll_to_row(self, index: int) -> None:
		UI.Misc.update_idletasks(self)
		self.scroll_view.scroll_to_view(self.rows[index])

	def validate(self) -> ReqScript | None:
		# The edited script, or `None` after highlighting and showing its error
		if self.entry_id is None:
			return None
		script = ReqScript(self.entry_id, [CodeCommand(command.definition, list(command.params)) for command in self.commands])
		if invalid := script.find_invalid_command(self.language):
			error, index = invalid
			self.rows[index].set_error(True)
			self.scroll_to_row(index)
			ErrorDialog(self, PyMSError('Validate', error))
			return None
		return script

	def test(self) -> None:
		if self.validate() is None:
			return
		UI.MessageBox.showinfo(parent=self, title='Test Completed', message='The script has no errors.')

	def apply_changes(self) -> None:
		self.apply()

	def apply(self) -> bool:
		script = self.validate()
		if script is None:
			return False
		if not self.editor_delegate.apply_script(script):
			return False
		# Refreshing updates the list and status bar, and reloads the script (no longer edited)
		self.delegate.refresh()
		return True
