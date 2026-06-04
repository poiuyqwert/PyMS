
from .Delegates import MainDelegate

from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities import Config

import re

class FindDialog(PyMSDialog):
	def __init__(self, parent: UI.Misc, delegate: MainDelegate, window_geometry_config: Config.WindowGeometry, find_history_config: Config.List[str]) -> None:
		self.delegate = delegate
		self.window_geometry_config = window_geometry_config
		self.find_history_config = find_history_config
		self.resettimer: str | None = None
		self.lists: list[UI.ScrolledListbox] = []
		self.findentry_c: str | None = None
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False)

	def widgetize(self) -> UI.Misc | None:
		self.find = UI.StringVar()
		self.regex = UI.IntVar()
		self.casesens = UI.IntVar()
		self.ids = UI.IntVar()

		f = UI.Frame(self)
		UI.Label(f, text='Find: ').pack(side=UI.LEFT)
		self.findentry = UI.TextDropDown(f, self.find, self.find_history_config.data, 30)
		self.findentry_c = self.findentry['bg']
		self.findentry.pack(side=UI.LEFT,fill=UI.X, expand=1)
		f.pack(fill=UI.X)
		f = UI.Frame(self)
		UI.Checkbutton(f, text='Regex', variable=self.regex).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='Case Sensitive', variable=self.casesens).pack(side=UI.LEFT)
		UI.Checkbutton(f, text='Include ID\'s in Search', variable=self.ids).pack(side=UI.LEFT)
		f.pack()

		self.treelist = UI.TreeList(self, UI.EXTENDED, False)
		self.treelist.bind(UI.Mouse.Click_Left(), self.action_states)
		self.treelist.pack(fill=UI.BOTH, expand=1)

		buttons = UI.Frame(self)
		self.findb = UI.Button(buttons, text='Find', width=12, command=self.search, default=UI.NORMAL)
		self.findb.pack(side=UI.LEFT, padx=3, pady=3)
		self.addselectb = UI.Button(buttons, text='Add Selection', width=12, command=lambda: self.select(False), state=UI.DISABLED)
		self.addselectb.pack(side=UI.LEFT, padx=3, pady=3)
		self.selectb = UI.Button(buttons, text='Select', width=12, command=lambda: self.select(True), state=UI.DISABLED)
		self.selectb.pack(side=UI.LEFT, padx=3, pady=3)
		UI.Button(buttons, text='Cancel', width=12, command=self.cancel).pack(side=UI.LEFT, padx=3, pady=3)
		buttons.pack()
		self.action_states()

		self.bind(UI.Key.Return(), self.search)

		return self.findentry

	def setup_complete(self) -> None:
		self.minsize(330,160)
		self.window_geometry_config.load_size(self)

	def action_states(self, _event: UI.Event | None = None) -> None:
		if not self.treelist.cur_selection() == -1:
			s = [UI.NORMAL,UI.DISABLED][not self.treelist.cur_selection()]
		else:
			s = UI.DISABLED
		for b in [self.addselectb,self.selectb]:
			b['state'] = s

	def updatecolor(self) -> None:
		self.findentry.entry['bg'] = self.findentry_c

	def search(self, _event: UI.Event | None = None) -> None:
		self.lists = []
		self.treelist.delete(UI.ALL)
		if not self.find.get() in self.find_history_config.data:
			self.find_history_config.data.append(self.find.get())
		if self.regex.get():
			regex = self.find.get()
		else:
			regex = f'.*{re.escape(self.find.get())}.*'
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()])
		except Exception:
			self.findentry_c = self.findentry.entry['bg']
			self.findentry.entry['bg'] = '#FFB4B4'
			self.resettimer = self.after_managed(1000, self.updatecolor)
			return
		d: list[tuple[str, UI.ScrolledListbox]] = [
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

	def select(self, set_selection: bool) -> None:
		c = []
		for i in self.treelist.cur_selection():
			index = self.treelist.index(i)
			text = self.treelist.get(i)
			assert index is not None and text is not None
			g,s = int(index.split('.', maxsplit=1)[0]),int(text[:3].lstrip())
			if self.lists[g] == self.delegate.iscriptlist:
				s = sorted(script.id for script in self.delegate.get_iscript_bin().list_scripts()).index(s)
			if not g in c:
				if set_selection:
					self.lists[g].select_clear(0,UI.END)
				self.lists[g].see(s)
				c.append(g)
			self.lists[g].select_set(s)
			self.lists[g].listbox.event_generate(UI.WidgetEvent.Listbox.Select())
		self.ok()

	def dismiss(self) -> None:
		self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
