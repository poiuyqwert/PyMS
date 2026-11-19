from __future__ import annotations

from .ButtonRow import ButtonRow
from .PreviewGrid import PreviewGrid
from .ButtonSettingsView import ButtonSettingsView
from ..GraftData import ButtonsGraftData
from ..JumpTarget import JumpTarget

from ...FileFormats.Graft import Button, ButtonSet
from ...FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftSerializeContext, ButtonsLanguage, ButtonCodeCommands
from ...FileFormats.TBL import end_at_null, simplify_string

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.Config import WindowGeometry
from ...Utilities.DataContext import DataContext, CmdIconState
from ...Utilities.IconSelectDialog import ImageWithBounds
from ...Utilities.TextPreview.HotkeyString import HotkeyString, TooltipCosts
from ...Utilities.TextPreview.TextDrawing import TextDrawing
from ...Utilities.PyMSError import PyMSError
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities.WarningDialog import WarningDialog

import io

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The Builder mode of the button set editor, editing the selected button set without code.
# Changes are made straight to the button set (there is nothing to apply), so leaving it never asks anything.
class ButtonSetBuilderView(UI.NotebookTab):
	# The Buttons list shows this many rows before it scrolls
	VISIBLE_ROWS = 9.5

	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ButtonsGraftData) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.graft_data = graft_data
		self.entry_id: int | None = None
		self.entry_name = ''
		self.selected: int | None = None
		self.rows: list[ButtonRow] = []

		top = UI.Frame(self)
		preview_frame = UI.LabelFrame(top, text='Preview')
		self.preview = PreviewGrid(preview_frame, self)
		self.preview.pack(padx=5, pady=5)
		preview_frame.pack(side=UI.RIGHT, anchor=UI.N, padx=(2, 0))

		buttons_frame = UI.LabelFrame(top, text='Buttons')
		self.toolbar = UI.Toolbar(buttons_frame)
		self.add_button_button = self.toolbar.add_button(Assets.get_image('add'), self.add_button, 'Add Button')
		self.toolbar.add_section()
		self.copy_button = self.add_clipboard_button('copy', self.copy, 'Copy Buttons', UI.Ctrl.c)
		self.paste_button = self.add_clipboard_button('paste', self.paste, 'Paste Buttons', UI.Ctrl.v)
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)
		self.scroll_view = UI.ScrollView(buttons_frame, viewport_height=round(ButtonSetBuilderView.VISIBLE_ROWS * ButtonRow.ROW_HEIGHT), fill_width=True)
		self.scroll_view.pack(fill=UI.BOTH, expand=1, padx=2, pady=(0, 2))
		buttons_frame.pack(side=UI.LEFT, fill=UI.BOTH, expand=1)
		top.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)

		settings_frame = UI.LabelFrame(self, text='Button Settings')
		self.settings_view = ButtonSettingsView(settings_frame, self)
		self.settings_view.pack(padx=5, pady=5)
		# Sized to fit the settings, not the width of the Builder
		settings_frame.pack(side=UI.TOP, anchor=UI.W, padx=2, pady=2)

		self.update_read_only()

	def add_clipboard_button(self, icon: str, callback: Callable[[], None], tooltip: str, shortcut: UI.EventPattern) -> UI.Button:
		button = self.toolbar.add_button(Assets.get_image(icon), callback, tooltip, shortcut, bind_shortcut=False)
		# The Button Sets tab is one of the window's tabs, so the shortcut is added to the window (not replacing the others), and only the visible Builder runs it.
		# It's left to a focused text field (like a setting's entry, or the Script mode's code), which copies and pastes its own text.
		def triggered(_event: UI.Event) -> None:
			if button['state'] != UI.DISABLED and button.winfo_viewable() and not self.focus_has_clipboard():
				callback()
		self.winfo_toplevel().bind(shortcut(), triggered, True)
		return button

	@property
	def data_context(self) -> DataContext:
		return self.delegate.data_context

	def button_set(self) -> ButtonSet | None:
		if self.entry_id is None or not 0 <= self.entry_id < len(self.graft_data.graft.button_sets):
			return None
		return self.graft_data.graft.button_sets[self.entry_id]

	def buttons(self) -> list[Button]:
		button_set = self.button_set()
		return button_set.buttons if button_set else []

	# Loading

	def load(self, entry_id: int | None, entry_name: str) -> None:
		# Reloading the same button set keeps its selected button
		same_set = entry_id == self.entry_id
		self.entry_id = entry_id
		self.entry_name = entry_name
		self.settings_view.refresh_entries()
		buttons = self.buttons()
		if not buttons:
			self.selected = None
		elif same_set and self.selected is not None:
			self.selected = min(self.selected, len(buttons) - 1)
		else:
			self.selected = 0
		self.update_read_only()
		self.sync()

	def update_read_only(self) -> None:
		# Without a selected button set there is nothing to add to
		state = UI.DISABLED if self.button_set() is None else UI.NORMAL
		self.add_button_button['state'] = state
		self.copy_button['state'] = state
		self.paste_button['state'] = state

	def sync(self) -> None:
		# Shows the buttons in the rows (reusing the rows already made), the preview, and the settings of the selected button
		buttons = self.buttons()
		while len(self.rows) > len(buttons):
			self.rows.pop().destroy()
		new_rows: list[ButtonRow] = []
		while len(self.rows) < len(buttons):
			row = ButtonRow(self.scroll_view.content_view, self)
			self.rows.append(row)
			new_rows.append(row)
		for index, (row, button) in enumerate(zip(self.rows, buttons)):
			row.set_button(index, button, is_last=index == len(buttons) - 1)
		# New rows are only shown once they're loaded, so they all appear at once with their buttons
		for row in new_rows:
			row.pack(side=UI.TOP, fill=UI.X)
		self.update_selection()

	def update_selection(self) -> None:
		buttons = self.buttons()
		for index, row in enumerate(self.rows):
			row.set_selected(index == self.selected)
		self.preview.update_buttons(buttons, self.selected)
		self.settings_view.load(buttons[self.selected] if self.selected is not None else None)

	def scroll_to_selected(self) -> None:
		if self.selected is None:
			return
		UI.Misc.update_idletasks(self)
		self.scroll_view.scroll_to_view(self.rows[self.selected])

	def edited(self) -> None:
		# The button set was changed in place
		self.graft_data.edited = True
		self.delegate.update_status_bar()

	# Delegates (ButtonRow, PreviewGrid, ButtonSettingsView)

	def select_button(self, index: int) -> None:
		if index == self.selected or not 0 <= index < len(self.buttons()):
			return
		self.selected = index
		self.update_selection()
		self.scroll_to_selected()

	def move_button(self, index: int, delta: int) -> None:
		buttons = self.buttons()
		other = index + delta
		if not 0 <= index < len(buttons) or not 0 <= other < len(buttons):
			return
		buttons[index], buttons[other] = buttons[other], buttons[index]
		# The selection stays on the same button
		if self.selected == index:
			self.selected = other
		elif self.selected == other:
			self.selected = index
		self.sync()
		self.edited()

	def delete_button(self, index: int) -> None:
		buttons = self.buttons()
		if not 0 <= index < len(buttons):
			return
		del buttons[index]
		if not buttons:
			self.selected = None
		elif self.selected is not None and self.selected > index:
			self.selected -= 1
		elif self.selected is not None:
			self.selected = min(self.selected, len(buttons) - 1)
		self.sync()
		self.edited()

	def add_button_after(self, index: int) -> None:
		self.insert_button(index + 1)

	def add_button(self) -> None:
		self.insert_button(len(self.buttons()))

	def insert_button(self, index: int) -> None:
		button_set = self.button_set()
		if button_set is None:
			return
		button_set.buttons.insert(index, ButtonSetBuilderView.new_button(button_set.buttons))
		self.selected = index
		self.sync()
		self.edited()
		self.scroll_to_selected()

	def copy(self) -> None:
		# The buttons as code, like the Script mode shows them
		button_set = self.button_set()
		if button_set is None:
			return
		output = io.StringIO()
		button_set.serialize(GraftSerializeContext(output, self.data_context))
		self.clipboard_set(output.getvalue())

	def paste(self) -> None:
		# Replaces the buttons with the buttons of the code on the clipboard
		if self.entry_id is None or self.button_set() is None:
			return
		try:
			code = self.clipboard_get()
		except UI.TclError:
			return
		parse_context = GraftParseContext(GraftLexer(code), self.data_context, ButtonsLanguage())
		try:
			button_set = ButtonSet.compile(parse_context, self.entry_id)
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		if parse_context.warnings and not WarningDialog(self, parse_context.warnings, True).cont:
			return
		self.graft_data.graft.set_button_set(self.entry_id, button_set)
		self.selected = 0 if button_set.buttons else None
		self.sync()
		self.edited()
		self.scroll_to_selected()

	@staticmethod
	def new_button(buttons: list[Button]) -> Button:
		# A button in the first free slot of the 9 (or the first slot when they're all used), that's always shown and does nothing
		used = set(button.position for button in buttons)
		position = next((position for position in range(1, 10) if position not in used), 1)
		return Button(position=position, condition=ButtonCodeCommands.Always.function_index, action=ButtonCodeCommands.Nothing.function_index)

	def button_icon(self, icon: int, state: CmdIconState = CmdIconState.enabled) -> ImageWithBounds | None:
		return self.data_context.get_cmdicon(icon, state)

	def button_set_unit_id(self) -> int | None:
		if self.entry_id is None:
			return None
		return self.graft_data.graft.first_unit_using_button_set(self.entry_id)

	def button_tooltip(self, button: Button, *, enabled: bool = True) -> TextDrawing | None:
		# The tooltip of the button like the game draws it.
		# Enabled: its hotkey string, with the cost line of its hotkey type. Disabled (greyed): plain text (usually its requirements), without a hotkey or cost line.
		# `None` when there's no string, an enabled string isn't a hotkey string, or the fonts aren't loaded.
		# String IDs are 1-based (0 is no string)
		string_id = button.enabled_string if enabled else button.disabled_string
		if not string_id:
			return None
		raw = self.data_context.stat_txt_raw_string(string_id - 1)
		if raw is None:
			return None
		if not enabled:
			return TextDrawing.tooltip(end_at_null(raw), self.data_context)
		hotkey_string = HotkeyString.parse(raw)
		if hotkey_string is None:
			return None
		costs = TooltipCosts.for_kind(hotkey_string.kind, button.action_param, self.data_context, self.button_set_unit_id())
		return TextDrawing.tooltip(hotkey_string.tooltip_runs(costs, self.data_context), self.data_context)

	def string_text(self, string_id: int) -> str:
		# String IDs are 1-based (0 is no string)
		if string_id == 0:
			return 'No String'
		raw = self.data_context.stat_txt_raw_string(string_id - 1)
		if raw is None:
			return f'Unknown String {string_id}'
		# The plain text, without its hotkey or control characters
		return simplify_string(raw)

	def button_settings_changed(self) -> None:
		# The selected button was changed, which can change its row and the preview (its position, icon, or string)
		if self.selected is not None:
			buttons = self.buttons()
			self.rows[self.selected].set_button(self.selected, buttons[self.selected], is_last=self.selected == len(buttons) - 1)
			self.preview.update_buttons(buttons, self.selected)
		self.edited()

	def icon_select_geometry(self) -> WindowGeometry:
		return self.delegate.config_.windows.icon_select

	def can_jump(self, target: JumpTarget, entry_id: int) -> bool:
		return self.delegate.can_jump(target, entry_id)

	def jump(self, target: JumpTarget, entry_id: int) -> None:
		self.delegate.jump(target, entry_id)

	# Editor mode

	def confirm_leave(self) -> bool:
		return True

	def confirm_apply_before_save(self) -> bool:
		return True
