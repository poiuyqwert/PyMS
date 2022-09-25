
from .DataID import DATID, DataID

from ..FileFormats.MPQ.MPQ import MPQ, MPQCompressionFlag

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UIKit import *
from ..Utilities.ScrolledListbox import ScrolledListbox
from ..Utilities import Assets
from ..Utilities.FileType import FileType

import os, shutil

class SaveMPQDialog(PyMSDialog):
	OPTIONS = (
		('units.dat', 'arr\\units.dat', DATID.units),
		('weapons.dat', 'arr\\weapons.dat', DATID.weapons),
		('flingy.dat', 'arr\\flingy.dat', DATID.flingy),
		('sprites.dat', 'arr\\sprites.dat', DATID.sprites),
		('images.dat', 'arr\\images.dat', DATID.images),
		('upgrades.dat', 'arr\\upgrades.dat', DATID.upgrades),
		('techdata.dat', 'arr\\techdata.dat', DATID.techdata),
		('sfxdata.dat', 'arr\\sfxdata.dat', DATID.sfxdata),
		('portdata.dat', 'arr\\portdata.dat', DATID.portdata),
		('mapdata.dat', 'arr\\mapdata.dat', DATID.mapdata),
		('orders.dat', 'arr\\orders.dat', DATID.orders),
		('stat_txt.tbl', 'rez\\stat_txt.tbl', DataID.stat_txt),
		('images.tbl', 'arr\\images.tbl', DataID.imagestbl),
		('sfxdata.tbl', 'arr\\sfxdata.tbl', DataID.sfxdatatbl),
		('portdata.tbl', 'arr\\portdata.tbl', DataID.portdatatbl),
		('mapdata.tbl', 'arr\\mapdata.tbl', DataID.mapdatatbl),
		('cmdicons.grp', 'unit\\cmdbtns\\cmdicons.grp', DataID.cmdicons)
	)

	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'Save MPQ', resizable=(False, False))

	def widgetize(self):
		Label(self, text='Select the files you want to save:', justify=LEFT, anchor=W).pack(fill=X)
		self.listbox = ScrolledListbox(self, selectmode=MULTIPLE, font=Font.fixed(), width=14, height=len(SaveMPQDialog.OPTIONS))
		self.listbox.pack(fill=BOTH, expand=1, padx=5)
		sel = Frame(self)
		Button(sel, text='Select All', command=lambda: self.listbox.select_set(0,END)).pack(side=LEFT, fill=X, expand=1)
		Button(sel, text='Unselect All', command=lambda: self.listbox.select_clear(0,END)).pack(side=LEFT, fill=X, expand=1)
		sel.pack(fill=X, padx=5)
		self.sempq = IntVar()
		self.sempq.set(self.parent.data_context.settings.get('sempq', False))
		Checkbutton(self, text='Self-executing MPQ (SEMPQ)', variable=self.sempq).pack(pady=3)
		for filename,_,_ in SaveMPQDialog.OPTIONS:
			self.listbox.insert(END, filename)
			if filename in self.parent.mpq_export:
				self.listbox.select_set(END)
		btns = Frame(self)
		save = Button(btns, text='Save', width=10, command=self.save)
		save.pack(side=LEFT, pady=5, padx=3)
		Button(btns, text='Ok', width=10, command=self.ok).pack(side=LEFT, pady=5, padx=3)
		btns.pack()
		return save

	def save(self):
		selected_options = [SaveMPQDialog.OPTIONS[i] for i in self.listbox.curselection()]
		if not selected_options:
			MessageBox.showinfo('Nothing to save', 'Please choose at least one item to save.')
		else:
			if self.sempq.get():
				file = self.parent.data_context.settings.lastpath.sempq.select_save_file(self, title='Save SEMPQ to...', filetypes=[FileType.exe_mpq()])
			else:
				file = self.parent.data_context.settings.lastpath.mpq.select_save_file(self, title='Save MPQ to...', filetypes=[FileType.mpq()])
			if file:
				if self.sempq.get() and not os.path.exists(file):
					try:
						shutil.copy(Assets.data_file_path('SEMPQ.exe'), file)
					except:
						ErrorDialog(self, PyMSError('Saving','Could not create SEMPQ "%s".' % file))
						return
				not_saved = []
				try:
					mpq = MPQ.of(file)
					with mpq.open_or_create():
						buffer = None
						for filename,filepath,id in selected_options:
							try:
								if isinstance(id, DATID):
									dat_data = self.parent.data_context.dat_data(id)
									buffer = dat_data.save_data()
								else:
									data_data = self.parent.data_context.data_data(id)
									buffer = data_data.save_data()
								mpq.add_data(buffer, filepath, compression=MPQCompressionFlag.pkware)
								buffer = None
							except:
								not_saved.append(filename)
				except PyMSError as e:
					ErrorDialog(self, e)
					return
				if not_saved:
					MessageBox.showwarning(title='Save problems', message='%s could not be saved to the MPQ.' % ', '.join(not_saved))

	def ok(self):
		self.parent.data_context.settings.sempq = not not self.sempq.get()
		self.parent.mpq_export = [self.listbox.get(i) for i in self.listbox.curselection()]
		PyMSDialog.ok(self)
