
from ..FileFormats.MPQ.SFmpq import *

from ..Utilities.utils import BASE_DIR, couriernew
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities.ErrorDialog import ErrorDialog
from ..Utilities.UIKit import *

import os, shutil

class SaveMPQDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'Save MPQ', resizable=(False, False))

	def widgetize(self):
		Label(self, text='Select the files you want to save:', justify=LEFT, anchor=W).pack(fill=X)
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, activestyle=DOTBOX, selectmode=MULTIPLE, font=couriernew, width=12, height=10, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', lambda a,l=self.listbox: self.scroll(a,l)),
			('<Home>', lambda a,l=self.listbox,i=0: self.move(a,l,i)),
			('<End>', lambda a,l=self.listbox,i=END: self.move(a,l,i)),
			('<Up>', lambda a,l=self.listbox,i=-1: self.move(a,l,i)),
			('<Left>', lambda a,l=self.listbox,i=-1: self.move(a,l,i)),
			('<Down>', lambda a,l=self.listbox,i=1: self.move(a,l,i)),
			('<Right>', lambda a,l=self.listbox,i=-1: self.move(a,l,i)),
			('<Prior>', lambda a,l=self.listbox,i=-10: self.move(a,l,i)),
			('<Next>', lambda a,l=self.listbox,i=10: self.move(a,l,i)),
		]
		for b in bind:
			listframe.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=X, expand=1)
		listframe.pack(fill=BOTH, expand=1, padx=5)
		sel = Frame(self)
		Button(sel, text='Select All', command=lambda: self.listbox.select_set(0,END)).pack(side=LEFT, fill=X, expand=1)
		Button(sel, text='Unselect All', command=lambda: self.listbox.select_clear(0,END)).pack(side=LEFT, fill=X, expand=1)
		sel.pack(fill=X, padx=5)
		self.sempq = IntVar()
		self.sempq.set(self.parent.data_context.settings.get('sempq', False))
		Checkbutton(self, text='Self-executing MPQ (SEMPQ)', variable=self.sempq).pack(pady=3)
		for f in ['units.dat','weapons.dat','flingy.dat','sprites.dat','images.dat','upgrades.dat','techdata.dat','sfxdata.dat','portdata.dat','mapdata.dat','orders.dat','stat_txt.tbl','images.tbl','sfxdata.tbl','portdata.tbl','mapdata.tbl','cmdicons.grp']:
			self.listbox.insert(END,f)
			if f in self.parent.mpq_export:
				self.listbox.select_set(END)
		btns = Frame(self)
		save = Button(btns, text='Save', width=10, command=self.save)
		save.pack(side=LEFT, pady=5, padx=3)
		Button(btns, text='Ok', width=10, command=self.ok).pack(side=LEFT, pady=5, padx=3)
		btns.pack()
		return save

	def scroll(self, e, lb):
		if e.delta > 0:
			lb.yview('scroll', -2, 'units')
		else:
			lb.yview('scroll', 2, 'units')

	def move(self, e, lb, a):
		if a == END:
			a = lb.size()-2
		elif a not in [0,END]:
			a = max(min(lb.size()-1, int(lb.curselection()[0]) + a),0)
		lb.see(a)

	def save(self):
		sel = [self.listbox.get(i) for i in self.listbox.curselection()]
		if not sel:
			MessageBox.askquestion(parent=self, title='Nothing to save', message='Please choose at least one item to save.', type=MessageBox.OK)
		else:
			if self.sempq.get():
				file = self.parent.data_context.settings.lastpath.sempq.select_file('save', self, 'Save SEMPQ to...', '.exe', [('Executable Files','*.exe'),('All Files','*')], save=True)
			else:
				file = self.parent.data_context.settings.lastpath.mpq.select_file('save', self, 'Save MPQ to...', '.mpq', [('MPQ Files','*.mpq'),('All Files','*')], save=True)
			if file:
				if self.sempq.get():
					if os.path.exists(file):
						h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
					else:
						try:
							shutil.copy(os.path.join(BASE_DIR,'PyMS','Data','SEMPQ.exe'), file)
							h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
						except:
							h = -1
				else:
					h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
				if h == -1:
					ErrorDialog(self, PyMSError('Saving','Could not open %sMPQ "%s".' % (['','SE'][self.sempq.get()],file)))
					return
				undone = []
				s = SFile()
				for f in sel:
					if f == 'stat_txt.tbl':
						p = 'rez\\' + f
					elif f.endswith('.grp'):
						p = 'unit\\cmdbtns\\' + f
					else:
						p = 'arr\\' + f
					try:
						if f in self.parent.dats:
							self.parent.dats[f].compile(s)
							MpqAddFileFromBuffer(h, s.text, p, MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
							s.text = ''
						elif f.endswith('tbl'):
							if f == 'stat_txt.tbl':
								t = self.parent.stat_txt_file
							elif f == 'images.tbl':
								t = self.parent.imagestbl_file
							elif f == 'sfxdata.tbl':
								t = self.parent.sfxdatatbl_file
							elif f == 'portdata.tbl':
								t = self.parent.portdatatbl_file
							else:
								t = self.parent.mapdatatbl_file
							MpqAddFileToArchive(h, t, p, MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
						else:
							self.parent.cmdicon.save_file(s)
							MpqAddFileFromBuffer(h, s.text, p, MAFA_COMPRESS | MAFA_REPLACE_EXISTING)
							s.text = ''
					except:
						undone.append(f)
				MpqCloseUpdatedArchive(h)
				if undone:
					MessageBox.askquestion(parent=self, title='Save problems', message='%s could not be saved to the MPQ.' % ', '.join(undone), type=MessageBox.OK)

	def ok(self):
		self.parent.data_context.settings.sempq = not not self.sempq.get()
		self.parent.mpq_export = [self.listbox.get(i) for i in self.listbox.curselection()]
		PyMSDialog.ok(self)
