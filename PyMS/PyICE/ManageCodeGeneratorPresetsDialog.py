
from .Config import PyICEConfig
from .Delegates import ManagePresetsDelegate
from .CodeGenerators.GeneratorPreset import GeneratorPreset
from .NameDialog import NameDialog

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Assets
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.AtomicWriter import AtomicWriter
from ..Utilities.CheckSaved import CheckSaved

import json

class ManageCodeGeneratorPresetsDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: ManagePresetsDelegate, config: PyICEConfig):
		self.config_ = config
		self.delegate = delegate
		PyMSDialog.__init__(self, parent, 'Manage Presets', grabwait=True)

	def widgetize(self) -> Misc | None:
		self.listbox = ScrolledListbox(self, selectmode=EXTENDED, width=30)
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.update_states)
		self.listbox.bind(Double.Click_Left(), self.rename)
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

	def setup_complete(self) -> None:
		self.config_.windows.generator.presets.load_size(self)
		self.update_list()

	def remove(self) -> None:
		selected = int(self.listbox.curselection()[0])
		preset = self.config_.generator.presets.data[selected]
		cont = MessageBox.askquestion(parent=self, title='Remove Preset?', message="'%s' will be removed and you won't be able to get it back. Continue?" % preset.name, default=MessageBox.OK, type=MessageBox.OKCANCEL)
		if cont == MessageBox.CANCEL:
			return
		del self.config_.generator.presets.data[selected]
		self.update_list()

	def export(self) -> None:
		if not self.listbox.curselection():
			return
		path = self.config_.last_path.generators.txt.select_save(self)
		if not path:
			return
		selected = int(self.listbox.curselection()[0])
		preset = self.config_.generator.presets.data[selected]
		try:
			f = AtomicWriter(path, 'w')
			f.write(json.dumps(preset, indent=4))
			f.close()
		except:
			ErrorDialog(self, PyMSError('Export',"Could not write to file '%s'" % path))

	def iimport(self) -> None:
		path = self.config_.last_path.generators.txt.select_open(self)
		if not path:
			return
		try:
			preset_json = None
			try:
				with open(path, 'r') as f:
					preset_json = json.loads(f.read())
			except:
				raise PyMSError('Import',"Could not read preset '%s'" % path, capture_exception=True)
			preset = GeneratorPreset.from_json(preset_json)
			copy = 1
			while True:
				check = '%s%s' % (preset.name,'' if copy == 1 else str(copy))
				for p in self.config_.generator.presets.data:
					if check == p.name:
						copy += 1
						break
				else:
					break
			if copy > 1:
				preset.name += str(copy)
			self.config_.generator.presets.data.insert(0, preset)
			self.update_list()
		except PyMSError as e:
			ErrorDialog(self, e)
	
	def rename(self, event: Event | None = None) -> None:
		if not self.listbox.curselection():
			return
		selected = int(self.listbox.curselection()[0])
		def do_rename(window: AnyWindow, name: str) -> CheckSaved:
			for preset in self.config_.generator.presets.data:
				if preset.name == name:
					ErrorDialog(self, PyMSError('Renaming','That name already exists'))
					return CheckSaved.cancelled
			self.config_.generator.presets.data[selected].name = name
			self.update_list()
			return CheckSaved.saved
		name = self.config_.generator.presets.data[selected].name
		NameDialog(self, self.config_.windows.generator.name, title='Rename Preset', value=name, done='Rename', save_callback=do_rename)

	def update_states(self, event: Event | None = None) -> None:
		selected = None
		if self.listbox.curselection():
			selected = int(self.listbox.curselection()[0])
		self.toolbar.tag_enabled('preset_selected', selected is not None)
		self.toolbar.tag_enabled('can_move_up', not not selected)
		self.toolbar.tag_enabled('can_move_down', selected is not None and selected+1 < len(self.config_.generator.presets.data))

	def update_list(self) -> None:
		select = None
		if self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		for preset in self.config_.generator.presets.data:
			self.listbox.insert(END, preset.name)
		if select is not None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def move(self, move: int) -> None:
		selected = int(self.listbox.curselection()[0])
		preset = self.config_.generator.presets.data.pop(selected)
		index = selected+move
		self.config_.generator.presets.data.insert(index, preset)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(index)
		self.update_list()

	def select(self) -> None:
		selected = int(self.listbox.curselection()[0])
		preset = self.config_.generator.presets.data[selected]
		if self.delegate.load_preset(preset, self):
			self.ok()

	def dismiss(self) -> None:
		self.config_.windows.generator.presets.save_size(self)
		PyMSDialog.dismiss(self)
