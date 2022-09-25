
from .utils import isstr
from .UIKit import *

import re

class RichList(Frame):
	selregex = re.compile(r'\bsel\b')
	idregex = re.compile(r'(\d+)\.(\d+).(\d+)(.+)?')

	def __init__(self, parent, **kwargs):
		self.entry = 0
		self.entries = []

		Frame.__init__(self, parent, bd=2, relief=SUNKEN)
		self.hscroll = Scrollbar(self, orient=HORIZONTAL)
		self.vscroll = Scrollbar(self)
		self.text = Text(self, cursor='arrow', height=1, bd=0, wrap=NONE, insertontime=0, insertofftime=65535, highlightthickness=0, xscrollcommand=self.hscroll.set, yscrollcommand=self.vscroll.set, exportselection=0, **kwargs)
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
		return self.text.image_configure(self.index(index), **options)

	def image_cget(self, index, option):
		return self.text.image_configure(self.index(index), option)

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
