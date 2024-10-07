
from .FindReplaceDialog import FindReplaceDialog
from .Config import PyAIConfig
from .Delegates import MainDelegate

from ..FileFormats.AIBIN import AIBIN
from ..FileFormats.AIBIN.AICodeHandlers import CodeCommands, CodeTypes, CodeDirectives

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ..Utilities import ItemSelectDialog
from ..Utilities.EditedState import EditedState
from ..Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog

import re, io
from dataclasses import dataclass

class CodeEditDialog(PyMSDialog, ItemSelectDialog.Delegate, CodeTextDelegate):
	def __init__(self, parent: AnyWindow, delegate: MainDelegate, config: PyAIConfig, ids: list[str]):
		self.delegate = delegate
		self.config_ = config
		self.ids = ids

		self.edited_state = EditedState()
		self.edited_state.callback += self.update_edited

		self.decompile = ''
		self.file: str | None = None
		t = ''
		if ids:
			t = ', '.join(ids[:5])
			if len(ids) > 5:
				t += '...'
			t += ' - '
		t += 'AI Script Editor'
		PyMSDialog.__init__(self, parent, t, grabwait=False)
		self.findwindow: FindReplaceDialog | None = None

	def widgetize(self) -> Widget:
		self.bind(Alt.Left(), lambda _: self.gotosection(0))
		self.bind(Alt.Right(), lambda _: self.gotosection(1))
		self.bind(Alt.Up(), lambda _: self.gotosection(2))
		self.bind(Alt.Down(), lambda _: self.gotosection(3))

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s)
		self.toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', Ctrl.t)
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Code', Ctrl.e)
		self.toolbar.add_button(Assets.get_image('saveas'), self.exportas, 'Export As...', Ctrl.Alt.a)
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Code', Ctrl.i)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', Ctrl.f)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', Ctrl.Alt.c)
		self.toolbar.add_section()
		self.toolbar.add_button(Assets.get_image('insert'), self.insert_string_id, 'Insert String ID', Ctrl.Alt.i, enabled=self.delegate.get_data_context().stattxt_tbl is not None)
		self.toolbar.add_button(Assets.get_image('asc3topyai'), self.transpile_to_pyai, 'Transpile to PyAI code', Ctrl.Alt.p)
		self.toolbar.add_button(Assets.get_image('debug'), self.debuggerize, 'Debuggerize your code', Ctrl.d)
		self.toolbar.pack(fill=X, padx=2, pady=2)

		self.text = CodeText(self, self.edited_state, self)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.bind(CodeText.WidgetEvent.InsertCursorMoved(), self.statusupdate)
		self.text.text.bind(WidgetEvent.Text.Selection(), self.statusupdate)

		self.setup_syntax_highlighting()

		self.status = StringVar()
		if self.ids:
			self.status.set("Original ID's: " + ', '.join(self.ids))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = StatusBar(self)
		statusbar.add_label(self.status, weight=1)
		self.editstatus = statusbar.add_icon(Assets.get_image('save.gif'))
		statusbar.add_label(self.scriptstatus, weight=1)
		statusbar.pack(side=BOTTOM, fill=X)

		if self.ids:
			self.after(1, self.load)

		return self.text

	def setup_complete(self) -> None:
		self.config_.windows.code_edit.load_size(self)

	def setup_syntax_highlighting(self) -> None:
		cmd_names = [cmd.name for cmd in CodeCommands.all_basic_commands + CodeCommands.all_header_commands]
		type_names = [type.name for type in CodeTypes.all_basic_types]
		directive_names = [directive.name for directive in CodeDirectives.all_basic_directives + CodeDirectives.all_defs_directives]
		# TODO: Get keywords from Types?
		keywords = ['aiscript', 'bwscript', 'LessThan', 'GreaterThan']
		self.syntax_highlighting = SyntaxHighlighting(
			syntax_components=(
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Comment',
							description='The style of a comment.',
							highlight_style=self.config_.code.highlights.comment
						),
						pattern=r'(?:#|;)[^\n]*$'
					),
				)),
				SyntaxComponent((
					r'^[ \t]*',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Header',
							description='The style of a `script` header.',
							highlight_style=self.config_.code.highlights.header
						),
						pattern=r'script'
					),
					r'[ \t]+',
					HighlightPattern(
						highlight=HighlightComponent(
							name='AI ID',
							description='The style of the AI ID in the AI header.',
							highlight_style=self.config_.code.highlights.ai_id
						),
						pattern=r'[^\n\x00,():]{4}'
					),
					r'(?=[ \t]+\{)',
				)),
				SyntaxComponent((
					r'^[ \t]*',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Block',
							description='The style of a --block-- or :block in the code.',
							highlight_style=self.config_.code.highlights.block
						),
						pattern=r'--\w+--|:\w+'
					)
				)),
				SyntaxComponent((
					r'\b',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Command',
							description='The style of command names.',
							highlight_style=self.config_.code.highlights.command
						),
						pattern='|'.join(cmd_names)
					),
					r'\b'
				)),
				SyntaxComponent((
					r'\b',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Type',
							description='The style of type names.',
							highlight_style=self.config_.code.highlights.type
						),
						pattern='|'.join(type_names)
					),
					r'\b'
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Directive',
							description='The style of @directive names.',
							highlight_style=self.config_.code.highlights.directive
						),
						pattern=f'@(?:{"|".join(directive_names)})'
					),
					r'\b'
				)),
				SyntaxComponent((
					r'\b',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Number',
							description='The style of all numbers.',
							highlight_style=self.config_.code.highlights.number
						),
						pattern=r'\d+'
					),
					r'\b'
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='TBL Format',
							description='The style of TBL formatted characters, like null: <0>',
							highlight_style=self.config_.code.highlights.tbl_format
						),
						pattern=r'<0*(?:25[0-5]|2[0-4]\d|1?\d?\d)?>'
					),
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Operator',
							description='The style of the operators:\n    ( ) , = { }',
							highlight_style=self.config_.code.highlights.operator
						),
						pattern=r'[(),={}]'
					),
				)),
				SyntaxComponent((
					r'\b',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Keyword',
							description='The style of keywords.',
							highlight_style=self.config_.code.highlights.keyword
						),
						pattern='|'.join(keywords)
					),
					r'\b'
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Newline',
							description='The style of newlines',
							highlight_style=self.config_.code.highlights.newline
						),
						pattern=r'\n'
					),
				)),
			),
			highlight_components=(
				HighlightComponent(
					name='Selection',
					description='The style of selected text in the editor.',
					highlight_style=self.config_.code.highlights.selection,
					tag='sel'
				),
				HighlightComponent(
					name='Error',
					description='The style of highlighted errors in the editor.',
					highlight_style=self.config_.code.highlights.error
				),
				HighlightComponent(
					name='Warning',
					description='The style of highlighted warnings in the editor.',
					highlight_style=self.config_.code.highlights.warning
				),
			)
		)
		self.text.set_syntax_highlighting(self.syntax_highlighting)

	# TODO: Cleanup
	def gotosection(self, i: int) -> None:
		c = [self.text.tag_prevrange, self.text.tag_nextrange][i % 2]
		t = [('Error','Warning'),('AIID','Block')][i > 1]
		a = c(t[0], INSERT)
		b = c(t[1], INSERT)
		s = None
		if a:
			if not b or self.text.compare(a[0], '<' if i % 2 else '>', b[0]):
				s = a
			else:
				s = b
		elif b:
			s = b
		if s:
			self.text.see(s[0])
			self.text.mark_set(INSERT, s[0])

	def statusupdate(self, event: Event | None = None) -> None:
		line, column = self.text.index(INSERT).split('.')
		selected = 0
		sel_range = self.text.tag_ranges('sel')
		if sel_range:
			selected = len(self.text.get(*sel_range))
		self.scriptstatus.set(f'Line: {line}  Column: {column}  Selected: {selected}')

	def update_edited(self, edited: bool) -> None:
		self.editstatus['state'] = NORMAL if edited else DISABLED
		if self.file:
			self.title('AI Script Editor [*%s*]' % self.file)

	def cancel(self, _: Event | None = None) -> None:
		if self.edited_state.is_edited:
			save = MessageBox.askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return
				self.save()
		self.ok()

	def save(self, _: Event | None = None) -> None:
		code = self.text.get('1.0', END)
		if self.delegate.save_code(code, self):
			self.text.edit_modified(False)

	def test(self, _: Event | None = None) -> None:
		code = self.text.get('1.0', END)
		parse_context = self.delegate.get_parse_context(code)
		try:
			AIBIN.AIBIN.compile(parse_context)
		except PyMSError as e:
			if e.line is not None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line is not None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if parse_context.warnings:
			c = False
			for w in parse_context.warnings:
				if w.line is not None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, parse_context.warnings, True)
		else:
			MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def export(self, _: Event | None = None) -> None:
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('AI Script Editor [%s]' % self.file)

	def exportas(self, _: Event | None = None) -> None:
		file = self.config_.last_path.txt.ai.select_save(self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, _: Event | None = None) -> None:
		iimport = self.config_.last_path.txt.ai.select_save(self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				self.text.edit_reset()
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import',"Could not import file '%s'" % iimport))

	def find(self, _: Event | None = None) -> None:
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind(Key.F3(), self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, _: Event | None = None) -> None:
		dialog = SyntaxHighlightingDialog(self, self.syntax_highlighting.all_highlight_components())
		if dialog.updated:
			self.text.update_highlight_styles()

	RE_ASC3_HEADER = re.compile(r'^\s*script_name\s+([^;\n]+)\s*(?:;[^\n]+)?$.+?^\s*script_id\s+(....)', re.MULTILINE | re.DOTALL)
	RE_OLD_PYAI_HEADER = re.compile(r'^(?:\s*# stat_txt.tbl entry \d+:\s*(.+?))?\s*(....)\(\s*(\d+)\s*,\s*([01])([01])([01])\s*,\s*((?:bw|ai)script)\s*\):', re.MULTILINE)
	RE_OLD_PYAI_BLOCK = re.compile(r'^(\s*--)([^-]+)--', re.MULTILINE)
	RE_OLD_PYAI_COMMAND = re.compile(r'^(\s*)([\w]+)\(([^)]*)\)(.*)', re.MULTILINE)
	RE_COMMA = re.compile(r'\s*,\s*')
	def transpile_to_pyai(self, _: Event | None = None) -> None:
		code = self.text.text.get('1.0',END)

		def replace_asc3_header(match: re.Match) -> str:
			header_string = match.group(1)
			if re.match('bw|brood ?war', header_string, re.I):
				header_bin_file = 'bwscript'
			else:
				header_bin_file = 'aiscript'
			header_string_index = self.delegate.get_data_context().stattxt_id(header_string) or 0
			header_id = match.group(2)
			return f"""### NOTE: There is no way to determine the scripts flags or if it is a BW script or not!
###       please update the header below appropriately!
script {header_id} {{
    name_string {header_string_index} # {header_string}
    bin_file {header_bin_file}
    broodwar_only 1
    staredit_hidden 1
    requires_location 1
    entry_point {header_id}_entry_point
}}

:{header_id}_entry_point"""
		code = CodeEditDialog.RE_ASC3_HEADER.sub(replace_asc3_header, code)

		def replace_old_pyai_header(match: re.Match) -> str:
			return f"""script {match.group(2)} {{
    name_string {match.group(3)} # {match.group(1)}
    bin_file {match.group(7)}
    broodwar_only {match.group(4)}
    staredit_hidden {match.group(5)}
    requires_location {match.group(6)}
    entry_point {match.group(2)}_entry_point
}}

--{match.group(2)}_entry_point--"""
		code = CodeEditDialog.RE_OLD_PYAI_HEADER.sub(replace_old_pyai_header, code)

		def replace_old_pyai_block(match: re.Match) -> str:
			return match.group(1) + str(match.group(2)).replace(' ', '_') + '--'
		code = CodeEditDialog.RE_OLD_PYAI_BLOCK.sub(replace_old_pyai_block, code)

		def replace_old_pyai_command(match: re.Match) -> str:
			cmd_name = match.group(2)
			for cmd_def in CodeCommands.all_basic_commands:
				if cmd_def.name == cmd_name:
					result = match.group(1) + match.group(2) + '('
					params = CodeEditDialog.RE_COMMA.split(match.group(3))
					for n,(param,param_type) in enumerate(zip(params, cmd_def.param_types)):
						if n > 0:
							result += ', '
						if isinstance(param_type, CodeTypes.BlockCodeType):
							result += str(param).replace(' ', '_')
						else:
							result += param
					return result + ')' + match.group(4)
			return match.group(0)
		code = CodeEditDialog.RE_OLD_PYAI_COMMAND.sub(replace_old_pyai_command, code)

		with self.text.undo_group():
			self.text.delete('1.0', END)
			self.text.insert(END, code)

	def debuggerize(self) -> None:
		d = 0
		data = ''
		debug = {
			'goto':('debug(%(param1)s, Goto block "%(param1)s". %(s)s)%(c)s',0),
			'notowns_jump':('notowns_jump(%(param1)s,%(debug1)s)%(c)s\ndebug(%(debug2)s, I do not own the unit "%(param1)s"<44> continuing the current block... %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I own the unit "%(param1)s"<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'expand':('debug(%(debug1)s, Running block "%(param2)s" for expansion number "%(param1)s". %(s)s)\n	--%(debug1)s--\nexpand(%(param1)s, %(param2)s)%(c)s',1),
			'debug':('debug(%(param1)s, %(param2)s [%(param1)s]%(s)s)%(c)s',0),
			'random_jump':('random_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I randomly chose to continue this block instead of going to block "%(param2)s". %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, I randomly chose to go to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'time_jump':('time_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, "%(param1)s" minutes have not passed in game<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, "%(param1)s" minutes have passed in game<44> going to block "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'race_jump':('race_jump(%(debug1)s, %(debug2)s, %(debug3)s)%(c)s\n	--%(debug1)s--\ndebug(%(param1)s, My current enemy is Terran<44> going to block "%(param1)s". %(s)s)\n	--%(debug2)s--\ndebug(%(param2)s, My current enemy is Zerg<44> going to block "%(param2)s". %(s)s)\n	--%(debug3)s--\ndebug(%(param3)s, My current enemy is Protoss<44> going to block "%(param3)s". %(s)s)',3),
			#'region_size':('',),
			'groundmap_jump':('groundmap_jump(%(debug1)s)%(c)s\ndebug(%(debug2)s, The map is not a ground map<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param1)s, The map is a ground map<44> going to "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			'call':('debug(%(debug1)s, Calling block "%(param1)s". %(s)s)\n	--%(debug1)s--\ncall(%(param1)s)%(c)s\ndebug(%(debug2)s, Returned from a call to block "%(param1)s". %(s)s)\n	--%(debug2)s--',2),
			#'panic':('',),
			'multirun':('debug(%(debug1)s, Running block "%(param1)s" in another thread. %(s)s)\n	--%(debug1)s--\nmultirun(%(param1)s)%(c)s',1),
			#'rush':('',),
			'resources_jump':('resources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, I do not have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, I have at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyowns_jump':('enemyowns_jump(%(param1)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t own the unit "%(param1)s"<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param2)s, My current enemy owns the unit "%(param1)s"<44> going to "%(param2)s". %(s)s)\n	--%(debug2)s--',2),
			'enemyresources_jump':('enemyresources_jump(%(param1)s, %(param2)s, %(debug1)s)%(c)s\ndebug(%(debug2)s, My current enemy doesn\'t have at least "%(param1)s" minerals and "%(param2)s" vespene<44> continuing the current block. %(s)s)\n	--%(debug1)s--\ndebug(%(param3)s, My current enemy has at least "%(param1)s" minerals and "%(param2)s" vespene<44> going to "%(param3)s". %(s)s)\n	--%(debug2)s--',2),
			'stop':('debug(%(debug1)s, Stopping the current block. %(s)s)\n	--%(debug1)s--\nstop()%(c)s',1),
			#'if_owned':('',),
			#'allies_watch':('',),
			#'try_townpoint':('',),
		}
		header = re.compile(r'\A([^(]{4})\([^)]+\):\s*(?:\{.+\})?(?:\s*#.*)?\Z')
		label = re.compile(r'\A\s*--\s*(.+)\s*--(?:\s*\{(.+)\})?(?:\s*#.*)?\\Z')
		jump = re.compile(r'\A(\s*)(%s)\((.+)\)(\s*#.*)?\Z' % '|'.join(list(debug.keys())))
		script,block = '',''
		for n,line in enumerate(self.text.text.get('1.0',END).split('\n')):
			m = header.match(line)
			if m:
				script = m.group(1)
				block = ''
				data += line + '\n'
				continue
			m = label.match(line)
			if m:
				block = m.group(1)
				data += line + '\n'
				continue
			m = jump.match(line)
			if m and m.group(2) in debug:
				inblock = ''
				if block:
					inblock = ' block "%s"' % block
				rep = {
					'debug1':'== Debug %s ==' % d,
					'debug2':'== Debug %s ==' % (d+1),
					'debug3':'== Debug %s ==' % (d+2),
					's':'[Line: %s | Inside script "%s"%s]' % (n, script, inblock),
					'c':m.group(4) or '',
				}
				cmd_def = CodeCommandDefinition.find_by_name(m.group(2), CodeCommands.all_basic_commands)
				if cmd_def is not None and cmd_def.param_types:
					p = re.match('\\A%s\\Z' % ','.join(['\\s*(.+)\\s*'] * len(cmd_def.param_types)), m.group(3))
					if not p:
						data += line + '\n'
						continue
					for g,param in enumerate(p.groups()):
						rep['param%s' % (g+1)] = param
				data += m.group(1) + (debug[m.group(2)][0] % rep).replace('\n','\n' + m.group(1)) + '\n'
				d += debug[m.group(2)][1]
				continue
			data += line + '\n'
		with self.text.undo_group():
			self.text.delete('1.0', END)
			self.text.insert(END, data)

	def load(self) -> None:
		try:
			output = io.StringIO()
			serialize_context = self.delegate.get_serialize_context(output)
			self.delegate.get_ai_bin().decompile(serialize_context, self.ids)
			code = output.getvalue()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.text.load(code)
		# TODO: Warnings?
		# if warnings:
		# 	WarningDialog(self, warnings)

	# def close(self) -> None:
	# 	if self.decompile:
	# 		self.text.insert('1.0', self.decompile.strip())
	# 		self.decompile = ''
	# 		self.text.text.mark_set(INSERT, '1.0')
	# 		self.text.text.see(INSERT)
	# 		self.text.edit_reset()
	# 		self.text.edited = False
	# 		self.editstatus['state'] = DISABLED

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		Toplevel.destroy(self)

	def dismiss(self) -> None:
		self.config_.windows.code_edit.save_size(self)
		PyMSDialog.dismiss(self)

	RE_NAME_STRING_COMMAND: re.Pattern | None = None
	def re_name_string_command(self) -> re.Pattern:
		if CodeEditDialog.RE_NAME_STRING_COMMAND is None:
			CodeEditDialog.RE_NAME_STRING_COMMAND = re.compile(rf'(\s*{CodeCommands.HeaderNameString.name}\s+)(\d+)')
		return CodeEditDialog.RE_NAME_STRING_COMMAND

	def insert_string_id(self) -> None:
		initial_selection = []
		line = self.text.get(f'{INSERT} linestart', f'{INSERT} lineend')
		if match := self.re_name_string_command().match(line):
			initial_selection.append(int(match.group(2)))
		ItemSelectDialog.ItemSelectDialog(self, 'Select String', self, initial_selection)

	# ItemSelectDialog.Delegate
	def get_items(self) -> Sequence[ItemSelectDialog.Item]:
		strings = self.delegate.get_data_context().stattxt_strings()
		if not strings:
			return []
		# return [ItemSelectDialog.DisplayItem(string, f'{index}: {string}') for index, string in enumerate(strings)]
		return strings

	def item_selected(self, index: int) -> bool:
		with self.text.undo_group():
			line = self.text.get(f'{INSERT} linestart', f'{INSERT} lineend')
			insert_index: str = self.text.index(INSERT)
			if match := self.re_name_string_command().match(line):
				insert_index = f'{INSERT} linestart +{len(match.group(1))}c'
				self.text.delete(insert_index, f'{INSERT} lineend')
			str_index = str(index)
			comment = ''
			if string := self.delegate.get_data_context().stattxt_string(index):
				comment = self.delegate.get_formatters().comment.serialize([string])
			self.text.insert(insert_index, str_index + comment)
			self.text.mark_set(INSERT, f'{insert_index} +{len(str_index)}c')
		return True

	def items_selected(self, indexes: list[int]) -> bool:
		return True

	# CodeTextDelegate
	def comment_symbols(self) -> list[str]:
		return ['#', ';']

	def comment_symbol(self) -> str:
		# TODO: Formatter based
		return '#'

	def autocomplete_override_keys(self) -> str:
		return ' (,)'

	RE_FIRST_IDENTIFIER = re.compile(r'^\s*[a-z]')
	RE_BLOCK_NAME = re.compile(r'(?:--|:)(\w+)')
	def get_autocomplete_options(self, line: str) -> list[str] | None:
		autocompete_options = list(type.name for type in CodeTypes.all_basic_types)
		# TODO: Get type values 
		autocompete_options.extend(('aiscript', 'bwscript', 'LessThan', 'GreaterThan'))

		data_context = self.delegate.get_data_context()
		for unit_id in range(228):
			unit_name = data_context.unit_name(unit_id)
			if unit_name and not unit_name in autocompete_options:
				autocompete_options.append(unit_name)
		for upgrade_id in range(61):
			upgrade_name = data_context.upgrade_name(upgrade_id)
			if upgrade_name and not upgrade_name in autocompete_options:
				autocompete_options.append(upgrade_name)
		for tech_id in range(44):
			tech_name = data_context.technology_name(tech_id)
			if tech_name and not tech_name in autocompete_options:
				autocompete_options.append(tech_name)

		head = '1.0'
		while True:
			block_range = self.text.tag_nextrange('Block', head)
			if not block_range:
				break
			block_text = self.text.get(*block_range)
			match = CodeEditDialog.RE_BLOCK_NAME.match(block_text)
			if match and not match.group(1) in autocompete_options:
				autocompete_options.append(match.group(1))
			head = block_range[1]
		autocompete_options.sort()

		main_identifiers = list(cmd.name for cmd in CodeCommands.all_basic_commands + CodeCommands.all_header_commands)
		main_identifiers.sort()
		# TODO: Directives
		main_identifiers.extend(('@spellcaster','@supress_all','@suppress_next_line'))
		main_identifiers.append('script')

		is_first_identifier = not not CodeEditDialog.RE_FIRST_IDENTIFIER.match(line)
		if is_first_identifier:
			autocompete_options = main_identifiers + autocompete_options
		else:
			autocompete_options.extend(main_identifiers)
			
		return autocompete_options
