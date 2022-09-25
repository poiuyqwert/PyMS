
from ..FileFormats.MPQ.MPQ import MPQ

from . import Assets
from .setutils import PYMS_SETTINGS
from .UIKit import *
from .Toolbar import Toolbar
from .ScrolledListbox import ScrolledListbox
from .FileType import FileType

import os

class MPQSettings(Frame):
	def __init__(self, parent, mpqs, settings, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		self.mpqs = list(mpqs)
		self.settings = settings
		Frame.__init__(self, parent)
		Label(self, text='MPQ Settings:', font=Font.default().bolded(), anchor=W).pack(fill=X)
		Label(self, text="Files will be read from the highest priority MPQ that contains them.\nThe higher an MPQ is on the list the higher its priority.", anchor=W, justify=LEFT).pack(fill=X)

		self.listbox = ScrolledListbox(self, width=35, height=1)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for mpq in self.mpqs:
			self.listbox.insert(END,mpq)
		if self.listbox.size():
			self.listbox.select_set(0)

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add MPQ', Key.Insert),
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove MPQ', Key.Delete, enabled=False, tags='has_selection'),
		self.toolbar.add_button(Assets.get_image('opendefault'), self.adddefault, "Add default StarCraft MPQ's", Shift.Insert),
		self.toolbar.add_spacer(10, flexible=True)
		self.toolbar.add_button(Assets.get_image('up'), lambda e=None,i=0: self.movempq(e,i), 'Move MPQ Up', Shift.Up, enabled=False, tags='has_selection'),
		self.toolbar.add_button(Assets.get_image('down'), lambda e=None,i=1: self.movempq(e,i), 'Move MPQ Down', Shift.Down, enabled=False, tags='has_selection'),
		self.toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def activate(self):
		self.listbox.focus_set()

	def action_states(self):
		has_selection = not not self.listbox.curselection()
		self.toolbar.tag_enabled('has_selection', has_selection)

	def movempq(self, key=None, dir=0):
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

	def add(self, key=None, add=None):
		if add == None:
			n,s = 0,0
			add = self.settings.lastpath.settings.select_open_files(self, key='mpqs', title="Add MPQ's", filetypes=[FileType.mpq_all(),FileType.mpq(),FileType.exe_mpq(),FileType.scm(),FileType.scx()])
		else:
			n,s = END,self.listbox.size()
		if add:
			for i in add:
				if not i in self.mpqs:
					mpq = MPQ.of(i)
					try:
						mpq.open()
						mpq.close()
					except:
						continue
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
