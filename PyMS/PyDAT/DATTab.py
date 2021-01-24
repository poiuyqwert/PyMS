
from ContinueImportDialog import ContinueImportDialog

from ..FileFormats.DAT import WeaponsDAT
from ..FileFormats.DAT import UnitsDAT
from ..FileFormats.TBL import decompile_string

from ..Utilities.utils import BASE_DIR, fit, isstr, ccopy
from ..Utilities.Notebook import NotebookTab
from ..Utilities.Tooltip import Tooltip
from ..Utilities.DataCache import DATA_CACHE
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog

from Tkinter import *
import tkMessageBox

import os

DAT_DATA_REF_FILES = {
	'units.dat': 'Units.txt',
	'weapons.dat': 'Weapons.txt',
	'flingy.dat': 'Flingy.txt',
	'sprites.dat': 'Sprites.txt',
	'images.dat': 'Images.txt',
	'upgrades.dat': 'Upgrades.txt',
	'techdata.dat': 'Techdata.txt',
	'sfxdata.dat': 'Sfxdata.txt',
	'portdata.dat': 'Portdata.txt',
	'mapdata.dat': 'Mapdata.txt',
	'orders.dat': 'Orders.txt',
}

class DATTab(NotebookTab):
	data = None

	def __init__(self, parent, toplevel):
		self.id = 0
		self.toplevel = toplevel
		self.icon = self.toplevel.icon
		self.dat = None
		self.file = None
		self.listbox = None
		self.entrycopy = None
		self.edited = False
		self.dattabs = None
		self.usedby = None
		NotebookTab.__init__(self, parent)

	def tip(self, obj, tipname, hint):
		obj.tooltip = Tooltip(obj, '%s:\n' % tipname + fit('  ', self.toplevel.data_context.hints[hint], end=True)[:-1], mouse=True)

	def makeCheckbox(self, frame, var, txt, hint):
		c = Checkbutton(frame, text=txt, variable=var)
		self.tip(c, txt, hint)
		return c

	def setuplistbox(self):
		f = LabelFrame(self, text='Used By:')
		listframe = Frame(f, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, width=1, activestyle=DOTBOX, height=6, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		self.listbox.bind('<Double-Button-1>', self.usedbyjump)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=X, padx=2, pady=2)
		f.pack(side=BOTTOM, fill=X, padx=2, pady=2)

	def usedbyjump(self, key=None):
		s = self.listbox.curselection()
		if s:
			dat = self.listbox.get(int(s[0])).split(' ', 3)
			self.toplevel.dattabs.display(self.toplevel.dats[dat[0]].idfile.split('.')[0])
			self.toplevel.changeid(i=int(dat[2][:-1]))

	def jump(self, type, id, o=0):
		i = id.get() + o
		if i < len(DATA_CACHE['%s.txt' % type]) - 1:
			self.toplevel.dattabs.display(type)
			self.toplevel.changeid(i=i)

	def files_updated(self):
		pass

	def update_status(self):
		if self.file:
			self.toplevel.status.set(self.file)
		else:
			self.toplevel.status.set(os.path.join(BASE_DIR, 'PyMS', 'MPQ', 'arr',  self.dat.FILE_NAME))

	def activate(self):
		if self.dat:
			self.toplevel.listbox.delete(0,END)
			d = []
			if self.toplevel.data_context.settings.settings.get('customlabels', False):
				if self.data == 'Units.txt':
					d = [decompile_string(s) for s in self.toplevel.stat_txt.strings[0:228]]
				elif self.data in ['Weapons.txt','Upgrades.txt','Techdata.txt']:
					# TODO: Expanded DAT
					for i in range(WeaponsDAT.FORMAT.entries):
						s = self.toplevel.defaults['%s.dat' % self.data.split('.')[0].lower()].get_value(i, 'Label')
						if s:
							d.append(decompile_string(self.toplevel.stat_txt.strings[s-1]))
						else:
							d.append('None')
			if not d:
				d = list(DATA_CACHE[self.data])
				if d[-1] == 'None':
					del d[-1]
			self.toplevel.jumpid.range[1] = len(d) - 1
			self.toplevel.jumpid.editvalue()
			for n,l in enumerate(d):
				self.toplevel.listbox.insert(END, ' %s%s  %s' % (' ' * (4-len(str(n))),n,l))
			self.toplevel.listbox.select_set(self.id)
			self.toplevel.listbox.see(self.id)
			self.update_status()
			self.load_data()

	def deactivate(self):
		self.save_data()

	def load_data(self, id=None):
		if not self.dat:
			return
		if id != None:
			self.id = id
		entry = self.dat.get_entry(self.id)
		self.load_entry(entry)
		self.checkreference()

	def load_entry(self, entry):
		pass

	def save_data(self):
		if not self.dat:
			return
		entry = self.dat.get_entry(self.id)
		self.save_entry(entry)
		self.checkreference()
		if self.edited:
			self.toplevel.action_states()

	def save_entry(self, entry):
		pass

	def unsaved(self):
		if self == self.toplevel.dattabs.active:
			self.save_data()
		if self.edited:
			file = self.file
			if not file:
				file = self.dat.FILE_NAME
			save = tkMessageBox.askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=tkMessageBox.YES, type=tkMessageBox.YESNOCANCEL)
			if save != tkMessageBox.NO:
				if save == tkMessageBox.CANCEL:
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def checkreference(self, lookup_id=None, used_by=None):
		if self.listbox:
			self.listbox.delete(0,END)
			if not used_by:
				used_by = self.usedby
			if not lookup_id:
				lookup_id = self.id
			for dat_name,lookup in used_by:
				dat = self.toplevel.dats[dat_name]
				# TODO: Expanded DAT
				for id in range(dat.FORMAT.entries):
					entry = dat.get_entry(id)
					check_ids = lookup(entry)
					for check_id in check_ids:
						# If `lookup` returns a tuple, it represents a range of IDs, and we must check if the `lookup_id` is within that range
						if check_id == lookup_id or (isinstance(check_id, tuple) and lookup_id >= check_id[0] and lookup_id <= check_id[1]):
							ref = DATA_CACHE[DAT_DATA_REF_FILES[dat_name]][id]
							if self.toplevel.data_context.settings.settings.get('customlabels', False) and type(dat) == UnitsDAT:
								ref = decompile_string(self.toplevel.stat_txt.strings[id])
							self.listbox.insert(END, '%s entry %s: %s' % (dat.FILE_NAME, id, ref))
							break

	def popup(self, e):
		self.toplevel.listmenu.entryconfig(1, state=[NORMAL,DISABLED][not self.entrycopy])
		if self.dat.FILE_NAME == 'units.dat':
			self.toplevel.listmenu.entryconfig(3, state=NORMAL)
			self.toplevel.listmenu.entryconfig(4, state=[NORMAL,DISABLED][not self.dattabs.active.tabcopy])
		else:
			self.toplevel.listmenu.entryconfig(3, state=DISABLED)
			self.toplevel.listmenu.entryconfig(4, state=DISABLED)
		self.toplevel.listmenu.post(e.x_root, e.y_root)

	def copy(self, t):
		if not t:
			self.entrycopy = list(self.dat.entries[self.id])
		elif self.dat.FILE_NAME == 'units.dat':
			self.dattabs.active.tabcopy = list(self.dat.entries[self.id])

	def paste(self, t):
		if not t:
			if self.entrycopy:
				self.dat.entries[self.id] = list(self.entrycopy)
		elif self.dat.FILE_NAME == 'units.dat' and self.dattabs.active.tabcopy:
			for v in self.dattabs.active.values.keys():
				self.dat.set_value(self.id, v, self.dattabs.active.tabcopy[self.dat.labels.index(v)])
		self.activate()

	def reload(self):
		self.dat.entries[self.id] = list(self.toplevel.defaults[self.dat.FILE_NAME].entries[self.id])
		self.activate()

	def new(self, key=None):
		if not self.unsaved():
			self.dat.entries = list(self.toplevel.defaults[self.dat.FILE_NAME].entries)
			self.file = None
			self.id = 0
			self.activate()

	def open(self, file, save=True):
		if not save or not self.unsaved():
			if isstr(file):
				entries = ccopy(self.dat.entries)
				try:
					self.dat.load_file(file)
				except PyMSError, e:
					self.dat.entries = entries
					if save:
						ErrorDialog(self, e)
					else:
						raise
					return
				self.file = file
			elif isinstance(file, tuple):
				dat,self.file = file
				self.dat.entries = dat.entries
			self.id = 0
			self.toplevel.listbox.select_clear(0,END)
			self.toplevel.listbox.select_set(0)
			if self.toplevel.dattabs.active == self:
				self.toplevel.status.set(self.file)
				self.load_data()

	def iimport(self, key=None, file=None, c=True, parent=None):
		if parent == None:
			parent = self
		if not file:
			file = self.toplevel.data_context.settings.lastpath.txt.select_file('import', self, 'Import TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return
		entries = ccopy(self.dat.entries)
		try:
			ids = self.dat.interpret(file)
		except PyMSError, e:
			self.dat.entries = entries
			ErrorDialog(self, e)
			return
		cont = c
		for n,_entry in enumerate(entries):
			if cont != 3 and n in ids:
				if cont != 2:
					x = ContinueImportDialog(parent, self.dat.FILE_NAME, n)
					cont = x.cont
					if cont in [0,3]:
						self.dat.entries[n] = entries[n]
			else:
				self.dat.entries[n] = entries[n]
		return cont

	def save(self, key=None):
		if self.file == None:
			self.saveas()
			return
		try:
			self.dat.compile(self.file)
		except PyMSError, e:
			ErrorDialog(self, e)
		else:
			self.edited = False
			self.toplevel.action_states()

	def saveas(self, key=None):
		file = self.toplevel.data_context.settings.lastpath.dat.save.select_file(self.dat.FILE_NAME, self, 'Save %s As' % self.dat.FILE_NAME, '*.dat', [('StarCraft %s files' % self.dat.FILE_NAME,'*.dat'),('All Files','*')], save=True)
		if not file:
			return True
		self.file = file
		self.save()
		self.update_status()

	def export(self, key=None):
		file = self.toplevel.data_context.settings.lastpath.txt.select_file('export', self, 'Export TXT', '*.txt', [('Text Files','*.txt'),('All Files','*')], save=True)
		if not file:
			return True
		try:
			self.dat.decompile(file)
		except PyMSError, e:
			ErrorDialog(self, e)
