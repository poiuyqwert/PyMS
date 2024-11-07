
from __future__ import annotations

from .RichList import RichList
from ..Widgets import *
from ..Font import Font
from ..EventPattern import *
from ..Types import SelectMode

from typing import Literal, Sequence, Callable

class EditableReportSubList(RichList):
	def __init__(self, parent: Misc, selectmode: SelectMode, report: ReportList, **kwargs) -> None:
		self.report = report
		self.lastsel: str | None = None
		self.selectmode = selectmode
		self.checkedit: str | None = None
		self.edittext = StringVar()
		self.entry = 0
		self.entries = []
		self.dctimer: str | None = None
		self.editing = False
		self.lineselect = False

		Frame.__init__(self, parent)
		self.text = Text(self, cursor='arrow', height=1, width=1, font=Font.fixed(), wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=False, **kwargs)
		self.text.config(bd=0)
		self.text.pack(fill=BOTH, expand=1)

		text_w = getattr(self.text, '_w')
		self.text_orig = text_w + '_orig'
		self.tk.call('rename', text_w, self.text_orig)
		self.tk.createcommand(text_w, self.dispatch)
		self.text.tag_config('Selection', background='lightblue')
		self.text.tag_bind('Selection', Mouse.Click_Left(), self.edit)
		bind = [
			(Mouse.Click_Left(), self.deselect),
			(Key.Up(), lambda e: self.movesel(-1)),
			(Key.Down(), lambda e: self.movesel(1)),
			(Shift.Up(), lambda e: self.movesel(-1,True)),
			(Shift.Down(), lambda e: self.movesel(1,True)),
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

	def insert(self, index: int | Literal['end'], text, tags: str | Sequence[str] | None = None) -> str:
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		def doselect_callback(tag_name: str, s: int) -> Callable[[Event], None]:
			def doselect(event: Event) -> None:
				self.doselect(tag_name, s)
			return doselect
		def popup_callback(tag_name: str) -> Callable[[Event], None]:
			def popup(event: Event) -> None:
				self.popup(event, tag_name)
			return popup
		self.text.tag_bind(e, Mouse.Click_Left(), doselect_callback(e,0))
		self.text.tag_bind(e, Double.Click_Left(), self.doubleclick)
		self.text.tag_bind(e, Mouse.Click_Right(), popup_callback(e))
		self.text.tag_bind(e, Shift.Click_Left(), doselect_callback(e,1))
		self.text.tag_bind(e, Ctrl.Click_Left(), doselect_callback(e,2))
		if tags is None:
			tags = e
		elif isinstance(tags, str):
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
		return self.execute('insert',(i + ' lineend', '\n'))

	def doubleclick(self, e: Event) -> None:
		if self.report.dcmd:
			self.report.dcmd(e)

	def popup(self, e: Event, i: str) -> None:
		if self.report.pcmd:
			self.report.pcmd(e,i)

	def selected(self, e: int | str) -> bool:
		if isinstance(e,int):
			e = 'entry%s' % e
		return not not [n for n in self.text.tag_names('%s.first' % e) if n == 'Selection']

	def deselect(self, e: Event) -> None:
		if self.lineselect:
			self.lineselect = False
		else:
			self.lastsel = None
			self.text.tag_remove('Selection', '1.0', END)

	def movesel(self, d: int, s: bool = False) -> None:
		if self.lastsel:
			l = self.lastsel
		elif self.entries:
			l = str(self.entries[0])
		if not l:
			return
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

	def doselect(self, i: str, t: int) -> None:
		self.lineselect = True
		if self.editing:
			self.text.tag_remove('Selection', '1.0', END)
			self.report.scmd()
			return
		if t == 0 or (t == 1 and self.selectmode == EXTENDED and self.lastsel is None) or (t == 2 and self.selectmode != SINGLE):
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

	def nodc(self) -> None:
		self.dctimer = None

	def edit(self, e: Event | None = None) -> None:
		if self.dctimer:
			self.after_cancel(self.dctimer)
			self.dctimer = None
			return
		self.editing = True
		if isinstance(e,int):
			tag_name = 'entry%s' % self.entries[e]
		elif e is None:
			tag_name = [n for n in self.text.tag_names('Selection.first') if n.startswith('entry')][0]
		else:
			c = '@%s,%s' % (e.x,e.y)
			tag_name = [n for n in self.text.tag_names(c) if n.startswith('entry')][0]
		index = self.text.index(tag_name + '.first')
		text = self.text.get(tag_name + '.first', tag_name + '.last')
		self.checkedit = text
		self.edittext.set(text)
		entry = Entry(self.text, width=len(text) + 5, textvariable=self.edittext, bd=1, relief=SOLID)
		entry.select_range(0,END)
		def endedit_callback(index: str, tag_name: str) -> Callable[[Event], None]:
			def endedit(e: Event) -> None:
				self.endedit(index, tag_name)
			return endedit
		entry.bind(Key.Return(), endedit_callback(index,tag_name))
		entry.bind(Focus.Out(), endedit_callback(index,tag_name))
		self.text.window_create('%s.first' % tag_name, window=entry)
		entry.focus_set()
		self.execute('delete',(tag_name + '.first', tag_name + '.last'))
		self.text.tag_remove('Selection', '1.0', END)

	def endedit(self, i: str, n: str) -> None:
		t = self.edittext.get()
		if self.checkedit is not None and self.checkedit != t and self.report.rcmd and not self.report.rcmd(self.entries.index(int(n[5:])),t):
			t = self.checkedit
		self.execute('delete',(i + ' linestart', i + ' lineend'))
		self.execute('insert',(i, t, n + ' Selection'))
		self.editing = False
		self.checkedit = None

	def get(self, index: int) -> str:
		if self.checkedit:
			return self.checkedit
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index])

class ReportSubList(RichList):
	def __init__(self, parent: Misc, **kwargs):
		self.entry = 0
		self.entries = []
		Frame.__init__(self, parent)
		self.text = Text(self, cursor='arrow', height=1, width=1, font=Font.fixed(), bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, exportselection=False, **kwargs)
		self.text.pack(fill=BOTH, expand=1)

		text_w = getattr(self.text, '_w')
		self.text_orig = text_w + '_orig'
		self.tk.call('rename', text_w, self.text_orig)
		self.tk.createcommand(text_w, self.dispatch)
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

	def select(self, e: int | str | Literal['end']) -> None:
		pass

	def insert(self, index: int | Literal['end'], text: str, tags: str | Sequence[str] | None = 'RightAlign') -> str:
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		# def select_callback(tag: str) -> Callable[[Event], None]:
		# 	def select(event: Event) -> None:
		# 		self.select(tag)
		# 	return select
		# self.text.tag_bind(e, Mouse.Click_Left(), select_callback(e))
		if tags is None:
			tags = e
		elif isinstance(tags, str):
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
	def __init__(self, parent: Misc, columns: list[str | None] = [''], selectmode: SelectMode = SINGLE, scmd=None, rcmd=None, pcmd=None, dcmd=None, min_widths: list[int] | None = None, **conf) -> None:
		self.scmd = scmd
		self.rcmd = rcmd
		self.pcmd = pcmd
		self.dcmd = dcmd
		self.entry = 0
		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.selectmode = selectmode
		self.panes = PanedWindow(self, orient=HORIZONTAL, borderwidth=0, sashpad=0, sashwidth=4, sashrelief=FLAT)
		self.columns: list[tuple[Button, RichList]] = []
		self.vscroll = Scrollbar(self)
		self.vscroll.config(command=self.yview)
		self.vscroll.pack(side=RIGHT, fill=Y)
		for n,title in enumerate(columns):
			l = Frame(self.panes)
			if title is None:
				b = Button(l, text=' ', state=DISABLED)
			else:
				b = Button(l, text=title)
			b.pack(side=TOP, fill=X)
			lb: RichList
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

	def select_set(self, i: int | Literal['end']) -> None:
		self.columns[0][1].select(i)

	def bind(self, event: str, cb: Callable[[Event], None], col: int | None = None, btn: bool = False) -> None: # type: ignore[override]
		if col is not None:
			self.columns[col][not btn].bind(event,cb,True)
		else:
			for c in self.columns:
				c[not btn].bind(event,cb,True)

	def yview(self, *a: float) -> None:
		for c in self.columns:
			c[1].yview(*a)

	def yscroll(self, *a: float) -> None:
		self.vscroll.set(*a)
		for c in self.columns:
			c[1].yview(MOVETO, a[0])

	# def select(self, e: Event, l: RichList) -> None:
	# 	sel = l.cur_selection()
	# 	for c in self.columns:
	# 		c[1].select_clear(0,END)
	# 		for s in sel:
	# 			c[1].select_set(s)

	def insert(self, index: int | Literal['end'], text: str | list[str]):
		if isinstance(text, str):
			text = [text]
		if len(text) < len(self.columns):
			for _ in range(len(self.columns) - len(text)):
				text.append('')
		for c,t in zip(self.columns,text):
			c[1].insert(index, t)

	def delete(self, index: int | Literal['all']) -> None:
		for c in self.columns:
			c[1].delete(index)

	def cur_selection(self) -> list[int]:
		return self.columns[0][1].cur_selection()

	def get(self, index: int) -> list[str]:
		return [c[1].get(index) for c in self.columns]

	def size(self) -> int: # type: ignore[override]
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
