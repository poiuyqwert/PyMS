
from .Delegates import MainDelegate, CodeGeneratorDelegate
from .Config import PyICEConfig
from .FindReplaceDialog import FindReplaceDialog
from .CodeGeneratorDialog import CodeGeneratorDialog
from .PreviewerDialog import PreviewerDialog, PREVIEWER_CMDS, EntryType
from .SoundDialog import SoundDialog
from .CodeTooltip import AnimationTooltip, CommandTooltip

from ..FileFormats.IScriptBIN import IScriptBIN
from ..FileFormats.IScriptBIN.CodeHandlers import CodeCommands, CodeTypes
# from ..FileFormats import GRP

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities import Assets
from ..Utilities.EditedState import EditedState
from ..Utilities.CodeHandlers import CodeType
from ..Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog

import re, io

from typing import Sequence, Any

class CodeEditDialog(PyMSDialog, UI.CodeTextDelegate, CodeGeneratorDelegate):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, config: PyICEConfig, ids: list[int]) -> None:
		self.delegate = delegate
		self.config_ = config
		self.ids = ids

		self.edited_state = EditedState()
		self.edited_state.callback += self.update_edited

		self.decompile = ''
		self.file: str | None = None

		title = ''
		if ids:
			title = ', '.join([str(i) for i in ids[:5]])
			if len(ids) > 5:
				title += '...'
			title += ' - '
		title += 'IScript Editor'
		PyMSDialog.__init__(self, parent, title, grabwait=False)
		self.findwindow: FindReplaceDialog | None = None
		self.previewer: PreviewerDialog | None = None

		self.syntax_highlighting: UI.SyntaxHighlighting

	def widgetize(self) -> UI.Widget:
		toolbar = UI.Toolbar(self)
		toolbar.add_button(Assets.get_image('save'), self.save, 'Save', UI.Ctrl.s)
		toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', UI.Ctrl.t)
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('export'), self.export, 'Export Code', UI.Ctrl.e)
		toolbar.add_button(Assets.get_image('saveas'), self.exportas, 'Export As...', UI.Ctrl.Alt.a)
		toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Code', UI.Ctrl.i)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', UI.Ctrl.f)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', UI.Ctrl.Alt.c)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('debug'), self.generate, 'Generate Code', UI.Ctrl.g)
		toolbar.add_button(Assets.get_image('insert'), self.preview, 'Insert/Preview Window', UI.Ctrl.w)
		toolbar.add_button(Assets.get_image('fwp'), self.sounds, 'Sound Previewer', UI.Ctrl.q)
		toolbar.pack(side=UI.TOP, fill=UI.X, padx=2, pady=2)

		self.text = UI.CodeText(self, self.edited_state, self)
		self.text.pack(fill=UI.BOTH, expand=1, padx=1, pady=1)

		self.setup_syntax_highlighting()

		self.status = UI.StringVar()
		self.status.set("Origional ID's: " + ', '.join([str(i) for i in self.ids]))
		self.scriptstatus = UI.StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = UI.Frame(self)
		UI.Label(statusbar, textvariable=self.status, bd=1, relief=UI.SUNKEN, anchor=UI.W).pack(side=UI.LEFT, expand=1, padx=1, fill=UI.X)
		self.editstatus = UI.Label(statusbar, image=Assets.get_image('save'), bd=0, state=UI.DISABLED)
		self.editstatus.pack(side=UI.LEFT, padx=1, fill=UI.Y)
		UI.Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=UI.SUNKEN, anchor=UI.W).pack(side=UI.LEFT, expand=1, padx=1, fill=UI.X)
		statusbar.pack(side=UI.BOTTOM, fill=UI.X)

		return self.text

	def setup_complete(self) -> None:
		self.after_managed(1, self.load)

		self.config_.windows.code_edit.load_size(self)

	def setup_syntax_highlighting(self) -> None:
		cmd_names = [cmd.name for cmd in CodeCommands.all_basic_commands]
		header_names = [cmd.name for cmd in CodeCommands.all_header_commands]
		keywords: list[str] = []
		for code_type in CodeTypes.all_basic_types + CodeTypes.all_header_types:
			if isinstance(code_type, CodeType.HasKeywords):
				keywords.extend(code_type.keywords())
		self.syntax_highlighting = UI.SyntaxHighlighting(
			syntax_components=(
				UI.SyntaxComponent((
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Comment',
							description='The style of a comment.',
							highlight_style=self.config_.code.highlights.comment
						),
						pattern=r'#[^\n]*$'
					),
				)),
				UI.SyntaxComponent((
					r'\b',
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Keyword',
							description='The style of keywords.',
							highlight_style=self.config_.code.highlights.keyword
						),
						pattern='|'.join(keywords)
					),
					r'\b'
				)),
				UI.SyntaxComponent((
					r'^[ \t]*',
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Block',
							description='The style of a --block-- or :block in the code.',
							highlight_style=self.config_.code.highlights.block
						),
						pattern=r'\w+:'
					)
				)),
				UI.SyntaxComponent((
					r'\b',
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Command',
							description='The style of command names.',
							highlight_style=self.config_.code.highlights.command
						),
						pattern='|'.join(cmd_names)
					),
					r'\b'
				)),
				UI.SyntaxComponent((
					r'\b',
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Header Command',
							description='The style of header command names.',
							highlight_style=self.config_.code.highlights.header_command
						),
						pattern='|'.join(header_names)
					),
					r'\b'
				)),
				UI.SyntaxComponent((
					r'\b',
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Number',
							description='The style of all numbers.',
							highlight_style=self.config_.code.highlights.number
						),
						pattern=r'\d+|0x[0-9a-fA-F]+'
					),
					r'\b'
				)),
				UI.SyntaxComponent((
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Operator',
							description='The style of the operators:\n    ( ) : , =',
							highlight_style=self.config_.code.highlights.operator
						),
						pattern=r'[():,=]'
					),
				)),
				UI.SyntaxComponent((
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Header',
							description='The style of a `script` header.',
							highlight_style=self.config_.code.highlights.header
						),
						pattern=r'\.headerstart|\.headerend'
					),
				)),
				UI.SyntaxComponent((
					UI.HighlightPattern(
						highlight=UI.HighlightComponent(
							name='Newline',
							description='The style of newlines',
							highlight_style=self.config_.code.highlights.newline
						),
						pattern=r'\n'
					),
				)),
			),
			highlight_components=(
				UI.HighlightComponent(
					name='Selection',
					description='The style of selected text in the editor.',
					highlight_style=self.config_.code.highlights.selection,
					tag='sel'
				),
				UI.HighlightComponent(
					name='Error',
					description='The style of highlighted errors in the editor.',
					highlight_style=self.config_.code.highlights.error
				),
				UI.HighlightComponent(
					name='Warning',
					description='The style of highlighted warnings in the editor.',
					highlight_style=self.config_.code.highlights.warning
				),
			)
		)
		self.text.set_syntax_highlighting(self.syntax_highlighting)

		AnimationTooltip(self.text.text)
		CommandTooltip(self.text.text)

	def statusupdate(self, _event: UI.Event | None = None) -> None:
		line, column = self.text.index(UI.INSERT).split('.')
		selected = 0
		sel_range = self.text.tag_ranges('sel')
		if sel_range:
			selected = len(self.text.get(*sel_range))
		self.scriptstatus.set(f'Line: {line}  Column: {column}  Selected: {selected}')

	def update_edited(self, edited: bool) -> None:
		self.editstatus['state'] = UI.NORMAL if edited else UI.DISABLED
		if self.file:
			self.title(f'IScript Editor [*{self.file}*]')

	def cancel(self, _event: UI.Event | None = None) -> None:
		if self.edited_state.is_edited:
			save = UI.MessageBox.askyesnocancel(parent=self, title='Save Code?', message="Would you like to save the code?", default=UI.MessageBox.YES)
			if save is None:
				return
			if save:
				self.save()
		self.ok()

	def save(self, _event: UI.Event | None = None) -> None:
		code = self.text.get('1.0', UI.END)
		if self.delegate.save_code(code, self):
			self.text.edit_modified(False)

	def dismiss(self) -> None:
		self.config_.windows.code_edit.save_size(self)
		PyMSDialog.dismiss(self)

	# TODO: Check frames
	# def checkframes(self, grp: GRP) -> int | None:
	# 	try:
	# 		if os.path.exists(grp):
	# 			p = grp
	# 		else:
	# 			p = self.parent.mpqhandler.load_file('MPQ:unit\\' + grp)
	# 		grp = GRP.CacheGRP()
	# 		grp.load_file(p)
	# 	except PyMSError:
	# 		return None
	# 	return grp.frames

	def test(self, _event: UI.Event | None = None) -> None:
		code = self.text.get('1.0', UI.END)
		parse_context = self.delegate.get_parse_context(code)
		try:
			IScriptBIN.IScriptBIN.compile(parse_context)
		except PyMSError as e:
			self.text.highlight_error(e)
			ErrorDialog(self, e)
			return
		if parse_context.warnings:
			self.text.highlight_warnings(parse_context.warnings)
			WarningDialog(self, parse_context.warnings, True)
		else:
			UI.MessageBox.showinfo(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.')

	def export(self, _event: UI.Event | None = None) -> None:
		if not self.file:
			self.exportas()
		else:
			with open(self.file, 'w', encoding='utf-8') as f:
				f.write(self.text.get('1.0', UI.END))
			self.title(f'IScript Editor [{self.file}]')

	def exportas(self, _event: UI.Event | None = None) -> None:
		file = self.config_.last_path.txt.select_save(self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, _event: UI.Event | None = None) -> None:
		iimport = self.config_.last_path.txt.select_open(self)
		if iimport:
			try:
				with open(iimport, 'r', encoding='utf-8') as f:
					self.text.delete('1.0', UI.END)
					self.text.insert('1.0', f.read())
					self.text.edit_reset()
			except Exception:
				ErrorDialog(self, PyMSError('Import', f'Could not import file "{iimport}"'))

	def find(self, _event: UI.Event | None = None) -> None:
		if self.findwindow is None:
			findwindow = FindReplaceDialog(self, self.text, self.config_.windows.find_replace)
			self.findwindow = findwindow
			self.bind(UI.Key.F3(), findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, _event: UI.Event | None = None) -> None:
		dialog = SyntaxHighlightingDialog(self, self.syntax_highlighting.all_highlight_components())
		if dialog.updated:
			self.text.update_highlight_styles()

	def generate(self, *_: Any) -> None:
		CodeGeneratorDialog(self, self.config_, self)

	def preview(self, _event: UI.Event | None = None) -> None:
		if not self.previewer or self.previewer.state() == 'withdrawn':
			if self.previewer is None:
				self.previewer = PreviewerDialog(self, self.delegate, self.config_, self.text)
			self.previewer.updatecurrentimages()
			t = re.split('\\s+',self.text.get(f'{UI.INSERT} linestart', f'{UI.INSERT} lineend').split('#',1)[0].strip())
			parse_context = self.delegate.get_parse_context(t[1])
			if t[0] in PREVIEWER_CMDS[EntryType.iscript] and self.previewer.curradio['state'] == UI.NORMAL:
				try:
					f = CodeTypes.FrameCodeType().parse(parse_context)
				except Exception:
					f = 0
				self.previewer.type.set(0)
				self.previewer.curid.set(0)
				self.previewer.curcmd.set(PREVIEWER_CMDS[EntryType.iscript].index(t[0]))
				self.previewer.select(0, EntryType.iscript, f)
			elif t[0] in PREVIEWER_CMDS[EntryType.images_dat]:
				try:
					n = CodeTypes.ImageIDCodeType().parse(parse_context)
				except Exception:
					n = 0
				self.previewer.type.set(1)
				self.previewer.image.set(n)
				self.previewer.imagecmd.set(PREVIEWER_CMDS[EntryType.images_dat].index(t[0]))
				self.previewer.select(n, EntryType.images_dat)
			elif t[0] in PREVIEWER_CMDS[EntryType.sprites_dat]:
				try:
					n = CodeTypes.SpriteIDCodeType().parse(parse_context)
				except Exception:
					n = 0
				self.previewer.type.set(2)
				self.previewer.sprites.set(n)
				self.previewer.spritescmd.set(PREVIEWER_CMDS[EntryType.sprites_dat].index(t[0]))
				self.previewer.select(n, EntryType.sprites_dat)
			elif t[0] in PREVIEWER_CMDS[EntryType.flingy_dat]:
				try:
					n = CodeTypes.FlingyIDCodeType().parse(parse_context)
				except Exception:
					n = 0
				self.previewer.type.set(3)
				self.previewer.flingys.set(n)
				self.previewer.flingyscmd.set(PREVIEWER_CMDS[EntryType.flingy_dat].index(t[0]))
				self.previewer.select(n, EntryType.flingy_dat)
			else:
				self.previewer.select(0, self.previewer.entry_type())
			self.previewer.deiconify()
			self.after_managed(50, self.previewer.updateframes)
		self.previewer.focus_set()

	def sounds(self) -> None:
		t = re.split('\\s+',self.text.get(f'{UI.INSERT} linestart', f'{UI.INSERT} lineend').split('#',1)[0].strip())
		i = 0
		if t[0] == 'playsnd':
			try:
				i = CodeTypes.SoundIDCodeType().parse(self.delegate.get_parse_context(t[1]))
			except Exception:
				pass
		SoundDialog(parent=self, delegate=self.delegate, config=self.config_.sounds, text=self.text, sound_id=i)

	def load(self) -> None:
		output = io.StringIO()
		serialize_context = self.delegate.get_serialize_context(output)
		try:
			self.delegate.get_iscript_bin().decompile(serialize_context, script_ids=self.ids)
			code = output.getvalue()
		except PyMSError as e:
			ErrorDialog(self, e)
			return
		self.text.load(code)
		# if warnings:
		# 	WarningDialog(self, warnings)

	def write(self, text: str) -> None:
		self.decompile += text

	def readlines(self) -> list[str]:
		return self.text.get('1.0', UI.END).split('\n')

	def destroy(self) -> None:
		if self.findwindow:
			UI.Toplevel.destroy(self.findwindow)
		if self.previewer:
			UI.Toplevel.destroy(self.previewer)
		UI.Toplevel.destroy(self)

	# CodeTextDelegate
	def comment_symbols(self) -> Sequence[str]:
		return ('#', )

	def comment_symbol(self) -> str:
		return '#'

	def autocomplete_override_keys(self) -> str:
		return ' (,):'

	RE_FIRST_IDENTIFIER = re.compile(r'^\s*[a-z]')
	RE_BLOCK_NAME = re.compile(r'(?:--|:)(\w+)')
	def get_autocomplete_options(self, line: str) -> Sequence[str] | None:
		autocomplete_options = ['.headerstart','.headerend']

		head = '1.0'
		while True:
			block_range = self.text.tag_nextrange('Block', head)
			if not block_range:
				break
			block_text = self.text.get(*block_range)
			match = CodeEditDialog.RE_BLOCK_NAME.match(block_text)
			if match and not match.group(1) in autocomplete_options:
				autocomplete_options.append(match.group(1))
			head = block_range[1]

		main_identifiers = sorted(cmd.name for cmd in CodeCommands.all_basic_commands + CodeCommands.all_header_commands)
		is_first_identifier = not not CodeEditDialog.RE_FIRST_IDENTIFIER.match(line)
		if is_first_identifier:
			autocomplete_options = main_identifiers + autocomplete_options
		else:
			autocomplete_options.extend(main_identifiers)

		return autocomplete_options

	def jump_highlights(self) -> Sequence[str] | None:
		return ('Error', 'Warning')

	def jump_sections(self) -> Sequence[str] | None:
		return ('Header', 'Block')

	# CodeGeneratorDelegate
	def insert_code(self, code: str) -> None:
		self.text.insert(UI.INSERT, code)
