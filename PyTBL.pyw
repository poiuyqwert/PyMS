from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import TBL,FNT,PCX,GRP,PAL

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys, re

VERSION = (1,8)
LONG_VERSION = 'v%s.%s' % VERSION

class PreviewDialog(PyMSDialog):
	letter_space = 1
	space_space = 4

	def __init__(self, parent):
		self.icons = {}
		self.hotkey = IntVar()
		self.hotkey.set(parent.settings.get('hotkey',1))
		self.endatnull = IntVar()
		self.endatnull.set(parent.settings.get('endatnull',1))
		PyMSDialog.__init__(self, parent, 'Text Previewer', resizable=(False,False))

	def geticon(self, n, f):
		if not n in self.icons:
			i = GRP.frame_to_photo(self.parent.unitpal.palette, self.parent.icons, f)
			self.icons[n] = (i[0],(i[2]+1,i[4],0,0))
		return self.icons[n]

	def preview(self, e=None):
		self.canvas.delete(ALL)
		self.canvas.characters = {}
		text = TBL.compile_string(self.parent.text.get('1.0',END)[:-1])
		if text:
			color = 2
			display = []
			hotkey = ord(text[1])
			if self.hotkey.get() and hotkey < 6:
				text = text[2:]
				if self.endatnull.get() and '\x00' in text:
					text = text[:text.index('\x00')]
				if hotkey == 1:
					text += '\n \x02200  100  2'
				elif hotkey == 2:
					text += '\n\x02Next Level: 1\n 100  100'
				elif hotkey == 3:
					text += '\n \x0275'
				elif hotkey in [4,5]:
					text += '\n \x02150  50'
				fnt = self.parent.font8
			else:
				if self.endatnull.get() and '\x00' in text:
					text = text[:text.index('\x00')]
				fnt = self.parent.font10
			width = 200
			for l in re.split('[\x0A\x0C]',text):
				w = 0
				display.append([])
				for c in l:
					a = ord(c)
					if a >= fnt.start and a < fnt.start + len(fnt.letters):
						a -= fnt.start
						if ord(c) == 32 and not fnt.sizes[a][0]:
							fnt.sizes[a][0] = self.space_space
						w += fnt.sizes[a][0] + self.letter_space
						if not c in self.canvas.characters:
							self.canvas.characters[c] = {}
						if not color in self.canvas.characters[c]:
							self.canvas.characters[c][color] = (FNT.letter_to_photo(self.parent.tfontgam, fnt.letters[a], color), fnt.sizes[a])
						display[-1].append(self.canvas.characters[c][color])
					elif a in FNT.COLOR_CODES_INGAME and not color in FNT.COLOR_OVERPOWER:
						color = a
				if w > width:
					width = w
			if self.hotkey.get() and hotkey and hotkey < 6:
				if hotkey == 1:
					display[-1][0] = self.geticon('mins',0)
					display[-1][5] = self.geticon('gas',1)
					display[-1][10] = self.geticon('supply',4)
				elif hotkey == 2:
					display[-1][0] = self.geticon('mins',0)
					display[-1][5] = self.geticon('gas',1)
				elif hotkey == 3:
					display[-1][0] = self.geticon('energy',7)
				elif hotkey in [4,5]:
					display[-1][0] = self.geticon('mins',0)
					display[-1][6] = self.geticon('gas',1)
			self.canvas.config(width=width+10, height=fnt.height*len(display)+10)
			y = 7
			for letters in display:
				x = 7
				for l in letters:
					self.canvas.create_image(x - l[1][2], y, image=l[0], anchor=NW)
					x += l[1][0] + self.letter_space
				y += fnt.height

	def widgetize(self):
		self.canvas = Canvas(self, width=200, height=16, background='#000000', bd=2, relief=SUNKEN)
		self.canvas.pack(padx=5, pady=5)
		f = Frame(self)
		Checkbutton(f, text='Hotkey String', variable=self.hotkey, command=self.preview).pack(side=LEFT)
		Checkbutton(f, text='End at Null', variable=self.endatnull, command=self.preview).pack(side=LEFT)
		f.pack()
		self.preview()
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=3)
		return ok

	def ok(self):
		self.parent.settings['hotkey'] = self.hotkey.get()
		self.parent.settings['endatnull'] = self.endatnull.get()
		PyMSDialog.ok(self)

class FindDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False, escape=True, resizable=(True,False))

	def widgetize(self):
		self.find = StringVar()
		self.casesens = BooleanVar()
		self.regex = BooleanVar()
		self.updown = IntVar()
		self.updown.set(1)
		self.wrap = BooleanVar()
		self.wrap.set(True)

		l = Frame(self)
		f = Frame(l)
		Label(f, text='Find:').pack(side=LEFT)
		self.findentry = TextDropDown(f, self.find, self.parent.findhistory, 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W).pack(fill=X)
		Checkbutton(f, text='Wrap', variable=self.wrap, anchor=W).pack(fill=X)
		f.pack(side=LEFT, fill=BOTH)
		f = Frame(l)
		lf = LabelFrame(f, text='Direction')
		self.up = Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=W)
		self.up.pack(fill=X)
		self.down = Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=W)
		self.down.pack()
		lf.pack()
		f.pack(side=RIGHT, fill=Y)
		l.pack(side=LEFT, fill=BOTH, pady=2, expand=1)

		l = Frame(self)
		Button(l, text='Find Next', command=self.findnext, default=NORMAL).pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind('<Return>', self.findnext)

		if 'findwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'findwindow', size=False)

		return self.findentry

	def findnext(self, key=None):
		self.updatecolor()
		t = self.find.get()
		if not t in self.parent.findhistory:
			self.parent.findhistory.insert(0, t)
		if self.parent.listbox.size():
			m = []
			if self.regex.get():
				regex = t
				if not regex.startswith('\\A'):
					regex = '.*' + regex
				if not regex.endswith('\\Z'):
					regex = regex + '.*'
			else:
				regex = '.*%s.*' % re.escape(t)
			try:
				regex = re.compile(regex, [re.I,0][self.casesens.get()])
			except:
				self.reset = self.findentry
				self.reset.c = self.reset['bg']
				self.reset['bg'] = '#FFB4B4'
				self.resettimer = self.after(1000, self.updatecolor)
				return
			u = self.updown.get()
			s = int(self.parent.listbox.curselection()[0])
			i = s-1+u*2
			while i != [-1,self.parent.listbox.size()][u]:
				print (i,s)
				if regex.match(self.parent.listbox.get(i)):
					self.parent.listbox.select_clear(0,END)
					self.parent.listbox.select_set(i)
					self.parent.listbox.see(i)
					self.parent.update()
					return
				if i == s:
					break
				i += -1+u*2
				if i == [-1,self.parent.listbox.size()][u] and self.wrap.get():
					if i == -1:
						i = self.parent.listbox.size()-1
					else:
						i = 0
		p = self
		if key and key.keycode != 13:
			p = self.parent
		askquestion(parent=p, title='Find', message="Can't find text.", type=OK)

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def destroy(self):
		savesize(self, self.parent.settings, 'findwindow', size=False)
		self.withdraw()

class GotoDialog(PyMSDialog):
	def __init__(self, parent):
		self.goto = IntegerVar(range=(0,65535), allow_hex=True)
		PyMSDialog.__init__(self, parent, 'Goto', grabwait=False, escape=True, resizable=(False,False))

	def widgetize(self):
		f = Frame(self)
		Label(f, text='Index:').grid(row=0,column=0)
		self.gotoentry = TextDropDown(f, self.goto, self.parent.gotohistory, 5)
		self.gotoentry.entry.selection_range(0, END)
		self.gotoentry.grid(row=0,column=1)

		Button(f, text='Goto', command=self.jump).grid(row=0,column=2, padx=(4,0))
		f.pack(padx=4,pady=4)

		self.bind('<Return>', self.jump)

		if 'gotowindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'gotowindow', size=False)

		return self.gotoentry

	def jump(self, event=None):
		s = self.goto.get(True)
		if not s in self.parent.gotohistory:
			self.parent.gotohistory.insert(0, s)
		i = min(self.goto.get(), len(self.parent.tbl.strings)-1)
		self.parent.listbox.select_clear(0,END)
		self.parent.listbox.select_set(i)
		self.parent.listbox.see(i)
		self.parent.update()

	def destroy(self):
		savesize(self, self.parent.settings, 'gotowindow', size=False)
		self.withdraw()

class PyTBL(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyTBL',
			{
				'tfontgam':'MPQ:game\\tfontgam.pcx',
				'font8':'MPQ:font\\font8.fnt',
				'font10':'MPQ:font\\font10.fnt',
				'icons':'MPQ:game\\icons.grp',
				'unitpal':os.path.join(BASE_DIR,'Palettes','Units.pal'),
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PyTBL %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyTBL.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyTBL.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyTBL')

		self.tbl = None
		self.file = None
		self.edited = False
		self.findhistory = []
		self.findwindow = None
		self.gotohistory = []
		self.gotowindow = None
		self.colorswindow = None
		self.tfontgam = None
		self.font8 = None
		self.font10 = None
		self.unitpal = None
		self.icons = None

		listmenu = [
			('Add String (Insert)', self.add, 4), # 0
			('Insert String (Shift+Insert)', self.insert, 1), # 1
			('Remove String (Delete)', self.remove, 0), # 2
			None,
			('Move String Up (Shift+Up)', lambda i=0: self.movestring(None,i), 12), # 4
			('Move String Down (Shift+Down)', lambda i=1: self.movestring(None,i), 12), # 5
		]
		self.listmenu = Menu(self, tearoff=0)
		for m in listmenu:
			if m:
				l,c,u = m
				self.listmenu.add_command(label=l, command=c, underline=u)
			else:
				self.listmenu.add_separator()

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('opendefault', self.open_default, 'Open Default TBL (Ctrl+D)', NORMAL, 'Ctrl+D'),
			('import', self.iimport, 'Import Strings (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('export', self.export, 'Export Strings (Ctrl+E)', DISABLED, 'Ctrl+E'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('add', self.add, 'Add String (Insert)', DISABLED, 'Insert'),
			('insert', self.insert, 'Insert String (Shift+Insert)', DISABLED, 'Shift+Insert'),
			('remove', self.remove, 'Remove String (Delete in Listbox, Shift+Delete in Textbox)', DISABLED, 'Shift+Delete'),
			4,
			('up', lambda e=None,i=0: self.movestring(e,i), 'Move String Up (Shift+Up)', DISABLED, 'Shift+Up'),
			('down', lambda e=None,i=1: self.movestring(e,i), 'Move String Down (Shift+Down)', DISABLED, 'Shift+Down'),
			4,
			('find', self.find, 'Find Strings (Ctrl+F)', DISABLED, 'Ctrl+F'),
			('ffw', self.goto, 'Go to (Ctrl+G)', DISABLED, 'Ctrl+G'),
			4,
			('test', self.preview, 'Test String (Ctrl+T)', DISABLED, 'Ctrl+T'),
			10,
			('asc3topyai', self.mpqsettings, 'Manage Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.tbl editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyTBL', NORMAL, ''),
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
				if len(btn) == 5:
					a = btn[4]
					if a:
						if not a.startswith('F'):
							self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
						else:
							self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.grid(row=0,column=0, padx=1,pady=1, sticky=EW)

		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)

		# listbox
		listframe = Frame(self.hor_pane, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, width=35, height=1, bd=0, yscrollcommand=scrollbar.set, exportselection=0, state=DISABLED, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Shift-Up>', lambda e,i=0: self.movestring(e,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Shift-Down>', lambda e,i=1: self.movestring(e,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
			('<Delete>', self.remove),
		]
		for b in bind:
			listframe.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', lambda e,i=listframe: self.update(e,i))
		self.listbox.bind('<ButtonRelease-3>', self.popup)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		# listframe.pack(side=LEFT, fill=Y, padx=1, pady=2)
		self.hor_pane.add(listframe, sticky=NSEW, minsize=200)

		# Textbox
		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		textframe = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0, state=DISABLED)
		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.mark_set('textend', '1.0')
		self.text.mark_gravity('textend', RIGHT)
		self.text.grid(sticky=NSEW)
		self.text.bind('<Control-a>', lambda e: self.after(1, self.selectall))
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(textframe, sticky=NSEW)
		colors = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(colors, orient=HORIZONTAL)
		vscroll = Scrollbar(colors)
		text = Text(colors, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		text.insert(END, '\n'.join([l[2:] for l in TBL.TBL_REF.split('\n')[1:-2]]))
		text['state'] = DISABLED
		text.grid(sticky=NSEW)
		hscroll.config(command=text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		colors.grid_rowconfigure(0, weight=1)
		colors.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(colors, sticky=NSEW)
		# self.ver_pane.pack(side=LEFT, fill=BOTH, expand=1)
		self.hor_pane.add(self.ver_pane, sticky=NSEW, minsize=200)

		self.hor_pane.grid(row=1,column=0, sticky=NSEW)

		#Statusbar
		self.status = StringVar()
		self.stringstatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.stringstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a TBL.')
		statusbar.grid(row=2,column=0, sticky=EW)

		self.grid_rowconfigure(1, weight=1)

		listframe.focus_set()

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)
		def update_panes():
			if 'stringlist' in self.settings:
				self.hor_pane.sash_place(0, *self.settings['stringlist'])
			if 'colorlist' in self.settings:
				self.ver_pane.sash_place(0, *self.settings['colorlist'])
		if 'stringlist' in self.settings or 'colorlist' in self.settings:
			self.after(200, update_panes)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

		if e:
			self.mpqsettings(err=e)

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tfontgam = PCX.PCX()
			font8 = FNT.FNT()
			font10 = FNT.FNT()
			unitpal = PAL.Palette()
			icons = GRP.GRP()
			tfontgam.load_file(self.mpqhandler.get_file(self.settings['tfontgam']))
			try:
				font8.load_file(self.mpqhandler.get_file(self.settings['font8'], False))
			except:
				font8.load_file(self.mpqhandler.get_file(self.settings['font8'], True))
			try:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], False))
			except:
				font10.load_file(self.mpqhandler.get_file(self.settings['font10'], True))
			unitpal.load_file(self.mpqhandler.get_file(self.settings['unitpal']))
			icons.load_file(self.mpqhandler.get_file(self.settings['icons']))
		except PyMSError, e:
			err = e
		else:
			self.tfontgam = tfontgam
			self.font8 = font8
			self.font10 = font10
			self.unitpal = unitpal
			self.icons = icons
		self.mpqhandler.close_mpqs()
		return err

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
		self.update()

	def update(self, e=None, i=None, status=False):
		if self.listbox.size():
			if i:
				i.focus_set()
			s = int(self.listbox.curselection()[0])
			if not status:
				self.text_delete('1.0', END)
				self.text_insert('1.0', TBL.decompile_string(self.tbl.strings[s], '\n'))
			self.stringstatus.set('String: %s / %s' % (s+1,self.listbox.size()))

	def popup(self, e):
		if self.tbl:
			if not self.listbox.curselection():
				s = DISABLED
			else:
				s = NORMAL
			for i in [2,4,5]:
				self.listmenu.entryconfig(i, state=s)
			self.listmenu.post(e.x_root, e.y_root)

	def selectall(self, e=None):
		self.text.tag_remove(SEL, '1.0', END)
		self.text.tag_add(SEL, '1.0', END)
		self.text.mark_set(INSERT, '1.0')

	def unsaved(self):
		if self.tbl and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.tbl'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.tbl', filetypes=[('StarCraft TBL Files','*.tbl'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.tbl]
		select = [NORMAL,DISABLED][not self.listbox.curselection()]
		self.listbox['state'] = file
		self.text['state'] = select
		for btn in ['save','saveas','export','close','add','find','ffw']:
			self.buttons[btn]['state'] = file
		for btn in ['insert','remove','up','down','test']:
			self.buttons[btn]['state'] = select

	def text_insert(self, pos, text):
		self.tk.call((self.text.orig, 'insert', pos, text))

	def text_delete(self, start, end=None):
		self.tk.call((self.text.orig, 'delete', start, end))

	def dispatch(self, cmd, *args):
		try:
			r = self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			r = ''
		if self.listbox.size() and cmd in ['insert','delete']:
			if not self.edited:
				self.edited = True
				self.editstatus['state'] = NORMAL
			i = int(self.listbox.curselection()[0])
			self.tbl.strings[i] = TBL.compile_string(self.text.get('1.0','textend'))
			self.listbox.delete(i)
			self.listbox.insert(i, TBL.decompile_string(self.tbl.strings[i]))
			self.listbox.select_set(i)
		return r

	def new(self, key=None):
		if not self.unsaved():
			self.tbl = TBL.TBL()
			self.file = None
			self.status.set('Editing new TBL.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.title('PyTBL %s (Unnamed.tbl)' % LONG_VERSION)
			if self.listbox.size():
				self.text_delete('1.0', END)
			self.listbox.delete(0, END)
			self.stringstatus.set('')
			self.action_states()

	def open(self, key=None, file=None):
		if not self.unsaved():
			if not file:
				file = self.select_file('Open TBL')
				if not file:
					return
			tbl = TBL.TBL()
			try:
				tbl.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.tbl = tbl
			self.title('PyTBL %s (%s)' % (LONG_VERSION,file))
			self.listbox['state'] = NORMAL
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			for string in self.tbl.strings:
				self.listbox.insert(END, TBL.decompile_string(string))
			if self.listbox.size():
				self.listbox.select_set(0)
				self.listbox.see(0)
			self.file = file
			self.status.set('Load Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.update()

	def open_default(self, key=None):
		self.open(key, os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez','stat_txt.tbl'))

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			tbl = TBL.TBL()
			try:
				tbl.interpret(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.tbl = tbl
			self.title('PyTBL %s (%s)' % (LONG_VERSION,file))
			self.listbox['state'] = NORMAL
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			for string in self.tbl.strings:
				self.listbox.insert(END, TBL.decompile_string(string))
			if self.listbox.size():
				self.listbox.select_set(0)
				self.listbox.see(0)
			self.file = file
			self.status.set('Import Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.update()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.tbl.compile(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save TBL As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return True
		try:
			self.tbl.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.tbl = None
			self.title('PyTBL %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a TBL.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.listbox.delete(0, END)
			self.text_delete('1.0', END)
			self.stringstatus.set('')
			self.action_states()

	def add(self, key=None, i=END):
		if key and self.buttons['add']['state'] != NORMAL:
			return
		self.tbl.strings.append('')
		self.listbox.insert(i, '')
		self.listbox.select_clear(0, END)
		self.listbox.select_set(i)
		self.listbox.see(i)
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update(status=True)

	def insert(self, key=None):
		if key and self.buttons['insert']['state'] != NORMAL:
			return
		self.add(None, int(self.listbox.curselection()[0]))

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		del self.tbl.strings[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1)
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update()

	def movestring(self, key=None, dir=0):
		if key and self.buttons[['up','down'][dir]]['state'] != NORMAL:
			return
		i = int(self.listbox.curselection()[0])
		if i == [0,self.listbox.size()-1][dir]:
			return
		self.listbox.delete(i)
		n = i + [-1,1][dir]
		s = self.tbl.strings[i]
		self.listbox.insert(n, TBL.decompile_string(s))
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.tbl.strings[i] = self.tbl.strings[n]
		self.tbl.strings[n] = s
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.action_states()
		self.update(status=True)

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		if not self.findwindow:
			self.findwindow = FindDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
			self.findwindow.findentry.focus_set(highlight=True)

	def goto(self, key=None):
		if key and self.buttons['ffw']['state'] != NORMAL:
			return
		if not self.gotowindow:
			self.gotowindow = GotoDialog(self)
		elif self.gotowindow.state() == 'withdrawn':
			self.gotowindow.deiconify()
			self.gotowindow.gotoentry.focus_set(highlight=True)

	def preview(self, key=None):
		if key and self.buttons['test']['state'] != NORMAL:
			return
		PreviewDialog(self)

	def colors(self, key=None):
		if not self.colorswindow:
			self.colorswindow = TBLFormatting(self)
		else:
			self.colorswindow.focus_set()

	def mpqsettings(self, key=None, err=None):
		data = [
			('Preview Settings',[
				('tfontgam.pcx','The special palette which holds text colors.','tfontgam','PCX'),
				('font8.fnt','The font used to preview hotkeys','font8','FNT'),
				('font10.fnt','The font used to preview strings other than hotkeys','font10','FNT'),
				('icons.grp','The icons used to preview hotkeys','icons','GRP'),
				('Unit Palette','The palette used to display icons.grp','unitpal','Palette'),
			])
		]
		SettingsDialog(self, data, (340,430), err)

	def register(self, e=None):
		try:
			register_registry('PyTBL','','tbl',os.path.join(BASE_DIR, 'PyTBL.pyw'),os.path.join(BASE_DIR,'Images','PyTBL.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyTBL.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyTBL', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			self.settings['stringlist'] = self.hor_pane.sash_coord(0)
			self.settings['colorlist'] = self.ver_pane.sash_coord(0)
			savesize(self, self.settings)
			savesettings('PyTBL', self.settings)
			self.destroy()

	def destroy(self):
		if self.findwindow != None:
			Toplevel.destroy(self.findwindow)
		Tk.destroy(self)

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pytbl.py','pytbl.pyw','pytbl.exe']):
		gui = PyTBL()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyTBL [options] <inp> [out]', version='PyTBL %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a TBL file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a TBL file")
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for colors and other special characters at the top [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyTBL(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			tbl = TBL.TBL()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'tbl'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print "Reading TBL '%s'..." % args[0]
					tbl.load_file(args[0])
					print " - '%s' read successfully\nDecompiling TBL file '%s'..." % (args[0],args[0])
					tbl.decompile(args[1], opt.reference)
					print " - '%s' written succesfully" % args[1]
				else:
					print "Interpreting file '%s'..." % args[0]
					tbl.interpret(args[0])
					print " - '%s' read successfully\nCompiling file '%s' to TBL format..." % (args[0],args[0])
					tbl.compile(args[1])
					print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()