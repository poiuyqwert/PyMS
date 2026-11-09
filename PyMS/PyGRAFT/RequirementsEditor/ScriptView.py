
from __future__ import annotations

from .ReqSyntaxHighlighting import build_syntax_highlighting
from .CommandTooltip import CommandTooltip
from ..GraftData import ReqGraftData

from ...FileFormats.Graft import ReqScript
from ...FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftSerializeContext

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.EditedState import EditedState
from ...Utilities.FindReplaceDialog import FindReplaceDialog
from ...Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities.WarningDialog import WarningDialog

import io

from typing import TYPE_CHECKING, Any, Callable, Sequence, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

# The Script mode of the requirements editor, editing the selected entry's script as code (only its commands, the entry is the selected one)
class ReqScriptView(UI.NotebookTab, UI.CodeTextDelegate):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, graft_data: ReqGraftData[Any]) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.graft_data = graft_data
		self.entry_id: int | None = None
		self.entry_name = ''
		self.commands = graft_data.graft_type.LANGUAGE.commands()
		self.findwindow: FindReplaceDialog | None = None

		self.edited_state = EditedState()
		self.edited_state.callback += self.update_edited

		# Created before the toolbar so its shortcuts can be bound on the text, only applying while editing (and not running the text's own bindings for them, like Ctrl+T transposing)
		self.text = UI.CodeText(self, self.edited_state, self)
		self.text.text.config(width=1, height=1)

		self.toolbar = UI.Toolbar(self, bind_target=self.text.text)
		self.apply_button = self.add_button('save', self.apply_changes, 'Apply Changes', UI.Ctrl.Return)
		self.revert_button = self.add_button('undo', self.revert, 'Revert Changes')
		self.toolbar.add_gap()
		self.add_button('test', self.test, 'Test Code', UI.Ctrl.t)
		self.toolbar.add_section()
		self.add_button('find', self.find, 'Find/Replace', UI.Ctrl.f)
		self.toolbar.add_section()
		self.add_button('colors', self.colors, 'Color Settings', UI.Ctrl.Alt.c)
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)

		self.script_status = UI.StringVar()
		self.cursor_status = UI.StringVar()
		statusbar = UI.StatusBar(self)
		statusbar.add_label(self.script_status, weight=0.5)
		statusbar.add_label(self.cursor_status)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.text.pack(fill=UI.BOTH, expand=1, padx=1, pady=1)
		self.text.bind(UI.CodeText.WidgetEvent.InsertCursorMoved(), self.update_cursor_status)
		self.text.text.bind(UI.WidgetEvent.Text.Selection(), self.update_cursor_status)

		self.syntax_highlighting = build_syntax_highlighting(delegate.config_.code.highlights, graft_data.graft_type.LANGUAGE)
		self.text.set_syntax_highlighting(self.syntax_highlighting)
		CommandTooltip(self.text.text, self.commands)

		self.update_edited(False)
		self.update_cursor_status()

	def add_button(self, icon: str, callback: Callable[[], Any], tooltip: str, shortcut: UI.EventPattern | None = None) -> UI.Button:
		return self.toolbar.add_button(Assets.get_image(icon), callback, tooltip, shortcut)

	def window(self) -> UI.AnyWindow:
		return cast(UI.AnyWindow, self.winfo_toplevel())

	def is_edited(self) -> bool:
		return bool(self.text.edit_modified())

	def update_edited(self, edited: bool) -> None:
		state = UI.NORMAL if edited else UI.DISABLED
		self.apply_button['state'] = state
		self.revert_button['state'] = state

	def update_cursor_status(self, _event: UI.Event | None = None) -> None:
		line, column = self.text.index(UI.INSERT).split('.')
		selected = 0
		if sel_range := self.text.tag_ranges('sel'):
			selected = len(self.text.get(*sel_range))
		self.cursor_status.set(f'Line: {line}  Column: {column}  Selected: {selected}')

	def update_highlight_styles(self) -> None:
		self.text.update_highlight_styles()

	def load(self, entry_id: int | None, entry_name: str) -> None:
		self.entry_id = entry_id
		self.entry_name = entry_name
		code = ''
		if entry_id is None:
			self.script_status.set('No entry')
		elif self.graft_data.has_script(entry_id):
			output = io.StringIO()
			try:
				self.graft_data.graft.decompile_script(GraftSerializeContext(output, self.delegate.data_context), entry_id)
				code = output.getvalue()
			except PyMSError as e:
				ErrorDialog(self, e)
			self.script_status.set(entry_name)
		else:
			self.script_status.set(f'{entry_name} (No script)')
		self.text.set_read_only(False)
		self.text.load(code)
		self.text.set_read_only(entry_id is None)
		self.edited_state.mark_edited(False)
		self.update_cursor_status()

	def compile(self) -> tuple[ReqScript, list[PyMSWarning]] | None:
		# Compiles the code, highlighting and showing any error
		if self.entry_id is None:
			return None
		code = self.text.get('1.0', UI.END)
		graft_type = self.graft_data.graft_type
		parse_context = GraftParseContext(GraftLexer(code), self.delegate.data_context, graft_type.LANGUAGE())
		try:
			script = graft_type.compile_script(parse_context, self.entry_id)
		except PyMSError as e:
			self.text.highlight_error(e)
			ErrorDialog(self, e)
			return None
		if parse_context.warnings:
			self.text.highlight_warnings(parse_context.warnings)
		return (script, parse_context.warnings)

	def test(self) -> None:
		result = self.compile()
		if result is None:
			return
		_, warnings = result
		if warnings:
			WarningDialog(self, warnings)
		else:
			UI.MessageBox.showinfo(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.')

	def apply_changes(self) -> None:
		self.apply()

	def apply(self) -> bool:
		# Compiles the code into the file, returning `False` if it couldn't be (or the user cancelled)
		result = self.compile()
		if result is None:
			return False
		script, warnings = result
		if warnings:
			warning_dialog = WarningDialog(self, warnings, True)
			if not warning_dialog.cont:
				return False
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
		# Refreshing updates the list and status bar, and reloads the script (no longer edited)
		self.delegate.refresh()
		return True

	def revert(self) -> None:
		self.load(self.entry_id, self.entry_name)

	def confirm_leave(self) -> bool:
		# Asks to apply changes before leaving the editor, returning `False` to stay
		if not self.is_edited():
			return True
		apply = UI.MessageBox.askyesnocancel(parent=self, title='Apply Changes?', message=f"Apply changes to '{self.entry_name}'?", default=UI.MessageBox.YES)
		if apply is None:
			return False
		if apply:
			return self.apply()
		self.revert()
		return True

	def confirm_apply_before_save(self) -> bool:
		# Asks to apply changes before saving the file, returning `False` to cancel the save
		if not self.is_edited():
			return True
		apply = UI.MessageBox.askyesnocancel(parent=self, title='Apply Changes?', message=f"Apply changes to '{self.entry_name}' before saving?\n\nNo saves the file without them (they stay in the editor).", default=UI.MessageBox.YES)
		if apply is None:
			return False
		if apply:
			return self.apply()
		return True

	def can_deactivate(self) -> bool:
		return self.confirm_leave()

	def find(self) -> None:
		if self.findwindow is None:
			self.findwindow = FindReplaceDialog(self, self.text, self.delegate.config_.windows.find_replace)
			self.text.text.bind(UI.Key.F3(), self.findwindow.findnext)
		else:
			self.findwindow.show()

	def colors(self) -> None:
		dialog = SyntaxHighlightingDialog(self.window(), self.syntax_highlighting.all_highlight_components())
		if dialog.updated:
			self.text.update_highlight_styles()

	# CodeTextDelegate
	def comment_symbols(self) -> Sequence[str]:
		return ('#', ';')

	def comment_symbol(self) -> str:
		return '#'

	def autocomplete_override_keys(self) -> str:
		return ' (,)'

	def get_autocomplete_options(self, line: str) -> Sequence[str] | None:
		return sorted(cmd_def.name for cmd_def in self.commands)

	def jump_highlights(self) -> Sequence[str] | None:
		return ('Error', 'Warning')

	def jump_sections(self) -> Sequence[str] | None:
		return None

	def find_definition(self, name: str) -> str | None:
		return None
