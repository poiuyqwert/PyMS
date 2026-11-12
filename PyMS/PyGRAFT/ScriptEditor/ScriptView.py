from __future__ import annotations

from .SyntaxHighlighting import build_syntax_highlighting
from .CommandTooltip import CommandTooltip

from ...FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftSerializeContext, GraftLanguage

from ..EditorModeView import EditorModeView

from ...Utilities import UIKit as UI
from ...Utilities import Assets
from ...Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ...Utilities.CodeHandlers import CodeType
from ...Utilities.EditedState import EditedState
from ...Utilities.FindReplaceDialog import FindReplaceDialog
from ...Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.ErrorDialog import ErrorDialog
from ...Utilities.WarningDialog import WarningDialog

import io

from typing import TYPE_CHECKING, Any, Callable, Generic, Sequence, TypeVar, cast
if TYPE_CHECKING:
	from ..Delegates import MainDelegate

CompiledT = TypeVar('CompiledT')

# The Script mode of an editor, editing the selected entry as code (only its contents, the entry is the selected one).
# Subclasses decompile, compile, and apply the code of their kind of entry.
class ScriptView(EditorModeView, UI.CodeTextDelegate, Generic[CompiledT]):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, commands: list[CodeCommandDefinition], block_keywords: Sequence[str] = ()) -> None:
		super().__init__(parent)
		self.delegate = delegate
		self.commands = commands
		# Block keywords (like `button`) are highlighted like commands, and parameter keywords (like button positions) have their own style
		command_names = [*block_keywords, *(cmd_def.name for cmd_def in commands)]
		param_keywords = ScriptView.collect_param_keywords(commands)
		# Every name the code can use, offered by autocomplete
		self.keywords = sorted([*command_names, *param_keywords])
		self.findwindow: FindReplaceDialog | None = None

		self.edited_state = EditedState()
		self.edited_state.callback += self.update_edited

		# Created before the toolbar so its shortcuts can be bound on the text, only applying while editing (and not running the text's own bindings for them, like Ctrl+T transposing)
		self.text = UI.CodeText(self, self.edited_state, self)
		self.text.text.config(width=1, height=1)

		self.toolbar = UI.Toolbar(self, bind_target=self.text.text)
		self.apply_button = self.add_button('save', self.apply_changes, 'Apply Changes', UI.Ctrl.Return)
		self.revert_button = self.add_button('reset', self.revert, 'Revert Changes')
		self.toolbar.add_gap()
		self.add_button('test', self.test, 'Test Code', UI.Ctrl.t)
		self.toolbar.add_section()
		self.add_button('find', self.find, 'Find/Replace', UI.Ctrl.f)
		self.toolbar.add_section()
		self.add_button('colors', self.colors, 'Color Settings', UI.Ctrl.Alt.c)
		self.toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)

		# The entry is selected in the main window's list, so the status bar doesn't repeat it
		self.cursor_status = UI.StringVar()
		statusbar = UI.StatusBar(self)
		statusbar.add_spacer(weight=0.5)
		self.editstatus = statusbar.add_icon(Assets.get_image('save'))
		statusbar.add_label(self.cursor_status)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.text.pack(fill=UI.BOTH, expand=1, padx=1, pady=1)
		self.text.bind(UI.CodeText.WidgetEvent.InsertCursorMoved(), self.update_cursor_status)
		self.text.text.bind(UI.WidgetEvent.Text.Selection(), self.update_cursor_status)

		self.syntax_highlighting = build_syntax_highlighting(delegate.config_.code.highlights, command_names, param_keywords)
		self.text.set_syntax_highlighting(self.syntax_highlighting)
		CommandTooltip(self.text.text, self.commands)

		self.update_edited(False)
		self.update_cursor_status()

	def decompile_entry(self, serialize_context: GraftSerializeContext, entry_id: int) -> None:
		# Writes the code of the entry (nothing if it has none)
		raise NotImplementedError(self.__class__.__name__ + '.decompile_entry()')

	def language(self) -> GraftLanguage:
		raise NotImplementedError(self.__class__.__name__ + '.language()')

	def compile_entry(self, parse_context: GraftParseContext, entry_id: int) -> CompiledT:
		raise NotImplementedError(self.__class__.__name__ + '.compile_entry()')

	def apply_compiled(self, compiled: CompiledT) -> bool:
		# Stores the compiled code into the file (marking it edited), returning `False` if the user cancelled
		raise NotImplementedError(self.__class__.__name__ + '.apply_compiled()')

	@staticmethod
	def collect_param_keywords(commands: Sequence[CodeCommandDefinition]) -> list[str]:
		# Each keyword once, in the order they're first found
		keywords: dict[str, None] = {}
		for cmd_def in commands:
			for param_type in cmd_def.param_types:
				if isinstance(param_type, CodeType.HasKeywords):
					keywords.update(dict.fromkeys(param_type.keywords()))
		return list(keywords)

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
		self.editstatus['state'] = state

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
		if entry_id is not None:
			output = io.StringIO()
			try:
				self.decompile_entry(GraftSerializeContext(output, self.delegate.data_context), entry_id)
				# The text widget supplies the final newline itself
				code = output.getvalue().rstrip('\n')
			except PyMSError as e:
				ErrorDialog(self, e)
		self.text.set_read_only(False)
		self.text.load(code)
		self.text.set_read_only(entry_id is None)
		self.edited_state.mark_edited(False)
		self.update_cursor_status()

	def compile(self) -> tuple[CompiledT, list[PyMSWarning]] | None:
		# Compiles the code, highlighting and showing any error
		if self.entry_id is None:
			return None
		code = self.text.get('1.0', UI.END)
		parse_context = GraftParseContext(GraftLexer(code), self.delegate.data_context, self.language())
		try:
			compiled = self.compile_entry(parse_context, self.entry_id)
		except PyMSError as e:
			self.text.highlight_error(e)
			ErrorDialog(self, e)
			return None
		if parse_context.warnings:
			self.text.highlight_warnings(parse_context.warnings)
		return (compiled, parse_context.warnings)

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
		compiled, warnings = result
		if warnings:
			warning_dialog = WarningDialog(self, warnings, True)
			if not warning_dialog.cont:
				return False
		if not self.apply_compiled(compiled):
			return False
		# Refreshing updates the list and status bar, and reloads the code (no longer edited)
		self.delegate.refresh()
		return True

	def find(self) -> None:
		if self.findwindow is None:
			self.findwindow = FindReplaceDialog(self, self.text, self.delegate.config_.windows.find_replace)
			self.text.text.bind(UI.Key.F3(), self.findwindow.findnext)
		else:
			self.findwindow.show()

	def colors(self) -> None:
		dialog = SyntaxHighlightingDialog(self.window(), self.syntax_highlighting.all_highlight_components(), self.delegate.config_.last_path.highlights)
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
		return self.keywords

	def jump_highlights(self) -> Sequence[str] | None:
		return ('Error', 'Warning')

	def jump_sections(self) -> Sequence[str] | None:
		return None

	def find_definition(self, name: str) -> str | None:
		return None
