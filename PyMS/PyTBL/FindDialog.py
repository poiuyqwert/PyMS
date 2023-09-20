
from .Delegates import MainDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *

import re

class FindDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.resettimer: str | None = None
		self.findhistory: list[str] = []
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False, escape=True, resizable=(True,False))

	def widgetize(self) -> (Misc | None):
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
		self.findentry = TextDropDown(f, self.find, self.findhistory, 30)
		self.findentry_c = self.findentry['bg']
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

		self.bind(Key.Return(), self.findnext)

		return self.findentry

	def setup_complete(self) -> None:
		self.delegate.config_.windows.find.load_size(self)

	def findnext(self, event: Event | None = None) -> None:
		self.updatecolor()
		t = self.find.get()
		if not t in self.findhistory:
			self.findhistory.insert(0, t)
		size: int = self.delegate.listbox.size() # type: ignore[assignment]
		if size:
			if self.regex.get():
				regex_str = t
				if not regex_str.startswith('\\A'):
					regex_str = '.*' + regex_str
				if not regex_str.endswith('\\Z'):
					regex_str = regex_str + '.*'
			else:
				regex_str = '.*%s.*' % re.escape(t)
			try:
				regex = re.compile(regex_str, 0 if self.casesens.get() else re.I)
			except:
				self.findentry['bg'] = '#FFB4B4'
				self.resettimer = self.after(1000, self.updatecolor)
				return
			wrap = self.wrap.get()
			down = self.updown.get()
			s = int(self.delegate.listbox.curselection()[0])
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
				if regex.match(self.delegate.listbox.get(i)):
					self.delegate.listbox.select_clear(0,END)
					self.delegate.listbox.select_set(i)
					self.delegate.listbox.see(i)
					self.delegate.update()
					return
				i = next(i, down, size)
		p: Misc = self
		if event and event.keycode != 13:
			p = self.parent
		MessageBox.showinfo('Find', "Can't find text.", parent=p)

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def dismiss(self) -> None:
		self.delegate.config_.windows.find.save_size(self)
		PyMSDialog.dismiss(self)
