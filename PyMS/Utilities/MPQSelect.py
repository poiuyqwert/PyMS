
from .PyMSDialog import PyMSDialog
from .UIKit import *
from . import Assets
from .MPQHandler import MPQHandler
from .Settings import Settings

import os, re

class MPQSelect(PyMSDialog):
	def __init__(self, parent, mpqhandler, filetype, search, settings, open_type='Open'): # type: (Misc, MPQHandler, str, str, Settings, str) -> None
		self.mpqhandler = mpqhandler
		self.search = StringVar()
		self.search.set(search)
		self.search.trace('w', self.updatesearch)
		self.settings = settings
		self.regex = IntVar()
		self.regex.set(0)
		self.files = [] # type: list[str]
		self.file = None # type: str | None
		self.resettimer = None # type: str | None
		self.searchtimer = None # type: str | None
		self.open_type = open_type
		PyMSDialog.__init__(self, parent, self.open_type + ' a ' + filetype)

	def widgetize(self): # type: () -> (Misc | None)
		self.listbox = ScrolledListbox(self, width=35, height=10)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()

		s = Frame(self)
		history = self.settings.settings.get('mpqselecthistory',[])[::-1]
		self.textdrop = TextDropDown(s, self.search, history)
		self.textdrop.entry.c = self.textdrop.entry['bg']
		self.textdrop.pack(side=LEFT, fill=X, padx=1, pady=2)
		self.open = Button(s, text=self.open_type, width=10, command=self.ok)
		self.open.pack(side=RIGHT, padx=1, pady=3)
		s.pack(fill=X)
		s = Frame(self)
		Radiobutton(s, text='Wildcard', variable=self.regex, value=0, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		Radiobutton(s, text='Regex', variable=self.regex, value=1, command=self.updatelist).pack(side=LEFT, padx=1, pady=2)
		Button(s, text='Cancel', width=10, command=self.cancel).pack(side=RIGHT, padx=1, pady=3)
		s.pack(fill=X)

		self.listfiles()
		self.updatelist()

		return self.open

	def setup_complete(self): # type: () -> None
		self.settings.windows.settings.load_window_size('mpqselect', self)

	def listfiles(self): # type: () -> None
		self.files = []
		for file_entry in self.mpqhandler.list_files():
			if not file_entry.file_name in self.files:
				self.files.append(file_entry.file_name.decode('utf-8'))
		for path,_,filenames in os.walk(Assets.mpq_dir):
			for filename in filenames:
				mpq_filename = Assets.mpq_file_path_to_file_name(os.path.join(path, filename))
				if not mpq_filename in self.files:
					self.files.append(mpq_filename)
		self.files.sort()

	def updatelist(self): # type: () -> None
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
			self.searchtimer = None
		self.listbox.delete(0,END)
		s = self.search.get()
		if not self.regex.get():
			s = '^' + re.escape(s).replace('\\?','.').replace('\\*','.+?') + '$'
		try:
			r = re.compile(s)
		except:
			self.resettimer = self.after(1000, self.updatecolor)
			self.textdrop.entry['bg'] = '#FFB4B4'
		else:
			for f in [p for p in self.files if r.match(p)]:
				self.listbox.insert(END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.open['state'] = NORMAL
		else:
			self.open['state'] = DISABLED

	def updatecolor(self): # type: () -> None
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop.entry.c

	def updatesearch(self, *_): # type: (Event) -> None
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def ok(self, _=None): # type: (Event | None) -> None
		f = self.listbox.get(self.listbox.curselection()[0])
		self.file = 'MPQ:' + f
		history = self.settings.settings.get('mpqselecthistory', [])
		if f in history:
			history.remove(f)
		history.append(f)
		if len(history) > 10:
			del history[0]
		PyMSDialog.ok(self)

	def dismiss(self): # type: () -> None
		self.settings.windows.settings.save_window_size('mpqselect', self)
		PyMSDialog.dismiss(self)
