from Tkinter import *
from utils import isstr
import re
import os.path

class RichList(Frame):
	selregex = re.compile('\\bsel\\b')
	idregex = re.compile('(\\d+)\.(\\d+).(\\d+)(.+)?')

	def __init__(self, parent, **kwargs):
		self.entry = 0
		self.entries = []

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		font = ('courier', -12, 'normal')
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0, **kwargs)
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind

	def index(self, index):
		m = self.idregex.match(index)
		if m:
			index = 'entry%s.first +%sl +%sc' % (self.entries[int(m.group(1))-1],int(m.group(2))-1,int(m.group(3)))
			if m.group(4):
				index += m.group(4)
		return self.execute('index',(index,))

	def tag_add(self, tag, index, *args):
		return self.text.tag_add(tag, self.index(index), tuple(map(self.index, args)))

	def tag_nextrange(self, tag, start, end):
		return self.text.tag_nextrange(tag, self.index(start), self.index(end))

	def tag_prevrange(self, tag, start, end):
		return self.text.tag_prevrange(tag, self.index(start), self.index(end))

	def image_create(self, index, cnf={}, **kw):
		return self.text.image_create(self.index(index), cnf, **kw)

	def image_configure(self, index, **options):
		return self.text.image_config(self.index(index), **options)

	def image_cget(self, index, option):
		return self.text.image_config(self.index(index), option)

	def select(self, e):
		if e == END:
			e = -1
		if isinstance(e, int):
			n = 'entry%s' % self.entries[e]
		elif isinstance(e, str):
			n = e
		else:
			for n in self.text.tag_names(self.text.index('@%s,%s' % (e.x,e.y))):
				if n.startswith('entry'):
					break
			else:
				return
		self.text.tag_remove('Selection', '1.0', END)
		self.text.tag_add('Selection', n + '.first', n + '.last')

	def insert(self, index, text, tags=None):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', self.select)
		if tags == None:
			tags = e
		elif isstr(tags):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		return self.execute('insert',(i, '%s\n' % text, tags))

	def delete(self, index):
		if index == ALL:
			self.entry = 0
			self.entries = []
			return self.execute('delete', ('1.0',END))
		if index == END:
			index == -1
		r = self.execute('delete',('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index]))
		if r:
			del self.entries[index]
		return r

	def execute(self, cmd, args):
		try:
			return self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			return ""

	def dispatch(self, cmd, *args):
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)

	def get(self, index):
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last -1c' % self.entries[index])

class EditableReportSubList(RichList):
	def __init__(self, parent, selectmode, report, **kwargs):
		self.report = report
		self.lastsel = None
		self.selectmode = selectmode
		self.checkedit = None
		self.edittext = StringVar()
		self.entry = 0
		self.entries = []
		self.dctimer = None
		self.editing = False
		self.lineselect = False

		Frame.__init__(self, parent)
		font = ('courier', -11, 'normal')
		self.text = Text(self, cursor='arrow', height=1, width=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_bind('Selection', '<Button-1>', self.edit)
		bind = [
			('<Button-1>', self.deselect),
			('<Up>', lambda e: self.movesel(-1)),
			('<Down>', lambda e: self.movesel(1)),
			('<Shift-Up>', lambda e: self.movesel(-1,True)),
			('<Shift-Down>', lambda e: self.movesel(1,True)),
		]
		for b in bind:
			self.text.bind(*b)

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind
		self.yview = self.text.yview

	def insert(self, index, text, tags=None):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', lambda e,i=e: self.doselect(i,0))
		self.text.tag_bind(e, '<DoubleButton-1>', self.doubleclick)
		self.text.tag_bind(e, '<Button-3>', lambda e,i=e: self.popup(e,i))
		self.text.tag_bind(e, '<Shift-Button-1>', lambda e,i=e: self.doselect(i,1))
		self.text.tag_bind(e, '<Control-Button-1>', lambda e,i=e: self.doselect(i,2))
		if tags == None:
			tags = e
		elif isstr(tags):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		self.execute('insert',(i, text, tags))
		self.execute('insert',(i + ' lineend', '\n'))

	def doubleclick(self, e):
		if self.report.dcmd:
			self.report.dcmd(e)

	def popup(self, e, i):
		if self.report.pcmd:
			self.report.pcmd(e,i)

	def selected(self, e):
		if isinstance(e,int):
			e = 'entry%s' % e
		return not not [n for n in self.text.tag_names('%s.first' % e) if n == 'Selection']

	def deselect(self, e):
		if self.lineselect:
			self.lineselect = False
		else:
			self.lastsel = None
			self.text.tag_remove('Selection', '1.0', END)

	def movesel(self, d, s=False):
		if self.lastsel:
			l = self.lastsel
		elif self.entries:
			l = self.entries[0]
		if l:
			if not s:
				self.text.tag_remove('Selection', '1.0', END)
			r = self.text.tag_names('%s.last %+dl lineend -1c' % (l,d))
			for e in r:
				if e.startswith('entry'):
					self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
					self.lastsel = e
					break
			else:
				self.text.tag_add('Selection', '%s.first' % self.lastsel, '%s.last' % self.lastsel)

	def doselect(self, i, t):
		self.lineselect = True
		if self.editing:
			self.text.tag_remove('Selection', '1.0', END)
			return
		if t == 0 or (t == 1 and self.selectmode == EXTENDED and self.lastsel == None) or (t == 2 and self.selectmode != SINGLE):
			if self.selectmode != MULTIPLE and t != 2:
				self.text.tag_remove('Selection', '1.0', END)
			if self.selectmode == EXTENDED:
				self.lastsel = i
			if not self.selected(i):
				self.text.tag_add('Selection',  '%s.first' % i, '%s.last' % i)
		elif t == 1 and self.selectmode == EXTENDED:
			if tuple(int(n) for n in self.text.index('%s.first' % self.lastsel).split('.')) > tuple(int(n) for n in self.text.index('%s.first' % i).split('.')):
				d = '-1l'
			else:
				d = '+1l'
			c,f = self.text.index('%s.last %s lineend -1c' % (self.lastsel,d)),self.text.index('%s.last %s lineend -1c' % (i,d))
			while d == '-1l' or c != f:
				r = self.text.tag_names(c)
				if not 'Selection' in r:
					for e in r:
						if e.startswith('entry'):
							self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
							break
				if d == '-1l' and c == f:
					break
				c = self.text.index('%s %s lineend -1c' % (c,d))
			self.lastsel = i
		self.dctimer = self.after(300, self.nodc)
		if self.report.scmd:
			self.report.scmd()

	def nodc(self):
		self.dctimer = None

	def edit(self, e=None):
		if self.dctimer:
			self.after_cancel(self.dctimer)
			self.dctimer = None
			return
		self.editing = True
		if isinstance(e,int):
			n = 'entry%s' % self.entries[e]
		elif e == None:
			n = [n for n in self.text.tag_names('Selection.first') if n.startswith('entry')][0]
		else:
			c = '@%s,%s' % (e.x,e.y)
			n = [n for n in self.text.tag_names(c) if n.startswith('entry')][0]
		i = self.text.index(n + '.first')
		self.checkedit = self.text.get(n + '.first', n + '.last')
		self.edittext.set(self.checkedit)
		e = Entry(self.text, width=len(self.checkedit) + 5, textvariable=self.edittext, bd=1, relief=SOLID)
		e.select_range(0,END)
		e.bind('<Return>', lambda _,i=i,n=n: self.endedit(i,n))
		e.bind('<FocusOut>', lambda _,i=i,n=n: self.endedit(i,n))
		self.text.window_create('%s.first' % n, window=e)
		e.focus_set()
		self.execute('delete',(n + '.first', n + '.last'))
		self.text.tag_remove('Selection', '1.0', END)

	def endedit(self, i, n):
		t = self.edittext.get()
		if self.checkedit != t and self.report.rcmd and not self.report.rcmd(self.entries.index(int(n[5:])),t):
			t = self.checkedit
		self.execute('delete',(i + ' linestart', i + ' lineend'))
		self.execute('insert',(i, t, n + ' Selection'))
		self.editing = False
		self.checkedit = None

	def cur_selection(self):
		s = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([self.entries.index(int(n[5:])) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

	def get(self, index):
		if self.checkedit:
			return self.checkedit
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index])

class ReportSubList(RichList):
	def __init__(self, parent, **kwargs):
		self.entry = 0
		self.entries = []
		Frame.__init__(self, parent)
		font = ('courier', -11, 'normal')
		self.text = Text(self, cursor='arrow', height=1, width=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_configure('RightAlign', justify=RIGHT)

		self.tag_bind = self.text.tag_bind
		self.tag_cget = self.text.tag_cget
		self.tag_config = self.text.tag_config
		self.tag_delete = self.text.tag_delete
		self.tag_lower = self.text.tag_lower
		self.tag_names = self.text.tag_names
		self.tag_raise = self.text.tag_raise
		self.tag_ranges = self.text.tag_ranges
		self.tag_unbind = self.text.tag_unbind
		self.yview = self.text.yview

	def select(self, e):
		pass

	def insert(self, index, text, tags='RightAlign'):
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		self.text.tag_bind(e, '<Button-1>', self.select)
		if tags == None:
			tags = e
		elif isstr(tags):
			tags = '%s %s' % (e,tags)
		else:
			tags = '%s %s' % (e,' '.join(tags))
		if self.entries:
			i = 'entry%s.last +1l' % self.entries[index]
		else:
			i = END
		if index == -1 or index == len(self.entries)-1:
			self.entries.append(self.entry)
		else:
			self.entries.insert(index+1, self.entry)
		self.entry += 1
		return self.execute('insert',(i, '%s\n' % text, tags))

class ReportList(Frame):
	def __init__(self, parent, columns=[''], selectmode=SINGLE, scmd=None, rcmd=None, pcmd=None, dcmd=None, min_widths=None, **conf):
		self.scmd = scmd
		self.rcmd = rcmd
		self.pcmd = pcmd
		self.dcmd = dcmd
		self.entry = 0
		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.selectmode = selectmode
		self.panes = PanedWindow(self, orient=HORIZONTAL, borderwidth=0, sashpad=0, sashwidth=4, sashrelief=FLAT)
		self.columns = []
		self.vscroll = Scrollbar(self)
		self.vscroll.config(command=self.yview)
		self.vscroll.pack(side=RIGHT, fill=Y)
		p = self
		for n,title in enumerate(columns):
			end = n+1 == len(columns)
			l = Frame(self.panes)
			if title == None:
				b = Button(l, text=' ', state=DISABLED)
			else:
				b = Button(l, text=title)
			b.pack(side=TOP, fill=X)
			if n == 0:
				lb = EditableReportSubList(l, selectmode, self, yscrollcommand=self.yscroll, **conf)
			else:
				lb = ReportSubList(l, yscrollcommand=self.yscroll, **conf)
			lb.pack(side=TOP, fill=BOTH, expand=1)
			if n == 0:
				self.panes['background'] = lb.text['background']
			self.panes.add(l)
			if min_widths and n < len(min_widths):
				self.panes.paneconfig(l, minsize=min_widths[n])
			self.columns.append((b,lb))
		self.panes.pack(fill=BOTH, expand=1)
		# bind = [
		# 	('<MouseWheel>', self.scroll),
		# 	('<Home>', lambda a,i=0: self.move(a,i)),
		# 	('<End>', lambda a,i=END: self.move(a,i)),
		# 	('<Up>', lambda a,i=-1: self.move(a,i)),
		# 	('<Left>', lambda a,i=-1: self.move(a,i)),
		# 	('<Down>', lambda a,i=1: self.move(a,i)),
		# 	('<Right>', lambda a,i=-1: self.move(a,i)),
		# 	('<Prior>', lambda a,i=-10: self.move(a,i)),
		# 	('<Next>', lambda a,i=10: self.move(a,i)),
		# ]
		# for d in bind:
			# parent.bind(*d)

	def select_set(self, i):
		self.columns[0][1].select(i)

	def scroll(self, e):
		if e.delta > 0:
			for c in self.columns:
				c[1].yview('scroll', -1, 'units')
		else:
			for c in self.columns:
				c[1].yview('scroll', 1, 'units')

	def move(self, e, a):
		s = self.curselection()
		if s:
			if a == END:
				a = self.size()-2
			elif a not in [0,END]:
				if a > 0:
					a = min(self.size()-1, int(s[-1]) + a)
				else:
					a = max(int(s[0]) + a,0)
			for c in self.columns:
				c[1].select_clear(0,END)
				c[1].select_set(a)
				c[1].see(a)

	def bind(self, event, cb, col=None, btn=False):
		if col != None:
			self.columns[col][not btn].bind(event,cb,True)
		else:
			for c in self.columns:
				c[not btn].bind(event,cb,True)

	def yview(self, *a):
		for c in self.columns:
			c[1].yview(*a)

	def yscroll(self, *a):
		self.vscroll.set(*a)
		for c in self.columns:
			c[1].yview(MOVETO, a[0])

	def select(self, e, l):
		sel = l.curselection()
		for c in self.columns:
			c[1].select_clear(0,END)
			for s in sel:
				c[1].select_set(s)

	def insert(self, index, text):
		if isstr(text):
			text = [text]
		if len(text) < len(self.columns):
			for _ in range(len(self.columns) - len(text)):
				text.append('')
		for c,t in zip(self.columns,text):
			c[1].insert(index, t)

	def delete(self, index):
		for c in self.columns:
			c[1].delete(index)

	def cur_selection(self):
		return self.columns[0][1].cur_selection()

	def get(self, index):
		return [c[1].get(index) for c in self.columns]

	def size(self):
		return self.columns[0][1].size()

# class ReportView(Frame):
	# def __init__(self, parent, columns=[''], **conf):
		# Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		# self.entry = 0
		# self.panes = []
		# self.columns = []
		# self.vscroll = Scrollbar(self, command=self.yview)
		# self.vscroll.pack(side=RIGHT, fill=Y)
		# p = self
		# while columns:
			# if len(columns) > 1:
				# c = PanedWindow(p, orient=HORIZONTAL, borderwidth=0, sashpad=2, sashwidth=0, sashrelief=RAISED)
				# self.panes.append(c)
				# l = Frame(c)
				# b = Button(l, text=columns[0])
				# b.pack(side=TOP, fill=X)
				# text = Text(l, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
				# text.pack(side=TOP, fill=BOTH, expand=1)
				# l.pack(side=LEFT, fill=BOTH, expand=1)
				# c['background'] = text['background']
				# if isinstance(p, PanedWindow):
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.disabled)
					# self.text.tag_config('Right')
					# p.add(c)
				# else:
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.dispatch)
					# text.tag_config('Selection', background='lightblue')
					# p['background'] = text['background']
					# c.pack(fill=BOTH, expand=1, padx=2, pady=2)
				# c.add(l)
				# p = c
			# else:
				# l = Frame(p)
				# b = Button(l, text=columns[0])
				# b.pack(side=TOP, fill=X)
				# text = Text(l, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
				# text.pack(side=TOP, fill=BOTH, expand=1)
				# l.pack(side=LEFT, fill=BOTH, expand=1)
				# if isinstance(p,PanedWindow):
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.disabled)
					# self.text.tag_config('Right')
					# p.add(l)
				# else:
					# text.orig = text._w + '_orig'
					# self.tk.call('rename', text._w, text.orig)
					# self.tk.createcommand(text._w, self.dispatch)
					# text.tag_config('Selection', background='lightblue')
					# l.pack()
			# self.columns.append((b,text))
			# del columns[0]
		# bind = [
			# ('<MouseWheel>', self.scroll),
			# ('<Home>', lambda a,i=0: self.move(a,i)),
			# ('<End>', lambda a,i=END: self.move(a,i)),
			# ('<Up>', lambda a,i=-1: self.move(a,i)),
			# ('<Left>', lambda a,i=-1: self.move(a,i)),
			# ('<Down>', lambda a,i=1: self.move(a,i)),
			# ('<Right>', lambda a,i=-1: self.move(a,i)),
			# ('<Prior>', lambda a,i=-10: self.move(a,i)),
			# ('<Next>', lambda a,i=10: self.move(a,i)),
		# ]
		# for d in bind:
			# parent.bind(*d)

	# def scroll(self, e):
		# if e.delta > 0:
			# for c in self.columns:
				# c[1].yview('scroll', -2, 'units')
		# else:
			# for c in self.columns:
				# c[1].yview('scroll', 2, 'units')

	# def move(self, e, a):
		# s = self.curselection()
		# if s:
			# if a == END:
				# a = self.size()-2
			# elif a not in [0,END]:
				# if a > 0:
					# a = min(self.size()-1, int(s[-1]) + a)
				# else:
					# a = max(int(s[0]) + a,0)
			# self.columns[0][1].select_clear(0,END)
			# self.columns[0][1].select_set(a)
			# self.columns[0][1].see(a)

	# def yview(self, *a):
		# for c in self.columns:
			# c[1].yview(*a)

	# def execute(self, t, cmd, args):
		# try:
			# return self.tk.call((t.orig, cmd) + args)
		# except TclError:
			# return ""

	# def insert(self, index, text):
		# if isstr(text):
			# text = [text]
		# if len(text) < len(self.columns):
			# for _ in range(len(self.columns) - len(text)):
				# text.append('')
		# l = False
		# for c,t in zip(self.columns,text):
			# if l:
				# self.execute(c[1],'insert',(i, text + '\n', 'entry%s' % self.entry, 'right'))
			# else:
				# self.execute(c[1],'insert',(i, text + '\n', 'entry%s' % self.entry))

# if group != None:
# 	self.entries[self.entry] = [index.count('.'),t,[self.entry,[],group],text]
# else:
# 	self.entries[self.entry] = [index.count('.'),t,None,text]
class TreeNode:
	def __init__(self, text, depth, entry):
		self.text = text
		self.depth = depth
		self.entry = entry
		self.parent = None

	def __repr__(self):
		return '<TreeNode text=%s depth=%d entry=%d>' % (repr(self.text), self.depth, self.entry)

class TreeGroup(TreeNode):
	def __init__(self, text, depth, entry, expanded):
		TreeNode.__init__(self, text, depth, entry)
		self.entry = entry
		self.expanded = expanded
		self.children = []

	def add_child(self, child):
		self.children.append(child)
		child.parent = self

	def __repr__(self):
		children = ''
		for child in self.children:
			children += '\n\t' + repr(child).replace('\n','\n\t')
		if children:
			children += '\n'
		return '<TreeGroup text=%s depth=%d entry=%d expanded=%d children=[%s]>' % (repr(self.text), self.depth, self.entry, self.expanded, children)

class TreeList(Frame):
	selregex = re.compile('\\bsel\\b')

	def __init__(self, parent, selectmode=SINGLE, groupsel=True, closeicon=None, openicon=None):
		self.selectmode = selectmode
		self.lastsel = None
		self.groupsel = groupsel
		self.entry = 0
		self.root = TreeGroup('<ROOT>', -1, -1, True)
		self.entries = {}
		if closeicon == None:
			closeicon = os.path.join('Images','treeclose.gif')
		if openicon == None:
			openicon = os.path.join('Images','treeopen.gif')
		self.icons = [PhotoImage(file=closeicon),PhotoImage(file=openicon)]

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		font = ('courier', -12, 'normal')
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, font=font, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0)
		self.text.configure(tabs=self.tk.call("font", "measure", self.text["font"], "-displayof", self, '  ')+9)
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		self.bind = self.text.bind

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_config('Hightlight', background='#CCCCCC')

	def execute(self, cmd, args):
		try:
			return self.tk.call((self.text.orig, cmd) + args)
		except TclError:
			return ""

	def dispatch(self, cmd, *args):
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)

	def lookup_coords(self, x,y):
		index = self.index('@%d,%d' % (x,y))
		if index:
			for o in xrange(1,100):
				for below in (True,False):
					check = self.index('@%d,%d' % (x,y + o * (1 if below else -1)))
					if check != index:
						return (index,below)
		return (index,True)

	def index(self, entry):
		index = None
		if isstr(entry) and entry.startswith('@'):
			entries = [int(n[5:]) for n in self.text.tag_names(entry) if n.startswith('entry')]
			if entries:
				entry = entries[0]
		if isinstance(entry, int):
			node = self.entries[entry]
			if node:
				index = ''
				while node != self.root:
					index = '%d%s%s' % (node.parent.children.index(node),'.' if index else '',index)
					node = node.parent
		return index

	def get_node(self, index):
		# print ('Get',index)
		node = None
		if isinstance(index, int):
			node = self.entries[index]
		elif isstr(index):
			node = self.root
			if index:
				indices = [int(i) for i in index.split('.')]
				while indices:
					node = node.children[indices[0]]
					del indices[0]
		return node

	def node_visibility(self, node):
		while node.parent != self.root:
			if not node.parent.expanded:
				return False
			node = node.parent
		return True

	def cur_highlight(self):
		ranges = self.text.tag_ranges('Hightlight')
		if ranges:
			entries = [int(n[5:]) for n in self.text.tag_names(ranges[0]) if n.startswith('entry')]
			if entries:
				return entries[0]
		return None

	def highlight(self, index):
		self.text.tag_remove('Hightlight', '1.0', END)
		if index == None:
			return
		node = self.get_node(index)
		self.text.tag_add('Hightlight',  'entry%s.first' % node.entry, 'entry%s.last' % node.entry)

	def cur_selection(self):
		s = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([int(n[5:]) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

	def select(self, index, modifier=0):
		if index == None:
			self.text.tag_remove('Selection', '1.0', END)
			self.lastsel = None
			return
		node = self.get_node(index)

		if modifier == 0 or (modifier == 1 and self.selectmode == EXTENDED and self.lastsel == None) or (modifier == 2 and self.selectmode != SINGLE):
			if self.selectmode != MULTIPLE and modifier != 2:
				self.text.tag_remove('Selection', '1.0', END)
			if self.selectmode == EXTENDED:
				self.lastsel = node.entry
			if not self.selected(node.entry):
				self.text.tag_add('Selection',  'entry%s.first' % node.entry, 'entry%s.last' % node.entry)
		elif modifier == 1 and self.selectmode == EXTENDED:
			if tuple(int(n) for n in self.text.index('entry%s.first' % self.lastsel).split('.')) > tuple(int(n) for n in self.text.index('entry%s.first' % node.entry).split('.')):
				d = '-1l'
			else:
				d = '+1l'
			c,f = self.text.index('entry%s.last %s lineend -1c' % (self.lastsel,d)),self.text.index('entry%s.last %s lineend -1c' % (node.entry,d))
			while c != f:
				r = self.text.tag_names(c)
				for e in r:
					if e.startswith('entry') and (self.groupsel or not isinstance(self.entries[int(e[5:])],TreeGroup)) and not 'Selection' in r:
						self.text.tag_add('Selection', '%s.first' % e, '%s.last' % e)
				c = self.text.index('%s %s lineend -1c' % (c,d))
			self.lastsel = node.entry

	def write_node(self, pos, node):
		# print ('Pos',pos)
		selectable = True
		if isinstance(node, TreeGroup):
			selectable = self.groupsel
			self.execute('insert',(pos, node.text, 'entry%s' % node.entry))
			self.execute('insert',(pos, '  ' * node.depth + '  '))
			self.execute('insert',('entry%s.last' % node.entry, '\n'))
			self.text.image_create('entry%s.first -1c' % node.entry, image=self.icons[node.expanded])
			self.text.tag_add('icon%s' % node.entry, 'entry%s.first -2c' % node.entry, 'entry%s.first -1c' % node.entry)
			self.text.tag_bind('icon%s' % node.entry, '<Button-1>', lambda e,i=node.entry: self.toggle(i))
		else:
			self.execute('insert',(pos, node.text, 'entry%s' % node.entry))
			self.execute('insert',(pos, '  ' * (node.depth+1)))
			self.execute('insert',('entry%s.last' % node.entry, '\n'))
		if selectable:
			self.text.tag_bind('entry%s' % node.entry, '<Button-1>', lambda e,i=node.entry: self.select(i,0))
			self.text.tag_bind('entry%s' % node.entry, '<Shift-Button-1>', lambda e,i=node.entry: self.select(i,1))
			self.text.tag_bind('entry%s' % node.entry, '<Control-Button-1>', lambda e,i=node.entry,t=0: self.select(i,2))

	def check_index(self, index):
		pieces = index.split(' ')
		for i in range(1,len(pieces)+1):
			test = ' '.join(pieces[:i])
			# print (test, self.text.index(test))

	def erase_branch(self, node, eraseRoot):
		end = 'entry%s.last lineend +1c' % node.entry
		if eraseRoot:
			start = 'entry%s.last linestart' % node.entry
		else:
			start = end
		while isinstance(node, TreeGroup) and node.expanded and node.children:
			deep_leaf = node.children[-1]
			end = 'entry%s.last lineend +1c' % deep_leaf.entry
			node = deep_leaf
		self.execute('delete', (start, end))

	def toggle(self, entry):
		group = self.get_node(entry)
		expanded = not group.expanded
		self.text.image_configure('icon%s.first' % group.entry, image=self.icons[expanded])
		if expanded:
			base = 'icon%s.first' % group.entry
			def insert_children(group, line_offset=1):
				for child in group.children:
					self.write_node('%s +%sl linestart' % (base,line_offset), child)
					line_offset += 1
					if isinstance(child, TreeGroup) and child.expanded:
						line_offset += insert_children(child, line_offset)
				return line_offset
			insert_children(group)
		else:
			self.erase_branch(group, False)
		group.expanded = expanded

	def delete(self, index):
		if index == ALL:
			self.entry = 0
			self.root.children = []
			self.entries = {}
			self.execute('delete', ('1.0', END))
		else:
			eraseRoot = True
			# print index
			if isstr(index):
				indices = index.split('.')
				if indices[-1] == ALL:
					eraseRoot = False
					index = '.'.join(indices[:-1])
			node = self.get_node(index)
			if self.node_visibility(node):
				self.erase_branch(node, eraseRoot)
			def delete_node(node):
				del self.entries[node.entry]
				if isinstance(node, TreeGroup):
					for child in node.children:
						delete_node(child)
			if eraseRoot:
				node.parent.children.remove(node)
				delete_node(node)
			else:
				# for child in node.children:
				while node.children:
					child = node.children[0]
					delete_node(child)
					del node.children[0]
			# print self.entries
			# print self.root

	# groupExpanded: None = not group, True = open by default, False = closed by default
	def insert(self, index, text, groupExpanded=None):
		# print ('Insert', index)
		indices = [int(i) for i in index.split('.')]
		parent_index = '.'.join(str(i) for i in indices[:-1])
		parent = self.get_node(parent_index)
		insert_index = indices[-1]
		if insert_index == -1:
			insert_index = len(parent.children)
			indices[-1] = insert_index
		node = None
		if groupExpanded != None:
			node = TreeGroup(text, parent.depth+1, self.entry, groupExpanded)
		else:
			node = TreeNode(text, parent.depth+1, self.entry)
		parent.add_child(node)
		self.entries[self.entry] = node
		self.entry += 1
		if self.node_visibility(node):
			base = '0.0'
			if len(parent.children) > 1:
				above = parent.children[-2]
				while isinstance(above, TreeGroup) and above.expanded and above.children:
					above = above.children[-1]
				base = 'entry%s.last +1l' % (above.entry)
			elif parent != self.root:
				base = 'entry%s.last +1l' % parent.entry
			self.write_node('%s linestart' % base, node)
		# print self.entries
		# print self.root
		return '.'.join(str(i) for i in indices)

	def get(self, index):
		node = self.get_node(index)
		return node.text

	def get_visibility(self, index):
		node = self.get_node(index)
		return self.node_visibility(node)

	def selected(self, index):
		node = self.get_node(index)
		return ('Selection' in self.text.tag_names('entry%s.first' % node.entry))

	def set(self, index, text):
		node = self.get_node(index)
		node.text = text
		selected = self.selected(index)
		start,end = self.text.tag_ranges('entry%s' % node.entry)
		self.execute('delete', (start, end))
		self.execute('insert', (start, text, 'entry%s' % node.entry))
		if selected:
			self.text.tag_add('Selection', start, end)

	def see(self, index):
		node = self.get_node(index)
		entry = 'entry%s' % node.entry
		ranges = self.text.tag_ranges(entry)
		if ranges:
			self.text.see(ranges[0])

# import TBL,DAT
# class Test(Tk):
	# def __init__(self):
		# Tk.__init__(self)
		# self.title('My Lists Test')

# #ReportList:
		# self.rl = ReportList(self, ['One','Two','Three'])
		# self.rl.pack(fill=BOTH, expand=1)
		# for n in range(50):
			# self.rl.insert(END, [str(n+x) for x in range(3)])
		# self.rl.bind('<ButtonRelease-1>', self.sel)

	# def sel(self, e):
		# s = self.rl.curselection()
		# for i in s:
			# print '\t',self.rl.get(i)

# #TreeList:
		# self.tl = TreeList(self)
		# self.tl.pack(fill=BOTH, expand=1)
		# self.tl.insert('-1', 'Zerg', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('-1', 'Protoss', False)
		# self.tl.insert('-1', 'Other', False)

		# tbl = TBL.TBL()
		# tbl.load_file('Libs\\MPQ\\rez\\stat_txt.tbl')
		# dat = DAT.UnitsDAT()
		# dat.load_file('Libs\\MPQ\\arr\\units.dat')

		# groups = [{},{},{},{}]
		# for i,n in enumerate(TBL.decompile_string(s) for s in tbl.strings[:228]):
			# g = dat.get_value(i,'StarEditGroupFlags')
			# s = n.split('<0>')
			# found = False
			# if s[0] == 'Zerg Zergling':
				# g = 1|2|4
			# for f in [1,2,4,3]:
				# if (f != 3 and g & f) or (f == 3 and not found):
					# if not s[2] in groups[f-1]:
						# if f == 4:
							# e = '2'
						# elif f == 3:
							# e = '3'
						# else:
							# e = str(f-1)
						# groups[f-1][s[2]] = self.tl.insert(e + '.-1', s[2], False)
					# self.tl.insert(groups[f-1][s[2]] + '.-1', '[%s] %s%s' % (i,s[0],['',' (%s)' % s[1]][s[1] != '*']))
					# found = True
		# self.tl.insert('-1', 'Zerg', True)
		# self.tl.insert('0.-1', 'Ground Units', True)
		# self.tl.insert('0.0.-1', 'Zerg Zergling')
		# self.tl.insert('0.0.-1', 'Zerg Zergling', False)
		# self.tl.insert('-1', 'Terran', False)
		# self.tl.insert('0', 'Test', False)
		# self.tl.bind('<Button-1>', self.test)
		# self.tl.bind('<Alt-d>', self.delete)
		# print self.tl.groups

	# def test(self, e):
		# print self.tl.text.tag_ranges('Selection')
		# s = self.tl.cur_selection()
		# print s
		# if s:
			# print self.tl.get(s[0],True)

	# def delete(self, e):
		# self.tl.delete(self.tl.cur_selection())

# #RichList:
		# self.rl = RichList(self)
		# self.rl.pack(fill=BOTH, expand=1)
		# self.rl.insert(END, 'test 1')
		# self.rl.insert(END, '  testing')
		# self.rl.insert(END, 'test 3')
		# print self.rl.index('2.1.0 lineend')
		# self.rl.text.tag_config('r', background='#FF0000')
		# print self.rl.tag_add('r','3.1.1','3.1.0 lineend -1c')
		# self.img = PhotoImage(file='Images\\treeopen.gif')
		# self.rl.image_create('2.1.1', image=self.img)
		# self.rl.bind('<Enter>', self.enter)

	# def enter(self, e):
		# self.rl.delete(0)

# def main():
	# gui = Test()
	# gui.mainloop()

# if __name__ == '__main__':
	# main()