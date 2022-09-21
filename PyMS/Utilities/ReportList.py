
from .utils import isstr
from .RichList import RichList
from .UIKit import *

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
		self.text = Text(self, cursor='arrow', height=1, width=1, font=Font.fixed(), bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		self.text.orig = self.text._w + '_orig'
		self.tk.call('rename', self.text._w, self.text.orig)
		self.tk.createcommand(self.text._w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_bind('Selection', Mouse.Click_Left, self.edit)
		bind = [
			(Mouse.Click_Left, self.deselect),
			(Key.Up, lambda e: self.movesel(-1)),
			(Key.Down, lambda e: self.movesel(1)),
			(Shift.Up, lambda e: self.movesel(-1,True)),
			(Shift.Down, lambda e: self.movesel(1,True)),
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
		self.text.tag_bind(e, Mouse.Click_Left, lambda e,i=e: self.doselect(i,0))
		self.text.tag_bind(e, Double.Click_Left, self.doubleclick)
		self.text.tag_bind(e, Mouse.Click_Right, lambda e,i=e: self.popup(e,i))
		self.text.tag_bind(e, Shift.Click_Left, lambda e,i=e: self.doselect(i,1))
		self.text.tag_bind(e, Ctrl.Click_Left, lambda e,i=e: self.doselect(i,2))
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
			self.report.scmd()
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
			tag_name = 'entry%s' % self.entries[e]
		elif e == None:
			tag_name = [n for n in self.text.tag_names('Selection.first') if n.startswith('entry')][0]
		else:
			c = '@%s,%s' % (e.x,e.y)
			tag_name = [n for n in self.text.tag_names(c) if n.startswith('entry')][0]
		index = self.text.index(tag_name + '.first')
		self.checkedit = self.text.get(tag_name + '.first', tag_name + '.last')
		self.edittext.set(self.checkedit)
		e = Entry(self.text, width=len(self.checkedit) + 5, textvariable=self.edittext, bd=1, relief=SOLID)
		e.select_range(0,END)
		e.bind(Key.Return, lambda _,i=index,n=tag_name: self.endedit(i,n))
		e.bind(Focus.Out, lambda _,i=index,n=tag_name: self.endedit(i,n))
		self.text.window_create('%s.first' % tag_name, window=e)
		e.focus_set()
		self.execute('delete',(tag_name + '.first', tag_name + '.last'))
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
		self.text = Text(self, cursor='arrow', height=1, width=1, font=Font.fixed(), bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=0, **kwargs)
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
		self.text.tag_bind(e, Mouse.Click_Left, self.select)
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
		for n,title in enumerate(columns):
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

	def select_set(self, i):
		self.columns[0][1].select(i)

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


# import TBL,DAT
# class Test(Tk):
	# def __init__(self):
		# Tk.__init__(self)
		# self.title('ReportList Test')

		# self.rl = ReportList(self, ['One','Two','Three'])
		# self.rl.pack(fill=BOTH, expand=1)
		# for n in range(50):
			# self.rl.insert(END, [str(n+x) for x in range(3)])
		# self.rl.bind('<ButtonRelease-1>', self.sel)

	# def sel(self, e):
		# s = self.rl.curselection()
		# for i in s:
			# print('\t',self.rl.get(i))

# def main():
	# gui = Test()
	# gui.mainloop()

# if __name__ == '__main__':
	# main()
