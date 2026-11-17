from __future__ import annotations

from .ButtonRow import ButtonRow, draw_icon
from .. import ParamEntries
from ..JumpTarget import JumpTarget

from ...FileFormats.Graft import Button
from ...FileFormats.Graft.CodeHandlers import ButtonCodeCommands, ButtonsLanguage
from ...FileFormats.Graft.CodeHandlers.CodeTypes import ButtonPositionCodeType
from ...FileFormats.Graft.CodeHandlers.GraftCommandDefinition import GraftCommandDefinition

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.utils import fit
from ...Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ...Utilities.CodeHandlers.CodeType import CodeType
from ...Utilities.DataContext import DataContext
from ...Utilities.IconSelectDialog import IconSelectDialog
from ...Utilities.Config import WindowGeometry
from ...Utilities.TextPreview.TextDrawing import TextDrawing

from typing import Callable, Protocol

class ButtonSettingsDelegate(Protocol):
	@property
	def data_context(self) -> DataContext:
		...

	def button_tooltip(self, button: Button, *, enabled: bool = True) -> TextDrawing | None:
		...

	def button_settings_changed(self) -> None:
		...

	def icon_select_geometry(self) -> WindowGeometry:
		...

	def can_jump(self, target: JumpTarget, entry_id: int) -> bool:
		...

	def jump(self, target: JumpTarget, entry_id: int) -> None:
		...

# A value of 0 to 65535 (the size of every button field the settings edit with an `EntryDropDown`)
U16_RANGE = [0, 0xFFFF]

def help_label(parent: UI.Misc, cmd_def: CodeCommandDefinition | None = None) -> tuple[UI.Label, UI.Tooltip]:
	# A `?` that shows the help of a command when hovered
	label = UI.Label(parent, text='?')
	tooltip = UI.Tooltip(label)
	if cmd_def is not None:
		tooltip.text = fit('', cmd_def.full_help_text())
	return (label, tooltip)

# Edits a condition or action of a button: the function, and its parameter (if it has one)
class FunctionEditor(UI.Frame):
	def __init__(self, parent: UI.Misc, functions: list[GraftCommandDefinition], delegate: ButtonSettingsDelegate, changed: Callable[[int, int], None]) -> None:
		super().__init__(parent)
		self.functions = functions
		self.delegate = delegate
		self.data_context = delegate.data_context
		self.changed = changed
		self.function_index = 0
		self.param = 0
		self.enabled = True
		# Set while the function is being loaded, so loading isn't reported as a change
		self.loading = False

		self.function = UI.IntVar()
		self.function_dropdown = UI.DropDown(self, self.function, [function.display_name for function in functions], self.function_chosen, width=34)
		self.function_dropdown.pack(side=UI.LEFT, padx=2)
		self.help_label, self.help_tooltip = help_label(self)
		self.help_label.pack(side=UI.LEFT, padx=2)

		# The parameter editor is rebuilt when the kind of parameter changes
		self.param_frame = UI.Frame(self)
		self.param_frame.pack(side=UI.LEFT, padx=2)
		self.param_type: CodeType | None = None
		self.param_value: UI.IntegerVar | None = None
		self.param_editor: UI.EntryDropDown | None = None

		# Only shown while the function's parameter references something that can be jumped to
		self.jump_button = UI.Button(self, image=Assets.get_image('jump'), command=self.jump, width=20, height=20)
		self.jump_tooltip = UI.Tooltip(self.jump_button) # Names the target of the chosen function
		self.jump_target: JumpTarget | None = None

	def definition(self) -> GraftCommandDefinition:
		return self.functions[self.function_index]

	def update_jump_button(self) -> None:
		target = JumpTarget.for_button_function(self.definition())
		if target != self.jump_target:
			self.jump_target = target
			if target is None:
				self.jump_button.pack_forget()
			else:
				self.jump_tooltip.text = target.tooltip
				self.jump_button.pack(side=UI.LEFT, padx=2, after=self.param_frame)
		if target is not None:
			self.jump_button['state'] = UI.NORMAL if self.enabled and self.delegate.can_jump(target, self.param) else UI.DISABLED

	def jump(self) -> None:
		if self.jump_target is not None:
			self.delegate.jump(self.jump_target, self.param)

	def load(self, function_index: int, param: int) -> None:
		self.loading = True
		try:
			self.function_index = function_index
			self.param = param
			if self.function.get() != function_index:
				self.function.set(function_index)
			self.help_tooltip.text = fit('', self.definition().full_help_text())
			self.update_param_editor()
			if self.param_value is not None and self.param_value.get() != param:
				self.param_value.set(param)
		finally:
			self.loading = False
		self.update_jump_button()

	def update_param_editor(self) -> None:
		# Rebuilds the parameter editor if the function's kind of parameter changed
		cmd_def = self.definition()
		param_type = cmd_def.param_types[0] if cmd_def.param_types else None
		if param_type is self.param_type:
			return
		if self.param_type is not None and param_type is not None and type(param_type) is type(self.param_type):
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
		self.param_value = UI.IntegerVar(self.param, list(ParamEntries.param_limits(self.data_context, ButtonsLanguage(), param_type)))
		self.param_editor = UI.EntryDropDown(self.param_frame, self.param_value, ParamEntries.param_entries(self.data_context, ButtonsLanguage(), param_type), entry_width=6, dropdown_width=30, callback=self.param_changed)
		self.param_editor.pack(side=UI.LEFT)

	def refresh_entries(self) -> None:
		# The names of the units/techs/upgrades may have changed (a different dat file was loaded)
		if self.param_editor is not None and self.param_type is not None:
			self.param_editor.set_entries(ParamEntries.param_entries(self.data_context, ButtonsLanguage(), self.param_type))
		# The entries that can be jumped to may have changed too
		self.update_jump_button()

	def function_chosen(self, function_index: int) -> None:
		cmd_def = self.functions[function_index]
		self.help_tooltip.text = fit('', cmd_def.full_help_text())
		if self.loading or function_index == self.function_index:
			return
		param = 0
		if cmd_def.param_types:
			param_type = cmd_def.param_types[0]
			# The same kind of parameter keeps its value (within the new function's limits)
			old_type = self.definition().param_types[0] if self.definition().param_types else None
			if type(old_type) is type(param_type):
				min_value, max_value = ParamEntries.param_limits(self.data_context, ButtonsLanguage(), param_type)
				param = max(min_value, min(self.param, max_value))
		self.load(function_index, param)
		self.changed(function_index, param)

	def param_changed(self, value: int) -> None:
		if self.loading or self.param == value:
			return
		self.param = value
		self.update_jump_button()
		self.changed(self.function_index, value)

	def set_enabled(self, enabled: bool) -> None:
		self.enabled = enabled
		state = UI.NORMAL if enabled else UI.DISABLED
		self.function_dropdown['state'] = state
		if self.param_editor is not None:
			self.param_editor.entry['state'] = state
			self.param_editor.dropdown['state'] = state
		self.update_jump_button()

# A preview of a tooltip like the game draws it, hidden while there's nothing to show
class TooltipPreview:
	PADDING = 4

	def __init__(self, parent: UI.Misc, row: int) -> None:
		self.canvas = UI.Canvas(parent, width=1, height=1, background='#000000', highlightthickness=0, borderwidth=0, theme_tag='preview') # type: ignore[call-arg]
		self.canvas.grid(row=row, column=1, sticky=UI.W, pady=(0, 2))
		self.canvas.grid_remove()
		self.drawing: TextDrawing | None = None

	def show(self, drawing: TextDrawing | None) -> None:
		if self.drawing:
			self.drawing.delete()
		self.drawing = drawing
		if drawing is None:
			self.canvas.grid_remove()
			return
		padding = TooltipPreview.PADDING
		self.canvas.config(width=drawing.width + padding * 2, height=drawing.height + padding * 2)
		drawing.draw(self.canvas, padding, padding)
		self.canvas.grid()

# Edits the settings of the selected button, writing each change straight into the button
class ButtonSettingsView(UI.Frame):
	def __init__(self, parent: UI.Misc, delegate: ButtonSettingsDelegate) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.button: Button | None = None
		# Set while the button is being loaded, so loading isn't reported as a change
		self.loading = False

		def add_field(row: int, name: str) -> UI.Frame:
			# A field's editor and its `?` share a frame, so an editor that grows (like a function's parameter appearing) doesn't move the other fields' `?`
			UI.Label(self, text=f'{name}:', anchor=UI.E).grid(row=row, column=0, sticky=UI.E, padx=(2, 4), pady=2)
			field = UI.Frame(self)
			field.grid(row=row, column=1, sticky=UI.W, pady=2)
			return field

		def add_help(field: UI.Frame, cmd_def: CodeCommandDefinition) -> None:
			label, _ = help_label(field, cmd_def)
			label.pack(side=UI.LEFT, padx=2)

		# The positions after the 9 slots (which the game doesn't show) can't be chosen, the button's position is only listed while it uses one
		self.position_names = [f'{position} ({name})' for position, name in enumerate(ButtonPositionCodeType.NAMES, 1)]
		field = add_field(0, 'Position')
		self.position = UI.IntVar()
		self.position_dropdown = UI.DropDown(field, self.position, self.position_names, self.position_chosen, width=20)
		self.position_dropdown.pack(side=UI.LEFT)
		add_help(field, ButtonCodeCommands.Position)

		field = add_field(1, 'Icon')
		self.icon = UI.IntegerVar(0, list(U16_RANGE))
		self.icon_editor = UI.EntryDropDown(field, self.icon, self.icon_entries(), entry_width=6, dropdown_width=30, callback=self.icon_changed)
		self.icon_editor.pack(side=UI.LEFT)
		self.find_icon_button = UI.Button(field, image=Assets.get_image('find'), command=self.choose_icon, width=20, height=20)
		self.find_icon_button.pack(side=UI.LEFT, padx=2)
		UI.Tooltip(self.find_icon_button, 'Find Icon')
		border = UI.Frame(field, relief=UI.SUNKEN, bd=1)
		self.icon_preview = UI.Canvas(border, width=ButtonRow.ICON_WIDTH, height=ButtonRow.ICON_HEIGHT, background='#000000', highlightthickness=0, borderwidth=0, theme_tag='preview') # type: ignore[call-arg]
		self.icon_preview.pack()
		self.icon_preview.bind(UI.Mouse.Click_Left(), lambda _: self.choose_icon())
		border.pack(side=UI.LEFT, padx=2)
		add_help(field, ButtonCodeCommands.Icon)

		# The function editors have their own `?` (for the chosen function), before their parameter
		field = add_field(2, 'Condition')
		self.condition_editor = FunctionEditor(field, ButtonCodeCommands.condition_commands, delegate, self.condition_changed)
		self.condition_editor.pack(side=UI.LEFT)
		field = add_field(3, 'Action')
		self.action_editor = FunctionEditor(field, ButtonCodeCommands.action_commands, delegate, self.action_changed)
		self.action_editor.pack(side=UI.LEFT)

		field = add_field(4, 'Enabled String')
		self.enabled_string = UI.IntegerVar(0, list(U16_RANGE))
		self.enabled_string_editor = UI.EntryDropDown(field, self.enabled_string, self.string_entries(), entry_width=6, dropdown_width=40, callback=self.enabled_string_changed)
		self.enabled_string_editor.pack(side=UI.LEFT)
		add_help(field, ButtonCodeCommands.EnabledStr)
		self.enabled_string_preview = TooltipPreview(self, 5)

		field = add_field(6, 'Disabled String')
		self.disabled_string = UI.IntegerVar(0, list(U16_RANGE))
		self.disabled_string_editor = UI.EntryDropDown(field, self.disabled_string, self.string_entries(), entry_width=6, dropdown_width=40, callback=self.disabled_string_changed)
		self.disabled_string_editor.pack(side=UI.LEFT)
		add_help(field, ButtonCodeCommands.DisabledStr)
		self.disabled_string_preview = TooltipPreview(self, 7)

		self.set_enabled(False)

	# Entries

	def icon_entries(self) -> list[tuple[str, int | None]]:
		return [*((name, icon_id) for icon_id, name in enumerate(self.delegate.data_context.icon_names())), ('Unknown', None)]

	def string_entries(self) -> list[tuple[str, int | None]]:
		# String IDs are 1-based (0 is no string)
		strings = self.delegate.data_context.stat_txt_strings() or []
		return [('None', 0), *((string, string_id) for string_id, string in enumerate(strings, 1)), ('Unknown', None)]

	def refresh_entries(self) -> None:
		# The data files may have changed since the entries were made
		self.loading = True
		try:
			self.icon_editor.set_entries(self.icon_entries())
			strings = self.string_entries()
			self.enabled_string_editor.set_entries(strings)
			self.disabled_string_editor.set_entries(strings)
			self.condition_editor.refresh_entries()
			self.action_editor.refresh_entries()
		finally:
			self.loading = False
		self.update_string_previews()

	# Loading

	def load(self, button: Button | None) -> None:
		# Shows the button's settings (without reporting them as changes), or disables the settings without a button
		self.button = button
		self.loading = True
		try:
			shown = button or Button()
			names = list(self.position_names)
			if not 1 <= shown.position <= len(self.position_names):
				names.append(f'{shown.position} (Invalid)')
			if names != self.position_dropdown.entries:
				self.position_dropdown.setentries(names)
			position_index = shown.position - 1 if 1 <= shown.position <= len(self.position_names) else len(self.position_names)
			if self.position.get() != position_index:
				self.position.set(position_index)
			if self.icon.get() != shown.icon:
				self.icon.set(shown.icon)
			self.update_icon_preview()
			self.condition_editor.load(shown.condition, shown.condition_param)
			self.action_editor.load(shown.action, shown.action_param)
			if self.enabled_string.get() != shown.enabled_string:
				self.enabled_string.set(shown.enabled_string)
			if self.disabled_string.get() != shown.disabled_string:
				self.disabled_string.set(shown.disabled_string)
		finally:
			self.loading = False
		self.update_string_previews()
		self.set_enabled(button is not None)

	def set_enabled(self, enabled: bool) -> None:
		state = UI.NORMAL if enabled else UI.DISABLED
		self.position_dropdown['state'] = state
		for editor in (self.icon_editor, self.enabled_string_editor, self.disabled_string_editor):
			editor.entry['state'] = state
			editor.dropdown['state'] = state
		self.find_icon_button['state'] = state
		self.condition_editor.set_enabled(enabled)
		self.action_editor.set_enabled(enabled)

	def update_string_previews(self) -> None:
		# The tooltips show the costs of the action's parameter, so they change with the action too
		button = self.button
		self.enabled_string_preview.show(self.delegate.button_tooltip(button) if button else None)
		self.disabled_string_preview.show(self.delegate.button_tooltip(button, enabled=False) if button else None)

	def update_icon_preview(self) -> None:
		draw_icon(self.icon_preview, self.delegate.data_context.get_cmdicon(self.icon.get()) if self.button else None)

	# Changes

	def edited(self) -> None:
		self.delegate.button_settings_changed()

	def position_chosen(self, index: int) -> None:
		if self.loading or self.button is None or index >= len(self.position_names):
			return
		position = index + 1
		if position == self.button.position:
			return
		self.button.position = position
		# The invalid position is no longer listed
		self.load(self.button)
		self.edited()

	def icon_changed(self, icon: int) -> None:
		if self.loading or self.button is None or icon == self.button.icon:
			return
		self.button.icon = icon
		self.update_icon_preview()
		self.edited()

	def choose_icon(self) -> None:
		if self.button is None:
			return
		IconSelectDialog(self, icon_source=self.delegate.data_context, window_geometry=self.delegate.icon_select_geometry(), delegate=self.icon.set, selected_index=self.icon.get())

	def condition_changed(self, condition: int, param: int) -> None:
		if self.loading or self.button is None:
			return
		self.button.condition = condition
		self.button.condition_param = param
		self.edited()

	def action_changed(self, action: int, param: int) -> None:
		if self.loading or self.button is None:
			return
		self.button.action = action
		self.button.action_param = param
		self.update_string_previews()
		self.edited()

	def enabled_string_changed(self, string_id: int) -> None:
		if self.loading or self.button is None or string_id == self.button.enabled_string:
			return
		self.button.enabled_string = string_id
		self.update_string_previews()
		self.edited()

	def disabled_string_changed(self, string_id: int) -> None:
		if self.loading or self.button is None or string_id == self.button.disabled_string:
			return
		self.button.disabled_string = string_id
		self.update_string_previews()
		self.edited()
