
from .CodeGenerators import *
from .NameDialog import NameDialog
from .ManageCodeGeneratorPresetsDialog import ManageCodeGeneratorPresetsDialog

from ..Utilities import Assets
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Tooltip import Tooltip
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

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
		listframe = Frame(leftframe, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=EXTENDED, activestyle=DOTBOX, width=15, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda e,l=self.listbox,i=0: self.move(e,l,i)),
			('<End>', lambda e,l=self.listbox,i=END: self.move(e,l,i)),
			('<Up>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Left>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Down>', lambda e,l=self.listbox,i=1: self.move(e,l,i)),
			('<Right>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Prior>', lambda e,l=self.listbox,i=-10: self.move(e,l,i)),
			('<Next>', lambda e,l=self.listbox,i=10: self.move(e,l,i)),
		]
		for b in bind:
			self.bind(*b)
			self.listbox.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.update_states)
		self.listbox.bind('<Double-Button-1>', self.edit)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
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
		buts = Frame(leftframe)
		# TODO: Toolbar?
		buttons = [
			('add', 'Add Variable', LEFT, 0, add_pressed),
			('remove', 'Remove Variable', LEFT, 0, self.remove),
			('save', 'Save Preset', LEFT, (5,0), self.save_preset),
			('open', 'Load Preset', LEFT, 0, load_preset_pressed),
			('edit', 'Edit Variable', RIGHT, 0, self.edit),
		]
		self.buttons = {}
		for icon,tip,side,padx,callback in buttons:
			button = Button(buts, image=Assets.get_image(icon), width=20, height=20, command=callback)
			Tooltip(button, tip)
			button.pack(side=side, padx=padx)
			self.buttons[icon] = button
		buts.pack(side=BOTTOM, fill=X)
		self.hor_pane.add(leftframe, sticky=NSEW)

		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		f = Frame(self.ver_pane)
		Label(f, text='Code:', anchor=W).pack(side=TOP, fill=X)
		textframe = Frame(f, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=NSEW)
		# self.text.bind('<Control-a>', lambda e: self.after(1, self.selectall))
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
		self.bind('<Control-a>', lambda *_: select_all(self.code))

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
			return 'break'
		try:
			return self.tk.call((self.code.orig, operation) + args)
		except TclError:
			return ''

	def update_states(self, *_):
		selection = DISABLED if not self.listbox.curselection() else NORMAL
		self.buttons['remove']['state'] = selection
		self.buttons['save']['state'] = NORMAL if (self.variables and self.text.get(1.0,END)) else DISABLED
		self.buttons['open']['state'] = NORMAL if self.settings.get('generator',{}).get('presets',None) else DISABLED
		self.buttons['edit']['state'] = selection

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

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		return "break"

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
