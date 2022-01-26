
from ..Utilities.utils import BASE_DIR, couriernew
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Tooltip import Tooltip

import os

class ImportListDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self):
		self.bind('<Insert>', self.add)
		self.bind('<Delete>', self.remove)
		self.bind('<Control-i>', self.iimport)

		buttons = [
			('add', self.add, 'Add File (Insert)', NORMAL),
			('remove', self.remove, 'Remove File (Delete)', DISABLED),
			10,
			('import', self.iimport, 'Import Selected Script (Ctrl+I)', DISABLED),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		##Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, font=couriernew, activestyle=DOTBOX, yscrollcommand=scrollbar.set, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, expand=1)

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall, state=[NORMAL,DISABLED][not self.parent.imports])
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.parent.imports:
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		self.minsize(200,150)
		self.parent.settings.windows.load_window_size('listimport')

		return ok

	# def select_files(self):
	# 	path = self.parent.settings.get('lastpath', BASE_DIR)
	# 	self._pyms__window_blocking = True
	# 	file = tkFileDialog.askopenfilename(parent=self, title='Add Imports', defaultextension='.txt', filetypes=[('Text Files','*.txt'),('All Files','*')], initialdir=path, multiple=True)
	# 	self._pyms__window_blocking = False
	# 	if file:
	# 		self.parent.settings['lastpath'] = os.path.dirname(file[0])
	# 	return file

	def add(self, key=None):
		iimport = self.select_files()
		if iimport:
			for i in iimport:
				if i not in self.parent.imports:
					self.parent.imports.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] == DISABLED:
			return
		index = int(self.listbox.curselection()[0])
		del self.parent.imports[index]
		if self.parent.imports and index == len(self.parent.imports):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, key=None):
		if key and self.buttons['import']['state'] == DISABLED:
			return
		self.parent.iimport(file=self.listbox.get(self.listbox.curselection()[0]), parent=self)

	def iimportall(self):
		self.parent.iimport(file=self.parent.imports, parent=self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.imports:
			self.buttons['remove']['state'] = NORMAL
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = NORMAL
			for file in self.parent.imports:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		else:
			self.buttons['remove']['state'] = DISABLED
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = DISABLED

	def ok(self):
		self.parent.settings.windows.save_window_size('listimport', self)
		PyMSDialog.ok(self)
