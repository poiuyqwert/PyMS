
from ..FileFormats.MPQ.SFmpq import SFileListFiles

from .utils import BASE_DIR
from .PyMSDialog import PyMSDialog
from .TextDropDown import TextDropDown
from .UIKit import *

import os

class MPQSelect(PyMSDialog):
	def __init__(self, parent, mpqhandler, filetype, search, settings, open_type='Open'):
		self.mpqhandler = mpqhandler
		self.search = StringVar()
		self.search.set(search)
		self.search.trace('w', self.updatesearch)
		self.settings = settings
		self.regex = IntVar()
		self.regex.set(0)
		self.files = []
		self.file = None
		self.resettimer = None
		self.searchtimer = None
		self.open_type = open_type
		PyMSDialog.__init__(self, parent, self.open_type + ' a ' + filetype)

	def widgetize(self):
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, width=35, height=10, bd=0, yscrollcommand=scrollbar.set, exportselection=0, activestyle=DOTBOX)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda a,i=0: self.move(a,i)),
			('<End>', lambda a,i=END: self.move(a,i)),
			('<Up>', lambda a,i=-1: self.move(a,i)),
			('<Left>', lambda a,i=-1: self.move(a,i)),
			('<Down>', lambda a,i=1: self.move(a,i)),
			('<Right>', lambda a,i=-1: self.move(a,i)),
			('<Prior>', lambda a,i=-10: self.move(a,i)),
			('<Next>', lambda a,i=10: self.move(a,i)),
		]
		for b in bind:
			listframe.bind(*b)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, padx=1, pady=1, expand=1)
		listframe.focus_set()
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

	def setup_complete(self):
		self.settings.windows.settings.load_window_size('mpqselect', self)

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, a):
		if a == END:
			a = self.listbox.size()-2
		elif a not in [0,END]:
			a = max(min(self.listbox.size()-1, int(self.listbox.curselection()[0]) + a),0)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(a)
		self.listbox.see(a)

	def listfiles(self):
		filelists = os.path.join(BASE_DIR,'PyMS','Data','Listfile.txt')
		self.files = []
		self.mpqhandler.open_mpqs()
		for h in self.mpqhandler.handles.values():
			for e in SFileListFiles(h, filelists):
				if e.fileName and not e.fileName in self.files:
					self.files.append(e.fileName)
		self.mpqhandler.close_mpqs()
		m = os.path.join(BASE_DIR,'PyMS','MPQ','')
		for p in os.walk(m):
			folder = p[0].replace(m,'')
			for f in p[2]:
				a = '%s\\%s' % (folder,f)
				if not a in self.files:
					self.files.append(a)
		self.files.sort()

	def updatelist(self):
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
			for f in filter(lambda p: r.match(p), self.files):
				self.listbox.insert(END,f)
		if self.listbox.size():
			self.listbox.select_set(0)
			self.open['state'] = NORMAL
		else:
			self.open['state'] = DISABLED

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.textdrop.entry['bg'] = self.textdrop.entry.c

	def updatesearch(self, *_):
		if self.searchtimer:
			self.after_cancel(self.searchtimer)
		self.searchtimer = self.after(200, self.updatelist)

	def ok(self):
		f = self.listbox.get(self.listbox.curselection()[0])
		self.file = 'MPQ:' + f
		history = self.settings.settings.get('mpqselecthistory', [])
		if f in history:
			history.remove(f)
		history.append(f)
		if len(history) > 10:
			del history[0]
		PyMSDialog.ok(self)

	def dismiss(self):
		self.settings.windows.settings.save_window_size('mpqselect', self)
		PyMSDialog.dismiss(self)
