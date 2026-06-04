
from .Config import PyICEConfig
from .CodeGenerators import CodeGeneratorTypeList, CodeGeneratorTypeMath, CodeGeneratorTypeRange, CodeGeneratorVariable, CodeGeneratorVariableEditor
from .NameDialog import NameDialog
from .ManageCodeGeneratorPresetsDialog import ManageCodeGeneratorPresetsDialog
from .CodeGenerators.GeneratorPreset import GeneratorPreset
from .Delegates import CodeGeneratorDelegate, VariableEditorDelegate

from ..Utilities import Assets
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.CheckSaved import CheckSaved

import re

from typing import Any

class CodeGeneratorDialog(PyMSDialog, VariableEditorDelegate):
	def __init__(self, parent: UI.Misc, config: PyICEConfig, delegate: CodeGeneratorDelegate) -> None:
		self.variables: list[CodeGeneratorVariable] = []
		self.previewing = False
		self.config_ = config
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'Code Generator', grabwait=True)

	def widgetize(self) -> UI.Widget:
		self.hor_pane = UI.PanedWindow(self,orient=UI.HORIZONTAL)
		leftframe = UI.Frame(self.hor_pane)
		UI.Label(leftframe, text='Variables:', anchor=UI.W).pack(side=UI.TOP, fill=UI.X)
		self.listbox = UI.ScrolledListbox(leftframe, selectmode=UI.EXTENDED, width=15, height=10)
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.update_states)
		self.listbox.bind(UI.Double.Click_Left(), self.edit)
		self.listbox.pack(side=UI.TOP, padx=1, pady=1, fill=UI.BOTH, expand=1)

		def add_variable(generator_class: type, name: str) -> None:
			gen_id = len(self.variables)
			self.variables.append(CodeGeneratorVariable(self.unique_name(name), generator_class()))
			self.update_list(gen_id)
			self.edit()
		def add_pressed() -> None:
			menu = UI.Menu(self, tearoff=0)
			menu.add_command(label="Range", command=lambda: add_variable(CodeGeneratorTypeRange, 'range'))
			menu.add_command(label="Math", command=lambda: add_variable(CodeGeneratorTypeMath, 'math'))
			menu.add_command(label="List", command=lambda: add_variable(CodeGeneratorTypeList, 'list'))
			menu.post(*self.winfo_pointerxy())
		def load_preset_pressed() -> None:
			menu = UI.Menu(self, tearoff=0)
			presets = self.config_.generator.presets.data
			for n,preset in enumerate(presets):
				if n == 5:
					menu.add_command(label='More...', command=self.manage_presets)
					break
				else:
					def load_preset(p: GeneratorPreset = preset) -> None:
						self.load_preset(p)
					menu.add_command(label=preset.name, command=load_preset)
			menu.add_separator()
			menu.add_command(label='Manage Presets', command=self.manage_presets)
			menu.post(*self.winfo_pointerxy())

		self.toolbar = UI.Toolbar(leftframe)
		self.toolbar.add_button(Assets.get_image('add'), add_pressed, 'Add Variable')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Variable', tags='has_selection')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save_preset, 'Save Preset', tags='can_save')
		self.toolbar.add_button(Assets.get_image('open'), load_preset_pressed, 'Load Preset', tags='has_presets')
		self.toolbar.add_spacer(10, flexible=True)
		self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit Variable', tags='has_selection')
		self.toolbar.pack(side=UI.BOTTOM, fill=UI.X)

		self.hor_pane.add(leftframe, sticky=UI.NSEW)

		self.ver_pane = UI.PanedWindow(self.hor_pane,orient=UI.VERTICAL)
		f = UI.Frame(self.ver_pane)
		UI.Label(f, text='Code:', anchor=UI.W).pack(side=UI.TOP, fill=UI.X)
		textframe = UI.Frame(f, bd=2, relief=UI.SUNKEN)
		hscroll = UI.Scrollbar(textframe, orient=UI.HORIZONTAL)
		vscroll = UI.Scrollbar(textframe)
		self.text = UI.Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=UI.NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=UI.NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=UI.EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=UI.NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		textframe.pack(side=UI.BOTTOM, expand=1, fill=UI.BOTH)
		self.ver_pane.add(f, sticky=UI.NSEW)
		colors = UI.Frame(self.ver_pane, bd=2, relief=UI.SUNKEN)
		hscroll = UI.Scrollbar(colors, orient=UI.HORIZONTAL)
		vscroll = UI.Scrollbar(colors)

		self.code = UI.Text(colors, height=1, bd=0, undo=1, maxundo=100, wrap=UI.NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.code.grid(sticky=UI.NSEW)

		self.code_orig = getattr(self.code, '_w') + '_orig'
		self.tk.call('rename', getattr(self.code, '_w'), self.code_orig)
		self.tk.createcommand(getattr(self.code, '_w'), self.code_dispatch)

		hscroll.config(command=self.code.xview)
		hscroll.grid(sticky=UI.EW)
		vscroll.config(command=self.code.yview)
		vscroll.grid(sticky=UI.NS, row=0, column=1)
		colors.grid_rowconfigure(0, weight=1)
		colors.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(colors, sticky=UI.NSEW)
		self.hor_pane.add(self.ver_pane, sticky=UI.NSEW)
		self.hor_pane.pack(fill=UI.BOTH, expand=1, padx=3, pady=(0,3))

		def select_all(_: UI.Event) -> None:
			self.code.tag_remove(UI.SEL, '1.0', UI.END)
			self.code.tag_add(UI.SEL, '1.0', UI.END)
			self.code.mark_set(UI.INSERT, UI.END)
		self.bind(UI.Ctrl.a(), select_all)

		buts = UI.Frame(self)
		self.insert_button = UI.Button(buts, text='Insert', command=self.insert)
		self.insert_button.pack(side=UI.LEFT)
		self.preview_button = UI.Button(buts, text='Preview', command=self.preview)
		self.preview_button.pack(side=UI.LEFT, padx=10)
		UI.Button(buts, text='Cancel', command=self.cancel).pack(side=UI.RIGHT)
		buts.pack(side=UI.BOTTOM, fill=UI.X, padx=3, pady=(0,3))

		self.update_states()

		return self.insert_button

	def setup_complete(self) -> None:
		self.config_.windows.generator.main.load_size(self)
		self.update()
		self.config_.generator.pane.variables_list.load_size(self.hor_pane)
		self.config_.generator.pane.code_box.load_size(self.ver_pane)

	def code_dispatch(self, operation: str, *args: Any) -> str:
		if operation in ['insert','delete'] and not self.previewing:
			return UI.EventPropogation.Break
		try:
			return self.tk.call((self.code_orig, operation) + args)
		except Exception:
			return ''

	def update_states(self, *_: Any) -> None:
		has_selection = not not self.listbox.curselection()
		self.toolbar.tag_enabled('has_selection', has_selection)

		can_save = bool(self.variables and self.text.get(1.0,UI.END))
		self.toolbar.tag_enabled('can_save', can_save)

		has_presets = not not self.config_.generator.presets.data
		self.toolbar.tag_enabled('has_presets', has_presets)

	def remove(self, *_: Any) -> None:
		cont = UI.MessageBox.askyesno(parent=self, title='Remove Variable?', message="The variable settings will be lost.", default=UI.MessageBox.YES)
		if not cont:
			return
		del self.variables[int(self.listbox.curselection()[0])]
		self.update_list()

	def unique_name(self, name: str, ignore: CodeGeneratorVariable | None = None) -> str:
		n = 1
		unique = name
		if name == 'n':
			n = 2
			name = 'n2'
		for v in self.variables:
			if v == ignore:
				continue
			if v.name == unique:
				n += 1
				unique = f'{name}{n}'
		return unique

	def edit(self, *_: Any) -> None:
		if self.listbox.curselection():
			variable = self.variables[int(self.listbox.curselection()[0])]
			CodeGeneratorVariableEditor(self, self, variable, self.config_)

	def insert(self, *_: Any) -> None:
		code = self.generate()
		if code is None:
			return
		self.delegate.insert_code(code)
		self.ok()

	def save_preset(self, *_: Any) -> None:
		def do_save(window: UI.AnyWindow, name: str) -> CheckSaved:
			replace = None
			for n,preset in enumerate(self.config_.generator.presets.data):
				if preset.name == name:
					cont = UI.MessageBox.askyesnocancel(parent=window, title='Overwrite Preset?', message=f"A preset with the name '{name}' already exists. Do you want to overwrite it?", default=UI.MessageBox.YES)
					if cont is None:
						return CheckSaved.cancelled
					if not cont:
						return CheckSaved.saved
					replace = n
					break
			preset = GeneratorPreset(
				name=name,
				code=self.text.get(1.0,UI.END).rstrip('\r\n'),
				variables=list(self.variables)
			)
			if replace is None:
				self.config_.generator.presets.data.insert(0, preset)
			else:
				self.config_.generator.presets.data[replace] = preset
			return CheckSaved.saved
		NameDialog(parent=self, window_geometry_config=self.config_.windows.generator.name, title='Save Preset', done='Save', save_callback=do_save)

	def load_preset(self, preset: GeneratorPreset, window: UI.AnyWindow | None = None) -> bool:
		if self.variables or self.text.get(1.0, UI.END).strip():
			cont = UI.MessageBox.askyesno(parent=window if window else self, title='Load Preset?', message="Your current variables and code will be lost.", default=UI.MessageBox.YES)
			if not cont:
				return False
		self.text.delete(1.0, UI.END)
		self.text.insert(UI.END, preset.code)
		self.variables = list(preset.variables)
		self.update_list()
		return True

	def manage_presets(self) -> None:
		ManageCodeGeneratorPresetsDialog(self, self, self.config_)

	def preview(self, *_: Any) -> None:
		code = self.generate()
		if code is not None:
			self.previewing = True
			self.code.delete(1.0, UI.END)
			self.code.insert(UI.END, code)
			self.previewing = False

	def update_list(self, select: int | None = None) -> None:
		if select is None and self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,UI.END)
		for v in self.variables:
			self.listbox.insert(UI.END, f'${v.name} = {v.generator.description()}')
		if select is not None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def generate(self) -> str | None:
		variable_re = re.compile(r'([$%])([a-zA-Z0-9_]+)')
		code = self.text.get(1.0, UI.END)
		generated = ''
		count = None
		for v in self.variables:
			c = v.generator.count()
			if c is not None:
				if count is None:
					count = c
				else:
					count = max(count,c)
		if count is None:
			ErrorDialog(self, PyMSError('Generate', 'No finite variables to generate with'))
			return None
		def calculate_variable(variable: CodeGeneratorVariable, values: dict[str, str], lookup: list[str]) -> str:
			def calculate_variable_named(name: str, values: dict[str, str], lookup: list[str]) -> str:
				if name in values:
					return values[name]
				for v in self.variables:
					if v.name == name:
						return calculate_variable(v, values, lookup)
				return '$' + name
			if not variable.name in values:
				if variable.name in lookup:
					raise PyMSError('Generate', f'Cyclical reference detected: {" > ".join(lookup + [variable.name])}')
				lookup.append(variable.name)
				values[variable.name] = variable.generator.value(lambda n: calculate_variable_named(n,values,lookup))
			return values[variable.name]
		def replace_variable(match: re.Match, values: dict) -> str:
			tohex = (match.group(1) == '%')
			name = match.group(2)
			replacement = values.get(name, match.group(0))
			if tohex:
				try:
					replacement = f'0x{int(replacement):02X}'
				except Exception:
					pass
			return str(replacement)
		for n in range(count):
			values = {'n': str(n)}
			for v in self.variables:
				if not v.name in values:
					try:
						calculate_variable(v, values, [])
					except PyMSError as e:
						ErrorDialog(self, e)
						return None
			generated += variable_re.sub(lambda m,v=values: replace_variable(m, v), code) # type: ignore[misc]
		return generated

	def dismiss(self) -> None:
		self.config_.windows.generator.main.save_size(self)
		self.config_.generator.pane.variables_list.save_size(self.hor_pane)
		self.config_.generator.pane.code_box.save_size(self.ver_pane)
		PyMSDialog.dismiss(self)
