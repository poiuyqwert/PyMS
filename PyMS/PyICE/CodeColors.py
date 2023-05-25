
from ..Utilities.utils import couriernew, fit
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

from copy import deepcopy
from collections import OrderedDict

class CodeColors(PyMSDialog):
	def __init__(self, parent):
		self.cont = False
		self.tags = deepcopy(parent.text.tags)
		self.info = OrderedDict()
		self.info['Block'] = 'The color of a "block:" in the code.'
		self.info['Keywords'] = ['Keywords:\n    .headerstart  .headerend  [NONE]','HeaderStart']
		#self.info['Types'] = 'Variable types:\n    ' + '  '.join(AIBIN.types)
		self.info['Commands'] = 'The color of all the commands.'
		self.info['Animations'] = 'The color of all the header labels (IsID, Type, and Animations).'
		self.info['Number'] = 'The color of all numbers.'
		self.info['Comment'] = 'The color of a regular comment.'
		self.info['Operators'] = 'The color of the operators:\n    ( ) , = :'
		self.info['Error'] = 'The color of an error when compiling.'
		self.info['Warning'] = 'The color of a warning when compiling.'
		self.info['Selection'] = 'The color of selected text in the editor.'
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self):
		self.listbox = ScrolledListbox(self, font=couriernew, width=20, height=16)
		self.listbox.bind(ButtonRelease.Click_Left, self.select)
		for t in list(self.info.keys()):
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
		c.bind(ButtonRelease.Click_Left, lambda e,i=0: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Background', variable=self.bg)
		c.bind(ButtonRelease.Click_Left, lambda e,i=1: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Bold', variable=self.bold)
		c.bind(ButtonRelease.Click_Left, lambda e,i=2: self.select(e,i))
		c.grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind(Mouse.Click_Left, lambda e,i=0: self.colorselect(e, i))
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind(Mouse.Click_Left, lambda e,i=1: self.colorselect(e, i))
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
		i = list(self.info.keys())[int(self.listbox.curselection()[0])]
		s = self.tags[i.replace(' ', '')]
		if n == None:
			if isinstance(self.info[i], list):
				t = self.info[i][0].split('\n')
			else:
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
			c = ColorChooser.askcolor(parent=self, initialcolor=v['background'], title='Select %s color' % g)
			if c[1]:
				v['background'] = c[1]
				k = list(self.info.keys())[int(self.listbox.curselection()[0])].replace(' ','')
				self.tags[k][g] = c[1]
				if isinstance(self.info[k], list):
					self.tags[self.info[k][1]][g] = c[1]
			self.focus_set()

	def ok(self):
		self.cont = self.tags
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)
