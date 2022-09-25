
from ..Utilities.utils import lpad
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities.UIKit import *
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.EventPattern import *
from ..Utilities.Toolbar import Toolbar
from ..Utilities import Assets
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.FileType import FileType

import re

RE_OVERRIDE = re.compile(r'\s*(\d{1,5})\s*(\+?)\s*:(.*)')
class EntryNameOverrides(PyMSDialog):
	def __init__(self, parent, data_context, dat_id, entry_id=None):
		self.data_context = data_context
		self.dat_id = dat_id
		self.entry_id = IntegerVar(range=(0, 99999))
		if entry_id:
			self.entry_id.set(entry_id)
		self.name = StringVar()
		self.append = IntVar()
		PyMSDialog.__init__(self, parent, '%s Name Overrides' % data_context.dat_data(dat_id).entry_type_name, True, True, escape=True, set_min_size=(True,True))

	def widgetize(self):
		toolbar = Toolbar(self)
		toolbar.add_button(Assets.get_image('open'), self.open, 'Open', Ctrl.o)
		toolbar.add_button(Assets.get_image('saveas'), self.saveas, 'Save As', Ctrl.Alt.s)
		toolbar.pack(side=TOP, fill=X)

		self.listbox = ScrolledListbox(self, font=Font.fixed(), width=1, height=6)
		self.listbox.pack(side=TOP, fill=BOTH, expand=1, padx=3, pady=3)
		self.listbox.bind(WidgetEvent.Listbox.Select, self.selection_updated)

		f = Frame(self)
		f.pack(side=TOP, fill=X, padx=3)

		Label(f, text='ID:').pack(side=LEFT)
		Entry(f, textvariable=self.entry_id, width=5).pack(side=LEFT, padx=3)
		Label(f, text='Name:').pack(side=LEFT)
		name_entry = Entry(f, textvariable=self.name)
		name_entry.pack(side=LEFT, fill=X, expand=1)
		Checkbutton(f, text="Append", variable=self.append).pack(side=LEFT)
		Button(f, text='Update', command=self.update).pack(side=LEFT, padx=3)
		Button(f, image=Assets.get_image('remove'), width=20, height=20, command=self.remove).pack(side=LEFT)

		f = Frame(self)
		f.pack(side=TOP, fill=X, padx=3, pady=3)

		Button(f, text='Ok', command=self.ok).pack(side=TOP)

		self.bind(Key.Return, self.update)

		self.refresh_list()

		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = self.entry_id.get()
		if entry_id in name_overrides:
			index = sorted(name_overrides.keys()).index(entry_id)
			self.listbox.select_set(index)
			self.listbox.see(index)
			self.selection_updated()

		name_entry.focus_set()
		name_entry.icursor(END)

	def setup_complete(self):
		self.data_context.settings.windows.load_window_size('entry_name_overrides', self)

	def refresh_list(self):
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		self.listbox.insert(END, *[' %s %s %s' % (lpad(entry_id, 5), '+' if name_overrides[entry_id][0] else ' ', name_overrides[entry_id][1]) for entry_id in sorted(name_overrides.keys())])
		self.listbox.yview_moveto(y)

	def selection_updated(self, _=None):
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = sorted(name_overrides.keys())[int(self.listbox.curselection()[0])]
		self.entry_id.set(entry_id)
		self.name.set(name_overrides[entry_id][1])
		self.append.set(name_overrides[entry_id][0])

	def open(self, _=None):
		path = self.data_context.settings.lastpath.entry_name_overrides.select_open_file(self, title='Open Name Overrides', filetypes=[FileType.txt()])
		if not path:
			return
		try:
			self.data_context.dat_data(self.dat_id).load_name_overrides(path, update_names=False)
		except PyMSError as e:
			ErrorDialog(self, e)
		except:
			ErrorDialog(self, PyMSError('Open', "Couldn't open name overrides '%s'" % path))
		self.refresh_list()

	def saveas(self, _=None):
		path = self.data_context.settings.lastpath.entry_name_overrides.select_save_file(self, title='Save Name Overrides', filetypes=[FileType.txt()], filename=self.dat_id.filename.replace('.dat', '.txt'))
		if not path:
			return
		try:
			self.data_context.dat_data(self.dat_id).save_name_overrides(path)
		except:
			ErrorDialog(self, PyMSError('Save', "Couldn't save name overrides to '%s'" % path))

	def update(self, _=None):
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = self.entry_id.get()
		name = self.name.get()
		append = not not self.append.get()
		if name:
			name_overrides[entry_id] = (append, name)
		elif entry_id in name_overrides:
			del name_overrides[entry_id]
		self.refresh_list()

	def remove(self):
		name_overrides = self.data_context.dat_data(self.dat_id).name_overrides
		entry_id = self.entry_id.get()
		if entry_id in name_overrides:
			del name_overrides[entry_id]
		self.refresh_list()

	def dismiss(self):
		self.data_context.settings.windows.save_window_size('entry_name_overrides', self)
		self.data_context.dat_data(self.dat_id).update_names()
		PyMSDialog.dismiss(self)
