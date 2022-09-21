
from .CodeGenerators import *
from .NameDialog import NameDialog
from .ManageCodeGeneratorPresetsDialog import ManageCodeGeneratorPresetsDialog

from ..Utilities import Assets
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.Toolbar import Toolbar
from ..Utilities.ScrolledListbox import ScrolledListbox

import os

class CodeGeneratorDialog(PyMSDialog):
	PRESETS = [
		{
			'name': 'Play Frames', 
			'code': """\
	playfram            $frame
	wait                2""", 
			'variables': [
				{
					'name': 'frame',
					'generator': {
						'type': 'range',
						'start': 0, 
						'stop': 20, 
						'step': 1
					}
				}
			]
		}, 
		{
			'name': 'Play Framesets', 
			'code': """\
	playfram            %frameset
	wait                2""", 
			'variables': [
				{
					'name': 'frameset',
					'generator': {
						'type': 'range',
						'start': 0, 
						'stop': 51, 
						'step': 17
					}
				}
			]
		},
		{
            'name': 'Play Framesets (Advanced)', 
            'code': """\
	playfram            %frame
	wait                2""", 
            'variables': [
                {
                    'name': 'frameset',
                    'generator': {
                        'type': 'range',
                        'start': 0, 
                        'stop': 20, 
                        'step': 1
                    }
                }, 
                {
                    'name': 'frame',
                    'generator': {
                        'type': 'math',
                        'math': '$frameset * 17'
                    }
                }
            ]
        },
        {
            'name': 'Hover Bobbing', 
            'code': """\
	setvertpos          $offset
	waitrand            8 10""", 
            'variables': [
                {
                    'name': 'offset',
                    'generator': {
                        'type': 'list',
                        'list': [
                            '0', 
                            '1', 
                            '2'
                        ], 
                        'repeater': 'inverted_once'
                    }
                }
            ]
        }
	]
	def __init__(self, parent):
		self.variables = []
		self.previewing = False
		self.settings = parent.parent.settings
		if not 'generator' in self.settings:
			self.settings['generator'] = {}
		if not 'presets' in self.settings['generator']:
			self.settings['generator']['presets'] = CodeGeneratorDialog.PRESETS
		PyMSDialog.__init__(self, parent, 'Code Generator', grabwait=True)

	def widgetize(self):
		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)
		leftframe = Frame(self.hor_pane)
		Label(leftframe, text='Variables:', anchor=W).pack(side=TOP, fill=X)
		self.listbox = ScrolledListbox(leftframe, selectmode=EXTENDED, width=15, height=10)
		self.listbox.bind(WidgetEvent.Listbox.Select, self.update_states)
		self.listbox.bind(Double.Click_Left, self.edit)
		self.listbox.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)

		def add_variable(generator_class, name):
			id = len(self.variables)
			self.variables.append(CodeGeneratorVariable(generator_class(), self.unique_name(name)))
			self.update_list(id)
			self.edit()
		def add_pressed():
			menu = Menu(self, tearoff=0)
			menu.add_command(label="Range", command=lambda: add_variable(CodeGeneratorTypeRange, 'range'))
			menu.add_command(label="Math", command=lambda: add_variable(CodeGeneratorTypeMath, 'math'))
			menu.add_command(label="List", command=lambda: add_variable(CodeGeneratorTypeList, 'list'))
			menu.post(*self.winfo_pointerxy())
		def load_preset_pressed():
			menu = Menu(self, tearoff=0)
			presets = self.settings.get('generator', {}).get('presets',[])
			for n,preset in enumerate(presets):
				if n == 5:
					menu.add_command(label='More...', command=self.manage_presets)
					break
				else:
					menu.add_command(label=preset['name'], command=lambda n=n: self.load_preset(n))
			menu.add_separator()
			menu.add_command(label='Manage Presets', command=self.manage_presets)
			menu.post(*self.winfo_pointerxy())
		
		self.toolbar = Toolbar(leftframe)
		self.toolbar.add_button(Assets.get_image('add'), add_pressed, 'Add Variable')
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Variable', tags='has_selection')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('save'), self.save_preset, 'Save Preset', tags='can_save')
		self.toolbar.add_button(Assets.get_image('open'), load_preset_pressed, 'Load Preset', tags='has_presets')
		self.toolbar.add_spacer(10, flexible=True)
		self.toolbar.add_button(Assets.get_image('edit'), self.edit, 'Edit Variable', tags='has_selection')
		self.toolbar.pack(side=BOTTOM, fill=X)

		self.hor_pane.add(leftframe, sticky=NSEW)

		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		f = Frame(self.ver_pane)
		Label(f, text='Code:', anchor=W).pack(side=TOP, fill=X)
		textframe = Frame(f, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=NSEW)
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		textframe.pack(side=BOTTOM, expand=1, fill=BOTH)
		self.ver_pane.add(f, sticky=NSEW)
		colors = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(colors, orient=HORIZONTAL)
		vscroll = Scrollbar(colors)
		self.code = Text(colors, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.code.grid(sticky=NSEW)
		self.code.orig = self.text._w + '_orig'
		self.tk.call('rename', self.code._w, self.code.orig)
		self.tk.createcommand(self.code._w, self.code_dispatch)
		hscroll.config(command=self.code.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.code.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		colors.grid_rowconfigure(0, weight=1)
		colors.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(colors, sticky=NSEW)
		self.hor_pane.add(self.ver_pane, sticky=NSEW)
		self.hor_pane.pack(fill=BOTH, expand=1, padx=3, pady=(0,3))

		def select_all(text):
			text.tag_remove(SEL, '1.0', END)
			text.tag_add(SEL, '1.0', END)
			text.mark_set(INSERT, '1.0')
		self.bind(Ctrl.a, lambda *_: select_all(self.code))

		buts = Frame(self)
		self.insert_button = Button(buts, text='Insert', command=self.insert)
		self.insert_button.pack(side=LEFT)
		self.preview_button = Button(buts, text='Preview', command=self.preview)
		self.preview_button.pack(side=LEFT, padx=10)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		self.update_states()

		return self.insert_button

	def setup_complete(self):
		self.settings.windows.generator.load_window_size('main', self)
		def update_panes():
			if 'variables_list' in self.settings.generator:
				self.hor_pane.sash_place(0, *self.settings.generator['variables_list'])
			if 'code_box' in self.settings.generator:
				self.ver_pane.sash_place(0, *self.settings.generator['code_box'])
		self.after(200, update_panes)

	def code_dispatch(self, operation, *args):
		if operation in ['insert','delete'] and not self.previewing:
			return EventPropogation.Break
		try:
			return self.tk.call((self.code.orig, operation) + args)
		except TclError:
			return ''

	def update_states(self, *_):
		has_selection = not not self.listbox.curselection()
		self.toolbar.tag_enabled('has_selection', has_selection)

		can_save = self.variables and self.text.get(1.0,END)
		self.toolbar.tag_enabled('can_save', can_save)

		has_presets = not not self.settings.get('generator',{}).get('presets',None)
		self.toolbar.tag_enabled('has_presets', has_presets)

	def remove(self, *_):
		cont = MessageBox.askquestion(parent=self, title='Remove Variable?', message="The variable settings will be lost.", default=MessageBox.YES, type=MessageBox.YESNO)
		if cont == MessageBox.NO:
			return
		del self.variables[int(self.listbox.curselection()[0])]
		self.update_list()

	def unique_name(self, name, ignore=None):
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
				unique = '%s%d' % (name,n)
		return unique

	def edit(self, *_):
		if self.listbox.curselection():
			variable = self.variables[int(self.listbox.curselection()[0])]
			CodeGeneratorVariableEditor(self, variable)

	def insert(self, *_):
		code = self.generate()
		if code == None:
			return
		self.parent.text.insert(INSERT, code)
		self.ok()

	def save_preset(self, *_):
		def do_save(window, name):
			replace = None
			for n,preset in enumerate(self.settings.get('generator',{}).get('presets',[])):
				if preset['name'] == name:
					cont = MessageBox.askquestion(parent=window, title='Overwrite Preset?', message="A preset with the name '%s' already exists. Do you want to overwrite it?" % name, default=MessageBox.YES, type=MessageBox.YESNOCANCEL)
					if cont == MessageBox.NO:
						return
					elif cont == MessageBox.CANCEL:
						return False
					replace = n
					break
			preset = {
				'name': name,
				'code': self.text.get(1.0,END),
				'variables': []
			}
			if preset['code'].endswith('\r\n'):
				preset['code'] = preset['code'][:-2]
			elif preset['code'].endswith('\n'):
				preset['code'] = preset['code'][:-1]
			for v in self.variables:
				preset['variables'].append({
					'name': v.name,
					'generator': v.generator.save()
				})
			if not 'generator' in self.settings:
				self.settings['generator'] = {}
			if not 'presets' in self.settings['generator']:
				self.settings['generator']['presets'] = []
			if replace == None:
				self.settings['generator']['presets'].insert(0, preset)
			else:
				self.settings['generator']['presets'][replace] = preset
		NameDialog(self, title='Save Preset', done='Save', callback=do_save)
	def load_preset(self, preset, window=None):
		if self.variables or self.text.get(1.0, END).strip():
			cont = MessageBox.askquestion(parent=window if window else self, title='Load Preset?', message="Your current variables and code will be lost.", default=MessageBox.YES, type=MessageBox.YESNO)
			if cont == MessageBox.NO:
				return False
		if isinstance(preset, int):
			preset = self.settings['generator']['presets'][preset]
		self.text.delete(1.0, END)
		self.text.insert(END, preset['code'])
		self.variables = []
		for var in preset['variables']:
			generator = var['generator']
			self.variables.append(CodeGeneratorVariable(CodeGeneratorType.TYPES[generator['type']](generator), var['name']))
		self.update_list()
		return True

	def manage_presets(self):
		ManageCodeGeneratorPresetsDialog(self)

	def preview(self, *_):
		code = self.generate()
		if code != None:
			self.previewing = True
			self.code.delete(1.0, END)
			self.code.insert(END, code)
			self.previewing = False

	def update_list(self, select=None):
		if select == None and self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		for v in self.variables:
			self.listbox.insert(END, '$%s = %s' % (v.name, v.generator.description()))
		if select != None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def generate(self):
		variable_re = re.compile(r'([$%])([a-zA-Z0-9_]+)')
		code = self.text.get(1.0, END)
		generated = ''
		count = None
		for v in self.variables:
			c = v.generator.count()
			if c != None:
				if count == None:
					count = c
				else:
					count = max(count,c)
		if count == None:
			ErrorDialog(self, PyMSError('Generate','No finite variables to generate with'))
			return
		def calculate_variable(variable, values, lookup):
			def calculate_variable_named(name, values, lookup):
				if name in values:
					return values[name]
				for v in self.variables:
					if v.name == name:
						return calculate_variable(v, values, lookup)
				return '$' + name
			if not variable.name in values:
				if variable.name in lookup:
					raise PyMSError('Generate', 'Cyclical reference detected: %s' % ' > '.join(lookup + [variable.name]))
				lookup.append(variable.name)
				values[variable.name] = variable.generator.value(lambda n,v=values,l=lookup: calculate_variable_named(n,v,l))
			return values[variable.name]
		def replace_variable(match, values):
			tohex = (match.group(1) == '%')
			name = match.group(2)
			replacement = values.get(name, match.group(0))
			if tohex:
				try:
					replacement = '0x%02X' % int(replacement)
				except:
					pass
			return str(replacement)
		for n in range(count):
			values = {'n': n}
			for v in self.variables:
				if not v.name in values:
					try:
						calculate_variable(v, values, [])
					except PyMSError as e:
						ErrorDialog(self, e)
						return
			generated += variable_re.sub(lambda m: replace_variable(m, values), code)
		return generated

	def dismiss(self):
		self.settings.windows.generator.save_window_size('main', self)
		self.settings.generator.variables_list = self.hor_pane.sash_coord(0)
		self.settings.generator.code_box = self.ver_pane.sash_coord(0)
		PyMSDialog.dismiss(self)
