
from ..Widgets import *
from ..EventPattern import *
from ..Font import Font
from ..SyntaxHighlighting import SyntaxHighlighting, HighlightComponent
from ..Types import Comparitors

from ...EditedState import EditedState
from ...PyMSError import PyMSError
from ...PyMSWarning import PyMSWarning

import re
from dataclasses import dataclass

from typing import Generator, Protocol, Sequence

@dataclass
class AutocompleteState:
	text_prefix: str
	options: list[str]
	option_index: int
	start_index: str
	end_index: str

class CodeTextDelegate(Protocol):
	def comment_symbols(self) -> Sequence[str]:
		...

	def comment_symbol(self) -> str:
		...

	def autocomplete_override_keys(self) -> str:
		...

	def get_autocomplete_options(self, line: str) -> Sequence[str] | None:
		...

	def jump_highlights(self) -> Sequence[str] | None:
		...

	def jump_sections(self) -> Sequence[str] | None:
		...

class _UndoGroup:
	def __init__(self, text: Text) -> None:
		self.text = text
		self.autoseparator = self.text['autoseparator']

	def __enter__(self) -> None:
		self.text['autoseparator'] = False
		self.text.edit_separator()

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.text['autoseparator'] = self.autoseparator

class CodeText(Frame):
	autoindent = re.compile('^([ \\t]*)')
	selregex = re.compile('\\bsel\\b')

	class WidgetEvent:
		TextChanged = CustomEventPattern(Field('TextChanged'))
		InsertCursorMoved = CustomEventPattern(Field('InsertCursorMoved'))

	def __init__(self, parent: Misc, edited_state: EditedState, delegate: CodeTextDelegate) -> None:
		self.edited_state = edited_state
		self.delegate = delegate

		self.highlight_components: Sequence[HighlightComponent] | None = None
		self.re_syntax: re.Pattern | None = None
		self.autocomplete_state: AutocompleteState | None = None

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		frame = Frame(self)
	
		font = Font.fixed().sized(12)
		self.lines = Text(frame, height=1, font=font, bg='#E4E4E4', fg='#808080', width=8, cursor='')
		self.lines.config(bd=0)
		self.lines.pack(side=LEFT, fill=Y)

		hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)

		self.text = Text(frame, height=1, font=font, undo=True, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=self.yscroll, exportselection=False)
		self.text.config(bd=0)
		self.text.configure(tabs=self.tk.call("font", "measure", self.text["font"], "-displayof", frame, '    '))
		self.text.pack(side=LEFT, fill=BOTH, expand=1)
		self.text.bind(Ctrl.a(), lambda e: self.after(1, self.selectall))

		frame.grid(sticky=NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.tag_configure = self.text.tag_configure
		self.tag_add = self.text.tag_add
		self.tag_remove = self.text.tag_remove
		self.tag_raise = self.text.tag_raise
		self.tag_nextrange = self.text.tag_nextrange
		self.tag_prevrange = self.text.tag_prevrange
		self.tag_ranges = self.text.tag_ranges
		self.tag_names = self.text.tag_names
		self.tag_bind = self.text.tag_bind
		self.tag_delete = self.text.tag_delete
		self.mark_set = self.text.mark_set
		self.index = self.text.index
		self.get = self.text.get
		self.see = self.text.see
		self.compare = self.text.compare
		self.edit_undo = self.text.edit_undo
		self.edit_redo = self.text.edit_redo
		self.edit_reset = self.text.edit_reset
		self.edit_modified = self.text.edit_modified
		self.edit_separator = self.text.edit_separator
		self.delete = self.text.delete
		self.insert = self.text.insert

		self.textmenu = Menu(self, tearoff=0)
		self.textmenu.add_command('Undo', self.edit_undo, tags='can_undo', underline='u')
		self.textmenu.add_command('Redo', self.edit_redo, tags='can_redo', underline='r')
		self.textmenu.add_separator()
		self.textmenu.add_command('Cut', lambda: self.copy(True), tags='has_selection', underline='t')
		self.textmenu.add_command('Copy', self.copy, tags='has_selection', underline='c')
		self.textmenu.add_command('Paste', self.paste, tags='can_paste', underline='p')
		self.textmenu.add_command('Delete', lambda: self.delete('sel.first', 'sel.last'), tags='has_selection', underline='d')
		self.textmenu.add_separator()
		self.textmenu.add_command('Select All', self.selectall, underline='a')

		self.lines.insert('1.0', '      1')

		self.lines.bind(Mouse.Scroll(), lambda _: EventPropogation.Break)
		self.lines.bind(Focus.In(), self.selectline)

		self.afterid: str | None = None
		self.last_delete: tuple[str, str, str] | None = None
		self.coloring = False
		self.dnd = False
		self.motion_bind: str | None = None

		self.text.bind(Key.Tab(), self.autocomplete)
		self.text.bind(Ctrl.BracketRight(), self.indent)
		self.text.bind(Ctrl.BracketLeft(), self.dedent)
		self.text.bind(Shift.Tab(), self.dedent)
		self.text.bind(ButtonRelease.Click_Right(), self.popup)
		self.text.bind(WidgetEvent.Text.Modified(), self.modified)
		self.text.bind(Ctrl.Slash(), self.comment_range)
		self.text.bind(Key.Pressed(), self.key_pressed)

		if self.delegate.jump_highlights():
			self.text.bind(Alt.Left(), lambda _: self.goto_highlight(-1))
			self.text.bind(Alt.Right(), lambda _: self.goto_highlight(1))
		if self.delegate.jump_sections():
			self.text.bind(Alt.Up(), lambda _: self.goto_section(-1))
			self.text.bind(Alt.Down(), lambda _: self.goto_section(1))

		self.tag_configure('sel', foreground='')

		self.text_orig = getattr(self.text, '_w') + '_orig'
		self.tk.call('rename', getattr(self.text, '_w'), self.text_orig)
		self.tk.createcommand(getattr(self.text, '_w'), self.dispatch)

	def edit_canundo(self) -> bool:
		try:
			return self.tk.call(getattr(self.text, '_w'), 'edit', 'canundo')
		except:
			return True

	def edit_canredo(self) -> bool:
		try:
			return self.tk.call(getattr(self.text, '_w'), 'edit', 'canredo')
		except:
			return True

	def undo_group(self) -> _UndoGroup:
		return _UndoGroup(self.text)

	def has_selection(self) -> bool:
		return not not self.tag_ranges('sel')

	def load(self, text: str) -> None:
		self.delete('1.0', END)
		self.insert(END, text)
		self.edit_reset()
		self.edit_modified(False)

	def popup(self, e: Event) -> str | None:
		if not self.text['state'] == NORMAL:
			return EventPropogation.Break
		
		self.textmenu.tag_enabled('can_undo', self.edit_canundo())
		self.textmenu.tag_enabled('can_redo', self.edit_canredo())
		self.textmenu.tag_enabled('has_selection', not not self.tag_ranges('sel'))
		self.textmenu.tag_enabled('can_paste', self.clipboard_not_empty())

		self.textmenu.post(e.x_root, e.y_root)

		return EventPropogation.Break

	def copy(self, cut=False) -> None:
		self.clipboard_set(self.get('sel.first','sel.last'))
		if cut:
			self.mark_set('insert', 'sel.first')
			self.delete('sel.first','sel.last')
			self.update_lines()

	def paste(self) -> None:
		text = self.clipboard_get()
		if not text:
			return
		with self.undo_group():
			if self.has_selection():
				self.mark_set(INSERT, 'sel.first')
				self.delete('sel.first','sel.last')
			self.insert(INSERT, text)
		self.update_lines()

	def focus_set(self) -> None:
		self.text.focus_set()

	def __setitem__(self, item: str, value: Any) -> None:
		if item == 'state':
			self.lines['state'] = value
			self.text['state'] = value
		else:
			Frame.__setitem__(self, item, value)

	def selectall(self, e: Event | None = None) -> None:
		self.tag_add('sel', '1.0', END)
		self.mark_set(INSERT, '1.0')

	def lines_indexes(self) -> tuple[str, str]:
		sel_range = self.tag_ranges('sel')
		if sel_range:
			return (self.index(f'{sel_range[0]} linestart'), self.index(f'{sel_range[1]} linestart'))
		index = self.index('insert linestart')
		return (index, index)

	def lines_range(self, head: str | None = None, tail: str | None = None) -> Generator[str, None, None]:
		if head is None or tail is None:
			head, tail = self.lines_indexes()
		while self.compare(head, '<=', tail):
			yield head
			next_head = self.index('%s +1line' % head)
			if next_head == head:
				break
			head = next_head

	def indent(self, event: Event | None = None) -> str | None:
		for line_index in self.lines_range():
			self.insert(line_index, '\t')
		return EventPropogation.Break

	def dedent(self, event: Event | None = None) -> str | None:
		for line_index in self.lines_range():
			if self.get(line_index) in ' \t':
				self.delete(line_index)
		return EventPropogation.Break

	def comment_range(self, event: Event | None = None) -> str | None:
		regex = re.compile(rf'(\s*)({"|".join(self.delegate.comment_symbols())}\s*)?(.*)')
		with self.undo_group():
			for line_index in self.lines_range():
				m = regex.match(self.get(line_index, f'{line_index} lineend'))
				if m:
					start = self.index(f'{line_index} +{len(m.group(1))}c')
					if m.group(2):
						self.delete(start, f'{line_index} +{len(m.group(1))+len(m.group(2))}c')
					else:
						self.insert(start, f'{self.delegate.comment_symbol()} ')
		return EventPropogation.Break

	def key_pressed(self, event: Event | None) -> str | None:
		if self.autocomplete_state and event and event.char and event.char in self.delegate.autocomplete_override_keys():
			self.tag_remove('sel', '1.0', END)
			self.mark_set(INSERT, self.autocomplete_state.end_index)
			self.autocomplete_state = None
		return EventPropogation.Continue

	def yview(self, *args: float) -> None:
		self.lines.yview(*args)
		self.text.yview(*args)

	def yscroll(self, *args: float) -> None:
		self.vscroll.set(*args)
		self.lines.yview(MOVETO, args[0])

	def selectline(self, e: Event | None = None) -> None:
		self.tag_remove('sel', '1.0', END)
		head = self.lines.index('current linestart')
		tail = self.index('%s lineend+1c' % head)
		self.tag_add('sel', head, tail)
		self.mark_set(INSERT, tail)
		self.focus_set()

	def modified(self, event: Event | None = None) -> None:
		self.edited_state.mark_edited(self.text.edit_modified())
		self.update_lines()

	def update_lines(self) -> None:
		lines = self.lines.get('1.0', END).count('\n')
		dif = self.get('1.0', END).count('\n') - lines
		if dif > 0:
			self.lines.insert(END, '\n' + '\n'.join(['%s%s' % (' ' * (7-len(str(n))), n) for n in range(lines+1,lines+1+dif)]))
		elif dif:
			self.lines.delete('%s%slines' % (END,dif),END)

	def mark_recolor_line(self, index: str) -> None:
		self.mark_recolor_range(f'{index} linestart', f'{index} lineend')

	def mark_recolor_range(self, start: str, end: str) -> None:
		self.tag_add("Update", start, end)
		if self.coloring:
			self.coloring = False
		if not self.afterid:
			self.afterid = self.after(1, self.docolor)

	def set_syntax_highlighting(self, syntax_highlighting: SyntaxHighlighting) -> None:
		if self.highlight_components is not None:
			for highlight_component in self.highlight_components:
				self.tag_delete(highlight_component.tag_name)
		self.highlight_components = syntax_highlighting.all_highlight_components()
		self.re_syntax = syntax_highlighting.re_pattern
		self.update_highlight_styles()
		self.focus_set()
		self.mark_recolor_range('1.0', END)

	def update_highlight_styles(self) -> None:
		if not self.highlight_components:
			return
		for highlight_component in self.highlight_components:
			self.tag_delete(highlight_component.tag_name)
			self.tag_configure(highlight_component.tag_name, **highlight_component.highlight_style.style.configuration)
		self.tag_raise('sel')

	def docolor(self) -> None:
		self.afterid = None
		if self.coloring:
			return
		self.coloring = True
		self.colorize()
		self.coloring = False
		if self.tag_ranges('Update'):
			self.after_id = self.after(1, self.docolor)

	def colorize(self) -> None:
		if self.re_syntax is None or self.highlight_components is None:
			return
		next = '1.0'
		while True:
			item = self.tag_nextrange('Update', next)
			if not item:
				break
			self.tag_remove('Update', *item)
			head, tail = item
			next = self.index(f'{tail} +1lines linestart')
			head = self.index(f'{head} linestart')
			tail = self.index(f'{tail} lineend')
			for highlight_compoent in self.highlight_components:
				if highlight_compoent.tag_name != 'sel':
					self.tag_remove(highlight_compoent.tag_name, head, tail)
			for line_index in self.lines_range(head, tail):
				line = self.get(line_index, f'{line_index} lineend')
				match = self.re_syntax.search(line)
				while match:
					for key, value in list(match.groupdict().items()):
						if value is not None:
							match_head, match_tail = match.span(key)
							self.tag_add(key, f'{line_index} +{match_head}c', f'{line_index} +{match_tail}c')
					match = self.re_syntax.search(line, match.end())
			if not self.coloring:
				return

	def autocomplete(self, event: Event | None) -> str | None:
		if self.has_selection() and not self.autocomplete_state:
			return EventPropogation.Continue
		
		if not self.autocomplete_state:
			index = self.index('insert')
			line = self.get(f'{index} linestart', index)
			text_prefix = line
			if ' ' in text_prefix:
				text_prefix = text_prefix.split(' ')[-1]
			if not text_prefix:
				return EventPropogation.Continue

			autocomplete_options = self.delegate.get_autocomplete_options(line)
			if autocomplete_options is None:
				return EventPropogation.Continue

			next_char = self.get(index)
			if next_char and not next_char in ' \t\n':
				return EventPropogation.Continue
			
			options = list(option[len(text_prefix):] for option in autocomplete_options if option.startswith(text_prefix))
			if not options:
				return EventPropogation.Break
			self.autocomplete_state = AutocompleteState(text_prefix, options + [''], 0, index, index)
		
		# TODO: How does this affect undo/redo?
		with self.undo_group():
			self.delete(self.autocomplete_state.start_index, self.autocomplete_state.end_index)
			option = self.autocomplete_state.options[self.autocomplete_state.option_index]
			self.insert(self.autocomplete_state.start_index, option)
			end_index = self.index(f'{self.autocomplete_state.start_index} +{len(option)}c')
			self.tag_remove('sel', '1.0', END)
			self.tag_add('sel', self.autocomplete_state.start_index, end_index)

		self.autocomplete_state.option_index += 1
		if self.autocomplete_state.option_index == len(self.autocomplete_state.options):
			self.autocomplete_state.option_index = 0
		self.autocomplete_state.end_index = end_index

		return EventPropogation.Break

	def dispatch(self, cmd: str, *args: str) -> str:
		recolor_range: tuple[str, str] | None = None
		if cmd == 'insert':
			index = args[0]
			if index == 'end':
				index = 'end -1c'
			index = self.index(index)
			recolor_range = (index, f'{index} +{len(args[1])}c')
		elif cmd == 'delete':
			index = self.index(f'{args[0]} linestart')
			recolor_range = (index, f'{index} lineend')
		elif cmd == 'edit' and args[0] in ('redo', 'undo'):
			# When an undo/redo happens we don't know what it does, so we need to recolor everything
			recolor_range = ('1.0', END)
		try:
			result = self.tk.call((self.text_orig, cmd) + args)
		except:
			result = ""
		# print(cmd, args, result)
		if recolor_range:
			self.mark_recolor_range(*recolor_range)
			self.event_generate(CodeText.WidgetEvent.TextChanged())
		if cmd == 'mark' and args[0] == 'set' and args[1] == INSERT:
			self.event_generate(CodeText.WidgetEvent.InsertCursorMoved())
			pass
		return result

	def _goto_tag(self, tags: Sequence[str], direction: int) -> None:
		next_range = self.text.tag_prevrange if direction < 0 else self.text.tag_nextrange
		comparitor: Comparitors = '>' if direction < 0 else '<'
		closest_index: str | None = None
		for tag in tags:
			tag_range = next_range(tag, INSERT)
			if tag_range and (not closest_index or self.text.compare(tag_range[0], comparitor, closest_index)):
				closest_index = tag_range[0]
		if closest_index:
			self.text.see(closest_index)
			self.text.mark_set(INSERT, closest_index)

	def goto_highlight(self, direction: int) -> None:
		if (tags := self.delegate.jump_highlights()):
			self._goto_tag(tags, direction)

	def goto_section(self, direction: int) -> None:
		if (tags := self.delegate.jump_sections()):
			self._goto_tag(tags, direction)

	def highlight_error(self, error: PyMSError, tag: str = 'Error', warnings_tag: str = 'Warning') -> None:
		if error.line is not None:
			self.text.see('%s.0' % error.line)
			self.text.tag_add(tag, '%s.0' % error.line, '%s.end' % error.line)
			if error.warnings and warnings_tag:
				self.highlight_warnings(error.warnings, warnings_tag, see=False)

	def highlight_warning(self, warning: PyMSWarning, tag: str = 'Warning', see: bool = True) -> None:
		if warning.line is not None:
			self.text.see('%s.0' % warning.line)
			self.text.tag_add(tag, '%s.0' % warning.line, '%s.end' % warning.line)

	def highlight_warnings(self, warnings: list[PyMSWarning], tag: str = 'Warning', see: bool = True) -> None:
		for warning in warnings:
			self.highlight_warning(warning, tag, see)
			see = False
