
from ..Widgets import *
from ..EventPattern import *

import re

from typing import Literal, Sequence, Callable

class RichList(Frame):
	selregex = re.compile(r'\bsel\b')
	idregex = re.compile(r'(\d+)\.(\d+).(\d+)(.+)?')

	def __init__(self, parent: Misc, **kwargs):
		self.entry = 0
		self.entries: list[int] = []

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=False, **kwargs)
		self.text.config(bd=0)
		self.text.grid(sticky=NSEW)
		self.hscroll.config(command=self.text.xview)
		self.hscroll.grid(sticky=EW)
		self.vscroll.config(command=self.text.yview)
		self.vscroll.grid(sticky=NS, row=0, column=1)
		self.grid_rowconfigure(0,weight=1)
		self.grid_columnconfigure(0,weight=1)

		text_w = getattr(self.text, '_w')
		self.text_orig = text_w + '_orig'
		self.tk.call('rename', text_w, self.text_orig)
		self.tk.createcommand(text_w, self.dispatch)
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
		self.yview = self.text.yview

	def index(self, index: str) -> int:
		m = self.idregex.match(index)
		if m:
			index = 'entry%s.first +%sl +%sc' % (self.entries[int(m.group(1))-1],int(m.group(2))-1,int(m.group(3)))
			if m.group(4):
				index += str(m.group(4))
		return int(self.execute('index',(index,)))

	def tag_add(self, tag: str, index: str, *args: str) -> None:
		self.text.tag_add(tag, self.index(index), *tuple(map(self.index, args)))

	def tag_nextrange(self, tag: str, start: str, end: str) -> (tuple[str, str] | tuple[()]):
		return self.text.tag_nextrange(tag, self.index(start), self.index(end))

	def tag_prevrange(self, tag: str, start: str, end: str) -> (tuple[str, str] | tuple[()]):
		return self.text.tag_prevrange(tag, self.index(start), self.index(end))

	def image_create(self, index: str, cnf={}, **kw) -> Any:
		return self.text.image_create(self.index(index), cnf, **kw)

	def image_configure(self, index: str, **options) -> Any:
		return self.text.image_configure(self.index(index), **options)

	def image_cget(self, index: str, option: str) -> Any:
		return self.text.image_configure(self.index(index), option)

	def select(self, e: int | str | Literal['end']) -> None:
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

	def insert(self, index: int | Literal['end'], text: str, tags: str | Sequence[str] | None = None) -> str:
		if index == END:
			index = -1
		e = 'entry%s' % self.entry
		def select_callback(tag: str) -> Callable[[Event], None]:
			def select(event: Event) -> None:
				self.select(tag)
			return select
		self.text.tag_bind(e, Mouse.Click_Left(), select_callback(e))
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

	def delete(self, index: int | Literal['all', 'end']) -> str:
		if index == ALL:
			self.entry = 0
			self.entries = []
			return self.execute('delete', ('1.0',END))
		if index == END:
			index = -1
		r = self.execute('delete',('entry%s.first' % self.entries[index],'entry%s.last' % self.entries[index]))
		if r:
			del self.entries[index]
		return r

	def execute(self, cmd: str, args: tuple[str, ...]) -> str:
		try:
			return self.tk.call((self.text_orig, cmd) + args)
		except:
			return ""

	def dispatch(self, cmd: str, *args: str) -> str:
		if not cmd in ['insert','delete'] and not 'sel' in args:
			return self.execute(cmd, args)
		return ''

	def get(self, index: int) -> str:
		return self.text.get('entry%s.first' % self.entries[index],'entry%s.last -1c' % self.entries[index])

	def size(self) -> int: # type: ignore[override]
		lines = int(self.text.index('end-1c').split('.')[0])
		index = 1
		last_char = self.text.get('end-1c', 'end')
		while last_char and last_char in '\r\n':
			lines -= 1
			index += 1
			last_char = self.text.get(f'end-{index}c', f'end-{index+1}c')
		return lines

	def cur_selection(self) -> list[int]:
		s: list[int] = []
		for i in self.text.tag_ranges('Selection')[::2]:
			s.extend([self.entries.index(int(n[5:])) for n in self.text.tag_names(i) if n.startswith('entry')])
		return s

# import TBL,DAT
# class Test(Tk):
	# def __init__(self):
		# Tk.__init__(self)
		# self.title('RichList Test')

		# self.rl = RichList(self)
		# self.rl.pack(fill=BOTH, expand=1)
		# self.rl.insert(END, 'test 1')
		# self.rl.insert(END, '  testing')
		# self.rl.insert(END, 'test 3')
		# print(self.rl.index('2.1.0 lineend'))
		# self.rl.text.tag_config('r', background='#FF0000')
		# print(self.rl.tag_add('r','3.1.1','3.1.0 lineend -1c'))
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
