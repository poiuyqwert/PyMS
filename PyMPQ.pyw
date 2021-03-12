from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SpecialLists import ReportList
from Libs.SFmpq import *
from Libs.analytics import *

# from Libs import TRG, GOT

from Tkinter import *
# from tkMessageBox import *
# import tkFileDialog,tkColorChooser

from thread import start_new_thread
from operator import itemgetter
import optparse, os, webbrowser, sys, time
#import ntpath

if FOLDER:
	e = DependencyError('PyMPQ', 'PyMS currently only has Windows and Mac support for MPQ files, thus this program is useless.\nIf you can help compile and test SFmpq for your operating system, then please Contact me!', ('Contact','file:///%s' % os.path.join(BASE_DIR, 'Docs', 'intro.html')))
	e.mainloop()
	sys.exit()

LONG_VERSION = 'v%s' % VERSIONS['PyMPQ']
PYMPQ_SETTINGS = Settings('PyMPQ', '1')
PYMPQ_SETTINGS.set_defaults({
	'sort': [0,False,None],
	'compress': [0,0]
})
PYMPQ_SETTINGS.settings.set_defaults({
	'listfiles': [os.path.join(BASE_DIR,'Libs','Data','Listfile.txt')],
	'autocompression': SettingDict({
		'Default':[1,0],
		'.smk':[0,0],
		'.mpq':[0,0],
		'.wav':[3,1]
	})
})
PYMPQ_SETTINGS.settings.defaults.set_defaults({
	'maxfiles': 1024,
	'locale': 0,
	'blocksize': 3
})
PYMPQ_SETTINGS.settings.autocompression.set_defaults({
	'Default':[1,0]
})

def size(b):
	s = ['B','KB','MB','GB']
	while b / 1024.0 >= 1:
		b = b / 1024.0
		del s[0]
	r = '%r' % float(b)
	if r.endswith('.0') or '.00' in r:
		r = r[:r.index('.')]
	else:
		r = r[:r.index('.')+3]
	return r + s[0]

class CheckThread:
	delay = 1

	def __init__(self, parent, path):
		self.parent = parent
		self.path = path
		self.cont = True
		self.thread = None

	def check_update(self, dummy):
		m = {}
		def check_dir(path, main=False):
			u = []
			for r,ds,fs in os.walk(path, topdown=False):
				#print r,ds,fs
				if main and not fs and not ds:
					return None
				for f in fs:
					p = os.path.join(r,f)
					s = os.stat(p).st_mtime
					#print '\t',p,s,m
					if p in m and s > m[p]:
						u.append(p)
					m[p] = s
				for d in ds:
					u.extend(check_dir(os.path.join(r,d)))
			#print u
			return u
		while self.cont:
			if not os.path.exists(self.path):
				break
			#print '-----'
			u = check_dir(self.path, True)
			if u == None:
				break
			elif u:
				u.append('test')
				self.parent.after(1, self.parent.update_files, map(lambda f: f.replace(self.path,''),u))
			time.sleep(self.delay)
		self.thread = None

	def start(self):
		if self.thread == None:
			self.thread = start_new_thread(self.check_update,(0,))

	def end(self):
		if self.thread != None:
			self.cont = False

	def __nonzero__(self):
		return self.thread != None

class UpdateFiles(PyMSDialog):
	def __init__(self, parent, files):
		self.files = files
		PyMSDialog.__init__(self, parent, 'Files Edited', resizable=(False, False))

	def widgetize(self):
		Label(self, text='These files have been modified since they were extracted.\n\nChoose which files to update the archive with:', justify=LEFT, anchor=W).pack(fill=X)
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, activestyle=DOTBOX, selectmode=MULTIPLE, font=couriernew, width=20, height=10, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
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
		for f in self.files:
			self.listbox.insert(END,f)
			self.listbox.select_set(END)
		btns = Frame(self)
		save = Button(btns, text='Ok', width=10, command=self.ok)
		save.pack(side=LEFT, pady=5, padx=3)
		Button(btns, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, pady=5, padx=3)
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

	def cancel(self):
		self.files = []
		PyMSDialog.ok(self)

	def ok(self):
		self.files = []
		for i in self.listbox.curselection():
			self.files.append(self.listbox.get(i))
		PyMSDialog.ok(self)

class GeneralSettings(Frame):
	def __init__(self, parent, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		Frame.__init__(self, parent)
		self.maxfiles = IntegerVar(1,[1,65535])
		self.maxfiles.set(PYMPQ_SETTINGS.settings.defaults.get('maxfiles'))
		self.localeid = IntegerVar(0,[0,65535])
		self.localeid.set(PYMPQ_SETTINGS.settings.defaults.get('locale'))
		self.blocksize = IntegerVar(1,[1,23])
		self.blocksize.set(PYMPQ_SETTINGS.settings.defaults.get('blocksize'))
		f = Frame(self)
		Label(f, text='Max Files', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
		Label(f, text='Max file capacity for new archives (cannot be changed for an existing archive)', anchor=W).pack(fill=X, expand=1)
		Entry(f, textvariable=self.maxfiles, width=5).pack(side=LEFT)
		f.pack(side=TOP, fill=X)
		f = Frame(self)
		Label(f, text='Locale ID', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
		Entry(f, textvariable=self.localeid, width=5).pack(side=LEFT)
		f.pack(side=TOP, fill=X, pady=10)
		f = Frame(self)
		Label(f, text='Block Size', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X, expand=1)
		Label(f, text='Block size for new archives (default is 3)', anchor=W).pack(fill=X, expand=1)
		Entry(f, textvariable=self.blocksize, width=2).pack(side=LEFT)
		f.pack(side=TOP, fill=X)

	def save(self):
		PYMPQ_SETTINGS.settings.default.maxfiles = self.maxfiles.get()
		PYMPQ_SETTINGS.settings.default.locale = self.localeid.get()
		PYMPQ_SETTINGS.settings.default.blocksize = self.blocksize.get()

class ListfileSettings(Frame):
	def __init__(self, parent, setdlg=None):
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		Frame.__init__(self, parent)
		Label(self, text='File Lists', font=('Courier', -12, 'bold'), anchor=W).pack(fill=X)
		Label(self, text="Note: Each file list added will increase the load time for archives", anchor=W, justify=LEFT).pack(fill=X)
		self.listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, width=35, height=1, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
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
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for l in PYMPQ_SETTINGS.settings.get('listfiles', []):
			self.listbox.insert(0,l)
		if self.listbox.size():
			self.listbox.select_set(0)

		buttons = [
			('add', self.add, 'Add MPQ (Insert)', NORMAL, 'Insert', LEFT),
			('remove', self.remove, 'Remove MPQ (Delete)', DISABLED, 'Delete', RIGHT),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
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

	def action_states(self):
		self.buttons['remove']['state'] = [NORMAL,DISABLED][not self.listbox.curselection()]

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

	def add(self, key=None):
		add = PYMPQ_SETTINGS.lastpath.settings.select_files('listfiles', self, 'Add Listfiles', '.txt', [('Text files','*.txt'),('All Files','*')])
		if add:
			error = []
			for i in add:
				self.listbox.insert(END,i)
			self.action_states()
			self.setdlg.edited = True

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.setdlg.edited = True

	def save(self):
		PYMPQ_SETTINGS.settings.listfiles = []
		for i in range(self.listbox.size()):
			PYMPQ_SETTINGS.settings.listfiles.append(self.listbox.get(i))

class CompressionSettings(Frame):
	def __init__(self, parent, setdlg=None):
		self.autocompression = PYMPQ_SETTINGS.settings.autocompression.deepcopy()
		if setdlg == None:
			self.setdlg = parent.parent
		else:
			self.setdlg = setdlg
		Frame.__init__(self, parent)
		self.extension = SStringVar(callback=self.addstate)
		left = Frame(self)
		Label(left, text='File Extension:', anchor=W, justify=LEFT).pack(fill=X)
		e = Frame(left)
		Entry(e, textvariable=self.extension).pack(side=LEFT, fill=X, expand=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','add.gif'))
		self.addbutton = Button(e, image=image, width=20, height=20, command=self.add, state=DISABLED)
		self.addbutton.image = image
		self.addbutton.pack(side=LEFT, padx=2)
		e.pack(side=TOP)
		self.listframe = Frame(left, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(self.listframe)
		self.listbox = Listbox(self.listframe, width=15, height=1, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
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
		self.listbox.bind('<ButtonRelease-1>', self.action_states)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		self.listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for l in [None] + self.autocompression.keys():
			if l == None:
				l = 'Default'
			elif l == 'Default':
				continue
			self.listbox.insert(END,l)
		self.listbox.select_set(0)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','remove.gif'))
		self.rembutton = Button(left, image=image, width=20, height=20, command=self.remove, state=DISABLED)
		self.rembutton.image = image
		self.rembutton.pack()
		left.pack(side=LEFT, fill=Y, padx=2)

		self.compression = IntVar()
		right = Frame(self)
		Label(right, text='Compression Type:', anchor=W, justify=LEFT).pack(fill=X)
		DropDown(right, self.compression, ['None','Standard','Deflate','Audio'], self.choosecompression).pack(fill=X)
		self.complevel = IntVar()
		self.level = None
		self.levels = []
		self.levels.append(Frame(right))
		Label(self.levels[-1], text='Compression Level:', anchor=W, justify=LEFT).pack(fill=X)
		l = []
		for n in range(-1,10):
			if n == -1:
				l.append('Default')
			elif n == 0:
				l.append('0 (None)')
			elif n == 1:
				l.append('1 (Best Speed)')
			elif n == 9:
				l.append('9 (Best Compression)')
			else:
				l.append(str(n))
		DropDown(self.levels[-1], self.complevel, l, self.compresslevel).pack(fill=X)
		self.levels.append(LabelFrame(right, text='Compression Level'))
		f = Frame(self.levels[-1])
		Radiobutton(f, text='Lowest (Best Quality)', variable=self.complevel, value=0, command=lambda: self.compresslevel(0)).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(self.levels[-1])
		Radiobutton(f, text='Medium', variable=self.complevel, value=1, command=lambda: self.compresslevel(1)).pack(side=LEFT)
		f.pack(fill=X)
		f = Frame(self.levels[-1])
		Radiobutton(f, text='Highest (Least Space)', variable=self.complevel, value=2, command=lambda: self.compresslevel(2)).pack(side=LEFT)
		f.pack(fill=X)
		right.pack(side=LEFT, fill=BOTH, expand=1, padx=2)
		self.action_states()

	def addstate(self, val):
		if val:
			self.addbutton['state'] = NORMAL
		else:
			self.addbutton['state'] = DISABLED

	def action_states(self, k=None):
		s = int(self.listbox.curselection()[0])
		self.rembutton['state'] = [NORMAL,DISABLED][not s]
		self.set = True
		self.compression.set(self.autocompression[self.listbox.get(s)][0])
		if self.compression.get() > 1:
			self.complevel.set(self.autocompression[self.listbox.get(s)][1])
		self.set = False

	def choosecompression(self, type):
		if self.level:
			self.level.forget()
		s = int(self.listbox.curselection()[0])
		if not self.set:
			self.autocompression[self.listbox.get(s)] = [type,0]
		if type > 1:
			self.level = self.levels[type-2]
			if type == 2:
				self.level.pack(pady=5, fill=X)
			else:
				self.level.pack(pady=5)
			if not self.set:
				self.complevel.set(0)

	def compresslevel(self, level):
		s = int(self.listbox.curselection()[0])
		self.autocompression[self.listbox.get(s)][1] = level

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
	
	def add(self, key=None):
		if self.addbutton['state'] == DISABLED:
			return
		e = self.extension.get()
		if not e.startswith(os.extsep):
			e = os.extsep + e
		self.extension.set('')
		self.addbutton['state'] = DISABLED
		if not e in self.autocompression:
			self.autocompression[e] = [0,0]
			s = self.listbox.size()
			self.listbox.insert(END,e)
			self.listbox.select_clear(0,END)
			self.listbox.select_set(s)
			self.listbox.see(s)
			self.setdlg.edited = True
			self.action_states()

	def remove(self, key=None):
		if self.rembutton['state'] == DISABLED:
			return
		s = int(self.listbox.curselection()[0])
		del self.autocompression[self.listbox.get(s)]
		self.listbox.delete(s)
		if s == self.listbox.size():
			s -= 1
		self.listbox.select_set(s)
		self.listbox.see(s)
		self.setdlg.edited = True
		self.action_states()

	def save(self):
		PYMPQ_SETTINGS.settings.autocompression = self.autocompression

class FolderDialog(PyMSDialog):
	def __init__(self, parent):
		self.save = True
		self.result = StringVar()
		self.result.set(PYMPQ_SETTINGS['import'].get('add_folder', ''))
		PyMSDialog.__init__(self, parent, 'Folder name...')

	def widgetize(self):
		Label(self, text='The text in the box below will be put at the beginnings of the\nnames of every file you selected.\n\nExample: If "title.wav" is the original filename, and you type\n"music\\" the file will become "music\\title.wav"', anchor=W, justify=LEFT).pack(padx=5, pady=5)
		entry = Entry(self, textvariable=self.result)
		entry.icursor(END)
		entry.pack(padx=5, fill=X)

		buttons = Frame(self)
		Button(buttons, text='Ok', width=10, command=self.ok).pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		self.bind('<Return>', self.ok)
		def select_all(*_):
			entry.select_to(END)
			entry.icursor(END)
		self.bind('<Control-a>', select_all)

		return entry

	def cancel(self):
		self.save = False
		PyMSDialog.cancel(self)

	def ok(self, *_):
		PYMPQ_SETTINGS['import'].add_folder = self.result.get()
		PyMSDialog.ok(self)

class LocaleDialog(PyMSDialog):
	def __init__(self, parent, locale=0):
		self.save = True
		self.result = IntegerVar(0,[0,65535])
		self.result.set(locale)
		PyMSDialog.__init__(self, parent, 'Change Locale ID...')

	def widgetize(self):
		Label(self, text='Type in the new locale id for the select files below:', anchor=W, justify=LEFT).pack(padx=5, pady=5)
		Entry(self, textvariable=self.result, width=5).pack()

		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=10, command=self.cancel).pack(padx=3, pady=3)
		buttons.pack()

		return ok

	def cancel(self):
		self.save = False
		PyMSDialog.cancel(self)

class PyMPQ(Tk):
	def __init__(self, guifile=None):
		#Window
		Tk.__init__(self)
		self.title('PyMPQ %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyMPQ.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyMPQ.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		ga.set_application('PyMPQ', VERSIONS['PyMPQ'])
		ga.track(GAScreen('PyMPQ'))
		setup_trace(self, 'PyMPQ')

		self.file = None
		self.files = []
		self.totalsize = 0
		self.id = int(time.time())
		self.thread = CheckThread(self, os.path.join(BASE_DIR,'Libs','Temp',str(self.id),''))

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('add', self.add, 'Add Files (Ctrl+I)', DISABLED, 'Ctrl+I'),
			('openfolder', self.adddir, 'Add Directory (Ctrl+D)', DISABLED, 'Ctrl+D'),
			('remove', self.remove, 'Delete Files (Delete)', DISABLED, 'Delete'),
			('export', self.extract, 'Extract Files (Ctrl+E)', DISABLED, 'Ctrl+Alt+E'),
			5,
			('edit', self.rename, 'Rename File (Ctrl+R)', DISABLED, 'Ctrl+R'),
			('debug', self.compact, 'Compact Archive (Ctrl+P)', DISABLED, 'Ctrl+P'),
			#('insert', self.editlistfile, 'Edit Internal Listfile (Ctrl+L)', DISABLED, 'Ctrl+L'),
			10,
			('asc3topyai', self.mansets, 'Manage Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.mpq editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyMPQ', NORMAL, ''),
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

		self.regex = IntVar()
		self.regex.set(PYMPQ_SETTINGS.get('regex', False))
		self.filter = StringVar()
		self.filter.set(['*','.+'][self.regex.get()])
		filter = Frame(self)
		Label(filter, text='Filter: ').pack(side=LEFT)
		self.textdrop = TextDropDown(filter, self.filter, PYMPQ_SETTINGS.get('filters', []))
		self.textdrop.pack(side=LEFT, fill=X, expand=1)
		self.textdrop.entry.bind('<Return>', self.dofilter)
		self.textdrop.c = self.textdrop.entry['bg']
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))
		b = Button(filter, image=image, width=20, height=20, command=self.dofilter, state=DISABLED)
		b.image = image
		b.tooltip = Tooltip(b, 'List Matches')
		b.pack(side=LEFT, padx=2)
		self.buttons['find'] = b
		Radiobutton(filter, text='Regex', variable=self.regex, value=1).pack(side=RIGHT)
		Radiobutton(filter, text='Wildcard', variable=self.regex, value=0).pack(side=RIGHT)
		filter.pack(side=TOP, fill=X)

		self.encvar = IntVar()
		self.compvar = IntVar()

		self.setmenu = Menu(self, tearoff=0)
		self.compmenu = Menu(self.setmenu, tearoff=0)
		self.deflatemenu = Menu(self.compmenu, tearoff=0)
		for n in range(-1,10):
			a = ''
			if n == -1:
				l = 'Default'
				a = 'F9' 
			elif n == 0:
				l = '0 (None)'
			elif n == 1:
				l = '1 (Best Speed)'
			elif n == 9:
				l = '9 (Best Compression)'
			else:
				l = str(n)
			self.deflatemenu.add_radiobutton(label=l, command=lambda c=2,l=n+1: self.compress(c,l), underline=0, variable=self.compvar, value=3 + n, accelerator=a)
		self.audiomenu = Menu(self.compmenu, tearoff=0)
		self.audiomenu.add_radiobutton(label='Lowest (Best Quality)', command=lambda c=3,l=0: self.compress(c,l), underline=0, variable=self.compvar, value=13, accelerator='F6')
		self.audiomenu.add_radiobutton(label='Medium', command=lambda c=3,l=1: self.compress(c,l), underline=0, variable=self.compvar, value=14, accelerator='F7')
		self.audiomenu.add_radiobutton(label='Highest (Least Space)', command=lambda c=3,l=2: self.compress(c,l), underline=0, variable=self.compvar, value=15, accelerator='F8')
		self.compmenu.add_radiobutton(label='Auto-Select', command=lambda c=4,l=0: self.compress(c,l), underline=0, variable=self.compvar, value=16, accelerator='F4')
		self.compmenu.add_separator()
		self.compmenu.add_radiobutton(label='None', command=lambda c=0,l=0: self.compress(c,l), underline=0, variable=self.compvar, value=0, accelerator='F2')
		self.compmenu.add_radiobutton(label='Standard', command=lambda c=1,l=0: self.compress(c,l), underline=0, variable=self.compvar, value=1, accelerator='F3')
		self.compmenu.add_cascade(label='Deflate', menu=self.deflatemenu, underline=0)
		self.compmenu.add_cascade(label='Audio', menu=self.audiomenu, underline=0)
		self.setmenu.add_command(label='Settings Dialog', command=lambda: self.mansets(1), underline=0, accelerator='Ctrl+M')
		self.setmenu.add_separator()
		self.setmenu.add_cascade(label='Compression', menu=self.compmenu, underline=0)
		self.setmenu.add_checkbutton(label='Encrypt', command=self.encrypt, underline=0, variable=self.encvar, accelerator='F5')

		self.listmenu = Menu(self, tearoff=0)
		self.listmenu.add_command(label='Open', command=self.openfile, underline=0)
		self.listmenu.add_separator()
		self.listmenu.add_command(label='Extract', command=self.extract, underline=0)
		self.listmenu.add_command(label='Delete', command=self.remove, underline=0)
		self.listmenu.add_command(label='Rename', command=self.rename, underline=0)
		self.listmenu.add_command(label='Change Locale', command=self.changelocale, underline=0)
		self.listbox = ReportList(self, ['Name','Size','Ratio','Packed','Locale','Attributes',None], EXTENDED, self.select, self.do_rename, self.popup, self.openfile, min_widths=[50]*6)
		self.listbox.arrows = [PhotoImage(file=os.path.join(BASE_DIR,'Images','arrow.gif')),PhotoImage(file=os.path.join(BASE_DIR,'Images','arrowup.gif')),PhotoImage(file=os.path.join(BASE_DIR,'Images','arrowblank.gif'))]
		for n,b in enumerate(self.listbox.columns):
			if n != 6:
				b[0]['command'] = lambda n=n: self.sort(n)
			b[0]['compound'] = LEFT
			b[0]['image'] = self.listbox.arrows[2]
		self.update_list()
		self.listbox.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.selected = StringVar()
		self.info = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=25, anchor=W).pack(side=LEFT, padx=1)
		Label(statusbar, textvariable=self.selected, bd=1, relief=SUNKEN, width=30, anchor=W).pack(side=LEFT, padx=1)
		Label(statusbar, textvariable=self.info, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Open or create an MPQ.')
		statusbar.pack(side=BOTTOM, fill=X)

		PYMPQ_SETTINGS.windows.load_window_size('main', self, default_size=(700,500))
		PYMPQ_SETTINGS.load_pane_sizes('list_sizes', self.listbox.panes, (317,74,45,67,52,64))

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyMPQ'))

	def open_files(self):
		return not SFileSetLocale(PYMPQ_SETTINGS.settings.defaults.get('locale', 0))

	def compress(self, c, l):
		PYMPQ_SETTINGS.settings.compress = [c,l]

	def encrypt(self):
		PYMPQ_SETTINGS.settings.encrypt = not PYMPQ_SETTINGS.settings.get('encrypt', False)

	def sort(self, n):
		sort = PYMPQ_SETTINGS.get('sort')
		if n == sort[0]:
			PYMPQ_SETTINGS.sort[1] = not sort[1]
		else:
			PYMPQ_SETTINGS.sort[2] = sort[0]
			PYMPQ_SETTINGS.sort[0] = n
			PYMPQ_SETTINGS.sort[1] = False
		self.update_list()

	def select(self):
		if self.file:
			s = self.listbox.cur_selection()
			t = 0
			for i in s:
				t += self.files[i].fullSize
			self.selected.set('Selected %s files, %s' % (len(s),size(t)))
		else:
			self.selected.set('')
		self.action_states()

	def action_states(self):
		f = [NORMAL,DISABLED][not self.file]
		s = [NORMAL,DISABLED][not self.listbox.cur_selection()]
		for b in ['close','add','openfolder','find']:#,'insert']:
			self.buttons[b]['state'] = f
		for b in ['remove','export','edit']:
			self.buttons[b]['state'] = s

	def dofilter(self, e=None):
		if self.file:
			f = self.filter.get()
			filters = PYMPQ_SETTINGS.get('filters', [])
			if f in filters:
				filters.remove(f)
			filters.append(self.filter.get())
			if len(filters) > 10:
				del filters[0]
			if self.files:
				self.update_list()

	def list_files(self, h=-1):
		close = False
		if h == -1:
			close = True
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Read MPQ (List Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		self.files = []
		self.totalsize = 0
		for e in SFileListFiles(h, str('\r\n'.join(PYMPQ_SETTINGS.settings.get('listfiles', [])))):
			if e.fileExists:
				self.files.append(e)
				self.totalsize += e.fullSize
		if close:
			MpqCloseUpdatedArchive(h)

	def updatecolor(self):
		self.textdrop.entry['bg'] = self.textdrop.c
		self.resettimer = None

	def update_list(self):
		sort = PYMPQ_SETTINGS.get('sort')
		if sort[2] != None:
			self.listbox.columns[sort[2]][0]['image'] = self.listbox.arrows[2]
			sort[2] = None
		self.listbox.columns[sort[0]][0]['image'] = self.listbox.arrows[sort[1]]
		sel = []
		if self.listbox.size():
			for i in self.listbox.cur_selection():
				sel.append(tuple(self.listbox.get(i)))
			self.listbox.delete(ALL)
		if self.file and self.files:
			s = [6,4,3,2,1,5]
			o = [6,2,3,4,1,5]
			del o[o.index(s[sort[0]])]
			o.insert(0, s[sort[0]])
			def keysort(l):
				t = list(l)
				t[6] = t[6].lower()
				return map(lambda i: t[i], o)
			self.files.sort(key=keysort, reverse=sort[1])
			check = True
			s = self.filter.get()
			if not self.regex.get():
				if not s.replace('*','').replace('?',''):
					check = False
				s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
			elif s == '.+':
				check = False
			if check:
				try:
					r = re.compile(s)
				except:
					check = False
					self.resettimer = self.after(1000, self.updatecolor)
					self.textdrop.entry['bg'] = '#FFB4B4'
			for f in self.files:
				if check and not r.match(f.fileName):
					continue
				if f.fullSize:
					p = '%i%%' % (f.compressedSize / float(f.fullSize) * 100)
				else:
					p = '0%'
				i = (f.fileName,size(f.fullSize),p,size(f.compressedSize),str(f.locale),''.join([[l,'-'][not (f.flags & a)] for l,a in [('C',MAFA_COMPRESS | MAFA_COMPRESS2),('E',MAFA_ENCRYPT),('X',MAFA_MODCRYPTKEY)]]),'')
				self.listbox.insert(END, i)
				if i in sel:
					self.listbox.select_set(END)
		self.action_states()

	def update_info(self, h=None):
		if self.file or h:
			close = False
			if h == None:
				close = True
				h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Read MPQ (Update Info)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			f = SFileGetFileInfo(h,SFILE_INFO_NUM_FILES)
			self.info.set('Total %s/%s files, %s' % (len(self.files),f,size(self.totalsize)))
			self.buttons['debug']['state'] = [DISABLED,NORMAL][f > len(self.files)]
			if close:
				MpqCloseUpdatedArchive(h)
		else:
			self.info.set('')

	def do_rename(self, entry, new):
		l = self.listbox.get(entry)
		success = False
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if not SFInvalidHandle(h) and MpqRenameAndSetFileLocale(h, l[0], new, int(l[4]), int(l[4])):
			success = True
		MpqCloseUpdatedArchive(h)
		return success

	def flagcomp(self, file=None):
		if isinstance(file,list):
			c = file
		else:
			c = PYMPQ_SETTINGS.get('compress')
		f,l = MAFA_REPLACE_EXISTING,0
		if c[0]:
			f |= MAFA_COMPRESS
			if [0] == 2:
				l = c[1]
			elif c[0] == 3:
				l = [MAWA_QUALITY_LOW,MAWA_QUALITY_MEDIUM,MAWA_QUALITY_HIGH][c[1]]
			elif c[0] == 4:
				e = os.extsep + file.split(os.extsep)[-1]
				if e in PYMPQ_SETTINGS.autocompression:
					return self.flagcomp(PYMPQ_SETTINGS.autocompression[e])
				return self.flagcomp(PYMPQ_SETTINGS.autocompression.Default)
		if PYMPQ_SETTINGS.get('encrypt', False):
			f |= MAFA_ENCRYPT
		return (f,[0,MAFA_COMPRESS_STANDARD,MAFA_COMPRESS_DEFLATE,MAFA_COMPRESS_WAVE][c[0]],l)

	def popup(self, e, i):
		if not self.listbox.cur_selection():
			self.listbox.select_set(i)
		self.listmenu.post(*self.winfo_pointerxy())

	def changelocale(self):
		l = LocaleDialog(self)
		if l.save:
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Write MPQ (Change Locale)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			l = l.result.get()
			for i in self.listbox.cur_selection():
				if self.files[i].locale != l and MpqSetFileLocale(h, self.files[i].fileName, self.files[i].locale, l):
					self.files[i].locale = l
			MpqCloseUpdatedArchive(h)
			self.update_list()

	def openfile(self, e=None):
		path = os.path.join(BASE_DIR,'Libs','Temp',str(self.id))
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Open MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for i in self.listbox.cur_selection():
			n = self.listbox.get(i)[0]
			try:
				os.makedirs(os.path.join(path,os.path.dirname(n)))
			except (OSError, IOError), e:
				if e.errno != 17:
					raise
			fh = SFileOpenFileEx(h, n)
			if fh:
				r = SFileReadFile(fh)
				SFileCloseFile(fh)
				fn = os.path.join(path,n)
				f = open(fn,'wb')
				f.write(r[0])
				f.close()
				start_new_thread(os.system, ('"%s"' % fn,))
		if not self.thread:
			self.thread.start()
		MpqCloseUpdatedArchive(h)

	def update_files(self, fs):
		p = os.path.join(BASE_DIR,'Libs','Temp',str(self.id),'')
		if len(fs) == 1:
			if not askyesno(parent=self, title='File Edited', message='File "%s" has been modified since it was extracted.\n\nUpdate the archive with this file?' % fs[0]):
				return
		else:
			u = UpdateFiles(self, fs)
			if not u.files:
				return
			fs = u.files
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Write MPQ (Update Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		fc = None
		for file in fs:
			if fc == None or PYMPQ_SETTINGS.get('compress')[0] == 4:
				fc = self.flagcomp(file)
			MpqAddFileToArchiveEx(h, os.path.join(BASE_DIR,'Libs','Temp',str(self.id),file), file, *fc)
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def new(self, key=None):
		file = PYMPQ_SETTINGS.lastpath.mpq.select_file('new', self, 'Save new MPQ', '.mpq', [('StarCraft MPQ','*.mpq'),('Embedded MPQ','*.exe'),('StarCraft Map','*.scm'),('BroodWar Map','*.scx'),('All Files','*')], save=True)
		if file:
			h = MpqOpenArchiveForUpdateEx(file, MOAU_CREATE_ALWAYS, PYMPQ_SETTINGS.settings.defaults.get('maxfiles'), PYMPQ_SETTINGS.settings.defaults.get('blocksize'))
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('New MPQ', "The MPQ could not be created/opened."))
				return
			MpqCloseUpdatedArchive(h)
			self.file = file
			self.files = []
			self.totalsize = 0
			self.status.set('Editing new MPQ.')
			self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
			self.update_list()
			self.select()

	def open(self, key=None, file=None):
		if file == None:
			file = PYMPQ_SETTINGS.lastpath.mpq.select_file('open', self, 'Open MPQ', '.mpq', [('Any MPQ', '*.mpq;*.exe;*.scm;*.scx'),('StarCraft MPQ','*.mpq'),('Embedded MPQ','*.exe'),('StarCraft Map','*.scm'),('BroodWar Map','*.scx'),('All Files','*')])
			if not file:
				return
		h = MpqOpenArchiveForUpdateEx(file, MOAU_OPEN_EXISTING | MOAU_READ_ONLY)
		if SFInvalidHandle(h):
			askquestion(parent=self, title='Open', message='There is no MPQ in "%s".' % file, type=OK)
			return
		self.file = file
		self.title('PyMPQ %s (%s)' % (LONG_VERSION,file))
		self.status.set('Load Successful!')
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		self.file = None
		self.files = []
		self.title('PyMPQ %s' % LONG_VERSION)
		self.status.set('Open or create an MPQ.')
		self.update_info()
		self.update_list()
		self.select()

	def add(self, key=None):
		if key and self.buttons['add']['state'] != NORMAL:
			return
		files = PYMPQ_SETTINGS.lastpath.files.select_files('import', self, 'Add files...', '*', [('All Files','*')])
		if files:
			f = FolderDialog(self)
			if f.save:
				PYMPQ_SETTINGS['import'].add_folder = f.result.get()
				h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
				if SFInvalidHandle(h):
					ErrorDialog(self, PyMSError('Write MPQ (Add File)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
					return
				fc = None
				for file in files:
					p = os.path.basename(file)
					folder = PYMPQ_SETTINGS['import'].get('add_folder', '')
					if folder:
						p = folder + p
					if fc == None or PYMPQ_SETTINGS.get('compress')[0] == 4:
						fc = self.flagcomp(file)
					MpqAddFileToArchiveEx(h, file, p, *fc)
				self.list_files(h)
				self.update_info(h)
				MpqCloseUpdatedArchive(h)
				self.update_list()
				self.select()

	def adddir(self, key=None):
		if key and self.buttons['openfolder']['state'] != NORMAL:
			return
		path = PYMPQ_SETTINGS.lastpath.files.select_directory('import_dir', self, 'Add files from folder...')
		if not path:
			return
		path = os.path.join(path,'')
		fo = FolderDialog(self)
		if fo.save:
			h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
			if SFInvalidHandle(h):
				ErrorDialog(self, PyMSError('Write MPQ (Add Folder)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
				return
			fc = None
			for p in os.walk(path):
				folder = PYMPQ_SETTINGS['import'].get('add_folder', '')
				path_folder = p[0].replace(path,'')
				if path_folder:
					folder += path_folder + '\\'
				for f in p[2]:
					if folder:
						p = folder + f
					else:
						p = f
					if fc == None or PYMPQ_SETTINGS.get('compress')[0] == 4:
						fc = self.flagcomp(f)
					MpqAddFileToArchiveEx(h, os.path.join(path,f), p, *fc)
			self.list_files(h)
			self.update_info(h)
			MpqCloseUpdatedArchive(h)
			self.update_list()
			self.select()

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING | MOAU_MAINTAIN_LISTFILE)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Write MPQ (Remove Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for i in self.listbox.cur_selection():
			l = self.listbox.get(i)
			MpqDeleteFileWithLocale(h, l[0], int(l[4]))
		self.list_files(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)
		self.update_list()
		self.select()

	def rename(self, key=None):
		if key and self.buttons['edit']['state'] != NORMAL:
			return
		self.listbox.columns[0][1].edit()

	# def editlistfile(self, key=None):
		# if key and self.buttons['insert']['state'] != NORMAL:
			# return
		# pass

	def extract(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		path = PYMPQ_SETTINGS.lastpath.files.select_directory('export', self, 'Extract files...')
		if not path:
			return
		h = SFileOpenArchive(self.file)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Read MPQ (Extract Files)', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		for i in self.listbox.cur_selection():
			n = self.listbox.get(i)[0]
			p = n.split('\\')
			try:
				os.makedirs(os.path.join(path,*p[:-1]))
			except (OSError, IOError), e:
				if e.errno != 17:
					raise
			fh = SFileOpenFileEx(h, n)
			if fh:
				r = SFileReadFile(fh)
				SFileCloseFile(fh)
				f = open(os.path.join(path,*p),'wb')
				f.write(r[0])
				f.close()
			else:
				ErrorDialog(self, PyMSError('Extract', "Couldn't load file '%s'" % n))
		SFileCloseArchive(h)

	def mansets(self, key=None):
		if key:
			SettingsDialog(self, [('General',GeneralSettings),('List Files',ListfileSettings),('Compression Auto-Selection',CompressionSettings)], (400,255), None, settings=PYMPQ_SETTINGS)
		else:
			compress = PYMPQ_SETTINGS.get('compress')
			self.compvar.set([0,1,2,13,16][compress[0]] + compress[1])
			self.setmenu.post(*self.winfo_pointerxy())

	def compact(self, key=None):
		h = MpqOpenArchiveForUpdate(self.file, MOAU_OPEN_EXISTING)
		if SFInvalidHandle(h):
			ErrorDialog(self, PyMSError('Compact MPQ', "The MPQ could not be opened. Other non-PyMS programs may lock MPQ's while open. Please try closing any programs that might be locking your MPQ."))
			return
		MpqCompactArchive(h)
		self.update_info(h)
		MpqCloseUpdatedArchive(h)

	def register(self, e=None):
		try:
			register_registry('PyMPQ','','mpq',os.path.join(BASE_DIR, 'PyMPQ.pyw'),os.path.join(BASE_DIR,'Images','PyMPQ.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyMPQ.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyMPQ', LONG_VERSION)

	def exit(self, e=None):
		self.thread.end()
		removedir(os.path.join(BASE_DIR,'Libs','Temp',str(self.id)))
		PYMPQ_SETTINGS.windows.save_window_size('main', self)
		PYMPQ_SETTINGS.save_pane_sizes('list_sizes', self.listbox.panes)
		PYMPQ_SETTINGS.save()
		self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pympq.py','pympq.pyw','pympq.exe']):
		gui = PyMPQ()
		gui.startup()
	else:
		p = optparse.OptionParser(usage='usage: PyMPQ [options] <inp> [out]', version='PyMPQ %s' % LONG_VERSION)
		# p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a GOT file [default]", default=True)
		# p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a GOT file")
		# p.add_option('-t', '--trig', help="Used to compile a TRG file to a GOT compatable TRG file")
		# p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for settings at the top of the file [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyMPQ(opt.gui)
			gui.startup()
		# else:
		# 	if not len(args) in [1,2]:
		# 		p.error('Invalid amount of arguments')
		# 	path = os.path.dirname(args[0])
		# 	if not path:
		# 		path = os.path.abspath('')
		# 	got = GOT.GOT()
		# 	if len(args) == 1:
		# 		if opt.convert:
		# 			ext = 'txt'
		# 		else:
		# 			ext = 'got'
		# 		args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
		# 	try:
		# 		if opt.convert:
		# 			print "Reading GOT '%s'..." % args[0]
		# 			got.load_file(args[0])
		# 			print " - '%s' read successfully\nDecompiling GOT file '%s'..." % (args[0],args[0])
		# 			got.decompile(args[1], opt.reference)
		# 			print " - '%s' written succesfully" % args[1]
		# 		else:
		# 			print "Interpreting file '%s'..." % args[0]
		# 			got.interpret(args[0])
		# 			print " - '%s' read successfully\nCompiling file '%s' to GOT format..." % (args[0],args[0])
		# 			lo.compile(args[1])
		# 			print " - '%s' written succesfully" % args[1]
		# 			if opt.trig:
		# 				print "Reading TRG '%s'..." % args[0]
		# 				trg = TRG.TRG()
		# 				trg.load_file(opt.trig)
		# 				print " - '%s' read successfully" % args[0]
		# 				path = os.path.dirname(opt.trig)
		# 				if not path:
		# 					path = os.path.abspath('')
		# 				file = '%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[1]).split(os.extsep)[:-1])), os.extsep, 'trg')
		# 				print "Compiling file '%s' to GOT compatable TRG..." % file
		# 				trg.compile(file, True)
		# 				print " - '%s' written succesfully" % file
		# 	except PyMSError, e:
		# 		print repr(e)

if __name__ == '__main__':
	main()