from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import LO,GRP,PAL

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, webbrowser, sys

LONG_VERSION = 'v%s' % VERSIONS['PyLO']

SIGNED_INT = '-128|-?(?:12[0-7]|1[01]\\d|\\d?\\d)'
COORDINATES = re.compile('^\\s*\\(\\s*(%s)\\s*,\\s*(%s)\\s*\\)\\s*(?:#.+)?$' % (SIGNED_INT,SIGNED_INT))
DRAG_COORDS = re.compile('^(\\s*\\(\\s*)(?:%s)(\\s*,\\s*)(?:%s)(\\s*\\)\\s*(?:#.+)?)$' % (SIGNED_INT,SIGNED_INT))

GRP_CACHE = [{},{}]

class Decompile:
	def __init__(self):
		self.text = ''

	def write(self, text):
		self.text += text

	def close(self):
		pass

class CodeTooltip(Tooltip):
	tag = 'Selection'

	def __init__(self, widget):
		Tooltip.__init__(self, widget)

	def setupbinds(self, press):
		if self.tag:
			self.widget.tag_bind(self.tag, '<Enter>', self.enter, '+')
			self.widget.tag_bind(self.tag, '<Leave>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<Motion>', self.motion, '+')
			self.widget.tag_bind(self.tag, '<Button-1>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<ButtonPress>', self.leave)

	def showtip(self):
		if self.tip:
			return
		pos = list(self.widget.winfo_pointerxy())
		head,tail = self.widget.tag_prevrange(self.tag,self.widget.index('@%s,%s+1c' % (pos[0] - self.widget.winfo_rootx(),pos[1] - self.widget.winfo_rooty())))
		m = COORDINATES.match(self.widget.get(head,tail))
		if not m:
			return
		try:
			self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			c = Canvas(self.tip, borderwidth=0, width=255, height=255, background='#FFFFC8', highlightthickness=0, takefocus=False)
			c.pack()
			c.create_line(123,128,134,128,fill='#00FF00')
			c.create_line(128,123,128,134,fill='#00FF00')
			x,y = int(m.group(1)),int(m.group(2))
			c.create_line(-x+123,y+128,-x+134,y+128,fill='#0000FF')
			c.create_line(-x+128,y+123,-x+128,y+134,fill='#0000FF')
			pos = list(self.widget.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip['background'] = '#FF0000'
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self):
		self.find = StringVar()
		self.replacewith = StringVar()
		self.replace = IntVar()
		self.inselection = IntVar()
		self.casesens = IntVar()
		self.regex = IntVar()
		self.multiline = IntVar()
		self.updown = IntVar()
		self.updown.set(1)

		l = Frame(self)
		f = Frame(l)
		s = Frame(f)
		Label(s, text='Find:', anchor=E, width=12).pack(side=LEFT)
		self.findentry = TextDropDown(s, self.find, self.parent.findhistory, 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(fill=X)
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.parent.replacehistory, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda i=1: self.check(i)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda i=2: self.check(i))
		self.multicheck.pack(fill=X)
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
		Button(l, text='Find Next', command=self.findnext).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind('<FocusIn>', lambda e,i=3: self.check(i))

		if 'findreplacewindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'findreplacewindow')

		return self.findentry

	def check(self, i):
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = NORMAL
			else:
				self.multicheck['state'] = DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [NORMAL,DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.parent.text.tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, key=None, replace=0):
		f = self.find.get()
		if not f in self.parent.findhistory:
			self.parent.findhistory.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			if replace:
				rep = self.replacewith.get()
				if not rep in self.parent.replacehistory:
					self.parent.replacehistory.append(rep)
				item = self.parent.text.tag_ranges('Selection')
				if item and r.match(self.parent.text.get(*item)):
					ins = r.sub(rep, self.parent.text.get(*item))
					self.parent.text.delete(*item)
					self.parent.text.insert(item[0], ins)
					self.parent.text.update_range(item[0])
			if self.multiline.get():
				m = r.search(self.parent.text.get(INSERT, END))
				if m:
					self.parent.text.tag_remove('Selection', '1.0', END)
					s,e = '%s +%sc' % (INSERT, m.start(0)),'%s +%sc' % (INSERT,m.end(0))
					self.parent.text.tag_add('Selection', s, e)
					self.parent.text.mark_set(INSERT, e)
					self.parent.text.see(s)
					self.check(3)
				else:
					p = self
					if key:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[self.parent.text.index('1.0 lineend'),self.parent.text.index(END)][u]
				i = self.parent.text.index(INSERT)
				if i == e:
					return
				if i == self.parent.text.index('%s %s' % (INSERT, rlse)):
					i = self.parent.text.index('%s %s1lines %s' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(self.parent.text.get(i, '%s %s' % (i, rlse)))
					else:
						m = None
						a = r.finditer(self.parent.text.get('%s %s' % (i, rlse), i))
						c = 0
						for x,f in enumerate(a):
							if x == n or n == -1:
								m = f
								c = x
						n = c - 1
					if m:
						self.parent.text.tag_remove('Selection', '1.0', END)
						if u:
							s,e = '%s +%sc' % (i,m.start(0)),'%s +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc' % (i,m.start(0)),'%s linestart +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, s)
						self.parent.text.tag_add('Selection', s, e)
						self.parent.text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and self.parent.text.index('%s lineend' % i) == e) or i == e:
						p = self
						if key:
							p = self.parent
						askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
						break
					i = self.parent.text.index('%s %s1lines %s' % (i, s, lse))
				else:
					p = self
					if key:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)

	def count(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			askquestion(parent=self, title='Count', message='%s matches found.' % len(r.findall(self.parent.text.get('1.0', END))), type=OK)

	def replaceall(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			text = r.subn(self.replacewith.get(), self.parent.text.get('1.0', END))
			if text[1]:
				self.parent.text.delete('1.0', END)
				self.parent.text.insert('1.0', text[0].rstrip('\n'))
				self.parent.text.update_range('1.0')
			askquestion(parent=self, title='Replace Complete', message='%s matches replaced.' % text[1], type=OK)

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def destroy(self):
		self.parent.settings['findreplacewindow'] = self.winfo_geometry()
		PyMSDialog.withdraw(self)

class CodeColors(PyMSDialog):
	def __init__(self, parent):
		self.cont = False
		self.tags = dict(parent.text.tags)
		self.info = odict()
		self.info['Number'] = 'The color of all numbers.'
		self.info['Comment'] = 'The color of a regular comment.'
		self.info['Header'] = 'The color of the Frame header.'
		self.info['Operators'] = 'The color of the operators:\n    ( ) , :'
		self.info['Error'] = 'The color of an error when compiling.'
		self.info['Warning'] = 'The color of a warning when compiling.'
		self.info['Selection'] = 'The color of selected text in the editor.'
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self):
		self.listbox = Listbox(self, font=couriernew, width=20, height=16, exportselection=0)
		self.listbox.bind('<ButtonRelease-1>', self.select)
		for t in self.info.keys():
			self.listbox.insert(END, t)
		self.listbox.select_set(0)
		self.listbox.pack(side=LEFT, fill=Y, padx=2, pady=2)

		self.fg = IntVar()
		self.bg = IntVar()
		self.bold = IntVar()
		self.infotext = StringVar()

		r = Frame(self)
		opt = LabelFrame(r, text='Style:', padx=5, pady=5)
		f = Frame(opt)
		c = Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=W)
		c.bind('<ButtonRelease-1>', lambda e,i=0: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Background', variable=self.bg)
		c.bind('<ButtonRelease-1>', lambda e,i=1: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Bold', variable=self.bold)
		c.bind('<ButtonRelease-1>', lambda e,i=2: self.select(e,i))
		c.grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind('<Button-1>', lambda e,i=0: self.colorselect(e, i))
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind('<Button-1>', lambda e,i=1: self.colorselect(e, i))
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=TOP)
		Label(opt, textvariable=self.infotext, height=6, justify=LEFT).pack(side=BOTTOM, fill=X)
		opt.pack(side=TOP, fill=Y, expand=1, padx=2, pady=2)
		f = Frame(r)
		ok = Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		Button(f, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		f.pack(side=BOTTOM, pady=2)
		r.pack(side=LEFT, fill=Y)

		self.select()

		return ok

	def select(self, e=None, n=None):
		i = self.info.getkey(int(self.listbox.curselection()[0]))
		s = self.tags[i.replace(' ', '')]
		if n == None:
			t = self.info[i].split('\n')
			text = ''
			if len(t) == 2:
				d = '  '
				text = t[0] + '\n'
			else:
				d = ''
			text += fit(d, t[-1], 35, True)[:-1]
			self.infotext.set(text)
			if s['foreground'] == None:
				self.fg.set(0)
				self.fgcanvas['background'] = '#000000'
			else:
				self.fg.set(1)
				self.fgcanvas['background'] = s['foreground']
			if s['background'] == None:
				self.bg.set(0)
				self.bgcanvas['background'] = '#000000'
			else:
				self.bg.set(1)
				self.bgcanvas['background'] = s['background']
			self.bold.set(s['font'] != None)
		else:
			v = [self.fg,self.bg,self.bold][n].get()
			if n == 2:
				s['font'] = [self.parent.text.boldfont,couriernew][v]
			else:
				s[['foreground','background'][n]] = ['#000000',None][v]
				if v:
					[self.fgcanvas,self.bgcanvas][n]['background'] = '#000000'

	def colorselect(self, e, i):
		if [self.fg,self.bg][i].get():
			v = [self.fgcanvas,self.bgcanvas][i]
			g = ['foreground','background'][i]
			c = tkColorChooser.askcolor(parent=self, initialcolor=v['background'], title='Select %s color' % g)
			if c[1]:
				v['background'] = c[1]
				self.tags[self.info.getkey(int(self.listbox.curselection()[0])).replace(' ','')][g] = c[1]
			self.focus_set()

	def ok(self):
		self.cont = self.tags
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)

class LOCodeText(CodeText):
	def __init__(self, parent, ecallback=None, icallback=None, highlights=None, state=NORMAL):
		self.boldfont = ('Courier New', -11, 'bold')
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Header':{'foreground':'#FF00FF','background':None,'font':self.boldfont},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, icallback, state=state)

	def setedit(self):
		if self.ecallback != None:
			self.ecallback()
		self.edited = True

	def setupparser(self):
		comment = '(?P<Comment>#[^\\n]*$)'
		header = '^(?P<Header>Frame:)(?=[ \\t]*(#[^\\n]*)?)'
		num = '(?<!\\w)(?P<Number>%s)(?!\\w)' % SIGNED_INT
		operators = '(?P<Operators>[():,])'
		self.basic = re.compile('|'.join((comment, header, num, operators, '(?P<Newline>\\n)')), re.M)
		self.tooltip = CodeTooltip(self)
		self.tags = dict(self.highlights)

	def colorize(self):
		next = '1.0'
		while next:
			item = self.tag_nextrange("Update", next)
			if not item:
				break
			head, tail = item
			self.tag_remove('Newline', head, tail)
			item = self.tag_prevrange('Newline', head)
			if item:
				head = item[1] + ' linestart'
			else:
				head = "1.0"
			chars = ""
			next = head
			lines_to_get = 1
			ok = False
			while not ok:
				mark = next
				next = self.index(mark + '+%d lines linestart' % lines_to_get)
				lines_to_get = min(lines_to_get * 2, 100)
				ok = 'Newline' in self.tag_names(next + '-1c')
				line = self.get(mark, next)
				if not line:
					return
				for tag in self.tags.keys():
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.basic.search(chars)
				while m:
					for key, value in m.groupdict().items():
						if value != None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc' % a, head + '+%dc' % b)
					m = self.basic.search(chars, m.end())
				if 'Newline' in self.tag_names(next + '-1c'):
					head = next
					chars = ''
				else:
					ok = False
				if not ok:
					self.tag_add('Update', next)
				self.update()
				if not self.coloring:
					return

class PyLO(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyLO',
			{
				'basegrp':'MPQ:unit\\terran\\wessel.grp',
				'overlaygrp':'MPQ:unit\\terran\\wesselt.grp',
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PyLO %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyLO.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyLO.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		self.minsize(435,470)
		setup_trace(self, 'PyLO')

		self.lo = None
		self.file = None
		self.edited = False
		self.findhistory = []
		self.replacehistory = []
		self.findwindow = None
		self.basegrp = None
		self.overlaygrp = None
		self.unitpal = PAL.Palette()
		self.unitpal.load_file(os.path.join(BASE_DIR,'Palettes','Units.pal'))
		self.previewing = None
		self.overlayframe = None
		self.dragoffset = None
		self.pauseupdate = False

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			2,
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('import', self.iimport, 'Import LO? (Ctrl+I)', NORMAL, 'Ctrl+I'),
			2,
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('export', self.export, 'Export LO? (Ctrl+E)', DISABLED, 'Ctrl+E'),
			('test', self.test, 'Test Code (Ctrl+T)', DISABLED, '<Control-t>'),
			2,
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			5,
			('find', self.find, 'Find/Replace (Ctrl+F)', DISABLED, 'Ctrl+F'),
			10,
			('colors', self.colors, 'Color Settings (Ctrl+Alt+C)', NORMAL, 'Ctrl+Alt+C'),
			2,
			('asc3topyai', self.mpqsettings, 'Manage MPQ Settings (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.lo? editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyLO', NORMAL, ''),
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

		m = Frame(self)
		# Text editor
		self.text = LOCodeText(m, self.edit, highlights=self.settings.get('highlights'), state=DISABLED)
		self.text.grid(sticky=NSEW)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs

		self.usebasegrp = IntVar()
		self.usebasegrp.set(not not self.settings.get('usebasegrp'))
		self.useoverlaygrp = IntVar()
		self.useoverlaygrp.set(not not self.settings.get('useoverlaygrp'))
		self.baseframes = StringVar()
		self.baseframes.set('Base Frame: - / -')
		self.overlayframes = StringVar()
		self.overlayframes.set('Overlay Frame: - / -')

		# Previewer
		f = Frame(m)
		c = Frame(f)
		l = Frame(c)
		Label(l, textvariable=self.baseframes, anchor=W).pack(side=LEFT)
		Label(l, textvariable=self.overlayframes, anchor=W).pack(side=RIGHT)
		l.pack(fill=X, expand=1)
		self.canvas = Canvas(c, borderwidth=0, width=275, height=275, background='#000000', highlightthickness=0)
		for t in [0,1]:
			self.canvas.bind('<Button-1>', lambda e,t=t: self.drag(e,t,0))
			self.canvas.bind('<B1-Motion>', lambda e,t=t: self.drag(e,t,1))
			self.canvas.bind('<ButtonRelease-1>', lambda e,t=t: self.drag(e,t,2))
		self.canvas.pack(side=TOP)
		self.framescroll = Scrollbar(c, orient=HORIZONTAL, command=self.scrolling)
		self.framescroll.set(0,1)
		self.framescroll.pack(side=TOP, fill=X)
		c.pack(side=TOP)
		self.grppanel = SettingsPanel(f, (('Base GRP:',False,'basegrp','CacheGRP',self.updatebasegrp),('Overlay GRP:',False,'overlaygrp','CacheGRP',self.updateoverlaygrp)), self.settings, self.mpqhandler, self)
		self.grppanel.pack(side=TOP)
		x = Frame(f)
		Checkbutton(x, text='Use base GRP', variable=self.usebasegrp, command=self.updateusebase).pack(side=LEFT)
		Checkbutton(x, text='Use overlay GRP', variable=self.useoverlaygrp, command=self.updateuseoverlay).pack(side=RIGHT)
		x.pack(side=TOP, fill=X, padx=5, pady=2)
		f.grid(row=0, column=1, sticky=NS)
		try:
			g = GRP.CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings['basegrp']))
			self.updatebasegrp(g)
		except PyMSError, e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
				ErrorDialog(self, e)
		try:
			g = GRP.CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings['overlaygrp']))
			self.updateoverlaygrp(g)
		except PyMSError, e:
			if self.useoverlaygrp.get():
				self.useoverlaygrp.set(0)
				ErrorDialog(self, e)
		self.updategrps()

		m.grid_rowconfigure(0,weight=1)
		m.grid_columnconfigure(0,weight=1)
		m.pack(fill=BOTH, expand=1)

		#Statusbar
		self.status = StringVar()
		self.codestatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.codestatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a LO?.')
		self.codestatus.set('Line: 1  Column: 0  Selected: 0')
		statusbar.pack(side=BOTTOM, fill=X)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyLO'))

	def scrolling(self, t, p, e=None):
		a = {'pages':17,'units':1}
		frames = self.overlaygrp.frames-1
		if t == 'moveto':
			self.overlayframe = int(frames * float(p))
		elif t == 'scroll':
			self.overlayframe = min(frames,max(0,self.overlayframe + int(p) * a[e]))
		self.previewupdate()
		self.updatescroll()
		self.framesupdate()

	def updatescroll(self):
		if self.overlayframe != None and self.overlaygrp != None:
			frames = float(self.overlaygrp.frames)
			step = 1 / frames
			self.framescroll.set(self.overlayframe*step, (self.overlayframe+1)*step)

	def updategrps(self):
		self.grppanel.variables['Base GRP:'][2][1]['state'] = [DISABLED,NORMAL][self.usebasegrp.get()]
		self.grppanel.variables['Overlay GRP:'][2][1]['state'] = [DISABLED,NORMAL][self.useoverlaygrp.get()]

	def drag(self, e, t, c):
		if c == 0 and self.previewing:
			self.dragoffset = (self.previewing[2] - e.x,self.previewing[3] - e.y)
			self.text.text.edit_separator()
		elif c == 1 and self.previewing and self.dragoffset:
			p = [max(-128,min(127,e.x + self.dragoffset[0])),max(-128,min(127,e.y + self.dragoffset[1]))]
			self.drawpreview(self.previewing[0],p)
		elif c == 2:
			s = self.text.index('%s linestart' % INSERT)
			m = DRAG_COORDS.match(self.text.get(s,'%s lineend' % INSERT))
			if m:
				self.pauseupdate = True
				self.text.delete(s,'%s lineend' % INSERT)
				self.text.insert(s,'%s%s%s%s%s' % (m.group(1),self.previewing[2],m.group(2),self.previewing[3],m.group(3)))
				self.pauseupdate = False
			self.dragoffset = None
			self.text.text.edit_separator()

	def updateusebase(self):
		self.updategrps()
		try:
			g = GRP.CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings['basegrp']))
			self.updatebasegrp(g)
		except PyMSError, e:
			if self.usebasegrp.get():
				self.usebasegrp.set(0)
			ErrorDialog(self, e)

	def updateuseoverlay(self):
		self.updategrps()
		try:
			g = GRP.CacheGRP()
			g.load_file(self.mpqhandler.get_file(self.settings['overlaygrp']))
			self.updateoverlaygrp(g)
		except PyMSError, e:
			if self.useoverlaygrp.get():
				self.useoverlaygrp.set(0)
			ErrorDialog(self, e)

	def updatebasegrp(self, grp):
		self.basegrp = grp
		GRP_CACHE[0] = {}
		self.previewing = None
		self.previewupdate()
		self.framesupdate()

	def updateoverlaygrp(self, grp):
		self.overlaygrp = grp
		GRP_CACHE[1] = {}
		self.previewing = None
		self.previewupdate()
		self.framesupdate()

	def unsaved(self):
		if self.lo and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.loa'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.loa', filetypes=[('All StarCraft Overlays','*.loa;*.lob;*.lod;*.lof;*.loo;*.los;*.lou;*.log;*.lol;*.lox'),('StarCraft Attack Overlays','*.loa'),('StarCraft Birth Overloays','*.lob'),('StarCraft Landing Dust Overlays','*.lod'),('StarCraft Fire Overlays','*.lof'),('StarCraft Powerup Overlays','*.loo'),('StarCraft Shield/Smoke Overlays','*.los'),('StarCraft Lift-Off Dust Overlays','*.lou'),('Misc. StarCraft Overlay','*.log'),('Misc. StarCraft Overlay','*.lol'),('Misc. StarCraft Overlay','*.lox'),('All Files','*')]):
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=self, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		self._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.lo]
		for btn in ['save','saveas','export','test','close','find']:
			self.buttons[btn]['state'] = file
		self.text['state'] = file

	def statusupdate(self):
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.codestatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))
		self.previewupdate()
		self.framesupdate()

	def framesupdate(self):
		bm,om,b,o = '-'*4
		if self.basegrp:
			bm = self.basegrp.frames
		if self.previewing:
			b = self.previewing[0] + 1
		if self.overlaygrp:
			om = self.overlaygrp.frames
		if self.overlayframe != None:
			o = self.overlayframe + 1
		self.baseframes.set('Base Frame: %s / %s' % (b,bm))
		self.overlayframes.set('Overlay Frame: %s / %s' % (o,om))

	def previewupdate(self):
		if not self.pauseupdate:
			m = COORDINATES.match(self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT))
			if m:
				i = INSERT
				f = -1
				while True:
					i = self.text.tag_prevrange('Header',i)
					if not i:
						break
					i = i[0]
					f += 1
				if f >= 0:
					self.drawpreview(f,list(int(n) for n in m.groups()))
					return
			self.canvas.delete(ALL)
			self.previewing = None

	def grp(self, f, t):
		if f != None:
			if not f in GRP_CACHE[t]:
				try:
					GRP_CACHE[t][f] = GRP.frame_to_photo(self.unitpal.palette, [self.basegrp,self.overlaygrp][t], f, True, False)
				except:
					GRP_CACHE[t][f] = None
			return GRP_CACHE[t][f]

	def drawpreview(self, f, offset):
		if [f,self.overlayframe]+offset != self.previewing:
			self.canvas.delete(ALL)
			base,overlay = self.grp(f,0),self.grp(self.overlayframe,1)
			if self.usebasegrp.get() and base:
				self.canvas.create_image(138, 138, image=base)
			else:
				self.canvas.create_line(133,138,144,138,fill='#00FF00')
				self.canvas.create_line(138,133,138,144,fill='#00FF00')
			if self.useoverlaygrp.get() and overlay:
				self.canvas.create_image(138 + offset[0], 138 + offset[1], image=overlay)
			else:
				x,y = offset
				self.canvas.create_line(x+133,y+138,x+144,y+138,fill='#0000FF')
				self.canvas.create_line(x+138,y+133,x+138,y+144,fill='#0000FF')
			self.previewing = [f,self.overlayframe]+offset

	def edit(self):
		self.editstatus['state'] = NORMAL
		self.previewupdate()

	def new(self, key=None):
		if not self.unsaved():
			self.lo = LO.LO()
			self.file = None
			self.status.set('Editing new LO?.')
			self.title('PyLO %s (Unnamed.loa)' % LONG_VERSION)
			GRP_CACHE = [{},{}]
			self.overlayframe = 0
			self.previewupdate()
			self.updatescroll()
			self.framesupdate()
			self.action_states()
			self.text.delete('1.0', END)
			self.text.insert('1.0', 'Frame:\n\t(0, 0)')
			self.text.edit_reset()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open LO')
				if not file:
					return
			lo = LO.LO()
			d = Decompile()
			try:
				lo.load_file(file)
				lo.decompile(d)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.lo = lo
			self.title('PyLO %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.overlayframe = 0
			self.previewupdate()
			self.updatescroll()
			self.action_states()
			self.text.delete('1.0', END)
			self.text.insert('1.0', d.text.rstrip('\n'))
			self.text.edit_reset()
			self.text.see('1.0')
			self.text.mark_set('insert', '2.0 lineend')
			self.edited = False
			self.editstatus['state'] = DISABLED

	def iimport(self, key=None):
		if not self.unsaved():
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
			if not file:
				return
			try:
				text = open(file,'r').read()
			except:
				ErrorDialog(self, PyMSError('Import', "Couldn't import file '%s'" % file))
				return
			self.lo = LO.LO()
			self.title('PyLO %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Import Successful!')
			self.overlayframe = 0
			self.previewupdate()
			self.updatescroll()
			self.framesupdate()
			self.action_states()
			self.text.delete('1.0', END)
			self.text.insert('1.0', text.rstrip('\n'))
			self.text.edit_reset()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.lo.interpret(self.text)
			self.lo.compile(self.file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('Save Successful!')
		self.edited = False
		self.editstatus['state'] = DISABLED

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save LO As', False)
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
			self.lo.decompile(file)
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def test(self, key=None):
		i = LO.LO()
		try:
			warnings = i.interpret(self)
		except PyMSError, e:
			if e.line != None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line != None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line != None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=OK)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.lo = None
			self.title('PyLO %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a LO?.')
			self.overlayframe = None
			self.previewupdate()
			self.updatescroll()
			self.framesupdate()
			GRP_CACHE = [{},{}]
			self.text.delete('1.0', END)
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.action_states()

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, key=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.highlights = c.cont

	def mpqsettings(self, key=None):
		SettingsDialog(self, None, (340,215))

	def register(self, e=None):
		for type,ext in [('Attack','a'),('Birth','b'),('Landing Dust','d'),('Fire','f'),('Powerup','o'),('Shield/Smoke','s'),('Liftoff Dust','u'),('Misc.','g'),('Misc.','l'),('Misc.','x')]:
			try:
				register_registry('PyLO',type + ' Overlay','lo' + ext,os.path.join(BASE_DIR, 'PyLO.pyw'),os.path.join(BASE_DIR,'Images','PyLO.ico'))
			except PyMSError, e:
				ErrorDialog(self, e)
				break

	def help(self, e=None):
		webbrowser.open(os.path.join(BASE_DIR, 'Docs', 'PyLO.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyLO', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['highlights'] = self.text.highlights
			m = os.path.join(BASE_DIR,'Libs','MPQ','')
			self.settings['basegrp'] = ['','MPQ:'][self.grppanel.variables['Base GRP:'][0].get()] + self.grppanel.variables['Base GRP:'][1].get().replace(m,'MPQ:',1)
			self.settings['overlaygrp'] = ['','MPQ:'][self.grppanel.variables['Overlay GRP:'][0].get()] + self.grppanel.variables['Overlay GRP:'][1].get().replace(m,'MPQ:',1)
			self.settings['usebasegrp'] = self.usebasegrp.get()
			self.settings['useoverlaygrp'] = self.useoverlaygrp.get()
			savesettings('PyLO', self.settings)
			self.destroy()

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		Tk.destroy(self)

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pylo.py','pylo.pyw','pylo.exe']):
		gui = PyLO()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyLO [options] <inp> [out]', version='PyLO %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile a LO? file [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile a LO? file")
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyLO(opt.gui)
			gui.mainloop()
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			lo = LO.LO()
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'lox'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			try:
				if opt.convert:
					print "Reading LO? '%s'..." % args[0]
					lo.load_file(args[0])
					print " - '%s' read successfully\nDecompiling LO? file '%s'..." % (args[0],args[0])
					lo.decompile(args[1])
					print " - '%s' written succesfully" % args[1]
				else:
					print "Interpreting file '%s'..." % args[0]
					lo.interpret(args[0])
					print " - '%s' read successfully\nCompiling file '%s' to LO? format..." % (args[0],args[0])
					lo.compile(args[1])
					print " - '%s' written succesfully" % args[1]
			except PyMSError, e:
				print repr(e)

if __name__ == '__main__':
	main()