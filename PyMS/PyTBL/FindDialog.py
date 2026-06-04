
from .Delegates import MainDelegate

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import UIKit as UI

import re

class FindDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.resettimer: str | None = None
		self.findhistory: list[str] = []
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False, escape=True, resizable=(True,False))

	def widgetize(self) -> (UI.Misc | None):
		self.find = UI.StringVar()
		self.casesens = UI.BooleanVar()
		self.regex = UI.BooleanVar()
		self.updown = UI.BooleanVar()
		self.updown.set(True)
		self.wrap = UI.BooleanVar()
		self.wrap.set(True)

		l = UI.Frame(self)
		f = UI.Frame(l)
		UI.Label(f, text='Find:').pack(side=UI.LEFT)
		self.findentry = UI.TextDropDown(f, self.find, self.findhistory, 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(fill=UI.X)
		self.findentry.entry.selection_range(0, UI.END)
		self.findentry.focus_set()
		f.pack(side=UI.TOP, fill=UI.X, pady=2)
		f = UI.Frame(l)
		UI.Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=UI.W).pack(fill=UI.X)
		UI.Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=UI.W).pack(fill=UI.X)
		UI.Checkbutton(f, text='Wrap', variable=self.wrap, anchor=UI.W).pack(fill=UI.X)
		f.pack(side=UI.LEFT, fill=UI.BOTH)
		f = UI.Frame(l)
		lf = UI.LabelFrame(f, text='Direction')
		self.up = UI.Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=UI.W)
		self.up.pack(fill=UI.X)
		self.down = UI.Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=UI.W)
		self.down.pack()
		lf.pack()
		f.pack(side=UI.RIGHT, fill=UI.Y)
		l.pack(side=UI.LEFT, fill=UI.BOTH, pady=2, expand=1)

		l = UI.Frame(self)
		UI.Button(l, text='Find Next', command=self.findnext, default=UI.NORMAL).pack(fill=UI.X, pady=1)
		UI.Button(l, text='Close', command=self.ok).pack(fill=UI.X, pady=4)
		l.pack(side=UI.LEFT, fill=UI.Y, padx=2)

		self.bind(UI.Key.Return(), self.findnext)

		return self.findentry

	def setup_complete(self) -> None:
		self.delegate.config_.windows.find.load_size(self)

	def findnext(self, event: UI.Event | None = None) -> None:
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
				regex_str = f'.*{re.escape(t)}.*'
			try:
				regex = re.compile(regex_str, 0 if self.casesens.get() else re.I)
			except Exception:
				self.findentry['bg'] = '#FFB4B4'
				self.resettimer = self.after_managed(1000, self.updatecolor)
				return
			wrap = self.wrap.get()
			down = self.updown.get()
			s = int(self.delegate.listbox.curselection()[0])
			def next_i(i: int, down: bool, size: int) -> int:
				if down:
					i += 1
					while i >= size:
						i -= size
				else:
					i -= 1
					while i < 0:
						i += size
				return i
			i = next_i(s, down, size)
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
					self.delegate.listbox.select_clear(0,UI.END)
					self.delegate.listbox.select_set(i)
					self.delegate.listbox.see(i)
					self.delegate.update()
					return
				i = next_i(i, down, size)
		p: UI.Misc = self
		if event and event.keycode != 13:
			p = self.parent
		UI.MessageBox.showinfo('Find', "Can't find text.", parent=p)

	def updatecolor(self) -> None:
		if self.resettimer:
			self.after_managed_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry_c

	def dismiss(self) -> None:
		self.delegate.config_.windows.find.save_size(self)
		PyMSDialog.dismiss(self)
