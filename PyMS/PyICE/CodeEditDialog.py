
from .Delegates import MainDelegate, CodeGeneratorDelegate
from .Config import PyICEConfig
from .FindReplaceDialog import FindReplaceDialog
from .CodeGeneratorDialog import CodeGeneratorDialog
from .PreviewerDialog import PreviewerDialog, PREVIEWER_CMDS, EntryType
from .SoundDialog import SoundDialog

from ..FileFormats.IScriptBIN import IScriptBIN
from ..FileFormats.IScriptBIN.CodeHandlers import CodeCommands, CodeTypes
from ..FileFormats import GRP

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.WarningDialog import WarningDialog
from ..Utilities import Assets
from ..Utilities.EditedState import EditedState
from ..Utilities.CodeHandlers import CodeType
from ..Utilities.SyntaxHighlightingDialog import SyntaxHighlightingDialog

import os, re, io

from typing import Sequence

class CodeEditDialog(PyMSDialog, CodeTextDelegate, CodeGeneratorDelegate):
	def __init__(self, parent: Misc, delegate: MainDelegate, config: PyICEConfig, ids: list[int]) -> None:
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

	def widgetize(self) -> Widget:
		toolbar = Toolbar(self)
		toolbar.add_button(Assets.get_image('save'), self.save, 'Save', Ctrl.s)
		toolbar.add_button(Assets.get_image('test'), self.test, 'Test Code', Ctrl.t)
		toolbar.add_gap()
		toolbar.add_button(Assets.get_image('export'), self.export, 'Export Code', Ctrl.e)
		toolbar.add_button(Assets.get_image('saveas'), self.exportas, 'Export As...', Ctrl.Alt.a)
		toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Code', Ctrl.i)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('find'), self.find, 'Find/Replace', Ctrl.f)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('colors'), self.colors, 'Color Settings', Ctrl.Alt.c)
		toolbar.add_section()
		toolbar.add_button(Assets.get_image('debug'), self.generate, 'Generate Code', Ctrl.g)
		toolbar.add_button(Assets.get_image('insert'), self.preview, 'Insert/Preview Window', Ctrl.w)
		toolbar.add_button(Assets.get_image('fwp'), self.sounds, 'Sound Previewer', Ctrl.q)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=2)

		self.text = CodeText(self, self.edited_state, self)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)

		self.setup_syntax_highlighting()

		self.status = StringVar()
		self.status.set("Origional ID's: " + ', '.join([str(i) for i in self.ids]))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.editstatus = Label(statusbar, image=Assets.get_image('save'), bd=0, state=DISABLED)
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		return self.text

	def setup_complete(self) -> None:
		self.after(1, self.load)

		self.config_.windows.code_edit.load_size(self)

	def setup_syntax_highlighting(self) -> None:
		cmd_names = [cmd.name for cmd in CodeCommands.all_basic_commands]
		header_names = [cmd.name for cmd in CodeCommands.all_header_commands]
		keywords: list[str] = []
		for type in CodeTypes.all_basic_types + CodeTypes.all_header_types:
			if isinstance(type, CodeType.HasKeywords):
				keywords.extend(type.keywords())
		self.syntax_highlighting = SyntaxHighlighting(
			syntax_components=(
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Comment',
							description='The style of a comment.',
							highlight_style=self.config_.code.highlights.comment
						),
						pattern=r'#[^\n]*$'
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
					r'^[ \t]*',
					HighlightPattern(
						highlight=HighlightComponent(
							name='Block',
							description='The style of a --block-- or :block in the code.',
							highlight_style=self.config_.code.highlights.block
						),
						pattern=r'\w+:'
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
							name='Header Command',
							description='The style of header command names.',
							highlight_style=self.config_.code.highlights.header_command
						),
						pattern='|'.join(header_names)
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
						pattern=r'\d+|0x[0-9a-fA-F]+'
					),
					r'\b'
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Operator',
							description='The style of the operators:\n    ( ) : , =',
							highlight_style=self.config_.code.highlights.operator
						),
						pattern=r'[():,=]'
					),
				)),
				SyntaxComponent((
					HighlightPattern(
						highlight=HighlightComponent(
							name='Header',
							description='The style of a `script` header.',
							highlight_style=self.config_.code.highlights.header
						),
						pattern=r'\.headerstart|\.headerend'
					),
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
			self.title('IScript Editor [*%s*]' % self.file)

	def cancel(self, event: Event | None = None) -> None:
		if self.edited_state.is_edited:
			save = MessageBox.askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
			if save != MessageBox.NO:
				if save == MessageBox.CANCEL:
					return
				self.save()
		self.ok()

	def save(self, event: Event | None = None) -> None:
		code = self.text.get('1.0', END)
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

	def test(self, event: Event | None = None) -> None:
		code = self.text.get('1.0', END)
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
			MessageBox.askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=MessageBox.OK)

	def export(self, event: Event | None = None) -> None:
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('IScript Editor [%s]' % self.file)

	def exportas(self, event: Event | None = None) -> None:
		file = self.config_.last_path.txt.select_save(self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, event: Event | None = None) -> None:
		iimport = self.config_.last_path.txt.select_open(self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				self.text.edit_reset()
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import','Could not import file "%s"' % iimport))

	def find(self, event: Event | None = None) -> None:
		if self.findwindow is None:
			findwindow = FindReplaceDialog(self, self.text, self.config_.windows.find_replace)
			self.findwindow = findwindow
			self.bind(Key.F3(), lambda e: findwindow.findnext(e))
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, event: Event | None = None) -> None:
		dialog = SyntaxHighlightingDialog(self, self.syntax_highlighting.all_highlight_components())
		if dialog.updated:
			self.text.update_highlight_styles()

	def generate(self, *_) -> None:
		CodeGeneratorDialog(self, self.config_, self)

	def preview(self, event: Event | None = None) -> None:
		if not self.previewer or self.previewer.state() == 'withdrawn':
			if self.previewer is None:
				self.previewer = PreviewerDialog(self, self.delegate, self.config_, self.text)
			self.previewer.updatecurrentimages()
			parse_context = self.delegate.get_parse_context('')
			t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
			if t[0] in PREVIEWER_CMDS[EntryType.iscript] and self.previewer.curradio['state'] == NORMAL:
				try:
					f = CodeTypes.FrameCodeType().parse(t[1], parse_context)
				except:
					f = 0
				self.previewer.type.set(0)
				self.previewer.curid.set(0)
				self.previewer.curcmd.set(PREVIEWER_CMDS[EntryType.iscript].index(t[0]))
				self.previewer.select(0, EntryType.iscript, f)
			elif t[0] in PREVIEWER_CMDS[EntryType.images_dat]:
				try:
					n = CodeTypes.ImageIDCodeType().parse(t[1], parse_context)
				except:
					n = 0
				self.previewer.type.set(1)
				self.previewer.image.set(n)
				self.previewer.imagecmd.set(PREVIEWER_CMDS[EntryType.images_dat].index(t[0]))
				self.previewer.select(n, EntryType.images_dat)
			elif t[0] in PREVIEWER_CMDS[EntryType.sprites_dat]:
				try:
					n = CodeTypes.SpriteIDCodeType().parse(t[1], parse_context)
				except:
					n = 0
				self.previewer.type.set(2)
				self.previewer.sprites.set(n)
				self.previewer.spritescmd.set(PREVIEWER_CMDS[EntryType.sprites_dat].index(t[0]))
				self.previewer.select(n, EntryType.sprites_dat)
			elif t[0] in PREVIEWER_CMDS[EntryType.flingy_dat]:
				try:
					n = CodeTypes.FlingyIDCodeType().parse(t[1], parse_context)
				except:
					n = 0
				self.previewer.type.set(3)
				self.previewer.flingys.set(n)
				self.previewer.flingyscmd.set(PREVIEWER_CMDS[EntryType.flingy_dat].index(t[0]))
				self.previewer.select(n, EntryType.flingy_dat)
			else:
				self.previewer.select(0, self.previewer.entry_type())
			self.previewer.deiconify()
			self.after(50, self.previewer.updateframes)
		self.previewer.focus_set()

	def sounds(self) -> None:
		t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
		i = 0
		if t[0] == 'playsnd':
			try:
				i = CodeTypes.SoundIDCodeType().parse(t[1], self.delegate.get_parse_context(''))
			except:
				pass
		SoundDialog(self, self.delegate, self.config_.sounds, self.text, i)

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

	def write(self, text) -> None:
		self.decompile += text

	def readlines(self) -> list[str]:
		return self.text.get('1.0', END).split('\n')

	def destroy(self) -> None:
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		if self.previewer:
			Toplevel.destroy(self.previewer)
		Toplevel.destroy(self)

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
		self.text.insert(INSERT, code)
