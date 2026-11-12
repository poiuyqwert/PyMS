from __future__ import annotations

from ...FileFormats.Graft.CodeHandlers.RequirementCodeCommands import ReqCommandDefinition

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.utils import fit
from ...Utilities.CodeHandlers.CodeType import IntCodeType

from typing import Protocol

class OpcodeEditorDelegate(Protocol):
	def opcode_changed(self, index: int, cmd_def: ReqCommandDefinition, params: list[int]) -> None:
		...

	def move_opcode(self, index: int, delta: int) -> None:
		...

	def delete_opcode(self, index: int) -> None:
		...

	def add_opcode_after(self, index: int) -> None:
		...

	def param_limits(self, param_type: IntCodeType) -> tuple[int, int]:
		...

	def param_entries(self, param_type: IntCodeType) -> list[tuple[str, int | None]]:
		...

# A row of the requirements Builder, editing one opcode of the script: its line number, the opcode, its parameter (if it has one),
# and the actions on the row (the Builder only shows them while hovering over the row)
class OpcodeEditorView(UI.Frame):
	INDENT_WIDTH = 20
	ERROR_COLOR = '#FFB4B4'

	def __init__(self, parent: UI.Misc, delegate: OpcodeEditorDelegate, commands: list[ReqCommandDefinition]) -> None:
		super().__init__(parent)
		self.delegate = delegate
		# The opcodes of the file, in the order the dropdown lists them
		self.available_commands = sorted(commands, key=lambda cmd_def: cmd_def.display_name)
		# The opcodes to choose from: the file's opcodes, plus the row's opcode if the file doesn't have it (loaded from a file that uses it)
		self.commands = list(self.available_commands)
		self.index = 0
		self.cmd_def = self.commands[0]
		self.params: list[int] = []
		self.indent = 0
		self.has_error = False
		# Set while the row is being loaded, so loading isn't reported as a change
		self.loading = False
		self.background_color = self.cget('bg')

		self.line_number = UI.StringVar()
		self.line_label = UI.Label(self, textvariable=self.line_number, width=4, anchor=UI.E)
		self.line_label.grid(row=0, column=1, padx=(0, 4))

		self.opcode = UI.IntVar()
		self.opcode_dropdown = UI.DropDown(self, self.opcode, [cmd_def.display_name for cmd_def in self.commands], self.opcode_chosen, width=28)
		self.opcode_dropdown.grid(row=0, column=2, padx=2, pady=2)
		OpcodeEditorView.pass_through_ctrl_return(self.opcode_dropdown)
		self.help_label = UI.Label(self, text='?')
		self.help_label.grid(row=0, column=3, padx=2)
		self.help_tooltip = UI.Tooltip(self.help_label) # Shows the help of the chosen opcode

		# The parameter editor is rebuilt when the kind of parameter changes
		self.param_frame = UI.Frame(self)
		self.param_frame.grid(row=0, column=4, sticky=UI.W, padx=2)
		self.param_type: IntCodeType | None = None
		self.param_value: UI.IntegerVar | None = None
		self.param_editor: UI.EntryDropDown | None = None

		self.actions = UI.Toolbar(self)
		self.move_up_button = self.actions.add_button(Assets.get_image('up'), lambda: self.delegate.move_opcode(self.index, -1), 'Move Up')
		self.move_down_button = self.actions.add_button(Assets.get_image('down'), lambda: self.delegate.move_opcode(self.index, 1), 'Move Down')
		self.actions.add_section()
		self.actions.add_button(Assets.get_image('remove'), lambda: self.delegate.delete_opcode(self.index), 'Delete')
		self.actions.add_button(Assets.get_image('add'), lambda: self.delegate.add_opcode_after(self.index), 'Add Opcode Below')
		self.actions.grid(row=0, column=6, sticky=UI.E, padx=2)
		self.grid_columnconfigure(5, weight=1)
		# The actions are hidden by covering them with a plain frame (in the row's background color), so they keep their space and rows don't change size when they're shown.
		# The cover always stays placed, and showing/hiding only raises the actions or the cover above the other: removing the cover relies on the actions being redrawn
		# once uncovered, which macOS doesn't always do (the actions work but still look covered), while a raised widget is always drawn.
		self.actions_cover = UI.Frame(self)
		self.actions_cover.place(in_=self.actions, x=0, y=0, relwidth=1, relheight=1)
		self.actions_visible = True
		self.hide_actions()
		self.bind(UI.Cursor.Enter(), self.pointer_entered)
		self.bind(UI.Cursor.Leave(), self.pointer_left)

	@staticmethod
	def pass_through_ctrl_return(dropdown: UI.DropDown) -> None:
		# A dropdown opens its list on Return, which would also catch the Apply shortcut (Ctrl+Return), so it's bound on its own to only run the shortcut
		dropdown.entry.bind(UI.Ctrl.Return(), lambda _: None)

	def set_command(self, index: int, cmd_def: ReqCommandDefinition, params: list[int], *, indent: int, is_last: bool) -> None:
		# Loads the opcode into the row (without reporting it as a change)
		self.loading = True
		try:
			self.index = index
			self.line_number.set(str(index + 1))
			if indent != self.indent:
				self.indent = indent
				self.grid_columnconfigure(0, minsize=indent * OpcodeEditorView.INDENT_WIDTH)
			self.cmd_def = cmd_def
			self.params = list(params)
			self.update_commands()
			opcode = self.commands.index(cmd_def)
			if self.opcode.get() != opcode:
				self.opcode.set(opcode)
			self.help_tooltip.text = fit('', cmd_def.full_help_text())
			self.update_param_editor()
			if self.param_value is not None and self.params and self.param_value.get() != self.params[0]:
				self.param_value.set(self.params[0])
			self.move_up_button['state'] = UI.DISABLED if index == 0 else UI.NORMAL
			self.move_down_button['state'] = UI.DISABLED if is_last else UI.NORMAL
		finally:
			self.loading = False

	def update_commands(self) -> None:
		# Lists the row's opcode after the file's opcodes when the file doesn't have it, so it can be shown (and its error reported) until it's changed
		commands = list(self.available_commands)
		if self.cmd_def not in commands:
			commands.append(self.cmd_def)
		if commands == self.commands:
			return
		self.commands = commands
		self.opcode_dropdown.setentries([cmd_def.display_name if cmd_def in self.available_commands else f'{cmd_def.display_name} (Not Available)' for cmd_def in self.commands])

	def update_param_editor(self) -> None:
		# Rebuilds the parameter editor if the opcode's kind of parameter (or its limits) changed
		param_type = self.cmd_def.param_types[0] if self.cmd_def.param_types else None
		assert param_type is None or isinstance(param_type, IntCodeType)
		if param_type is self.param_type:
			return
		if self.param_type is not None and param_type is not None and type(param_type) is type(self.param_type) and self.delegate.param_limits(param_type) == self.delegate.param_limits(self.param_type):
			self.param_type = param_type
			return
		if self.param_editor is not None:
			self.param_editor.destroy()
		self.param_editor = None
		self.param_value = None
		self.param_type = param_type
		if param_type is None:
			# An empty frame keeps its last size, so make sure it shrinks
			self.param_frame.config(width=1, height=1)
			return
		value = self.params[0] if self.params else 0
		self.param_value = UI.IntegerVar(value, list(self.delegate.param_limits(param_type)))
		self.param_editor = UI.EntryDropDown(self.param_frame, self.param_value, self.delegate.param_entries(param_type), entry_width=6, dropdown_width=30, callback=self.param_changed)
		self.param_editor.pack(side=UI.LEFT)
		OpcodeEditorView.pass_through_ctrl_return(self.param_editor.dropdown)
		self.apply_error_color()

	def refresh_param_entries(self) -> None:
		# The names of the units/techs may have changed (a different dat file was loaded)
		if self.param_editor is not None and self.param_type is not None:
			self.param_editor.set_entries(self.delegate.param_entries(self.param_type))

	def opcode_chosen(self, opcode: int) -> None:
		cmd_def = self.commands[opcode]
		self.help_tooltip.text = fit('', cmd_def.full_help_text())
		if self.loading or cmd_def is self.cmd_def:
			return
		params: list[int] = []
		if cmd_def.param_types:
			param_type = cmd_def.param_types[0]
			assert isinstance(param_type, IntCodeType)
			value = 0
			# The same kind of parameter keeps its value (within the new opcode's limits)
			min_value, max_value = self.delegate.param_limits(param_type)
			old_type = self.cmd_def.param_types[0] if self.cmd_def.param_types else None
			if self.params and type(old_type) is type(param_type):
				value = max(min_value, min(self.params[0], max_value))
			params = [value]
		self.delegate.opcode_changed(self.index, cmd_def, params)

	def param_changed(self, value: int) -> None:
		if self.loading or not self.params or self.params[0] == value:
			return
		self.params = [value]
		self.delegate.opcode_changed(self.index, self.cmd_def, [value])

	# Highlighting

	def set_error(self, has_error: bool) -> None:
		if has_error == self.has_error:
			return
		self.has_error = has_error
		self.apply_error_color()

	def apply_error_color(self) -> None:
		color = OpcodeEditorView.ERROR_COLOR if self.has_error else self.background_color
		# Only the row's own background is colored, the inputs keep theirs
		for widget in (self, self.line_label, self.help_label, self.param_frame, self.actions_cover):
			widget.config(bg=color)
		if self.param_editor is not None:
			self.param_editor.config(bg=color)
			for child in self.param_editor.winfo_children():
				if isinstance(child, UI.Label):
					child.config(bg=color)

	# Hovering

	def pointer_entered(self, _event: UI.Event) -> None:
		self.show_actions()

	def pointer_left(self, event: UI.Event) -> None:
		# The row also gets a Leave when the pointer moves onto one of its own widgets, so the actions stay shown while the pointer is still in the row
		path = str(self.tk.call('winfo', 'containing', '-displayof', str(self), event.x_root, event.y_root))
		row_path = str(self)
		if path == row_path or path.startswith(row_path + '.'):
			return
		self.hide_actions()

	def show_actions(self) -> None:
		if not self.actions_visible:
			self.actions_visible = True
			self.actions.lift(self.actions_cover)

	def hide_actions(self) -> None:
		if self.actions_visible:
			self.actions_visible = False
			self.actions_cover.lift(self.actions)

	def actions_shown(self) -> bool:
		return self.actions_visible
