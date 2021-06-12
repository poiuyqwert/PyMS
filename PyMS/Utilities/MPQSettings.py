
from ..FileFormats.MPQ.SFmpq import *

from utils import BASE_DIR
from Settings import SettingDict
from setutils import PYMS_SETTINGS
from Tooltip import Tooltip
from UIKit import *

import os

# TODO: Update settings handling once all programs use Settings objects
class MPQSettings(Frame):
	def __init__(self, parent, mpqs, settings, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		self.mpqs = list(mpqs)
		self.settings = settings
		Frame.__init__(self, parent)
		Label(self, text='MPQ Settings:', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X)
		Label(self, text="Files will be read from the highest priority MPQ that contains them.\nThe higher an MPQ is on the list the higher its priority.", anchor=W, justify=LEFT).pack(fill=X)
		self.listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, width=35, height=1, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
            # TODO: What should Shift-Up/Down do?
			# ('<Shift-Up>', lambda e,i=0: self.movestring(e,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			# ('<Shift-Down>', lambda e,i=1: self.movestring(e,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.listframe.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for mpq in self.mpqs:
			self.listbox.insert(END,mpq)
		if self.listbox.size():
			self.listbox.select_set(0)

		buttons = [
			('add', self.add, 'Add MPQ (Insert)', NORMAL, 'Insert', LEFT),
			('remove', self.remove, 'Remove MPQ (Delete)', DISABLED, 'Delete', LEFT),
			('opendefault', self.adddefault, "Add default StarCraft MPQ's (Shift+Insert)", NORMAL, 'Shift+Insert', LEFT),
			('up', lambda e=None,i=0: self.movempq(e,i), 'Move MPQ Up (Shift+Up)', DISABLED, 'Shift+Up', RIGHT),
			('down', lambda e=None,i=1: self.movempq(e,i), 'Move MPQ Down (Shift+Down)', DISABLED, 'Shift+Down', RIGHT),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'PyMS','Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=btn[5], padx=[0,10][btn[0] == 'opendefault'])
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def activate(self):
		self.listframe.focus_set()

	def action_states(self):
		select = [NORMAL,DISABLED][not self.listbox.curselection()]
		for btn in ['remove','up','down']:
			self.buttons[btn]['state'] = select

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def movempq(self, key=None, dir=0):
		if key and self.buttons[['up','down'][dir]]['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		if i == [0,self.listbox.size()-1][dir]:
			return
		s = self.listbox.get(i)
		n = i + [-1,1][dir]
		self.mpqs[i] = self.mpqs[n]
		self.mpqs[n] = s
		self.listbox.delete(i)
		self.listbox.insert(n, s)
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.setdlg.edited = True

	def select_files(self):
		if isinstance(self.settings, SettingDict):
			return self.settings.lastpath.settings.select_open_files(self, key='mpqs', title="Add MPQ's", filetypes=(('MPQ Files','*.mpq'),))
		else:
			path = self.settings.get('lastpath', BASE_DIR)
			file = FileDialog.askopenfilename(parent=self, title="Add MPQ's", defaultextension='.mpq', filetypes=[('MPQ Files','*.mpq'),('All Files','*')], initialdir=path, multiple=True)
			if file:
				self.settings['lastpath'] = os.path.dirname(file[0])
			return file

	def add(self, key=None, add=None):
		if add == None:
			n,s = 0,0
			add = self.select_files()
		else:
			n,s = END,self.listbox.size()
		if add:
			for i in add:
				if not i in self.mpqs:
					h = SFileOpenArchive(i)
					if not SFInvalidHandle(h):
						SFileCloseFile(h)
						if n == END:
							self.mpqs.append(i)
						else:
							self.mpqs.insert(int(n),i)
						self.listbox.insert(n,i)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.action_states()
			self.setdlg.edited = True

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		del self.mpqs[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.setdlg.edited = True

	def adddefault(self, key=None):
		scdir = PYMS_SETTINGS.get('scdir', autosave=False)
		if not scdir or not os.path.isdir(scdir):
			scdir = PYMS_SETTINGS.select_directory(self, key='scdir', title='Choose StarCraft Directory', store=False)
		if scdir and os.path.isdir(scdir):
			a = []
			for f in ['Patch_rt','BrooDat','StarDat']:
				p = os.path.join(scdir, '%s%smpq' % (f,os.extsep))
				if os.path.exists(p) and not p in self.mpqs:
					a.append(p)
			if len(a) == 3 and not 'scdir' in PYMS_SETTINGS:
				PYMS_SETTINGS.scdir = scdir
				PYMS_SETTINGS.save()
			if a:
				self.add(add=a)
