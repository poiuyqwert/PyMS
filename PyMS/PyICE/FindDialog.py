
from .Delegates import MainDelegate

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.Settings import Settings

import re

class FindDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: MainDelegate) -> None:
		self.delegate = delegate
		self.resettimer: str | None = None
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False)

	def widgetize(self) -> Misc | None:
		self.lists: list[ScrolledListbox] = []
		self.find = StringVar()
		self.regex = IntVar()
		self.casesens = IntVar()
		self.ids = IntVar()

		f = Frame(self)
		Label(f, text='Find: ').pack(side=LEFT)
		self.findentry = TextDropDown(f, self.find, self.delegate.settings.get('findhistory', []), 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(side=LEFT,fill=X, expand=1)
		f.pack(fill=X)
		f = Frame(self)
		Checkbutton(f, text='Regex', variable=self.regex).pack(side=LEFT)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens).pack(side=LEFT)
		Checkbutton(f, text='Include ID\'s in Search', variable=self.ids).pack(side=LEFT)
		f.pack()

		self.treelist = TreeList(self, EXTENDED, False)
		self.treelist.bind(Mouse.Click_Left(), self.action_states)
		self.treelist.pack(fill=BOTH, expand=1)

		buttons = Frame(self)
		self.findb = Button(buttons, text='Find', width=12, command=self.search, default=NORMAL)
		self.findb.pack(side=LEFT, padx=3, pady=3)
		self.addselectb = Button(buttons, text='Add Selection', width=12, command=lambda: self.select(False), state=DISABLED)
		self.addselectb.pack(side=LEFT, padx=3, pady=3)
		self.selectb = Button(buttons, text='Select', width=12, command=lambda: self.select(True), state=DISABLED)
		self.selectb.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=12, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttons.pack()
		self.action_states()

		self.bind(Key.Return(), self.search)

		return self.findentry

	def setup_complete(self) -> None:
		self.minsize(330,160)
		self.delegate.settings.windows.load_window_size('find', self)

	def action_states(self, event: Event | None = None) -> None:
		if not self.treelist.cur_selection() == -1:
			s = [NORMAL,DISABLED][not self.treelist.cur_selection()]
		else:
			s = DISABLED
		for b in [self.addselectb,self.selectb]:
			b['state'] = s

	def updatecolor(self) -> None:
		self.findentry.entry['bg'] = self.findentry_c

	def search(self, event: Event | None = None) -> None:
		self.lists = []
		self.treelist.delete(ALL)
		if not self.find.get() in self.delegate.settings.findhistory:
			self.delegate.settings.findhistory.append(self.find.get())
		if self.regex.get():
			regex = self.find.get()
		else:
			regex = '.*%s.*' % re.escape(self.find.get())
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()])
		except:
			self.findentry_c = self.findentry.entry['bg']
			self.findentry.entry['bg'] = '#FFB4B4'
			self.resettimer = self.after(1000, self.updatecolor)
			return
		d: list[tuple[str, ScrolledListbox]] = [
			('IScript Entries',self.delegate.iscriptlist),
			('Images',self.delegate.imageslist),
			('Sprites',self.delegate.spriteslist),
			('Flingys',self.delegate.flingylist),
			('Units',self.delegate.unitlist)
		]
		for n,l in d:
			added = False
			for x in range(l.size()): # type: ignore[call-overload]
				t = l.get(x)
				if not self.ids.get():
					t = t[4:]
					if n != 'IScript Entries':
						t = '['.join(t.split('[')[:-1])
				if r.match(t):
					if not added:
						self.treelist.insert('-1', n, True)
						self.lists.append(l)
						added = True
					self.treelist.insert('-1.-1', l.get(x))

	def select(self, set: bool) -> None:
		c = []
		for i in self.treelist.cur_selection():
			index = self.treelist.index(i)
			text = self.treelist.get(i)
			assert index is not None and text is not None
			g,s = int(index.split('.')[0]),int(text[:3].lstrip())
			if self.lists[g] == self.delegate.iscriptlist:
				s = sorted(self.delegate.get_ibin().headers.keys()).index(s)
			if not g in c:
				if set:
					self.lists[g].select_clear(0,END)
				self.lists[g].see(s)
				c.append(g)
			self.lists[g].select_set(s)
			self.lists[g].listbox.event_generate(WidgetEvent.Listbox.Select())
		self.ok()

	def dismiss(self) -> None:
		self.delegate.settings.windows.save_window_size('find', self)
		PyMSDialog.dismiss(self)
