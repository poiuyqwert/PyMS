
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *
from ..Utilities.TextDropDown import TextDropDown

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

		self.bind(Key.Return, self.findnext)

		return self.findentry

	def setup_complete(self):
		self.parent.settings.windows.load_window_size('find', self)

	def findnext(self, key=None):
		self.updatecolor()
		t = self.find.get()
		if not t in self.parent.findhistory:
			self.parent.findhistory.insert(0, t)
		size = self.parent.listbox.size()
		if size:
			if self.regex.get():
				regex = t
				if not regex.startswith('\\A'):
					regex = '.*' + regex
				if not regex.endswith('\\Z'):
					regex = regex + '.*'
			else:
				regex = '.*%s.*' % re.escape(t)
			try:
				regex = re.compile(regex, 0 if self.casesens.get() else re.I)
			except:
				self.reset = self.findentry
				self.reset.c = self.reset['bg']
				self.reset['bg'] = '#FFB4B4'
				self.resettimer = self.after(1000, self.updatecolor)
				return
			wrap = self.wrap.get()
			down = self.updown.get()
			s = int(self.parent.listbox.curselection()[0])
			def next(i, down, size):
				if down:
					i += 1
					while i >= size:
						i -= size
				else:
					i -= 1
					while i < 0:
						i += size
				return i
			i = next(s, down, size)
			check = 0
			if wrap:
				check = size - 1
			elif down:
				check = size - s - 1
			else:
				check = s
			while check:
				check -= 1
				if regex.match(self.parent.listbox.get(i)):
					self.parent.listbox.select_clear(0,END)
					self.parent.listbox.select_set(i)
					self.parent.listbox.see(i)
					self.parent.update()
					return
				i = next(i, down, size)
		p = self
		if key and key.keycode != 13:
			p = self.parent
		MessageBox.showinfo('Find', "Can't find text.")

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def dismiss(self):
		self.parent.settings.windows.save_window_size('find', self)
		PyMSDialog.dismiss(self)
