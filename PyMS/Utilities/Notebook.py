
from . import Assets
from .UIKit import *

class Notebook(Frame):
	def __init__(self, parent, relief=RAISED, switchcallback=None):
		self.parent = parent
		self.active = None
		self.tab = IntVar()
		self.overflowing = False
		self.overflow_button = None
		self.notebook = Frame(parent)
		self.tabs_area = Frame(self.notebook)
		self.tabs_area.pack(fill=X)
		self.tabs_container = Frame(self.tabs_area)
		self.tabs_container.grid(row=0, column=0, sticky=W)
		self.tabs_area.grid_columnconfigure(0, weight=1)
		self.tabs = []
		self.pages = {}
		Frame.__init__(self, self.notebook, borderwidth=2, relief=relief)
		Frame.pack(self, fill=BOTH, expand=1)

		def show_hidden_tabs(*_):
			visible_width = self.tabs_container.winfo_width()
			hidden_tabs = []
			for n,tab in enumerate(self.tabs):
				x = tab.winfo_x()
				w_req = tab.winfo_reqwidth()
				w = tab.winfo_width()
				if x > visible_width or w < w_req:
					hidden_tabs.append((n, tab.cget('text')))
			if hidden_tabs:
				menu = Menu(self)
				for index,tab_name in hidden_tabs:
					menu.add_command(label=tab_name, command=lambda name=tab_name: self.display(name), font=Font.default().bolded() if index == self.tab.get() else None)
				menu.post(*self.winfo_pointerxy())

		def resize(*_):
			overflowing = (self.tabs_container.winfo_reqwidth() > self.tabs_container.winfo_width())
			if overflowing and not self.overflowing:
				if not self.overflow_button:
					self.overflow_button = Button(self.tabs_area, image=Assets.get_image('arrow'), width=20, command=show_hidden_tabs)
				self.overflow_button.grid(row=0, column=1, sticky=NSEW)
			elif not overflowing and self.overflowing:
				self.overflow_button.grid_forget()
			self.overflowing = overflowing
		self.tabs_area.bind(WidgetEvent.Configure, resize)
		self.tabs_container.bind(WidgetEvent.Configure, resize)

	def pack(self, **kw):
		self.notebook.pack(kw)

	def grid(self, **kw):
		self.notebook.grid(kw)

	def add_tab(self, frame, title, tab_id=None):
		tab_id = tab_id or title
		tab = Radiobutton(self.tabs_container, image=Assets.get_image('trans_fix'), text=title, fg='#000', indicatoron=0, compound=RIGHT, variable=self.tab, value=len(self.pages), command=lambda: self.display(title))
		tab.pack(side=LEFT)
		self.tabs.append(tab)
		self.pages[tab_id] = (frame, len(self.pages))
		if not self.active:
			self.display(title)
		return tab

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
		self.update_idletasks()
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