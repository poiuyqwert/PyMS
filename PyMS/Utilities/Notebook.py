
from utils import BASE_DIR

from Tkinter import *

import os

class Notebook(Frame):
	TRANS_FIX = None

	def __init__(self, parent, relief=RAISED, switchcallback=None):
		self.parent = parent
		self.active = None
		self.tab = IntVar()
		self.notebook = Frame(parent)
		self.tabs = Frame(self.notebook)
		self.tabs.pack(fill=X)
		self.pages = {}
		Frame.__init__(self, self.notebook, borderwidth=2, relief=relief)
		Frame.pack(self, fill=BOTH, expand=1)

	def pack(self, **kw):
		self.notebook.pack(kw)

	def grid(self, **kw):
		self.notebook.grid(kw)

	def add_tab(self, frame, title, tab_id=None):
		tab_id = tab_id or title
		if not Notebook.TRANS_FIX:
			Notebook.TRANS_FIX = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images', 'trans_fix.gif'))
		b = Radiobutton(self.tabs, image=Notebook.TRANS_FIX, text=title, indicatoron=0, compound=RIGHT, variable=self.tab, value=len(self.pages), command=lambda: self.display(title))
		b.pack(side=LEFT)
		self.pages[tab_id] = (frame, len(self.pages))
		if not self.active:
			self.display(title)
		return b

	def display(self, tab_id):
		if self.pages[tab_id][0] == self.active:
			return self.active
		if self.active:
			if hasattr(self.active, 'deactivate'):
				self.active.deactivate()
			self.event_generate('<<TabDeactivated>>')
			self.active.forget()
		self.tab.set(self.pages[tab_id][1])
		self.active = self.pages[tab_id][0]
		self.active.pack(fill=BOTH, expand=1, padx=6, pady=6)
		if hasattr(self.active, 'activate'):
			self.active.activate()
		self.event_generate('<<TabActivated>>')
		return self.active

class NotebookTab(Frame):
	def __init__(self, parent):
		self.parent = parent
		Frame.__init__(self, parent)

	def activate(self):
		pass

	def deactivate(self):
		pass