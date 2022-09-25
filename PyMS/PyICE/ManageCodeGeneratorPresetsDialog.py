
from .CodeGenerators import CodeGeneratorType
from .NameDialog import NameDialog

from ..Utilities.utils import isstr
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AtomicWriter import AtomicWriter
from ..Utilities.FileType import FileType

import json

class ManageCodeGeneratorPresetsDialog(PyMSDialog):
	def __init__(self, parent):
		self.settings = parent.settings
		PyMSDialog.__init__(self, parent, 'Manage Presets', grabwait=True)

	def widgetize(self):
		self.listbox = ScrolledListbox(self, selectmode=EXTENDED, width=30)
		self.listbox.bind(WidgetEvent.Listbox.Select, self.update_states)
		self.listbox.bind(Double.Click_Left, self.rename)
		self.listbox.pack(side=TOP, padx=3, pady=3, fill=BOTH, expand=1)

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('test'), self.select, 'Use Preset', tags='preset_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove Preset', tags='preset_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('up'), lambda: self.move(-1), 'Move Up', tags='can_move_up')
		self.toolbar.add_button(Assets.get_image('down'), lambda: self.move(1), 'Move Down', tags='can_move_down')
		self.toolbar.add_spacer(5, flexible=True)
		self.toolbar.add_button(Assets.get_image('edit'), self.rename, 'Rename Preset', tags='preset_selected')
		self.toolbar.add_gap()
		self.toolbar.add_button(Assets.get_image('import'), self.iimport, 'Import Preset')
		self.toolbar.add_button(Assets.get_image('export'), self.export, 'Export Preset', tags='preset_selected')
		self.toolbar.pack(side=TOP, fill=X, padx=3)

		done = Button(self, text='Done', command=self.ok)
		done.pack(side=BOTTOM, padx=3, pady=(0,3))

		return done

	def setup_complete(self):
		self.settings.windows.generator.load_window_size('presets', self)
		self.update_list()

	def remove(self):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings.generator.presets[selected]
		cont = MessageBox.askquestion(parent=self, title='Remove Preset?', message="'%s' will be removed and you won't be able to get it back. Continue?" % preset['name'], default=MessageBox.OK, type=MessageBox.OKCANCEL)
		if cont == MessageBox.CANCEL:
			return
		del self.settings.generator.presets[selected]
		self.update_list()

	def export(self):
		if not self.listbox.curselection():
			return
		path = self.settings.lastpath.generators.txt.select_save_file(self, key='export', title='Export Preset', filetypes=[FileType.txt()])
		if not path:
			return
		selected = int(self.listbox.curselection()[0])
		preset = self.settings.generator.presets[selected]
		try:
			f = AtomicWriter(path, 'w')
			f.write(json.dumps(preset, indent=4))
			f.close()
		except:
			ErrorDialog(self, PyMSError('Export',"Could not write to file '%s'" % path))

	def iimport(self):
		path = self.settings.lastpath.generators.txt.select_open_file(self, key='import', title='Import Preset', filetypes=[FileType.txt()])
		if not path:
			return
		try:
			preset = None
			try:
				with open(path, 'r') as f:
					preset = json.loads(f.read())
			except:
				raise PyMSError('Import',"Could not read preset '%s'" % path, capture_exception=True)
			if not 'name' in preset or not isstr(preset['name']) \
					or not 'code' in preset or not isstr(preset['code']) \
					or not 'variables' in preset or not isinstance(preset['variables'], list):
				raise PyMSError('Import',"Invalid preset format in file '%s'" % path)
			for variable in preset['variables']:
				if not 'name' in variable or not isstr(variable['name']) \
						or not 'generator' in variable or not isinstance(variable['generator'], dict) \
						or not 'type' in variable['generator'] or not variable['generator']['type'] in CodeGeneratorType.TYPES \
						or not CodeGeneratorType.TYPES[variable['generator']['type']].validate(variable['generator']):
					raise PyMSError('Import',"Invalid preset format in file '%s'" % path)
			copy = 1
			while True:
				check = '%s%s' % (preset['name'],'' if copy == 1 else str(copy))
				for p in self.settings.generator.presets:
					if check == p['name']:
						copy += 1
						break
				else:
					break
			if copy > 1:
				preset['name'] += str(copy)
			self.settings.generator.presets.insert(0, preset)
			self.update_list()
		except PyMSError as e:
			ErrorDialog(self, e)
	
	def rename(self):
		if not self.listbox.curselection():
			return
		selected = int(self.listbox.curselection()[0])
		def do_rename(window, name):
			for preset in self.settings.generator.presets:
				if preset['name'] == name:
					ErrorDialog(self, PyMSError('Renaming','That name already exists'))
					return
			self.settings.generator.presets[selected]['name'] = name
			self.update_list()
		name = self.settings.generator.presets[selected]['name']
		NameDialog(self, title='Rename Preset', value=name, done='Rename', callback=do_rename)

	def update_states(self, *_):
		selected = None
		if self.listbox.curselection():
			selected = int(self.listbox.curselection()[0])
		self.toolbar.tag_enabled('preset_selected', selected != None)
		self.toolbar.tag_enabled('can_move_up', not not selected)
		self.toolbar.tag_enabled('can_move_down', selected != None and selected+1 < len(self.settings.generator.presets))

	def update_list(self):
		select = None
		if self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		for preset in self.settings.generator.get('presets',[]):
			self.listbox.insert(END, preset['name'])
		if select != None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def move(self, move):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings.generator.presets.pop(selected)
		index = selected+move
		self.settings.generator.presets.insert(index, preset)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(index)
		self.update_list()

	def select(self):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings.generator.presets[selected]
		if self.parent.load_preset(preset, self):
			self.ok()

	def dismiss(self):
		self.settings.windows.generator.save_window_size('presets', self)
		PyMSDialog.dismiss(self)
