from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SFmpq import *
from Libs.DAT import *
from Libs.TBL import TBL,decompile_string,compile_string
from Libs.PAL import Palette
from Libs.GRP import CacheGRP, frame_to_photo, rle_outline, OUTLINE_SELF
from Libs.IScriptBIN import IScriptBIN

from Tkinter import *
from tkMessageBox import *
import tkFileDialog

from thread import start_new_thread
from shutil import copy
from math import ceil
import optparse, os, re, sys
play_sound = None
try:
	from winsound import *
	def win_play(raw_audio):
		start_new_thread(PlaySound, (raw_audio, SND_MEMORY))
	play_sound = win_play
except:
	import subprocess
	def osx_play(raw_audio):
		def do_play(path):
			try:
				subprocess.call(["afplay", temp_file])
			except:
				pass
			try:
				os.remove(path)
			except:
				pass
		temp_file = create_temp_file('audio')
		handle = open(temp_file, 'wb')
		handle.write(raw_audio)
		handle.flush()
		os.fsync(handle.fileno())
		handle.close()
		start_new_thread(do_play, (temp_file,))
	play_sound = osx_play

VERSION = (1,12)
LONG_VERSION = 'v%s.%s' % VERSION
ICON_CACHE = {}
GRP_CACHE = {}
HINTS = {}
PALETTES = {}
for l in open(os.path.join(BASE_DIR,'Libs','Data','Hints.txt'),'r'):
	m = re.match('(\\S+)=(.+)\n?', l)
	if m:
		HINTS[m.group(1)] = m.group(2)

def tip(obj, tipname, hint):
	obj.tooltip = Tooltip(obj, '%s:\n' % tipname + fit('  ', HINTS[hint], end=True)[:-1], mouse=True)

def makeCheckbox(frame, var, txt, hint):
	c = Checkbutton(frame, text=txt, variable=var)
	tip(c, txt, hint)
	return c

class IScriptDropDown(DropDown):
	def __init__(self, parent, variable, entries, display=None, width=1, blank=None, state=NORMAL):
		self.ids = dict([(n,n) for n in range(0,len(entries))])
		DropDown.__init__(self, parent, variable, entries, display, width, blank, state)

	def set(self, num):
		#print num,'\t',self.ids[num]
		self.change(self.ids[num])
		Variable.set(self.variable, num)
		self.disp(num)

	def choose(self, e=None):
		if self.listbox['state'] == NORMAL:
			i = self.ids[self.variable.get()]
			c = DropDownChooser(self, self.entries, i)
			self.set(int(self.entries[c.result].split('[')[-1][:-1]))
			self.listbox.select_set(c.result)

	def disp(self, n):
		if self.display:
			if n == self.listbox.size()-1 and self.blank != None:
				n = self.blank
			if isinstance(self.display, Variable):
				self.display.set(n)
			else:
				self.display(n)

class DATSettingsDialog(SettingsDialog):
	def widgetize(self):
		self.custom = IntVar()
		self.custom.set(self.parent.settings.get('customlabels',0))
		self.minsize(*self.min_size)
		self.tabs = Notebook(self)
		self.mpqsettings = MPQSettings(self.tabs, self.parent.mpqhandler.mpqs, self.parent.settings)
		self.tabs.add_tab(self.mpqsettings, 'MPQ Settings')
		for d in self.data:
			f = Frame(self.tabs)
			f.parent = self
			pane = SettingsPanel(f, d[1], self.parent.settings, self.parent.mpqhandler)
			pane.pack(fill=BOTH, expand=1)
			self.pages.append(pane)
			if d[0].startswith('TBL'):
				Checkbutton(f, text='Use custom labels', variable=self.custom, command=self.doedit).pack()
			self.tabs.add_tab(f, d[0])
		self.tabs.pack(fill=BOTH, expand=1, padx=5, pady=5)
		btns = Frame(self)
		ok = Button(btns, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		btns.pack()
		if 'settingswindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'settingswindow', True)
		if self.err:
			self.after(1, self.showerr)
		return ok

	def doedit(self, e=None):
		self.edited = True

	def ok(self):
		savesize(self, self.parent.settings, 'settingswindow')
		if self.edited:
			t = self.parent.mpqhandler.mpqs
			self.parent.mpqhandler.set_mpqs(self.mpqsettings.mpqs)
			b = {}
			b['mpqs'] = self.parent.settings.get('mpqs',[])
			self.parent.settings['mpqs'] = self.mpqsettings.mpqs
			m = os.path.join(BASE_DIR,'Libs','MPQ','')
			for p,d in zip(self.pages,self.data):
				for s in d[1]:
					b[s[2]] = self.parent.settings[s[2]]
					self.parent.settings[s[2]] = ['','MPQ:'][p.variables[s[0]][0].get()] + p.variables[s[0]][1].get().replace(m,'MPQ:',1)
			b['customlabels'] = self.parent.settings.get('customlabels',False)
			self.parent.settings['customlabels'] = self.custom.get()
			e = self.parent.open_files()
			if e:
				self.parent.mpqhandler.set_mpqs(t)
				self.parent.settings.update(b)
				ErrorDialog(self, e)
				return
		PyMSDialog.ok(self)

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
		self.sempq.set(self.parent.settings.get('sempq',0))
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
			askquestion(parent=self, title='Nothing to save', message='Please choose at least one item to save.', type=OK)
		else:
			if self.sempq.get():
				file = self.parent.select_file('Save SEMPQ to...', False, '.exe', [('Executable Files','*.exe'),('All Files','*')], self)
			else:
				file = self.parent.select_file('Save MPQ to...', False, '.mpq', [('MPQ Files','*.mpq'),('All Files','*')], self)
			if file:
				if self.sempq.get():
					if os.path.exists(file):
						h = MpqOpenArchiveForUpdate(file, MOAU_OPEN_ALWAYS | MOAU_MAINTAIN_LISTFILE)
					else:
						try:
							copy(os.path.join(BASE_DIR,'Libs','Data','SEMPQ.exe'), file)
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
					askquestion(parent=self, title='Save problems', message='%s could not be saved to the MPQ.' % ', '.join(undone), type=OK)

	def ok(self):
		self.parent.settings['sempq'] = self.sempq.get()
		self.parent.mpq_export = [self.listbox.get(i) for i in self.listbox.curselection()]
		PyMSDialog.ok(self)

class ContinueImportDialog(PyMSDialog):
	def __init__(self, parent, dattype, id):
		self.dattype = dattype
		self.id = id
		self.cont = 0
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self):
		Label(self, text="You are about to import the %s entry %s, overwrite existing data?" % (self.dattype,self.id)).pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self):
		self.cont = 1
		self.ok()

	def yestoall(self):
		self.cont = 2
		self.ok()

	def cancel(self):
		self.cont = 3
		self.ok()

class DATTab(NotebookTab):
	data = None

	def __init__(self, parent, toplevel):
		self.id = 0
		self.values = {}
		self.toplevel = toplevel
		self.icon = self.toplevel.icon
		self.dat = None
		self.file = None
		self.listbox = None
		self.entrycopy = None
		self.edited = False
		NotebookTab.__init__(self, parent)

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

	def activate(self):
		if self.dat:
			self.toplevel.listbox.delete(0,END)
			d = []
			if self.toplevel.settings.get('customlabels',0):
				if self.data == 'Units.txt':
					d = [decompile_string(s) for s in self.toplevel.stat_txt.strings[0:228]]
				elif self.data in ['Weapons.txt','Upgrades.txt','Techdata.txt']:
					for i in range(WeaponsDAT.count):
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
			if self.file:
				self.toplevel.status.set(self.file)
			else:
				self.toplevel.status.set(os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr',  self.dat.datname))
			self.loadsave()

	def deactivate(self):
		selections = self.toplevel.listbox.curselection()
		if selections:
			self.id = int(selections[0])
		self.loadsave(True)

	def loadsave(self, save=False):
		if self.dat:
			for n,v in self.values.iteritems():
				if save:
					if isinstance(v, list):
						flags = 0
						for x,f in enumerate(v):
							if f.get():
								flags += 2 ** x
						if self.dat.get_value(self.id, n) != flags:
							self.edited = True
							self.dat.set_value(self.id,n,flags)
					elif isinstance(v, tuple):
						for x in v:
							r = x.get()
							if self.dat.get_value(self.id,n) != r:
								self.edited = True
								self.dat.set_value(self.id,n,r)
					else:
						r = v.get()
						if self.dat.get_value(self.id,n) != r:
							self.edited = True
							self.dat.set_value(self.id,n,r)
				else:
					c = self.dat.get_value(self.id,n)
					if isinstance(v, list):
						for x,f in enumerate(v):
							f.set(not not c & (2 ** x))
					else:
						v.set(c)
			self.checkreference()
			if save and self.edited:
				self.toplevel.action_states()

	def unsaved(self):
		if self.edited:
			file = self.file
			if not file:
				file = self.dat.datname
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def checkreference(self, v=None, c=None):
		if self.listbox:
			if not c:
				c = self.usedby
			self.listbox.delete(0,END)
			if not v:
				val = self.id
			else:
				val = v.get()
			for d,vals in c:
				dat = self.toplevel.dats[d]
				for id in range(dat.count):
					for dv in vals:
						if (isstr(dv) and dat.get_value(id, dv) == val) or (isinstance(dv, tuple) and val >= dat.get_value(id,dv[0]) and val <= dat.get_value(id,dv[1])):
							ref = DATA_CACHE[dat.idfile][id]
							if self.toplevel.settings.get('customlabels',0) and type(dat) == UnitsDAT:
								ref = decompile_string(self.toplevel.stat_txt.strings[id])
							self.listbox.insert(END, '%s entry %s: %s' % (dat.datname, id, ref))
							break

	def popup(self, e):
		self.toplevel.listmenu.entryconfig(1, state=[NORMAL,DISABLED][not self.entrycopy])
		if self.dat.datname == 'units.dat':
			self.toplevel.listmenu.entryconfig(3, state=NORMAL)
			self.toplevel.listmenu.entryconfig(4, state=[NORMAL,DISABLED][not self.dattabs.active.tabcopy])
		else:
			self.toplevel.listmenu.entryconfig(3, state=DISABLED)
			self.toplevel.listmenu.entryconfig(4, state=DISABLED)
		self.toplevel.listmenu.post(e.x_root, e.y_root)

	def copy(self, t):
		if not t:
			self.entrycopy = list(self.dat.entries[self.id])
		elif self.dat.datname == 'units.dat':
			self.dattabs.active.tabcopy = list(self.dat.entries[self.id])

	def paste(self, t):
		if not t:
			if self.entrycopy:
				self.dat.entries[self.id] = list(self.entrycopy)
		elif self.dat.datname == 'units.dat' and self.dattabs.active.tabcopy:
			for v in self.dattabs.active.values.keys():
				self.dat.set_value(self.id, v, self.dattabs.active.tabcopy[self.dat.labels.index(v)])
		self.activate()

	def reload(self):
		self.dat.entries[self.id] = list(self.toplevel.defaults[self.dat.datname].entries[self.id])
		self.activate()

	def new(self, key=None):
		self.loadsave(True)
		if not self.unsaved():
			self.dat.entries = list(self.toplevel.defaults[self.dat.datname].entries)
			self.file = None
			self.id = 0
			self.activate()

	def open(self, key=None, file=None, save=True):
		if self == self.toplevel.dattabs.active:
			self.loadsave(True)
		if not save or not self.unsaved():
			if file == None:
				file = self.toplevel.select_file('Open %s' % self.dat.datname, filetypes=[('StarCraft %s files' % self.dat.datname,'*.dat'),('All Files','*')])
				if not file:
					return
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
				self.dat,self.file = file
			self.id = 0
			self.toplevel.listbox.select_set(0)
			if self.toplevel.dattabs.active == self:
				self.toplevel.status.set(self.file)
				self.loadsave()

	def iimport(self, key=None, file=None, c=True, parent=None):
		if parent == None:
			parent = self
		if not file:
			file = self.toplevel.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')], parent)
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
		for n,entry in enumerate(entries):
			if cont != 3 and n in ids:
				if cont != 2:
					x = ContinueImportDialog(parent, self.dat.datname, n)
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
		file = self.toplevel.select_file('Save %s As' % self.dat.datname, False, filetypes=[('StarCraft %s files' % self.dat.datname,'*.dat'),('All Files','*')])
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		file = self.toplevel.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return True
		try:
			self.dat.decompile(file)
		except PyMSError, e:
			ErrorDialog(self, e)

class DATUnitsTab(NotebookTab):
	def __init__(self, parent, toplevel, parent_tab):
		self.values = {}
		self.toplevel = toplevel
		self.parent_tab = parent_tab
		self.icon = self.toplevel.icon
		self.tabcopy = None
		self.edited = False
		NotebookTab.__init__(self, parent)

	def jump(self, type, id, o=0):
		i = id.get() + o
		if i < len(DATA_CACHE['%s.txt' % type]) - 1:
			self.toplevel.dattabs.display(type)
			self.toplevel.changeid(i=i)

	def files_updated(self):
		pass

	def activate(self):
		self.loadsave()

	def deactivate(self):
		self.loadsave(True)

	def loadsave(self, save=False):
		if self.toplevel.units:
			for n,v in self.values.iteritems():
				if save:
					if isinstance(v, list):
						oldflags = self.toplevel.units.get_value(self.parent.parent.id,n)
						flags = 0
						for x,f in enumerate(v):
							if f and f.get():
								flags += 2 ** x
							else:
								flags += oldflags & (2 ** x)
						if flags != oldflags:
							self.edited = True
							self.toplevel.units.set_value(self.parent.parent.id,n,flags)
					elif isinstance(v, tuple):
						for x in v:
							r = x.get()
							if self.toplevel.units.get_value(self.parent.parent.id,n) != r:
								self.edited = True
								self.toplevel.units.set_value(self.parent.parent.id,n,r)
					else:
						r = v.get()
						if self.toplevel.units.get_value(self.parent.parent.id,n) != r:
							self.edited = True
							self.toplevel.units.set_value(self.parent.parent.id,n,r)
				else:
					c = self.toplevel.units.get_value(self.parent.parent.id,n)
					if isinstance(v, list):
						for x,f in enumerate(v):
							if f:
								f.set(not not c & (2 ** x))
					else:
						v.set(c)
			if save and self.edited:
				self.parent_tab.edited = self.edited
				self.toplevel.action_states()

class OrdersTab(DATTab):
	data = 'Orders.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.targetingentry = IntegerVar(0,[0,130])
		self.targeting = IntVar()
		self.energyentry = IntegerVar(0,[0,44])
		self.energy = IntVar()
		self.obscuredentry = IntegerVar(0,[0,189])
		self.obscured = IntVar()
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.label = IntVar()
		self.animationentry = IntegerVar(0,[0,28])
		self.animation = IntVar()
		self.highlightentry = IntegerVar(0, [0,65535])
		self.highlightdd = IntVar()
		self.unknown = IntegerVar(0, [0,65535])

		l = LabelFrame(frame, text='Order Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Targeting:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.targetingentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.targeting, DATA_CACHE['Weapons.txt'], self.targetingentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Weapons',i=self.targeting: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Targeting', 'OrdTargeting')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energyentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.energy, DATA_CACHE['Techdata.txt'], self.energyentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Techdata',i=self.energy: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Energy', 'OrdEnergy')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Obscured:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.obscuredentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.obscured, DATA_CACHE['Orders.txt'], self.obscuredentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Orders',i=self.obscured: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Obscured', 'OrdObscured')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Label:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, stattxt, self.labelentry, width=25)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Label', 'OrdLabel')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Animation:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.animationentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.animation, DATA_CACHE['Animations.txt'], self.animationentry, width=25).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Animation', 'OrdAnimation')
		f.pack(fill=X)
		m = Frame(s)
		ls = Frame(m)
		f = Frame(ls)
		Label(f, text='Highlight:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.highlightentry, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.highlightdd, DATA_CACHE['Icons.txt'], self.highlightentry, width=25, blank=65535).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Highlight', 'OrdHighlight')
		f.pack(fill=X)
		f = Frame(ls)
		Label(f, text='Unknown:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unknown, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(f, 'Unknown', 'OrdUnk13')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		ls = Frame(m, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		m.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.weapontargeting = IntVar()
		self.unknown2 = IntVar()
		self.unknown3 = IntVar()
		self.unknown4 = IntVar()
		self.unknown5 = IntVar()
		self.interruptable = IntVar()
		self.unknown7 = IntVar()
		self.queueable = IntVar()
		self.unknown9 = IntVar()
		self.unknown10 = IntVar()
		self.unknown11 = IntVar()
		self.unknown12 = IntVar()

		flags = [
			[
				('Use Weapon Targeting', self.weapontargeting, 'OrdWeapTarg'),
				('Secondary Order', self.unknown2, 'OrdUnk2'),
				('Unknown3', self.unknown3, 'OrdUnk3'),
				('Unknown4', self.unknown4, 'OrdUnk4'),
			],[
				('Unknown5', self.unknown5, 'OrdUnk5'),
				('Can be Interrupted', self.interruptable, 'OrdInterrupt'),
				('Unknown7', self.unknown7, 'OrdUnk7'),
				('Can be Queued', self.queueable, 'OrdQueue'),
			],[
				('Unknown9', self.unknown9, 'OrdUnk9'),
				('Unknown10', self.unknown10, 'OrdUnk10'),
				('Unknown11', self.unknown11, 'OrdUnk11'),
				('Unknown12', self.unknown12, 'OrdUnk12'),
			],
		]
		l = LabelFrame(frame, text='Flags:')
		s = Frame(l)
		for c in flags:
			cc = Frame(s, width=20)
			for t,v,h in c:
				f = Frame(cc)
				Checkbutton(f, text=t, variable=v).pack(side=LEFT)
				tip(f, t, h)
				f.pack(fill=X)
			cc.pack(side=LEFT, fill=Y)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['CompAIIdle','HumanAIIdle','ReturntoIdle','AttackUnit','AttackMove']),
		]
		self.setuplistbox()

		self.values = {
			'Label':self.label,
			'UseWeaponTargeting':self.weapontargeting,
			'Unknown1':self.unknown2,
			'MainOrSecondary':self.unknown3,
			'Unknown3':self.unknown4,
			'Unknown4':self.unknown5,
			'Interruptable':self.interruptable,
			'Unknown5':self.unknown7,
			'Queueable':self.queueable,
			'Unknown6':self.unknown9,
			'Unknown7':self.unknown10,
			'Unknown8':self.unknown11,
			'Unknown9':self.unknown12,
			'Targeting':self.targeting,
			'Energy':self.energy,
			'Animation':self.animation,
			'Highlight':self.highlightentry,
			'Unknown10':self.unknown,
			'ObscuredOrder':self.obscured,
		}

	def files_updated(self):
		self.dat = self.toplevel.orders
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.highlightentry.get()
			if i < self.toplevel.cmdicon.frames:
				if not i in ICON_CACHE:
					image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
					ICON_CACHE[i] = image
				else:
					image = ICON_CACHE[i]
				self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		if not save and 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()

class MapsTab(DATTab):
	data = 'Mapdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		frame = Frame(self)

		mapdata = [] # [decompile_string(s) for s in self.toplevel.mapdatatbl.strings]
		self.missionentry = IntegerVar(0, [0,len(mapdata)])
		self.missiondd = IntVar()

		l = LabelFrame(frame, text='Campaign Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Mission Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.missionentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.missions = DropDown(f, self.missiondd, mapdata, self.missionentry, width=30, blank=65)
		self.missions.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Mission Dir', 'MapFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {'MapFile':self.missionentry}

	def files_updated(self):
		self.dat = self.toplevel.campaigns
		mapdata = [decompile_string(s) for s in self.toplevel.mapdatatbl.strings]
		self.missionentry.range[1] = len(mapdata)
		self.missions.setentries(mapdata)
		self.missionentry.editvalue()

class PortraitsTab(DATTab):
	data = 'Portdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		portdata = [] # ['None'] + [decompile_string(s) for s in self.toplevel.portdatatbl.strings]
		self.portraitentry = IntegerVar(0, [0,len(portdata)-1])
		self.portraitdd = IntVar()

		l = LabelFrame(frame, text='Portrait:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Portrait Dir:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.portraitentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.portraits = DropDown(f, self.portraitdd, portdata, self.portraitentry, width=30)
		self.portraits.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Portrait Dir', 'PortFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.smkchange = IntegerVar(0, [0,255])
		self.unknown = IntegerVar(0, [0,255])

		m = Frame(frame)
		l = LabelFrame(m, text='General Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='SMK Change:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.smkchange, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'SMK Change', 'PortSMKChange')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Unknown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unknown, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Unknown', 'PortUnk1')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['Portrait']),
		]
		self.setuplistbox()

		self.values = {
			'PortraitFile':self.portraitentry,
			'SMKChange':self.smkchange,
			'Unknown':self.unknown,
		}

	def files_updated(self):
		self.dat = self.toplevel.portraits
		portdata = ['None'] + [decompile_string(s) for s in self.toplevel.portdatatbl.strings]
		self.portraitentry.range[1] = len(portdata)-1
		self.portraits.setentries(portdata)
		self.portraitentry.editvalue()

class SoundsTab(DATTab):
	data = 'Sfxdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		sfxdata = [] # ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		self.soundentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.sounddd = IntVar()

		l = LabelFrame(frame, text='Sound:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sound File:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.soundentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.sounds = DropDown(f, self.sounddd, sfxdata, self.changesound, width=30)
		self.soundentry.callback = self.sounds.set
		self.sounds.pack(side=LEFT, fill=X, expand=1, padx=2)
		i = PhotoImage(file=os.path.join(BASE_DIR,'Images','fwp.gif'))
		self.playbtn = Button(f, image=i, width=20, height=20, command=self.play)
		self.playbtn.image = i
		self.playbtn.pack(side=LEFT, padx=1)
		tip(f, 'Sound File', 'SoundFile')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.unknown1 = IntegerVar(0, [0,255])
		self.flags = IntegerVar(0, [0,255])
		self.race = IntVar()
		self.volume = IntegerVar(0, [0,100])

		m = Frame(frame)
		l = LabelFrame(m, text='General Properties:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Unknown1:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unknown1, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Unknown1', 'SoundUnk1')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Flags:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.flags, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Flags', 'SoundFlags')
		f.pack(fill=X)
		
		f = Frame(s)
		
		Label(f, text='Race:', width=9, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		tip(f, 'Race', 'SoundRace')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Volume %:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.volume, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Volume %', 'SoundVol')
		f.pack(fill=X)
		
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['ReadySound',('WhatSoundStart','WhatSoundEnd'),('PissSoundStart','PissSoundEnd'),('YesSoundStart','YesSoundEnd')]),
		]
		self.setuplistbox()

		self.values = {
			'SoundFile':self.soundentry,
			'Unknown1':self.unknown1,
			'Flags':self.flags,
			'Race':self.race,
			'Volume':self.volume,
		}

	def files_updated(self):
		self.dat = self.toplevel.sounds
		sfxdata = ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		self.soundentry.range[1] = len(sfxdata)-1
		self.sounds.setentries(sfxdata)
		self.soundentry.editvalue()

	def changesound(self, n=None):
		if n == None:
			n = self.soundentry.get()
		else:
			self.soundentry.set(n)
		self.playbtn['state'] = [DISABLED,NORMAL][play_sound and not FOLDER and n > 0]

	def play(self):
		if play_sound:
			f = self.toplevel.mpqhandler.get_file('MPQ:sound\\' + self.toplevel.sfxdatatbl.strings[self.soundentry.get()-1][:-1])
			if f:
				play_sound(f.read())

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		if not save:
			self.changesound()

class TechnologyTab(DATTab):
	data = 'Techdata.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.iconentry = IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = IntVar()

		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.labeldd = IntVar()

		self.item = None

		l = LabelFrame(frame, text='Technology Display:')
		s = Frame(l)
		ls = Frame(s)
		f = Frame(ls)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Technology Icon', 'TechIcon')
		f.pack(fill=X)
		f = Frame(ls)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.labeldd, stattxt, self.labelentry, width=30)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Technology Label', 'TechLabel')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		ls = Frame(s, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.minerals = IntegerVar(0, [0,65535])
		self.vespene = IntegerVar(0, [0,65535])
		self.time = IntegerVar(24, [1,65535], callback=lambda n,i=0: self.updatetime(n,i))
		self.secs = FloatVar(1, [0.0416,2730.625], callback=lambda n,i=1: self.updatetime(n,i), precision=4)
		self.energy = IntegerVar(0, [0,65535])

		m = Frame(frame)
		l = LabelFrame(m, text='Technology Cost:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minerals, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Mineral Cost', 'TechMinerals')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.vespene, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Vespene Cost', 'TechVespene')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.time, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.secs, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		tip(f, 'Build Time', 'TechTime')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Energy:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.energy, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Energy Cost', 'TechVespene')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.researchReq = IntegerVar(0, [0,65535])
		self.useReq = IntegerVar(0, [0,65535])
		self.race = IntVar()
		self.unused = IntVar()
		self.broodwar = IntVar()

		l = LabelFrame(m, text='Technology Properties:')
		s = Frame(l)
		f = Frame(s)
		
		Label(f, text='ResearchReq:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.researchReq, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Research Requirements', 'TechReq')
		f.pack(fill=X)
		f = Frame(s)

		Label(f, text='UseReq:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.useReq, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Usage Requirements', 'TechUseReq')
		f.pack(fill=X)
		f = Frame(s)

		Label(f, text='Race:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		tip(f, 'Race', 'TechRace')
		f.pack(fill=X)
		f = Frame(s)
		
		makeCheckbox(f, self.unused, 'Researched', 'TechUnused').pack(side=LEFT)
		makeCheckbox(f, self.broodwar, 'BroodWar', 'TechBW').pack(side=LEFT)

		f.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=Y)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('orders.dat', ['Energy']),
			('weapons.dat', ['Unused']),
		]
		self.setuplistbox()

		self.values = {
			'MineralCost':self.minerals,
			'VespeneCost':self.vespene,
			'ResearchTime':self.time,
			'EnergyRequired':self.energy,
			'ResearchRequirements':self.researchReq,
			'UseRequirements':self.useReq,
			'Icon':self.iconentry,
			'Label':self.labelentry,
			'Race':self.race,
			'Researched':self.unused,
			'BroodwarOnly':self.broodwar,
		}

	def files_updated(self):
		self.dat = self.toplevel.technology
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.iconentry.get()
			if not i in ICON_CACHE:
				image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
				ICON_CACHE[i] = image
			else:
				image = ICON_CACHE[i]
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def updatetime(self, num, type):
		if type:
			self.time.check = False
			self.time.set(int(float(num) * 24))
		else:
			self.secs.check = False
			s = str(int(num) / 24.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			self.secs.set(s)

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		if not save and 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()

class UpgradesTab(DATTab):
	data = 'Upgrades.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.iconentry = IntegerVar(0, [0,389], callback=lambda n: self.selicon(n,1))
		self.icondd = IntVar()
		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.labeldd = IntVar()
		self.item = None

		l = LabelFrame(frame, text='Upgrade Display:')
		s = Frame(l)
		ls = Frame(s)
		
		f = Frame(ls)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Upgrade Icon', 'UpgIcon')
		f.pack(fill=X)
		
		f = Frame(ls)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.labeldd, stattxt, self.labelentry, width=30)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Upgrade Label', 'UpgLabel')
		f.pack(fill=X)
		ls.pack(side=LEFT, fill=X)
		
		ls = Frame(s, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.baseminerals = IntegerVar(0, [0,65535])
		self.basevespene = IntegerVar(0, [0,65535])
		self.basetime = IntegerVar(24, [1,65535], callback=lambda n,b=0,i=0: self.updatetime(n,b,i))
		self.basesecs = FloatVar(1, [0.0416,2730.625], callback=lambda n,b=0,i=1: self.updatetime(n,b,i), precision=4)

		m = Frame(frame)
		l = LabelFrame(m, text='Base Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.baseminerals, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Base Mineral Cost', 'UpgMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basevespene, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Base Vespene Cost', 'UpgVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.basetime, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.basesecs, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		tip(f, 'Base Build Time', 'UpgTime')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.factorminerals = IntegerVar(0, [0,65535])
		self.factorvespene = IntegerVar(0, [0,65535])
		self.factortime = IntegerVar(24, [1,65535], callback=lambda n,b=1,i=0: self.updatetime(n,b,i))
		self.factorsecs = FloatVar(1, [0.0416,2730.625], callback=lambda n,b=1,i=1: self.updatetime(n,b,i), precision=4)

		l = LabelFrame(m, text='Factor Cost:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Minerals:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorminerals, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Mineral Cost Factor', 'UpgFactorMinerals')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Vespene:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factorvespene, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Vespene Cost Factor', 'UpgFactorVespene')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Time:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.factortime, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.factorsecs, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		tip(f, 'Build Time Factor', 'UpgFactorTime')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)
		m.pack(fill=X)

		self.maxrepeats = IntegerVar(0, [0,255])
		self.reqIndex = IntegerVar(0, [0,65535])
		self.race = IntVar()
		self.broodwar = IntVar()

		m = Frame(frame)
		l = LabelFrame(m, text='Image:')
		s = Frame(l)
		
		f = Frame(s)
		Label(f, text='Max Repeats:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.maxrepeats, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Max Repeats', 'UpgRepeats')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='ReqIndex:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.reqIndex, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Requirements Index', 'UpgReq')
		f.pack(fill=X)
		
		f = Frame(s)
		Label(f, text='Race:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.race, DATA_CACHE['Races.txt'], width=10).pack(side=LEFT, fill=X, expand=1)
		tip(f, 'Race', 'UpgRace')
		f.pack(fill=X)
		
		makeCheckbox(s, self.broodwar, 'BroodWar', 'UpgIsBW').pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		m.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['ArmorUpgrade']),
			('weapons.dat', ['DamageUpgrade']),
		]
		self.setuplistbox()

		self.values = {
			'MineralCostBase':self.baseminerals,
			'MineralCostFactor':self.factorminerals,
			'VespeneCostBase':self.basevespene,
			'VespeneCostFactor':self.factorvespene,
			'ResearchTimeBase':self.basetime,
			'ResearchTimeFactor':self.factortime,
			'Requirements':self.reqIndex,
			'Icon':self.iconentry,
			'Label':self.labelentry,
			'Race':self.race,
			'MaxRepeats':self.maxrepeats,
			'BroodwarOnly':self.broodwar,
		}

	def files_updated(self):
		self.dat = self.toplevel.upgrades
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.iconentry.get()
			if not i in ICON_CACHE:
				image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
				ICON_CACHE[i] = image
			else:
				image = ICON_CACHE[i]
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def updatetime(self, num, factor, type):
		if type:
			x = [self.basetime,self.factortime][factor]
			x.check = False
			x.set(int(float(num) * 24))
		else:
			x = [self.basesecs,self.factorsecs][factor]
			x.check = False
			s = str(int(num) / 24.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			x.set(s)

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		if not save and 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()

class ImagesTab(DATTab):
	data = 'Images.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		grps = [] # ['None'] + [decompile_string(s) for s in self.toplevel.imagestbl.strings]
		self.grpentry = IntegerVar(0, [0, len(grps)-1])
		self.grpdd = IntVar()
		iscripts = DATA_CACHE['IscriptIDList.txt']
		self.iscriptentry = IntegerVar(0, [0, len(iscripts)-1])
		self.iscriptdd = IntVar()

		l = LabelFrame(frame, text='Image:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='GRP:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.grpentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.grps = DropDown(f, self.grpdd, grps, self.grpentry, width=30)
		self.grps.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Check', command=lambda v=self.grpdd,c=[('images.dat',['GRPFile'])]: self.checkreference(v,c)).pack(side=LEFT, padx=2)
		tip(f, 'GRP File', 'ImgGRP')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Iscript ID:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iscriptentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.iscripts = DropDown(f, self.iscriptdd, iscripts, self.iscriptentry, width=30)
		self.iscripts.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Check', command=lambda v=self.iscriptdd,c=[('images.dat',['IscriptID'])]: self.checkreference(v,c)).pack(side=LEFT, padx=2)
		tip(f, 'Iscript ID', 'ImgIscriptID')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.graphicsturns = IntVar()
		self.drawifcloaked = IntVar()
		self.clickable = IntVar()
		self.usefulliscript = IntVar()

		p = Frame(frame)
		l = LabelFrame(p, text='General Properties:')
		s = Frame(l)
		ls = Frame(s)
		f = Frame(ls)
		Checkbutton(f, text='Graphics Turns', variable=self.graphicsturns).pack(side=LEFT)
		tip(f, 'Graphics Turns', 'ImgGfxTurns')
		f.pack(fill=X)
		f = Frame(ls)
		Checkbutton(f, text='Draw If Cloaked', variable=self.drawifcloaked).pack(side=LEFT)
		tip(f, 'Draw If Cloaked', 'ImgDrawCloaked')
		f.pack(fill=X)
		ls.pack(side=LEFT)
		ls = Frame(s)
		f = Frame(ls)
		Checkbutton(f, text='Clickable', variable=self.clickable).pack(side=LEFT)
		tip(f, 'Clickable', 'ImgClickable')
		f.pack(fill=X)
		f = Frame(ls)
		Checkbutton(f, text='Use Full Iscript', variable=self.usefulliscript).pack(side=LEFT)
		tip(f, 'Use Full Iscript', 'ImgUseFullIscript')
		f.pack(fill=X)
		ls.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)

		self.functionentry = IntegerVar(0, [0,17])
		self.functiondd = IntVar()
		self.remapentry = IntegerVar(0, [0,9])
		self.remapdd = IntVar()

		l = LabelFrame(p, text='Drawing Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Function:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.functionentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.functiondd, DATA_CACHE['DrawList.txt'], self.functionentry, width=15).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Drawing Function', 'ImgDrawFunction')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Remapping:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.remapentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.remapdd, DATA_CACHE['Remapping.txt'], self.remapentry, width=15).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Remapping', 'ImgRemap')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X)
		p.pack(fill=X)

		self.attackentry = IntegerVar(0, [0, 929])
		self.attackdd = IntVar()
		self.damageentry = IntegerVar(0, [0, 929])
		self.damagedd = IntVar()
		self.specialentry = IntegerVar(0, [0, 929])
		self.specialdd = IntVar()
		self.landingentry = IntegerVar(0, [0, 929])
		self.landingdd = IntVar()
		self.liftoffentry = IntegerVar(0, [0, 929])
		self.liftoffdd = IntVar()
		self.shieldentry = IntegerVar(0, [0, 929])
		self.shielddd = IntVar()
		self.shieldsizes = IntVar()

		ols = [
			('Attack', self.attackentry, self.attackdd, 'OL1'),
			('Damage', self.damageentry, self.damagedd, 'OL2'),
			('Special', self.specialentry, self.specialdd, 'OL3'),
			('Landing Dust', self.landingentry, self.landingdd, 'OL4'),
			('Lift-Off Dust', self.liftoffentry, self.liftoffdd, 'OL5'),
			('Shield', self.shieldentry, self.shielddd, 'Shield'),
		]
		l = LabelFrame(frame, text='Extra Overlay Placements:')
		s = Frame(l)
		for t,e,d,h in ols:
			f = Frame(s)
			Label(f, text=t + ':', width=12, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=e, font=couriernew, width=3).pack(side=LEFT, padx=2)
			Label(f, text='=').pack(side=LEFT)
			DropDown(f, d, grps, e, width=15).pack(side=LEFT, fill=X, expand=1, padx=2)
			tip(f, t + ' Overlay', 'Img' + h)
			f.pack(fill=X)
		f = Frame(s)
		Label(f, text='', width=12).pack(side=LEFT)
		self.sizedd = DropDown(f, self.shieldsizes, DATA_CACHE['ShieldSize.txt'], self.shieldupdate, width=6)
		self.sizedd.pack(side=LEFT, padx=2)
		tip(f, 'Shield Overlay', 'ImgShield')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['ConstructionAnimation']),
			('sprites.dat', ['ImageFile']),
		]
		self.setuplistbox()

		self.values = {
			'GRPFile':self.grpentry,
			'GfxTurns':self.graphicsturns,
			'Clickable':self.clickable,
			'UseFullIscript':self.usefulliscript,
			'DrawIfCloaked':self.drawifcloaked,
			'DrawFunction':self.functionentry,
			'Remapping':self.remapentry,
			'IscriptID':self.iscriptentry,
			'ShieldOverlay':self.shieldentry,
			'AttackOverlay':self.attackentry,
			'DamageOverlay':self.damageentry,
			'SpecialOverlay':self.specialentry,
			'LandingDustOverlay':self.landingentry,
			'LiftOffDustOverlay':self.liftoffentry,
		}

	def files_updated(self):
		self.dat = self.toplevel.images
		entries = []
		last = -1
		for id in self.toplevel.iscriptbin.headers.keys():
			if id-last > 1:
				entries.extend(['*Unused*'] * (id-last-1))
			if id in self.toplevel.iscriptbin.extrainfo:
				n = self.toplevel.iscriptbin.extrainfo[id]
			elif id < len(DAT.DATA_CACHE['IscriptIDList.txt']):
				n = DAT.DATA_CACHE['IscriptIDList.txt'][id]
			else:
				n = 'Unnamed Custom Entry'
			entries.append(n)
			last = id
		self.iscripts.setentries(entries)
		self.iscriptentry.range[1] = len(entries)-1
		self.iscriptentry.editvalue()

		grps = ['None'] + [decompile_string(s) for s in self.toplevel.imagestbl.strings]
		self.grps.setentries(grps)
		self.grpentry.range[1] = len(grps)-1
		self.grpentry.editvalue()

	def shieldupdate(self, n):
		self.shieldentry.set([0,133,2,184][n])
		self.sizedd.focus_set()

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		shield,sizes = self.shieldentry.get(),[0,133,2,184],
		if shield in sizes:
			self.shieldsizes.set(sizes.index(shield))

	# def checkreferences(self, t, v):
		# self.listbox.delete(0,END)
		# val = v.get()
		# for id in range(self.dat.count):
			# if self.dat.get_value(id, ['GRPFile','IscriptID'][t]) == val:
				# self.listbox.insert(END, 'images.dat entry %s: %s' % (id,DATA_CACHE['Images.txt'][id]))

class SpritesTab(DATTab):
	data = 'Sprites.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.imageentry = IntegerVar(0, [0,998])
		self.imagedd = IntVar()
		self.visible = IntVar()
		self.unknown = IntVar()
		self.selcircleentry = IntegerVar(0, [0,19], callback=lambda n: self.selcircle(n,1))
		self.selcircledd = IntVar()
		self.healthbar = IntegerVar(0, [0,255], callback=lambda n,i=0: self.updatehealth(n,i))
		self.boxes = IntegerVar(1, [1,84], callback=lambda n,i=1: self.updatehealth(n,i))
		self.vertpos = IntegerVar(0, [0,255])

		l = LabelFrame(frame, text='Sprite Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Image:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.imageentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.imagedd, DATA_CACHE['Images.txt'], self.imageentry, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Images',i=self.imagedd: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Image', 'SpriteImage')
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Is Visible', variable=self.visible)
		tip(c, 'Is Visible', 'SpriteVisible')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Unknown', variable=self.unknown)
		tip(c, 'Unknown', 'SpriteUnk1')
		c.pack(side=LEFT)
		f.pack()
		f = Frame(s)
		Label(f, text='Sel. Circle:', width=12, anchor=E).pack(side=LEFT)
		self.selentry = Entry(f, textvariable=self.selcircleentry, font=couriernew, width=3)
		self.selentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.seldd = DropDown(f, self.selcircledd, DATA_CACHE['SelCircleSize.txt'], self.selcircle, width=30)
		self.seldd.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Images',i=self.selcircledd,o=561: self.jump(t,i,o)).pack(side=LEFT, padx=2)
		tip(f, 'Selection Circle', 'SpriteSelCircle')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Health Bar:', width=12, anchor=E).pack(side=LEFT)
		self.hpentry = Entry(f, textvariable=self.healthbar, font=couriernew, width=3)
		self.hpentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.hpboxes = Entry(f, textvariable=self.boxes, font=couriernew, width=2)
		self.hpboxes.pack(side=LEFT, padx=2)
		Label(f, text='boxes').pack(side=LEFT)
		tip(f, 'Health Bar', 'SpriteHPBar')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vert. Position:', width=12, anchor=E).pack(side=LEFT)
		self.vertentry = Entry(f, textvariable=self.vertpos, font=couriernew, width=3)
		self.vertentry.pack(side=LEFT, padx=2)
		tip(f, 'Vertical Position', 'SpriteCircleOff')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.previewing = None
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.settings.get('spritepreview',1))

		x = Frame(frame)
		l = LabelFrame(x, text='Preview:')
		s = Frame(l)
		self.preview = Canvas(s, width=257, height=257, background='#000000')
		self.preview.pack()
		Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack()
		s.pack()
		l.pack(side=LEFT)
		x.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('flingy.dat', ['Sprite']),
		]
		self.setuplistbox()

		self.values = {
			'ImageFile':self.imageentry,
			'HealthBar':self.healthbar,
			'Unknown':self.unknown,
			'IsVisible':self.visible,
			'SelectionCircleImage':self.selcircleentry,
			'SelectionCircleOffset':self.vertpos,
		}

	def files_updated(self):
		self.dat = self.toplevel.sprites

	def selcircle(self, n, t=0):
		if t:
			self.selcircledd.set(n)
		else:
			self.selcircleentry.set(n)
		self.drawpreview()

	def updatehealth(self, num, type):
		if type:
			self.healthbar.check = False
			self.healthbar.set((num + 1) * 3)
		else:
			self.boxes.check = False
			self.boxes.set(max(1,(num - 1) / 3))

	def drawpreview(self, e=None):
		if self.previewing != self.id or (self.previewing != None and not self.showpreview.get()) or (self.previewing == None and self.showpreview.get()):
			self.preview.delete(ALL)
			if self.showpreview.get():
				i = int(self.selentry.get())
				if self.selentry['state'] == NORMAL:
					image_id = 561 + i
					g = self.toplevel.images.get_value(image_id,'GRPFile')
					if g:
						f = self.toplevel.imagestbl.strings[g-1][:-1]
						image = self.toplevel.grp('Units','unit\\' + f, rle_outline, OUTLINE_SELF)
						if image:
							y = 130+int(self.vertpos.get())
							self.preview.create_image(130, y, image=image[0])
							w = 3*int(self.boxes.get())
							hp = [130-(w/2),y+6+(image[4]-image[3])/2]
							self.preview.create_rectangle(hp[0], hp[1], hp[0]+w, hp[1]+4, fill='#000000')
							hp[0] += 1
							hp[1] += 1
							for n in range(int(self.boxes.get())):
								self.preview.create_rectangle(hp[0], hp[1], hp[0]+1, hp[1]+2, outline='#008000', fill='#008000')
								hp[0] += 3
				i = self.toplevel.sprites.get_value(self.id,'ImageFile')
				g = self.toplevel.images.get_value(i,'GRPFile')
				if g:
					f = self.toplevel.imagestbl.strings[g-1][:-1]
					if f.startswith('thingy\\tileset\\'):
						p = 'Terrain'
					else:
						p = 'Units'
						if self.toplevel.images.get_value(i, 'DrawFunction') == 9 and self.toplevel.images.get_value(i, 'Remapping') and self.toplevel.images.get_value(i, 'Remapping') < 4:
							p = ['o','b','g'][self.toplevel.images.get_value(i, 'Remapping')-1] + 'fire'
					sprite = self.toplevel.grp(p,'unit\\' + f)
					if sprite:
						self.preview.create_image(130, 130, image=sprite[0])
				self.previewing = i
			else:
				self.previewing = None

	def loadsave(self, save=False):
		if self.toplevel.sprites:
			if not save:
				id = self.id
				check = [
					('HealthBar', [self.hpentry,self.hpboxes]),
					('SelectionCircleImage', [self.selentry,self.seldd]),
					('SelectionCircleOffset', [self.vertentry])
				]
				for l,ws in check:
					frmt = self.toplevel.sprites.format[self.toplevel.sprites.labels.index(l)][0]
					state = [NORMAL,DISABLED][id < frmt[0] or id >= frmt[1]]
					for w in ws:
						w['state'] = state
			else:
				self.toplevel.settings['spritepreview'] = self.showpreview.get()
			DATTab.loadsave(self, save)
		if not save:
			self.drawpreview()

class FlingyTab(DATTab):
	data = 'Flingy.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.spriteentry = IntegerVar(0, [0,516])
		self.spritedd = IntVar()
		self.topspeed = IntegerVar(0, [0,4294967294], callback=lambda n,i=0: self.updatespeed(n,i))
		self.speed = FloatVar(1, [0,40265318.381], callback=lambda n,i=1: self.updatespeed(n,i), precision=3)
		self.acceleration = IntegerVar(0, [0,65535])
		self.haltdistance = IntegerVar(0, [0,4294967294], callback=lambda n,i=0: self.updatehalt(n,i))
		self.halt = FloatVar(1, [0,16777215.9921], callback=lambda n,i=1: self.updatehalt(n,i), precision=4)
		self.turnradius = IntegerVar(0, [0,255])
		self.movecontrol = IntVar()
		self.unused = IntegerVar(0, [0,255])

		l = LabelFrame(frame, text='Damage Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Sprite:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.spriteentry, font=couriernew, width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.spritedd, DATA_CACHE['Sprites.txt'], self.spriteentry, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Sprites',i=self.spritedd: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Sprite', 'FlingySprite')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Top Speed:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.topspeed, font=couriernew, width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.speed, font=couriernew, width=12).pack(side=LEFT, padx=2)
		Label(f, text='pixels/frame').pack(side=LEFT)
		tip(f, 'Top Speed', 'FlingySpeed')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Acceleration:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.acceleration, font=couriernew, width=10).pack(side=LEFT, padx=2)
		tip(f, 'Acceleration', 'FlingyAcceleration')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Halt Distance:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.haltdistance, font=couriernew, width=10).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.halt, font=couriernew, width=14).pack(side=LEFT, padx=2)
		Label(f, text='pixels').pack(side=LEFT)
		tip(f, 'Halt Distance', 'FlingyHaltDist')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Turn Radius:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.turnradius, font=couriernew, width=10).pack(side=LEFT, padx=2)
		tip(f, 'Turn Radius', 'FlingyTurnRad')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Move Control:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.movecontrol, DATA_CACHE['FlingyControl.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Move Control', 'FlingyMoveControl')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='IScript Mask:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.unused, font=couriernew, width=10).pack(side=LEFT, padx=2)
		tip(f, 'IScript Mask', 'FlingyUnused')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['Graphics']),
			('weapons.dat', ['Graphics']),
		]
		self.setuplistbox()

		self.values = {
			'Sprite':self.spriteentry,
			'Speed':self.topspeed,
			'Acceleration':self.acceleration,
			'HaltDistance':self.haltdistance,
			'TurnRadius':self.turnradius,
			'Unused':self.unused,
			'MovementControl':self.movecontrol,
		}

	def files_updated(self):
		self.dat = self.toplevel.flingy

	def updatespeed(self, num, type):
		if type:
			self.topspeed.check = False
			self.topspeed.set(int((float(num) * 320 / 3.0)))
		else:
			self.speed.check = False
			s = str(int(num) * 3 / 320.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 3:
				s = s[:s.index('.')+4]
			self.speed.set(s)

	def updatehalt(self, num, type):
		if type:
			self.haltdistance.check = False
			self.haltdistance.set(int((float(num) * 256)))
		else:
			self.halt.check = False
			s = str(int(num) / 256.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			self.halt.set(s)

class WeaponsTab(DATTab):
	data = 'Weapons.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.amount = IntegerVar(0, [0,65535])
		self.type = IntVar()
		self.bonus = IntegerVar(0, [0,65535])
		self.explosion = IntVar()
		self.factor = IntegerVar(0, [0,255])
		self.unused = IntVar()
		self.cooldown = IntegerVar(0, [1,255], callback=lambda n,i=0: self.updatetime(n,i))
		self.seconds = FloatVar(1, [0.06,17], callback=lambda n,i=1: self.updatetime(n,i), precision=2)
		self.upgradeentry = IntegerVar(0,[0,61])
		self.upgrade = IntVar()

		data = Frame(frame)
		left = Frame(data)
		l = LabelFrame(left, text='Damage Properties:')
		s = Frame(l)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Amount:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.amount, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(ls, 'Damage Amount', 'WeapDamageAmount')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Type:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.type, DATA_CACHE['DamTypes.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(ls, 'Damage Type', 'WeapDamageType')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Bonus:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.bonus, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(ls, 'Damage Bonus', 'WeapDamageBonus')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Explosion:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.explosion, DATA_CACHE['Explosions.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(ls, 'Explosion', 'WeapDamageExplosion')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		Label(ls, text='Factor:', width=12, anchor=E).pack(side=LEFT)
		Entry(ls, textvariable=self.factor, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(ls, 'Damage Factor', 'WeapDamageFactor')
		ls.pack(side=LEFT)
		ls = Frame(f)
		Label(ls, text='Unused:', width=9, anchor=E).pack(side=LEFT)
		DropDown(ls, self.unused, DATA_CACHE['Techdata.txt'], width=20).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(ls, 'Unused Technology', 'WeapUnused')
		ls.pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Cooldown:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.cooldown, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.seconds, font=couriernew, width=5).pack(side=LEFT, padx=2)
		Label(f, text='secs.').pack(side=LEFT)
		tip(f, 'Cooldown', 'WeapDamageCooldown')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Upgrade:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.upgradeentry, font=couriernew, width=2).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.upgrade, DATA_CACHE['Upgrades.txt'], self.upgradeentry, width=18).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Upgrades',i=self.upgrade: self.jump(t,i)).pack(side=LEFT)
		tip(f, 'Damage Upgrade', 'WeapDamageUpgrade')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		stattxt = [] # ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry = IntegerVar(0,[0,len(stattxt)-1])
		self.label = IntVar()
		self.errormsgentry = IntegerVar(0,[0,len(stattxt)-1])
		self.errormsg = IntVar()

		l = LabelFrame(left, text='Weapon Display:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Label:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.labelentry, font=couriernew, width=4).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.labels = DropDown(f, self.label, stattxt, self.labelentry, width=28)
		self.labels.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Label', 'WeapLabel')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Error Msg:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.errormsgentry, font=couriernew, width=4).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.errormsgs = DropDown(f, self.errormsg, stattxt, self.errormsgentry, width=28)
		self.errormsgs.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Error Message', 'WeapError')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.removeafter = IntegerVar(0, [0,255])
		self.behaviour = IntVar()
		self.graphicsentry = IntegerVar(0, [0,208])
		self.graphicsdd = IntVar()
		self.iconentry = IntegerVar(0, [0,389], callback=lambda n:self.selicon(n,1))
		self.icondd = IntVar()
		self.xoffset = IntegerVar(0, [0,255])
		self.yoffset = IntegerVar(0, [0,255])
		self.attackangle = IntegerVar(0, [0,255])
		self.launchspin = IntegerVar(0, [0,255])

		l = LabelFrame(left, text='Weapon Display:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Behaviour:', width=12, anchor=E).pack(side=LEFT)
		DropDown(f, self.behaviour, DATA_CACHE['Behaviours.txt'], width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Behaviour', 'WeapBehaviour')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Remove After:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.removeafter, font=couriernew, width=3).pack(side=LEFT, padx=2)
		tip(f, 'Remove After', 'WeapRemoveAfter')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Graphics:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.graphicsentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.graphicsdd, DATA_CACHE['Flingy.txt'], self.graphicsentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Flingy',i=self.graphicsdd: self.jump(t,i)).pack(side=LEFT, padx=2)
		tip(f, 'Graphics', 'WeapGraphics')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Icon:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.iconentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.icondd, DATA_CACHE['Icons.txt'], self.selicon).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Icon', 'WeapIcon')
		f.pack(fill=X)
		f = Frame(s)
		ls = Frame(f)
		rs = Frame(ls)
		Label(rs, text='X Offset:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.xoffset, font=couriernew, width=3).pack(side=LEFT, padx=2)
		tip(rs, 'X Offset', 'WeapOffsetForward')
		rs.pack(side=TOP)
		rs = Frame(ls)
		Label(rs, text='Y Offset:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.yoffset, font=couriernew, width=3).pack(side=LEFT, padx=2)
		tip(rs, 'Y Offset', 'WeapOffsetUpward')
		rs.pack(side=TOP)
		ls.pack(side=LEFT)
		ls = Frame(f)
		rs = Frame(ls)
		Label(rs, text='Attack Angle:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.attackangle, font=couriernew, width=3).pack(side=LEFT, padx=2)
		tip(rs, 'Attack Angle', 'WeapAttackAngle')
		rs.pack(side=TOP)
		rs = Frame(ls)
		Label(rs, text='Launch Spin:', width=12, anchor=E).pack(side=LEFT)
		Entry(rs, textvariable=self.launchspin, font=couriernew, width=3).pack(side=LEFT, padx=2)
		tip(rs, 'Launch Spin', 'WeapLaunchSpin')
		rs.pack(side=TOP)
		ls.pack(side=LEFT)
		ls = Frame(f, relief=SUNKEN, bd=1)
		self.preview = Canvas(ls, width=34, height=34, background='#000000')
		self.preview.pack()
		ls.pack(side=RIGHT)
		f.pack(fill=X)
		f = Frame(s)
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)
		left.pack(side=LEFT, fill=Y)

		self.minrange = IntegerVar(0, [0,4294967294])
		self.maxrange = IntegerVar(0, [0,4294967294])

		right = Frame(data)
		l = LabelFrame(right, text='Weapon Range:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Min:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minrange, font=couriernew, width=10).pack(side=LEFT, padx=2)
		tip(f, 'Minimum Range', 'WeapRangeMin')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.maxrange, font=couriernew, width=10).pack(side=LEFT, padx=2)
		tip(f, 'Maximum Range', 'WeapRangeMax')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack()

		self.innerradius = IntegerVar(0, [0,65535])
		self.mediumradius = IntegerVar(0, [0,65535])
		self.outerradius = IntegerVar(0, [0,65535])

		l = LabelFrame(right, text='Splash Radii:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Inner:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.innerradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(f, 'Inner Radius', 'WeapSplashInner')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Medium:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.mediumradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(f, 'Medium Radius', 'WeapSplashMed')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Outer:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.outerradius, font=couriernew, width=5).pack(side=LEFT, padx=2)
		tip(f, 'Outer Radius', 'WeapSplashOuter')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.air = IntVar()
		self.ground = IntVar()
		self.mechanical = IntVar()
		self.organic = IntVar()
		self.nonbuilding = IntVar()
		self.nonrobotic = IntVar()
		self.terrain = IntVar()
		self.orgormech = IntVar()
		self.own = IntVar()

		l = LabelFrame(right, text='Target Flags:')
		s = Frame(l)
		flags = [
			('Air', self.air, '001'),
			('Ground', self.ground, '002'),
			('Mechanical', self.mechanical, '004'),
			('Organic', self.organic, '008'),
			('Non-Building', self.nonbuilding, '010'),
			('Non-Robotic', self.nonrobotic, '020'),
			('Terrain', self.terrain, '040'),
			('Org. or Mech.', self.orgormech, '080'),
			('Own', self.own, '100'),
		]
		for t,v,h in flags:
			f = Frame(s)
			Checkbutton(f, text=t, variable=v).pack(side=LEFT)
			tip(f, t, 'WeapTarget' + h)
			f.pack(side=TOP, fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=BOTH)
		right.pack(side=LEFT)
		data.pack(pady=5)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('units.dat', ['GroundWeapon','AirWeapon']),
			('orders.dat', ['Targeting']),
		]
		self.setuplistbox()

		self.values = {
			'Label':self.label,
			'Graphics':self.graphicsentry,
			'Unused':self.unused,
			'TargetFlags':[self.air, self.ground, self.mechanical, self.organic, self.nonbuilding, self.nonrobotic, self.terrain, self.orgormech, self.own],
			'MinimumRange':self.minrange,
			'MaximumRange':self.maxrange,
			'DamageUpgrade':self.upgrade,
			'WeaponType':self.type,
			'WeaponBehavior':self.behaviour,
			'RemoveAfter':self.removeafter,
			'ExplosionType':self.explosion,
			'InnerSplashRange':self.innerradius,
			'MediumSplashRange':self.mediumradius,
			'OuterSplashRange':self.outerradius,
			'DamageAmount':self.amount,
			'DamageBonus':self.bonus,
			'WeaponCooldown':self.cooldown,
			'DamageFactor':self.factor,
			'AttackAngle':self.attackangle,
			'LaunchSpin':self.launchspin,
			'ForwardOffset':self.xoffset,
			'UpwardOffset':self.yoffset,
			'TargetErrorMessage':self.errormsg,
			'Icon':self.iconentry
		}

	def files_updated(self):
		self.dat = self.toplevel.weapons
		stattxt = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings]
		self.labelentry.range[1] = len(stattxt)-1
		self.labels.setentries(stattxt)
		self.labelentry.editvalue()
		self.errormsgentry.range[1] = len(stattxt)-1
		self.errormsgs.setentries(stattxt)
		self.errormsgentry.editvalue()

	def updatetime(self, num, type):
		if type:
			self.cooldown.check = False
			self.cooldown.set(int(float(num) * 15))
		else:
			self.seconds.check = False
			s = str(int(num) / 15.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 2:
				s = s[:s.index('.')+3]
			self.seconds.set(s)

	def selicon(self, n, t=0):
		if t:
			self.icondd.set(n)
		else:
			self.iconentry.set(n)
		self.drawpreview()

	def drawpreview(self):
		self.preview.delete(ALL)
		if 'Icons' in PALETTES and self.toplevel.cmdicon:
			i = self.iconentry.get()
			if not i in ICON_CACHE:
				image = frame_to_photo(PALETTES['Icons'], self.toplevel.cmdicon, i, True)
				ICON_CACHE[i] = image
			else:
				image = ICON_CACHE[i]
			self.preview.create_image(19-image[1]/2+(image[0].width()-image[2])/2, 19-image[3]/2+(image[0].height()-image[4])/2, image=image[0])

	def loadsave(self, save=False):
		DATTab.loadsave(self, save)
		if not save and 'Icons' in PALETTES and self.toplevel.cmdicon:
			self.drawpreview()

class AIActionsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.computeridleentry = IntegerVar(0,[0,189])
		self.computeridle = IntVar()
		self.humanidleentry = IntegerVar(0,[0,189])
		self.humanidle = IntVar()
		self.returntoidleentry = IntegerVar(0,[0,189])
		self.returntoidle = IntVar()
		self.attackunitentry = IntegerVar(0,[0,189])
		self.attackunit = IntVar()
		self.attackmoveentry = IntegerVar(0,[0,189])
		self.attackmove = IntVar()
		self.rightclick = IntVar()
		self.AI_NoSuicide = IntVar()
		self.AI_NoGuard = IntVar()

		ais = [
			('Computer Idle', self.computeridleentry, self.computeridle, 'UnitAICompIdle'),
			('Human Idle', self.humanidleentry, self.humanidle, 'UnitAIHumanIdle'),
			('Return to Idle', self.returntoidleentry, self.returntoidle, 'UnitAIReturn'),
			('Attack Unit', self.attackunitentry, self.attackunit, 'UnitAIAttackUnit'),
			('Attack Move', self.attackmoveentry, self.attackmove, 'UnitAIAttackMove'),
		]
		l = LabelFrame(frame, text='Sounds:')
		s = Frame(l)
		for t,e,d,h in ais:
			f = Frame(s)
			Label(f, text=t + ':', width=16, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=e, font=couriernew, width=3).pack(side=LEFT)
			Label(f, text='=').pack(side=LEFT)
			DropDown(f, d, DATA_CACHE['Orders.txt'], e, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
			Button(f, text='Jump ->', command=lambda t='Orders',i=d: self.jump(t,i)).pack(side=LEFT)
			tip(f, t, h)
			f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Right-Click Action:', width=16, anchor=E).pack(side=LEFT)
		DropDown(f, self.rightclick, DATA_CACHE['Rightclick.txt'], width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Right-Click Action', 'UnitAIRightClick')
		f.pack(fill=X, pady=5)

		f = Frame(s)
		# AI Flags
		makeCheckbox(f, self.AI_NoSuicide, 'Ignore Strategic Suicide missions', 'UnitAINoSuicide').pack(side=LEFT)
		makeCheckbox(f, self.AI_NoGuard, 'Don\'t become a guard', 'UnitAINoGuard').pack(side=LEFT)
		
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'CompAIIdle':self.computeridle,
			'HumanAIIdle':self.humanidle,
			'ReturntoIdle':self.returntoidle,
			'AttackUnit':self.attackunit,
			'AttackMove':self.attackmove,
			'AIInternal':[self.AI_NoSuicide,self.AI_NoGuard,None,None,None,None,None,None],
			'RightClickAction':self.rightclick,
		}
		
	def loadsave(self, save=False):
		if self.toplevel.units:
			id = self.parent.parent.id
			if save:
				r = (1 * self.AI_NoSuicide.get() + 2 * self.AI_NoGuard.get())
				if self.toplevel.units.get_value(id,'AIInternal') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'AIInternal', r)
			else:
				self.AI_NoSuicide.set( self.toplevel.units.get_value(id,'AIInternal') & 1 == 1)
				self.AI_NoGuard.set( self.toplevel.units.get_value(id,'AIInternal') & 2 == 2)
		DATUnitsTab.loadsave(self, save)


class StarEditUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.nonneutral = IntVar()
		self.unitlisting = IntVar()
		self.missionbriefing = IntVar()
		self.playersettings = IntVar()
		self.allraces = IntVar()
		self.setdoodadstate = IntVar()
		self.nonlocationtriggers = IntVar()
		self.unitherosettings = IntVar()
		self.locationtriggers = IntVar()
		self.broodwaronly = IntVar()
		self.men = IntVar()
		self.building = IntVar()
		self.factory = IntVar()
		self.independent = IntVar()
		self.neutral = IntVar()

		flags = [
			(
				'Availability',
				[
					[
						('Non-Neutral', self.nonneutral, 'UnitSENonNeutral'),
						('Unit Listing&Palette', self.unitlisting, 'UnitSEListing'),
						('Mission Briefing', self.missionbriefing, 'UnitSEBriefing'),
						('Player Settings', self.playersettings, 'UnitSEPlayerSet'),
						('All Races', self.allraces, 'UnitSEAllRaces'),
						('Set Doodad State', self.setdoodadstate, 'UnitSEDoodadState'),
						('Non-Location Triggers', self.nonlocationtriggers, 'UnitSENonLoc'),
						('Unit&Hero Settings', self.unitherosettings, 'UnitSEUnitHero'),
					],[
						('Location Triggers', self.locationtriggers, 'UnitSELoc'),
						('BroodWar Only', self.broodwaronly, 'UnitSEBW'),
					],
				],
			),(
				'Group',
				[
					[
						('Men', self.men, 'UnitSEGroupMen'),
						('Building', self.building, 'UnitSEGroupBuilding'),
						('Factory', self.factory, 'UnitSEGroupFactory'),
						('Independent', self.independent, 'UnitSEGroupInd'),
						('Neutral', self.neutral, 'UnitSEGroupNeutral'),
					],
				],
			)
		]
		top = Frame(frame)
		for lt,lf in flags:
			l = LabelFrame(top, text=lt + ' Flags:')
			s = Frame(l)
			for c in lf:
				cc = Frame(s, width=20)
				for t,v,h in c:
					f = Frame(cc)
					makeCheckbox(f, v, t, h).pack(side=LEFT)
					f.pack(fill=X)
				cc.pack(side=LEFT, fill=Y)
			s.pack(fill=BOTH, padx=5, pady=5)
			l.pack(side=LEFT, fill=BOTH)
		top.pack()

		r = 0 # min(255,len(self.toplevel.stat_txt.strings)-1302)
		ranks = [] # ['No Sublabel'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings[1302:1302+r]]
		self.rankentry = IntegerVar(0, [0,r])
		self.rankdd = IntVar()
		self.mapstring = IntegerVar(0, [0,65535])

		l = LabelFrame(frame, text='String Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Rank/Sublabel:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.rankentry, font=couriernew, width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.ranks = DropDown(f, self.rankdd, ranks, self.rankentry)
		self.ranks.pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Rank/Sublabel', 'UnitRank')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Map String:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.mapstring, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Map String', 'UnitMapString')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.width = IntegerVar(0, [0,65535])
		self.height = IntegerVar(0, [0,65535])

		bottom = Frame(frame)
		l = LabelFrame(bottom, text='Placement Box (Pixels):')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Width:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.width, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Placement Width', 'UnitSEPlaceWidth')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Height:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.height, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Placement Height', 'UnitSEPlaceHeight')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT)
		bottom.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'Sublabel':self.rankentry,
			'UnitMapString':self.mapstring,
			'StarEditPlacementBoxWidth':self.width,
			'StarEditPlacementBoxHeight':self.height,
			'StarEditGroupFlags':[None,None,None,self.men,self.building,self.factory,self.independent,self.neutral],
			'StarEditAvailabilityFlags':[self.nonneutral,self.unitlisting,self.missionbriefing,self.playersettings,self.allraces,self.setdoodadstate,self.nonlocationtriggers,self.unitherosettings,self.locationtriggers,self.broodwaronly,None,None,None,None,None,None],
		}

	def files_updated(self):
		r = min(255,len(self.toplevel.stat_txt.strings)-1302)
		ranks = ['No Sublabel'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings[1302:1302+r]]
		self.rankentry.range[1] = len(ranks)-1
		self.ranks.setentries(ranks)
		self.rankentry.editvalue()

	def loadsave(self, save=False):
		if self.toplevel.units:
			id = self.parent.parent.id
			if save:
				r = (self.toplevel.units.get_value(id,'StarEditGroupFlags') & 7) | (8*self.men.get() + 16*self.building.get() + 32*self.factory.get() + 64*self.independent.get() + 128*self.neutral.get())
				if self.toplevel.units.get_value(id,'StarEditGroupFlags') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'StarEditGroupFlags',r)
				r = 1*self.nonneutral.get() + 2*self.unitlisting.get() + 4*self.missionbriefing.get() + 8*self.playersettings.get() + 16*self.allraces.get() + 32*self.setdoodadstate.get() + 64*self.nonlocationtriggers.get() + 128*self.unitherosettings.get() + 256*self.locationtriggers.get() + 512*self.broodwaronly.get()
				if self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'StarEditAvailabilityFlags',r)
			else:
				#Staredit Group Flags
				self.men.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 8 == 8)
				self.building.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 16 == 16)
				self.factory.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 32 == 32)
				self.independent.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 64 == 64)
				self.neutral.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 128 == 128)
				#Staredit Availability Flags
				self.nonneutral.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 1 == 1)
				self.unitlisting.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 2 == 2)
				self.missionbriefing.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 4 == 4)
				self.playersettings.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 8 == 8)
				self.allraces.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 16 == 16)
				self.setdoodadstate.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 32 == 32)
				self.nonlocationtriggers.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 64 == 64)
				self.unitherosettings.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 128 == 128)
				self.locationtriggers.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 256 == 256)
				self.broodwaronly.set(self.toplevel.units.get_value(id,'StarEditAvailabilityFlags') & 512 == 512)
		DATUnitsTab.loadsave(self, save)
	
class GraphicsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.graphicsentry = IntegerVar(0, [0,208])
		self.graphicsdd = IntVar()
		self.constructionentry = IntegerVar(0, [0,998])
		self.constructiondd = IntVar()
		self.idleportraitentry = IntegerVar(0, [0,220])
		self.idleportraitdd = IntVar()
		self.elevationentry = IntegerVar(0, [0,19])
		self.elevationdd = IntVar()
		self.direction = IntegerVar(0, [0,255])

		gfx = [
			('Graphics', self.graphicsentry, self.graphicsdd, 'Flingy.txt', 'UnitGfx'),
			('Construction', self.constructionentry, self.constructiondd, 'Images.txt', 'UnitConstruction'),
			('Idle Portrait', self.idleportraitentry, self.idleportraitdd, 'Portdata.txt', 'UnitPortrait'),
			('Elevation', self.elevationentry, self.elevationdd, 'ElevationLevels.txt', 'UnitElevationLevel'),
		]
		l = LabelFrame(frame, text='Sounds:')
		s = Frame(l)
		for t,e,d,q,h in gfx:
			f = Frame(s)
			Label(f, text=t + ':', width=13, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=e, font=couriernew, width=3).pack(side=LEFT)
			Label(f, text='=').pack(side=LEFT)
			DropDown(f, d, DATA_CACHE[q], e, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
			if t != 'Elevation':
				Button(f, text='Jump ->', command=lambda t=q.split('.')[0],i=d: self.jump(t,i)).pack(side=LEFT)
			tip(f, t, h)
			f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Direction:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.direction, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Direction', 'UnitDirection')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.left = IntegerVar(0, [0,65535])
		self.right = IntegerVar(0, [0,65535])
		self.up = IntegerVar(0, [0,65535])
		self.down = IntegerVar(0, [0,65535])
		self.horizontal = IntegerVar(0, [0,65535])
		self.vertical = IntegerVar(0, [0,65535])
		self.previewing = None
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.settings.get('unitpreview',1))
		self.showplace = IntVar()
		self.showplace.set(self.toplevel.settings.get('showplacement',1))
		self.showdims = IntVar()
		self.showdims.set(self.toplevel.settings.get('showdimensions',1))

		bottom = Frame(frame)
		left = Frame(bottom)
		l = LabelFrame(left, text='Unit Dimensions:')
		s = Frame(l)
		dims = [
			('Left', self.left),
			('Right', self.right),
			('Up', self.up),
			('Down', self.down),
		]
		for t,v in dims:
			f = Frame(s)
			Label(f, text='%s:' % t, width=13, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=v, font=couriernew, width=5).pack(side=LEFT)
			tip(f, t + ' Dimension', 'UnitDim' + t)
			f.pack(fill=X)
		s.pack(padx=5, pady=5)
		l.pack(side=TOP, fill=X)
		l = LabelFrame(left, text='Addon Position:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Horizontal:', width=13, anchor=E).pack(side=LEFT)
		self.horizontalw = Entry(f, textvariable=self.horizontal, font=couriernew, width=5)
		self.horizontalw.pack(side=LEFT)
		tip(f, 'Addons Horizontal Position', 'UnitAddPosX')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vertical:', width=13, anchor=E).pack(side=LEFT)
		self.verticalw = Entry(f, textvariable=self.vertical, font=couriernew, width=5)
		self.verticalw.pack(side=LEFT)
		tip(f, 'Addons Vertical Position', 'UnitAddPosY')
		f.pack(fill=X)
		s.pack(padx=5, pady=5)
		l.pack(side=TOP, fill=X)
		left.pack(side=LEFT, fill=BOTH, expand=1)
		l = LabelFrame(bottom, text='Preview:')
		s = Frame(l)
		self.preview = Canvas(s, width=257, height=257, background='#000000')
		self.preview.pack()
		self.preview.create_rectangle(0, 0, 0, 0, outline='#00FF00', tags='size')
		self.preview.create_rectangle(0, 0, 0, 0, outline='#FF0000', tags='place')
		Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack()
		o = Frame(s)
		Checkbutton(o, text='Show Placement Box (Red)', variable=self.showplace, command=self.drawboxes).pack(side=LEFT)
		Checkbutton(o, text='Show Dimensions Box (Green)', variable=self.showdims, command=self.drawboxes).pack(side=LEFT)
		o.pack()
		s.pack()
		l.pack()
		bottom.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'Graphics':self.graphicsentry,
			'ConstructionAnimation':self.constructionentry,
			'UnitDirection':self.direction,
			'ElevationLevel':self.elevationentry,
			'UnitSizeLeft':self.left,
			'UnitSizeUp':self.up,
			'UnitSizeRight':self.right,
			'UnitSizeDown':self.down,
			'AddonHorizontal':self.horizontal,
			'AddonVertical':self.vertical,
			'Portrait':self.idleportraitentry,
		}

	def drawboxes(self):
		id = self.parent.parent.id
		if self.showpreview.get() and self.showplace.get():
			w,h = self.toplevel.units.get_value(id, 'StarEditPlacementBoxWidth') / 2,self.toplevel.units.get_value(id, 'StarEditPlacementBoxHeight') / 2
			self.preview.coords('place', 129-w, 129-h, 129+w, 129+h)
			self.preview.lift('place')
		else:
			self.preview.coords('place', 0, 0, 0, 0)
		if self.showpreview.get() and self.showdims.get():
			self.preview.coords('size', 129-self.toplevel.units.get_value(id, 'UnitSizeLeft'), 129-self.toplevel.units.get_value(id, 'UnitSizeUp'), 129+self.toplevel.units.get_value(id, 'UnitSizeRight'), 129+self.toplevel.units.get_value(id, 'UnitSizeDown'))
			self.preview.lift('size')
		else:
			self.preview.coords('size', 0, 0, 0 ,0)

	def drawpreview(self):
		id = self.parent.parent.id
		if self.previewing != id or (self.previewing != None and not self.showpreview.get()) or (self.previewing == None and self.showpreview.get()):
			self.preview.delete('unit')
			if self.showpreview.get():
				i = self.toplevel.sprites.get_value(self.toplevel.flingy.get_value(self.toplevel.units.get_value(id, 'Graphics'), 'Sprite'),'ImageFile')
				g = self.toplevel.images.get_value(i,'GRPFile')
				if g:
					f = self.toplevel.imagestbl.strings[g-1][:-1]
					if f.startswith('thingy\\tileset\\'):
						p = 'Terrain'
					else:
						p = 'Units'
						if self.toplevel.images.get_value(i, 'DrawFunction') == 9 and self.toplevel.images.get_value(i, 'Remapping') and self.toplevel.images.get_value(i, 'Remapping') < 4:
							p = ['o','b','g'][self.toplevel.images.get_value(i, 'Remapping')-1] + 'fire'
					sprite = self.toplevel.grp(p,'unit\\' + f)
					if sprite:
						self.preview.create_image(130, 130, image=sprite[0], tags='unit')
				self.previewing = id
			else:
				self.previewing = None
			self.drawboxes()

	def loadsave(self, save=False):
		if self.toplevel.units:
			if not save:
				id = self.parent.parent.id
				restricted = [
					('AddonHorizontal',self.horizontalw),
					('AddonVertical',self.verticalw),
				]
				for l,w in restricted:
					frmt = self.toplevel.units.format[self.toplevel.units.labels.index(l)]
					w['state'] = [NORMAL,DISABLED][id < frmt[0][0] or id >= frmt[0][1]]
			else:
				self.toplevel.settings['unitpreview'] = self.showpreview.get()
				self.toplevel.settings['showplacment'] = self.showplace.get()
				self.toplevel.settings['showdimensions'] = self.showdims.get()
			DATUnitsTab.loadsave(self, save)
		if not save:
			self.drawpreview()

class SoundsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		sfxdata = DATA_CACHE['Sfxdata.txt']
		# if self.toplevel.settings.get('customlabels',0):
		# 	sfxdata = ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		self.readyentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.readydd = IntVar()
		self.firstyesentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.firstyesdd = IntVar()
		self.lastyesentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.lastyesdd = IntVar()
		self.firstwhatentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.firstwhatdd = IntVar()
		self.lastwhatentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.lastwhatdd = IntVar()
		self.firstannoyedentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.firstannoyeddd = IntVar()
		self.lastannoyedentry = IntegerVar(0, [0,len(sfxdata)-1])
		self.lastannoyeddd = IntVar()

		l = LabelFrame(frame, text='Sounds:')
		s = Frame(l)

		f = Frame(s)
		Label(f, text='Ready:', width=13, anchor=E).pack(side=LEFT)
		self.readyentryw = Entry(f, textvariable=self.readyentry, font=couriernew, width=4)
		self.readyentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.readyddw = DropDown(f, self.readydd, sfxdata, self.readyentry, width=30)
		self.readyddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.readybtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.readydd: self.jump(t,i))
		self.readybtnw.pack(side=LEFT)
		tip(f, 'Ready', 'UnitSndReady')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Yes (First):', width=13, anchor=E).pack(side=LEFT)
		self.firstyesentryw = Entry(f, textvariable=self.firstyesentry, font=couriernew, width=4)
		self.firstyesentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.firstyesddw = DropDown(f, self.firstyesdd, sfxdata, self.firstyesentry, width=30)
		self.firstyesddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.firstyesbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.firstyesdd: self.jump(t,i))
		self.firstyesbtnw.pack(side=LEFT)
		tip(f, 'Yes (First)', 'UnitSndYesStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Yes (Last):', width=13, anchor=E).pack(side=LEFT)
		self.lastyesentryw = Entry(f, textvariable=self.lastyesentry, font=couriernew, width=4)
		self.lastyesentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.lastyesddw = DropDown(f, self.lastyesdd, sfxdata, self.lastyesentry, width=30)
		self.lastyesddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.lastyesbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.lastyesdd: self.jump(t,i))
		self.lastyesbtnw.pack(side=LEFT)
		tip(f, 'Yes (Last)', 'UnitSndYesEnd')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='What (First):', width=13, anchor=E).pack(side=LEFT)
		self.firstwhatentryw = Entry(f, textvariable=self.firstwhatentry, font=couriernew, width=4)
		self.firstwhatentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.firstwhatddw = DropDown(f, self.firstwhatdd, sfxdata, self.firstwhatentry, width=30)
		self.firstwhatddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.firstwhatbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.firstwhatdd: self.jump(t,i))
		self.firstwhatbtnw.pack(side=LEFT)
		tip(f, 'What (First)', 'UnitSndWhatStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='What (Last):', width=13, anchor=E).pack(side=LEFT)
		self.lastwhatentryw = Entry(f, textvariable=self.lastwhatentry, font=couriernew, width=4)
		self.lastwhatentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.lastwhatddw = DropDown(f, self.lastwhatdd, sfxdata, self.lastwhatentry, width=30)
		self.lastwhatddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.lastwhatbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.lastwhatdd: self.jump(t,i))
		self.lastwhatbtnw.pack(side=LEFT)
		tip(f, 'What (Last)', 'UnitSndWhatEnd')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Annoyed (First):', width=13, anchor=E).pack(side=LEFT)
		self.firstannoyedentryw = Entry(f, textvariable=self.firstannoyedentry, font=couriernew, width=4)
		self.firstannoyedentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.firstannoyedddw = DropDown(f, self.firstannoyeddd, sfxdata, self.firstannoyedentry, width=30)
		self.firstannoyedddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.firstannoyedbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.firstannoyeddd: self.jump(t,i))
		self.firstannoyedbtnw.pack(side=LEFT)
		tip(f, 'Annoyed (First)', 'UnitSndAnnStart')
		f.pack(fill=X)

		f = Frame(s)
		Label(f, text='Annoyed (Last):', width=13, anchor=E).pack(side=LEFT)
		self.lastannoyedentryw = Entry(f, textvariable=self.lastannoyedentry, font=couriernew, width=4)
		self.lastannoyedentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.lastannoyedddw = DropDown(f, self.lastannoyeddd, sfxdata, self.lastannoyedentry, width=30)
		self.lastannoyedddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.lastannoyedbtnw = Button(f, text='Jump ->', command=lambda t='Sfxdata',i=self.lastannoyeddd: self.jump(t,i))
		self.lastannoyedbtnw.pack(side=LEFT)
		tip(f, 'Annoyed (Last)', 'UnitSndAnnEnd')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'ReadySound':self.readyentry,
			'WhatSoundStart':self.firstwhatentry,
			'WhatSoundEnd':self.lastwhatentry,
			'PissSoundStart':self.firstannoyedentry,
			'PissSoundEnd':self.lastannoyedentry,
			'YesSoundStart':self.firstyesentry,
			'YesSoundEnd':self.lastyesentry,
		}

	def files_updated(self):
		# sfxdata = ['None'] + [decompile_string(s) for s in self.toplevel.sfxdatatbl.strings]
		sfxdata = DATA_CACHE['Sfxdata.txt']
		fields = (
			(self.readyentry,self.readyddw),
			(self.firstyesentry,self.firstyesddw),
			(self.lastyesentry,self.lastyesddw),
			(self.firstwhatentry,self.firstwhatddw),
			(self.lastwhatentry,self.lastwhatddw),
			(self.firstannoyedentry,self.firstannoyedddw),
			(self.lastannoyedentry,self.lastannoyedddw)
		)
		for entry,dd in fields:
			entry.range[1] = len(sfxdata)
			dd.setentries(sfxdata)
			entry.editvalue()

	def loadsave(self, save=False):
		if not save and self.toplevel.units:
			id = self.parent.parent.id
			restricted = [
				('ReadySound',[self.readyentryw,self.readyddw,self.readybtnw]),
				('PissSoundStart',[self.firstannoyedentryw,self.firstannoyedddw,self.firstannoyedbtnw]),
				('PissSoundEnd',[self.lastannoyedentryw,self.lastannoyedddw,self.lastannoyedbtnw]),
				('YesSoundStart',[self.firstyesentryw,self.firstyesddw,self.firstyesbtnw]),
				('YesSoundEnd',[self.lastyesentryw,self.lastyesddw,self.lastyesbtnw]),
			]
			for l,ws in restricted:
				frmt = self.toplevel.units.format[self.toplevel.units.labels.index(l)]
				state = [NORMAL,DISABLED][id < frmt[0][0] or id >= frmt[0][1]]
				for w in ws:
					w['state'] = state
		DATUnitsTab.loadsave(self, save)

class AdvancedUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.flyer = IntVar()
		self.hero = IntVar()
		self.regenerate = IntVar()
		self.spellcaster = IntVar()
		self.permanentcloak = IntVar()
		self.invincible = IntVar()
		self.organic = IntVar()
		self.mechanical = IntVar()
		self.robotic = IntVar()
		self.detector = IntVar()
		self.subunit = IntVar()
		self.resourcecontainter = IntVar()
		self.resourcedepot = IntVar()
		self.resourceminer = IntVar()
		self.requirespsi = IntVar()
		self.requirescreep = IntVar()
		self.twounitsinoneegg = IntVar()
		self.singleentity = IntVar()
		self.burrowable = IntVar()
		self.cloakable = IntVar()
		self.battlereactions = IntVar()
		self.fullautoattack = IntVar()
		self.building = IntVar()
		self.addon = IntVar()
		self.flyingbuilding = IntVar()
		self.usemediumoverlays = IntVar()
		self.uselargeoverlays = IntVar()
		self.ignoresupplycheck = IntVar()
		self.producesunits = IntVar()
		self.animatedidle = IntVar()
		self.pickupitem = IntVar()
		self.unused = IntVar()

		flags = [
			[
				('Flyer', self.flyer, 'UnitAdvFlyer'),
				('Hero', self.hero, 'UnitAdvHero'),
				('Regenerate', self.regenerate, 'UnitAdvRegenerate'),
				('Spellcaster', self.spellcaster, 'UnitAdvSpellcaster'),
				('Permanently Cloaked', self.permanentcloak, 'UnitAdvPermaCloak'),
				('Invincible', self.invincible, 'UnitAdvInvincible'),
				('Organic', self.organic, 'UnitAdvOrganic'),
				('Mechanical', self.mechanical, 'UnitAdvMechanical'),
				('Robotic', self.robotic, 'UnitAdvRobotic'),
				('Detector', self.detector, 'UnitAdvDetector'),
				('Subunit', self.subunit, 'UnitAdvSubunit'),
			],[
				('Resource Container', self.resourcecontainter, 'UnitAdvResContainer'),
				('Resource Depot', self.resourcedepot, 'UnitAdvResDepot'),
				('Resource Miner', self.resourceminer, 'UnitAdvWorker'),
				('Requires Psi', self.requirespsi, 'UnitAdvReqPsi'),
				('Requires Creep', self.requirescreep, 'UnitAdvReqCreep'),
				('Two Units in One Egg', self.twounitsinoneegg, 'UnitAdvTwoInEgg'),
				('Single Entity', self.singleentity, 'UnitAdvSingleEntity'),
				('Burrowable', self.burrowable, 'UnitAdvBurrow'),
				('Cloakable', self.cloakable, 'UnitAdvCloak'),
				('Battle Reactions', self.battlereactions, 'UnitAdvBattleReactions'),
				('Full Auto-Attack', self.fullautoattack, 'UnitAdvAutoAttack'),
			],[
				('Building', self.building, 'UnitAdvBuilding'),
				('Addon', self.addon, 'UnitAdvAddon'),
				('Flying Building', self.flyingbuilding, 'UnitAdvFlyBuilding'),
				('Use Medium Overlays', self.usemediumoverlays, 'UnitAdvOverlayMed'),
				('Use Large Overlays', self.uselargeoverlays, 'UnitAdvOverlayLarge'),
				('Ignore Supply Check', self.ignoresupplycheck, 'UnitAdvIgnoreSupply'),
				('Produces Units(?)', self.producesunits, 'UnitAdvProducesUnits'),
				('Animated Overlay', self.animatedidle, 'UnitAdvAnimIdle'),
				('Carryable', self.pickupitem, 'UnitAdvPickup'),
				('Unknown', self.unused, 'UnitAdvUnused'),
			],
		]
		l = LabelFrame(frame, text='Advanced Properties:')
		s = Frame(l)
		for c in flags:
			cc = Frame(s, width=20)
			for t,v,h in c:
				f = Frame(cc)
				Checkbutton(f, text=t, variable=v).pack(side=LEFT)
				tip(f, t, h)
				f.pack(fill=X)
			cc.pack(side=LEFT, fill=Y)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		units = DATA_CACHE['Units.txt']
		# if self.toplevel.settings.get('customlabels',0):
		# 	units = [decompile_string(s) for s in self.toplevel.stat_txt.strings[:228]] + ['None']
		self.infestentry = IntegerVar(0, [0,228])
		self.infestdd = IntVar()
		self.subunitoneentry = IntegerVar(0,[0,228])
		self.subunitone = IntVar()
		self.subunittwoentry = IntegerVar(0,[0,228])
		self.subunittwo = IntVar()
		self.reqIndex = IntegerVar(0, [0,65535])
		self.unknown1 = IntVar()
		self.unknown2 = IntVar()
		self.unknown4 = IntVar()
		self.unknown8 = IntVar()
		self.unknown10 = IntVar()
		self.unknown20 = IntVar()
		self.unknown40 = IntVar()
		self.unknown80 = IntVar()

		l = LabelFrame(frame, text='Other Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Infestation:', width=9, anchor=E).pack(side=LEFT)
		self.infestentryw = Entry(f, textvariable=self.infestentry, font=couriernew, width=3)
		self.infestentryw.pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		self.infestddw = DropDown(f, self.infestdd, units, self.infestentry)
		self.infestddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		self.infestbtnw = Button(f, text='Jump ->', command=lambda t='Units',i=self.infestdd: self.jump(t,i))
		self.infestbtnw.pack(side=LEFT)
		tip(f, 'Infestation', 'UnitInfestation')
		f.pack(fill=X)
		su = Frame(s)
		f = Frame(su)
		Label(f, text='Subunit 1:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.subunitoneentry, font=couriernew, width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.subunitone, units, self.subunitoneentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Subunit 1', 'UnitSub1')
		f.pack(fill=X)
		f = Frame(su)
		Label(f, text='Subunit 2:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.subunittwoentry, font=couriernew, width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.subunittwo, units, self.subunittwoentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		tip(f, 'Subunit 2', 'UnitSub2')
		f.pack(fill=X)
		f = Frame(su)
		Label(f, text='ReqIndex:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.reqIndex, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Requirements Index', 'UnitReq')
		f.pack(fill=X)
		su.pack(side=LEFT, fill=BOTH, expand=1)
		unknown = Frame(s)
		u = [
			[
				('01', self.unknown1),
				('02', self.unknown2),
				('04', self.unknown4),
				('08', self.unknown8),
			],[
				('10', self.unknown10),
				('20', self.unknown20),
				('40', self.unknown40),
				('80', self.unknown80),
			],
		]
		for c in u:
			cc = Frame(unknown)
			for t,v in c:
				f = Frame(cc)
				makeCheckbox(f,v,'0x'+t,'UnitMov'+t).pack(side=LEFT)
				f.pack(fill=X)
			cc.pack(side=LEFT)
		unknown.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'Subunit1':self.subunitone,
			'Subunit2':self.subunittwo,
			'Infestation':self.infestentry,
			'Unknown':[self.unknown1,self.unknown2,self.unknown4,self.unknown8,self.unknown10,self.unknown20,self.unknown40,self.unknown80],
			'SpecialAbilityFlags':[self.building,self.addon,self.flyer,self.resourceminer,self.subunit,self.flyingbuilding,self.hero,self.regenerate,self.animatedidle,self.cloakable,self.twounitsinoneegg,self.singleentity,self.resourcedepot,self.resourcecontainter,self.robotic,self.detector,self.organic,self.requirescreep,self.unused,self.requirespsi,self.burrowable,self.spellcaster,self.permanentcloak,self.pickupitem,self.ignoresupplycheck,self.usemediumoverlays,self.uselargeoverlays,self.battlereactions,self.fullautoattack,self.invincible,self.mechanical,self.producesunits],
			'Requirements':self.reqIndex,
		}

	def files_updated(self):
		units = DATA_CACHE['Units.txt']
		if self.toplevel.settings.get('customlabels',0):
			units = ['None'] + [decompile_string(s) for s in self.toplevel.stat_txt.strings[:229]]
		self.infestddw.setentries(units)
		
	def isFlagSet(self,category,value):
		return (self.toplevel.units.get_value(self.parent.parent.id, category) & value) == value;

	def loadsave(self, save=False):
		id = self.parent.parent.id
		if not save and self.toplevel.units:
			frmt = self.toplevel.units.format[self.toplevel.units.labels.index('Infestation')][0]
			state = [NORMAL,DISABLED][id < frmt[0] or id >= frmt[1]]
			self.infestentryw['state'] = state
			self.infestddw['state'] = state
			self.infestbtnw['state'] = state
		if save:
			r = (1<<0)*self.building.get() + (1<<1)*self.addon.get() + (1<<2)*self.flyer.get() + (1<<3)*self.resourceminer.get() + (1<<4)*self.subunit.get() + (1<<5)*self.flyingbuilding.get() + (1<<6)*self.hero.get() + (1<<7)*self.regenerate.get() + (1<<8)*self.animatedidle.get() + (1<<9)*self.cloakable.get() + (1<<10)*self.twounitsinoneegg.get() + (1<<11)*self.singleentity.get() + (1<<12)*self.resourcedepot.get() + (1<<13)*self.resourcecontainter.get() + (1<<14)*self.robotic.get() + (1<<15)*self.detector.get() + (1<<16)*self.organic.get() + (1<<17)*self.requirescreep.get() + (1<<18)*self.unused.get() + (1<<19)*self.requirespsi.get() + (1<<20)*self.burrowable.get() + (1<<21)*self.spellcaster.get() + (1<<22)*self.permanentcloak.get() + (1<<23)*self.pickupitem.get() + (1<<24)*self.ignoresupplycheck.get() + (1<<25)*self.usemediumoverlays.get() + (1<<26)*self.uselargeoverlays.get() + (1<<27)*self.battlereactions.get() + (1<<28)*self.fullautoattack.get() + (1<<29)*self.invincible.get() + (1<<30)*self.mechanical.get() + (1<<31)*self.producesunits.get()
			if self.toplevel.units.get_value(id,'SpecialAbilityFlags') != r:
				self.edited = True
				self.toplevel.units.set_value(id,'SpecialAbilityFlags', r)
			r = (1<<0)*self.unknown1.get() + (1<<1)*self.unknown2.get() + (1<<2)*self.unknown4.get() + (1<<3)*self.unknown8.get() + (1<<4)*self.unknown10.get() + (1<<5)*self.unknown20.get() + (1<<6)*self.unknown40.get() + (1<<7)*self.unknown80.get()
			if self.toplevel.units.get_value(id,'Unknown') != r:
				self.edited = True
				self.toplevel.units.set_value(id,'Unknown', r)
		else:
			self.building.set(self.isFlagSet('SpecialAbilityFlags', 1 << 0))
			self.addon.set(self.isFlagSet('SpecialAbilityFlags', 1 << 1))
			self.flyer.set(self.isFlagSet('SpecialAbilityFlags', 1 << 2))
			self.resourceminer.set(self.isFlagSet('SpecialAbilityFlags', 1 << 3))
			self.subunit.set(self.isFlagSet('SpecialAbilityFlags', 1 << 4))
			self.flyingbuilding.set(self.isFlagSet('SpecialAbilityFlags', 1 << 5))
			self.hero.set(self.isFlagSet('SpecialAbilityFlags', 1 << 6))
			self.regenerate.set(self.isFlagSet('SpecialAbilityFlags', 1 << 7))
			self.animatedidle.set(self.isFlagSet('SpecialAbilityFlags', 1 << 8))
			self.cloakable.set(self.isFlagSet('SpecialAbilityFlags', 1 << 9))
			self.twounitsinoneegg.set(self.isFlagSet('SpecialAbilityFlags', 1 << 10))
			self.singleentity.set(self.isFlagSet('SpecialAbilityFlags', 1 << 11))
			self.resourcedepot.set(self.isFlagSet('SpecialAbilityFlags', 1 << 12))
			self.resourcecontainter.set(self.isFlagSet('SpecialAbilityFlags', 1 << 13))
			self.robotic.set(self.isFlagSet('SpecialAbilityFlags', 1 << 14))
			self.detector.set(self.isFlagSet('SpecialAbilityFlags', 1 << 15))
			self.organic.set(self.isFlagSet('SpecialAbilityFlags', 1 << 16))
			self.requirescreep.set(self.isFlagSet('SpecialAbilityFlags', 1 << 17))
			self.unused.set(self.isFlagSet('SpecialAbilityFlags', 1 << 18))
			self.requirespsi.set(self.isFlagSet('SpecialAbilityFlags', 1 << 19))
			self.burrowable.set(self.isFlagSet('SpecialAbilityFlags', 1 << 20))
			self.spellcaster.set(self.isFlagSet('SpecialAbilityFlags', 1 << 21))
			self.permanentcloak.set(self.isFlagSet('SpecialAbilityFlags', 1 << 22))
			self.pickupitem.set(self.isFlagSet('SpecialAbilityFlags', 1 << 23))
			self.ignoresupplycheck.set(self.isFlagSet('SpecialAbilityFlags', 1 << 24))
			self.usemediumoverlays.set(self.isFlagSet('SpecialAbilityFlags', 1 << 25))
			self.uselargeoverlays.set(self.isFlagSet('SpecialAbilityFlags', 1 << 26))
			self.battlereactions.set(self.isFlagSet('SpecialAbilityFlags', 1 << 27))
			self.fullautoattack.set(self.isFlagSet('SpecialAbilityFlags', 1 << 28))
			self.invincible.set(self.isFlagSet('SpecialAbilityFlags', 1 << 29))
			self.mechanical.set(self.isFlagSet('SpecialAbilityFlags', 1 << 30))
			self.producesunits.set(self.isFlagSet('SpecialAbilityFlags', 1 << 31))
			
			self.unknown1.set(self.isFlagSet('Unknown', 1 << 0))
			self.unknown2.set(self.isFlagSet('Unknown', 1 << 1))
			self.unknown4.set(self.isFlagSet('Unknown', 1 << 2))
			self.unknown8.set(self.isFlagSet('Unknown', 1 << 3))
			self.unknown10.set(self.isFlagSet('Unknown', 1 << 4))
			self.unknown20.set(self.isFlagSet('Unknown', 1 << 5))
			self.unknown40.set(self.isFlagSet('Unknown', 1 << 6))
			self.unknown80.set(self.isFlagSet('Unknown', 1 << 7))
		DATUnitsTab.loadsave(self, save)

class BasicUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.health = IntegerVar(0,[0,4294967295])
		self.shields = IntegerVar(0,[0,65535])
		self.shieldsenabled = IntVar()
		self.armor = IntegerVar(0,[0,255])
		self.upgradeentry = IntegerVar(0,[0,60])
		self.upgrade = IntVar()

		statframe = Frame(frame)
		l = LabelFrame(statframe, text='Vital Statistics')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Hit Points:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.health, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Hit Points', 'UnitHP')
		f.pack(fill=X)
		f = Frame(s)
		x = Frame(f)
		Label(x, text='Shields:', width=9, anchor=E).pack(side=LEFT)
		Entry(x, textvariable=self.shields, font=couriernew, width=10).pack(side=LEFT)
		tip(x, 'Shields', 'UnitSP')
		x.pack(side=LEFT)
		x = Frame(f)
		Checkbutton(x, text='Enabled', variable=self.shieldsenabled).pack(side=LEFT)
		tip(x, 'Shields Enabled', 'UnitShieldEnable')
		x.pack(side=LEFT, fill=X)
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Armor:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.armor, font=couriernew, width=10).pack(side=LEFT)
		tip(f, 'Armor', 'UnitArmor')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Upgrade:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.upgradeentry, font=couriernew, width=2).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.upgrade, DATA_CACHE['Upgrades.txt'], self.upgradeentry, width=20).pack(side=LEFT, fill=X, expand=1)
		Button(f, text='Jump ->', command=lambda t='Upgrades',i=self.upgrade: self.jump(t,i)).pack(side=LEFT)
		tip(f, 'Armor Upgrade', 'UnitArmorUpgrade')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		self.minerals = IntegerVar(0, [0,65535])
		self.vespene = IntegerVar(0, [0,65535])
		self.time = IntegerVar(24, [1,65535], callback=lambda n,i=0: self.updatetime(n,i))
		self.seconds = FloatVar(1, [0.0416,2730.625], callback=lambda n,i=1: self.updatetime(n,i), precision=4)
		self.broodwar = IntVar()

		l = LabelFrame(statframe, text='Build Cost')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Minerals:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.minerals, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Minerals', 'UnitMinerals')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vespene:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.vespene, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Vespene', 'UnitVespene')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Time:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.time, font=couriernew, width=5).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		Entry(f, textvariable=self.seconds, font=couriernew, width=9).pack(side=LEFT)
		Label(f, text='secs.').pack(side=LEFT)
		tip(f, 'Build Time', 'UnitTime')
		f.pack(fill=X)
		c = Checkbutton(s, text='BroodWar', variable=self.broodwar)
		tip(c, 'BroodWar', 'UnitIsBW')
		c.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH)
		statframe.pack(fill=X)

		self.groundentry = IntegerVar(0, [0,130])
		self.grounddd = IntVar()
		self.groundmax = IntegerVar(0, [0,255])
		self.airentry = IntegerVar(0, [0,130])
		self.airdd = IntVar()
		self.airmax = IntegerVar(0, [0,255])

		l = LabelFrame(frame, text='Weapons')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Ground:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.groundentry, font=couriernew, width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.grounddd, DATA_CACHE['Weapons.txt'], self.groundentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Weapons',i=self.grounddd: self.jump(t,i)).pack(side=LEFT)
		tip(f, 'Ground Weapon', 'UnitWeaponGround')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.groundmax, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Max Ground Hits', 'UnitGroundMax')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Air:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.airentry, font=couriernew, width=3).pack(side=LEFT)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.airdd, DATA_CACHE['Weapons.txt'], self.airentry).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Weapons',i=self.airdd: self.jump(t,i)).pack(side=LEFT)
		tip(f, 'Air Weapon', 'UnitWeaponAir')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Max Hits:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.airmax, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Max Air Hits', 'UnitAirMax')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.suprequired = IntegerVar(0, [0,255])
		self.supreqhalf = IntVar()
		self.suprovided = IntegerVar(0, [0,255])
		self.suprovhalf = IntVar()
		self.zerg = IntVar()
		self.terran = IntVar()
		self.protoss = IntVar()

		ssframe = Frame(frame)
		l = LabelFrame(ssframe, text='Supply')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.suprequired, font=couriernew, width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5', variable=self.supreqhalf).pack(side=LEFT)
		tip(f, 'Supply Required', 'UnitSupReq')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.suprovided, font=couriernew, width=3).pack(side=LEFT)
		Checkbutton(f, text='+0.5', variable=self.suprovhalf).pack(side=LEFT)
		tip(f, 'Supply Provided', 'UnitSupProv')
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Zerg', variable=self.zerg)
		tip(c, 'Zerg', 'UnitSEGroupZerg')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Terran', variable=self.terran)
		tip(c, 'Terran', 'UnitSEGroupTerran')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Protoss', variable=self.protoss)
		tip(c, 'Protoss', 'UnitSEGroupProtoss')
		c.pack(side=LEFT)
		f.pack()
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=X, expand=1)

		self.sprequired = IntegerVar(0, [0,255])
		self.spprovided = IntegerVar(0, [0,255])

		l = LabelFrame(ssframe, text='Space')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Required:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.sprequired, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Space Required', 'UnitSpaceReq')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Provided:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.spprovided, font=couriernew, width=3).pack(side=LEFT)
		tip(f, 'Space Provided', 'UnitSpaceProv')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)

		self.build = IntegerVar(0, [0,65535])
		self.destroyscore = IntegerVar(0, [0,65535])

		l = LabelFrame(ssframe, text='Score')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Build:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.build, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Build Score', 'UnitScoreBuild')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Destroy:', width=9, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.destroyscore, font=couriernew, width=5).pack(side=LEFT)
		tip(f, 'Destroy Score', 'UnitScoreDestroy')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		ssframe.pack(fill=X)

		self.unitsize = IntVar()
		self.sight = IntegerVar(0, [0,11])
		self.tar = IntegerVar(0, [0,255])

		otherframe = Frame(frame)
		l = LabelFrame(otherframe, text='Other')
		s = Frame(l)
		t = Frame(s)
		Label(t, text='Unit Size:', anchor=E).pack(side=LEFT)
		DropDown(t, self.unitsize, DATA_CACHE['UnitSize.txt']).pack(side=LEFT, fill=X, expand=1)
		tip(t, 'Unit Size', 'UnitSize')
		t.pack(side=LEFT, fill=X, expand=1)
		t = Frame(s)
		Label(t, text='Sight:', anchor=E).pack(side=LEFT)
		Entry(t, textvariable=self.sight, font=couriernew, width=2).pack(side=LEFT)
		tip(t, 'Sight Range', 'UnitSight')
		t.pack(side=LEFT)
		t = Frame(s)
		Label(t, text='Target Acquisition Range:', anchor=E).pack(side=LEFT)
		Entry(t, textvariable=self.tar, font=couriernew, width=3).pack(side=LEFT)
		tip(t, 'Target Acquisition Range', 'UnitTAR')
		t.pack(side=LEFT)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(side=LEFT, fill=BOTH, expand=1)
		otherframe.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		self.values = {
			'HitPoints':self.health,
			'ShieldAmount':self.shields,
			'ShieldEnable':self.shieldsenabled,
			'Armor':self.armor,
			'ArmorUpgrade':self.upgrade,
			'MineralCost':self.minerals,
			'VespeneCost':self.vespene,
			'BuildTime':self.time,
			'BroodwarUnitFlag':self.broodwar,
			'GroundWeapon':self.groundentry,
			'MaxGroundHits':self.groundmax,
			'AirWeapon':self.airentry,
			'MaxAirHits':self.airmax,
			'SpaceRequired':self.sprequired,
			'SpaceProvided':self.spprovided,
			'BuildScore':self.build,
			'DestroyScore':self.destroyscore,
			'UnitSize':self.unitsize,
			'SightRange':self.sight,
			'TargetAcquisitionRange':self.tar,
		}

	def updatetime(self, num, type):
		if type:
			self.time.check = False
			self.time.set(int(float(num) * 24))
		else:
			self.seconds.check = False
			s = str(int(num) / 24.0)
			if s.endswith('.0'):
				s = s[:-2]
			elif len(s.split('.')[1]) > 4:
				s = s[:s.index('.')+5]
			self.seconds.set(s)

	def loadsave(self, save=False):
		if self.toplevel.units:
			id = self.parent.parent.id
			if save:
				r = self.suprequired.get() * 2 + self.supreqhalf.get()
				if self.toplevel.units.get_value(id,'SupplyRequired') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'SupplyRequired',r)
				r = self.suprovided.get() * 2 + self.suprovhalf.get()
				if self.toplevel.units.get_value(id,'SupplyProvided') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'SupplyProvided',r)
				r = (self.toplevel.units.get_value(id,'StarEditGroupFlags') & 248) | (1 * self.zerg.get() + 2 * self.terran.get() + 4 * self.protoss.get())
				if self.toplevel.units.get_value(id,'StarEditGroupFlags') != r:
					self.edited = True
					self.toplevel.units.set_value(id,'StarEditGroupFlags',r)
			else:
				x = self.toplevel.units.get_value(id,'SupplyRequired')
				self.suprequired.set(int(ceil((x - 1) / 2.0)))
				self.supreqhalf.set(x % 2)
				x = self.toplevel.units.get_value(id,'SupplyProvided')
				self.suprovided.set(int(ceil((x - 1) / 2.0)))
				self.suprovhalf.set(x % 2)
				#
				self.zerg.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 1)
				self.terran.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 2 == 2)
				self.protoss.set(self.toplevel.units.get_value(id,'StarEditGroupFlags') & 4 == 4)
		DATUnitsTab.loadsave(self, save)
				
class UnitsTab(DATTab):
	data = 'Units.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		self.dattabs = Notebook(self, FLAT)
		tabs = [
			('Basic', BasicUnitsTab),
			('Advanced', AdvancedUnitsTab),
			('Sounds', SoundsUnitsTab),
			('Graphics', GraphicsUnitsTab),
			('StarEdit', StarEditUnitsTab),
			('AI Actions', AIActionsUnitsTab),
		]
		for tab in tabs:
			self.dattabs.add_tab(tab[1](self.dattabs, toplevel, self), tab[0])
		self.dattabs.pack(fill=BOTH, expand=1)

	def files_updated(self):
		self.dat = self.toplevel.units
		for tab in self.dattabs.pages.values():
			page = tab[0]
			page.files_updated()

	def loadsave(self, save=False):
		self.dattabs.active.loadsave(save)

class PyDAT(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyDAT',
			{
				'stat_txt':'MPQ:rez\\stat_txt.tbl',
				'imagestbl':'MPQ:arr\\images.tbl',
				'sfxdatatbl':'MPQ:arr\\sfxdata.tbl',
				'portdatatbl':'MPQ:arr\\portdata.tbl',
				'mapdatatbl':'MPQ:arr\\mapdata.tbl',
				'cmdicons':'MPQ:unit\\cmdbtns\\cmdicons.grp',
				'iscriptbin':'MPQ:scripts\\iscript.bin',
			}
		)
		###### Remove later down the line (currently v1.9)
		if 'usemodmpq' in self.settings:
			del self.settings['usemodmpq']

		Tk.__init__(self)
		self.title('PyDAT %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR, 'Images','PyDAT.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyDAT.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyDAT')

		self.stat_txt = None
		self.imagestbl = None
		self.sfxdatatbl = None
		self.portdatatbl = None
		self.mapdatatbl = None
		self.cmdicon = None
		self.iscriptbin = None
		self.units = None
		self.weapons = None
		self.flingy = None
		self.sprites = None
		self.images = None
		self.upgrades = None
		self.technology = None
		self.sounds = None
		self.portraits = None
		self.campaigns = None
		self.orders = None

		pal = Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.settings.get('%spal' % p,os.path.join(BASE_DIR, 'Palettes', '%s%spal' % (p,os.extsep))))
			except:
				continue
			PALETTES[p] = pal.palette
		self.dats = {}
		self.defaults = {}

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('openfolder', self.opendirectory, 'Open Directory (Ctrl+D)', NORMAL, 'Ctrl+D'),
			('import', self.iimport, 'Import from TXT (Ctrl+I)', NORMAL, 'Ctrl+I'),
			('openmpq', self.openmpq, 'Open MPQ (Ctrl+Alt+O)', [NORMAL,DISABLED][FOLDER], 'Ctrl+Alt+O'),
			2,
			('save', self.save, 'Save (Ctrl+S)', NORMAL, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', NORMAL, 'Ctrl+Alt+A'),
			('export', self.export, 'Export to TXT (Ctrl+E)', NORMAL, 'Ctrl+E'),
			('savempq', self.savempq, 'Save MPQ (Ctrl+Alt+M)', [NORMAL,DISABLED][FOLDER], 'Ctrl+Alt+M'),
			10,
			('asc3topyai', self.mpqtbl, 'Manage MPQ and TBL files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.dat editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyDAT', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		mid = Frame(self)
		left = Frame(mid)
		##listbox
		self.listframe = Frame(left, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, font=couriernew, width=45, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			self.listframe.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.changeid)
		self.listbox.bind('<ButtonRelease-3>', self.popup)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(side=TOP, fill=BOTH, padx=2, pady=2, expand=1)

		self.findhistory = []
		self.find = StringVar()
		self.jumpid = IntegerVar('', [0,227], allow_hex=True)

		search = Frame(left)
		tdd = TextDropDown(search, self.find, self.findhistory, 30)
		tdd.pack(side=LEFT)
		tdd.entry.bind('<Return>', self.findnext)
		Button(search, text='Find Next', command=self.findnext).pack(side=LEFT)
		right = Frame(search)
		entry = Entry(right, textvariable=self.jumpid, width=4)
		entry.pack(side=LEFT)
		entry.bind('<Return>', self.jump)
		Button(right, text='ID Jump', command=self.jump).pack(side=LEFT)
		right.pack(side=RIGHT)
		search.pack(fill=X, padx=2, pady=2)
		self.bind('<Control-f>', lambda e: tdd.focus_set(highlight=True))

		left.pack(side=LEFT, fill=Y)

		listmenu = [
			('Copy Entry (Ctrl+Shift+C)', lambda t=0: self.copy(t), 0, 'Control-Shift-c'), # 0
			('Paste Entry (Ctrl+Shift+P)', lambda t=0: self.paste(t), 0, 'Control-Shift-p'), # 1
			None,
			('Copy Tab (Ctrl+Y)', lambda t=1: self.copy(t), 1, 'Control-y'), # 3
			('Paste Tab (Ctrl+B)', lambda t=1: self.paste(t), 1, 'Control-b'), # 4
			None,
			('Reload Entry (Ctrl+R)', self.reload, 0, 'Control-r'), #6
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u,b = m
				self.listmenu.add_command(label=l, command=c, underline=u)
				self.bind(b, c)
			else:
				self.listmenu.add_separator()

		self.status = StringVar()
		self.dattabs = Notebook(mid)
		self.pages = []
		tabs = (
			('Units', UnitsTab),
			('Weapons', WeaponsTab),
			('Flingy', FlingyTab),
			('Sprites', SpritesTab),
			('Images', ImagesTab),
			('Upgrades', UpgradesTab),
			('Techdata', TechnologyTab),
			('Sfxdata', SoundsTab),
			('Portdata', PortraitsTab),
			('Mapdata', MapsTab),
			('Orders', OrdersTab),
		)
		self.dattabs.pack(side=LEFT, fill=BOTH, expand=1, padx=2, pady=2)
		for tab in tabs:
			page = tab[1](self.dattabs, self)
			self.pages.append(page)
			self.dattabs.add_tab(page, tab[0])
		# self.dattabs.bind('<<TabDeactivated>>', self.tab_deactivated)
		self.dattabs.bind('<<TabActivated>>', self.tab_activated)
		mid.pack(fill=BOTH, expand=1)


		#Statusbar
		self.datstatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		self.mpq_export = self.settings.get('mpqexport',[])

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if not 'mpqs' in self.settings:
			self.mpqhandler.add_defaults()

		e = self.open_files()
		if e:
			self.mpqtbl(err=e)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		if guifile:
			for title,tab in self.dattabs.pages.iteritems():
				try:
					tab[0].open(file=guifile, save=False)
					self.dattabs.display(title)
					break
				except PyMSError, e:
					pass
			else:
				ErrorDialog(self, PyMSError('Load',"'%s' is not a valid StarCraft *.dat file, could possibly be corrupt" % guifile))

		start_new_thread(check_update, (self,))

	def tab_activated(self, event=None):
		self.action_states()

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			stat_txt = TBL()
			imagestbl = TBL()
			sfxdatatbl = TBL()
			portdatatbl = TBL()
			mapdatatbl = TBL()
			cmdicon = CacheGRP()
			stat_txt.load_file(self.mpqhandler.get_file(self.settings['stat_txt']))
			imagestbl.load_file(self.mpqhandler.get_file(self.settings['imagestbl']))
			sfxdatatbl.load_file(self.mpqhandler.get_file(self.settings['sfxdatatbl']))
			portdatatbl.load_file(self.mpqhandler.get_file(self.settings['portdatatbl']))
			mapdatatbl.load_file(self.mpqhandler.get_file(self.settings['mapdatatbl']))
			cmdicon.load_file(self.mpqhandler.get_file(self.settings['cmdicons']))
		except PyMSError, e:
			err = e
		else:
			units = UnitsDAT(stat_txt)
			weapons = WeaponsDAT(stat_txt)
			flingy = FlingyDAT(stat_txt)
			sprites = SpritesDAT(stat_txt)
			images = ImagesDAT(imagestbl)
			upgrades = UpgradesDAT(stat_txt)
			technology = TechDAT(stat_txt)
			sounds = SoundsDAT(sfxdatatbl)
			portraits = PortraitDAT(portdatatbl)
			campaigns = CampaignDAT(mapdatatbl)
			orders = OrdersDAT(stat_txt)
			defaults = [
				(units, UnitsDAT, stat_txt),
				(weapons, WeaponsDAT, stat_txt),
				(flingy, FlingyDAT, stat_txt),
				(sprites, SpritesDAT, stat_txt),
				(images, ImagesDAT, imagestbl),
				(upgrades, UpgradesDAT, stat_txt),
				(technology, TechDAT, stat_txt),
				(sounds, SoundsDAT, sfxdatatbl),
				(portraits, PortraitDAT, portdatatbl),
				(campaigns, CampaignDAT, mapdatatbl),
				(orders, OrdersDAT, stat_txt),
			]
			missing = []
			defaultmpqs = MPQHandler()
			defaultmpqs.add_defaults()
			defaultmpqs.open_mpqs()
			for v,c,t in defaults:
				n = c.datname
				try:
					v.load_file(defaultmpqs.get_file('MPQ:arr\\' + n, True))
				except:
					try:
						v.load_file(defaultmpqs.get_file('MPQ:arr\\' + n, False))
					except PyMSError, e:
						err = e
						break
			if not err:
				iscriptbin = IScriptBIN(weapons, flingy, images, sprites, sounds, stat_txt, imagestbl, sfxdatatbl)
				iscriptbin.load_file(self.mpqhandler.get_file(self.settings['iscriptbin']))
			defaultmpqs.close_mpqs()
		self.mpqhandler.close_mpqs()
		if not err:
			self.stat_txt = stat_txt
			self.imagestbl = imagestbl
			self.sfxdatatbl = sfxdatatbl
			self.portdatatbl = portdatatbl
			self.mapdatatbl = mapdatatbl
			self.cmdicon = cmdicon
			self.units = units
			self.weapons = weapons
			self.flingy = flingy
			self.sprites = sprites
			self.images = images
			self.upgrades = upgrades
			self.technology = technology
			self.sounds = sounds
			self.portraits = portraits
			self.campaigns = campaigns
			self.orders = orders
			self.iscriptbin = iscriptbin
			for v,c,t in defaults:
				n = c.datname
				self.dats[n] = v
				self.defaults[n] = c(t)
				self.defaults[n].entries = ccopy(v.entries)
			for page in self.pages:
				page.files_updated()
			self.dattabs.active.activate()
		return err

	def grp(self, pal, path, draw_function=None, draw_info=None):
		if not FOLDER and pal in PALETTES:
			p = os.path.join(BASE_DIR,'Libs','MPQ',os.path.join(*path.split('\\')))
			if not path in GRP_CACHE or not pal in GRP_CACHE[path]:
				p = self.mpqhandler.get_file('MPQ:' + path)
				try:
					grp = CacheGRP()
					grp.load_file(p,restrict=1)
				except PyMSError, e:
					return None
				if not path in GRP_CACHE:
					GRP_CACHE[path] = {}
				GRP_CACHE[path][pal] = frame_to_photo(PALETTES[pal], grp, 0, True, draw_function=draw_function, draw_info=draw_info)
			return GRP_CACHE[path][pal]

	def unsaved(self):
		for page in self.pages:
			if page.unsaved():
				return True

	def select_file(self, title, open=True, ext='.dat', filetypes=[('StarCraft DAT files','*.dat'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		edited = False
		if self.dattabs.active:
			edited = self.dattabs.active.edited
		self.editstatus['state'] = [DISABLED,NORMAL][edited]

	def loadsave(self, save=False):
		self.dattabs.active.loadsave(save)

	def changeid(self, key=None, i=None):
		s = True
		if i == None:
			i = int(self.listbox.curselection()[0])
			s = False
		if i != self.dattabs.active.id:
			self.loadsave(True)
			self.dattabs.active.id = i
			if s:
				self.listbox.select_clear(0,END)
				self.listbox.select_set(i)
				self.listbox.see(i)
			self.loadsave()
			self.listframe.focus_set()

	def popup(self, e):
		self.dattabs.active.popup(e)

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
		self.changeid(i=a)

	def findnext(self, key=None):
		f = self.find.get()
		if not f in self.findhistory:
			self.findhistory.append(f)
		start = int(self.listbox.curselection()[0])
		cur = (start + 1) % self.listbox.size()
		while cur != start:
			if f.lower() in DATA_CACHE[self.dattabs.active.data][cur].lower():
				self.changeid(i=cur)
				return
			cur = (cur+1) % self.listbox.size()
		askquestion(parent=self, title='Find', message="Can't find text.", type=OK)

	def jump(self, key=None):
		self.changeid(i=self.jumpid.get())

	def copy(self, t):
		self.dattabs.active.copy(t)

	def paste(self, t):
		self.dattabs.active.paste(t)

	def reload(self, key=None):
		self.dattabs.active.reload()

	def new(self, key=None):
		self.dattabs.active.new()

	def open(self, key=None):
		self.dattabs.active.open()

	def openmpq(self):
		file = self.select_file('Open MPQ', True, '.mpq', [('MPQ Files','*.mpq'),('Embedded MPQ Files','*.exe'),('All Files','*')])
		if not file:
			return
		h = SFileOpenArchive(file)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Open','Could not open MPQ "%s"' % file))
			return
		l = []
		found = []
		p = SFile()
		for n,d in self.dats.iteritems():
			entries = list(d.entries)
			p.text = ''
			f = SFileOpenFileEx(h, 'arr\\' + d.datname)
			if f in [None,-1]:
				continue
			r = SFileReadFile(f)
			SFileCloseFile(f)
			p.text = r[0]
			try:
				d.load_file(p)
			except:
				d.entries = entries
				continue
			l.append(d.datname)
			found.append((d,'%s:arr\\%s' % (file, d.datname)))
		SFileCloseArchive(h)
		if not found:
			ErrorDialog(self, PyMSError('Open','No DAT files found in MPQ "%s"' % file))
			return
		showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (file, ', '.join(l)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(file=d)

	def opendirectory(self, event):
		dir = tkFileDialog.askdirectory(parent=self, title='Open Directory', initialdir=self.settings.get('lastpath', BASE_DIR))
		if not dir:
			return
		self.settings['lastpath'] = dir
		dats = [UnitsDAT(),WeaponsDAT(),FlingyDAT(),SpritesDAT(),ImagesDAT(),UpgradesDAT(),TechDAT(),SoundsDAT(),PortraitDAT(),CampaignDAT(),OrdersDAT()]
		found = [None] * len(dats)
		files = [None] * len(dats)
		for f in os.listdir(dir):
			for n,d in enumerate(dats):
				if d == None:
					continue
				ff = os.path.join(dir,f)
				try:
					d.load_file(ff)
				except PyMSError, e:
					continue
				found[n] = (d,ff)
				name = f
				if name != d.datname:
					name += ' (%s)' % d.datname
				files[n] = name
				dats[n] = None
				break
			if not dats:
				break
		found = (f for f in found if f != None)
		if not found:
			ErrorDialog(self, PyMSError('Open','No DAT files found in directory "%s"' % dir))
			return
		files = [f for f in files if f != None]
		showinfo('DAT Files Found','DAT Files found in "%s":\n\t%s' % (dir, ', '.join(files)))
		for d in found:
			self.dattabs.pages[d[0].idfile.split('.')[0]][0].open(file=d)

	def iimport(self, key=None):
		self.dattabs.active.iimport()

	def save(self, key=None):
		self.loadsave(True)
		self.dattabs.active.save()

	def saveas(self, key=None):
		self.loadsave(True)
		self.dattabs.active.saveas()

	def export(self, key=None):
		self.loadsave(True)
		self.dattabs.active.export()

	def savempq(self, key=None):
		if not FOLDER:
			self.loadsave(True)
			SaveMPQDialog(self)

	def mpqtbl(self, key=None, err=None):
		data = [
			('TBL Settings',[
				('stat_txt.tbl', 'Contains Unit names', 'stat_txt', 'TBL'),
				('images.tbl', 'Contains GPR mpq file paths', 'imagestbl', 'TBL'),
				('sfxdata.tbl', 'Contains Sound mpq file paths', 'sfxdatatbl', 'TBL'),
				('portdata.tbl', 'Contains Portrait mpq file paths', 'portdatatbl', 'TBL'),
				('mapdata.tbl', 'Contains Campign map mpq file paths', 'mapdatatbl', 'TBL'),
			]),
			('Other Settings',[
				('cmdicons.grp', 'Contains icon images', 'cmdicons', 'CacheGRP'),
				('iscript.bin', 'Contains iscript entries for images.dat', 'iscriptbin', 'IScript'),
			])
		]
		DATSettingsDialog(self, data, (340,450), err)

	def register(self, e=None):
		try:
			register_registry('PyDAT','','dat',os.path.join(BASE_DIR, 'PyDAT.pyw'),os.path.join(BASE_DIR,'Images','PyDAT.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyDAT.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyDAT', LONG_VERSION, [('BroodKiller',"DatEdit, its design, format specs, and data files.")])

	def exit(self, e=None):
		self.loadsave(True)
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['mpqexport'] = self.mpq_export
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyDAT.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pydat.py','pydat.pyw','pydat.exe']):
		gui = PyDAT()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyDAT [options] <inp> [out]', version='PyDAT %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a DAT file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a DAT file")
		p.add_option('-u', '--units', action='store_const', const=0, dest='type', help="Decompiling/Compiling units.dat [default]", default=0)
		p.add_option('-w', '--weapons', action='store_const', const=1, dest='type', help="Decompiling/Compiling weapons.dat")
		p.add_option('-f', '--flingy', action='store_const', const=2, dest='type', help="Decompiling/Compiling flingy.dat")
		p.add_option('-s', '--sprites', action='store_const', const=3, dest='type', help="Decompiling/Compiling sprites.dat")
		p.add_option('-i', '--images', action='store_const', const=4, dest='type', help="Decompiling/Compiling images.dat")
		p.add_option('-g', '--upgrades', action='store_const', const=5, dest='type', help="Decompiling/Compiling upgrades.dat")
		p.add_option('-t', '--techdata', action='store_const', const=6, dest='type', help="Decompiling/Compiling techdata.dat")
		p.add_option('-l', '--sfxdata', action='store_const', const=7, dest='type', help="Decompiling/Compiling sfxdata.dat")
		p.add_option('-p', '--portdata', action='store_const', const=8, dest='type', help="Decompiling/Compiling portdata.dat")
		p.add_option('-m', '--mapdata', action='store_const', const=9, dest='type', help="Decompiling/Compiling mapdata.dat")
		p.add_option('-o', '--orders', action='store_const', const=10, dest='type', help="Decompiling/Compiling orders.dat")
		p.add_option('-n', '--ids', help="A list of ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-b', '--basedat', help="Used to signify the base DAT file to compile on top of", default='')
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for various values [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyDAT(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			dat = [UnitsDAT,WeaponsDAT,FlingyDAT,SpritesDAT,ImagesDAT,UpgradesDAT,TechDAT,SoundsDAT,PortraitDAT,CampaignDAT,OrdersDAT][opt.type]()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'dat'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					if opt.ids:
						ids = []
						try:
							for i in opt.ids.split(','):
								ids.append(int(i))
								if ids[-1] < 0 or ids[-1] >= dat.count:
									raise PyMSError('Options',"Invalid ID '%s'" % ids[-1])
						except:
							raise PyMSError('Options','Invalid ID list')
					else:
						ids = None
					print "Reading DAT '%s'..." % args[0]
					dat.load_file(args[0])
					print " - '%s' read successfully\nDecompiling DAT file '%s'..." % (args[0],args[0])
					dat.decompile(args[1], opt.reference, ids)
					print " - '%s' written succesfully" % args[1]
				else:
					if opt.basedat:
						basedat = os.path.abspath(opt.basedat)
					else:
						basedat = os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr','%s%sdat' % (['units','weapons','flingy','sprites','images','upgrades','techdata','sfxdata','portdata','mapdata','orders'][opt.type],os.extsep))
					print "Loading base DAT file '%s'..." % basedat
					dat.load_file(basedat)
					print " - '%s' read successfully\nInterpreting file '%s'..." % (basedat,args[0])
					dat.interpret(args[0])
					print " - '%s' read successfully\nCompiling file '%s' to DAT format..." % (args[0],args[0])
					dat.compile(args[1])
					print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()