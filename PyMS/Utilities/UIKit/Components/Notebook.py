
from ..Widgets import *
from ..Font import Font
from ..EventPattern import *
from ..Types import Relief

from ... import Assets

from typing import Callable

class Notebook(Frame):
	def __init__(self, parent: Misc, relief: Relief = RAISED, switchcallback=None) -> None:
		self.parent = parent
		self.active: Widget | None = None
		self.tab = IntVar()
		self.overflowing = False
		self.overflow_button: Button | None = None
		self.notebook = Frame(parent)
		self.tabs_area = Frame(self.notebook)
		self.tabs_area.pack(fill=X)
		self.tabs_container = Frame(self.tabs_area)
		self.tabs_container.grid(row=0, column=0, sticky=W)
		self.tabs_area.grid_columnconfigure(0, weight=1)
		self.tabs: list[Radiobutton] = []
		self.pages: dict[str, tuple[Widget, int]] = {}
		Frame.__init__(self, self.notebook, borderwidth=2, relief=relief)
		Frame.pack(self, fill=BOTH, expand=1)

		def show_hidden_tabs(*_) -> None:
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
				def command_callback(name: str) -> Callable[[], None]:
					def command() -> None:
						self.display(name)
					return command
				for index,tab_name in hidden_tabs:
					menu.add_command(label=tab_name, command=command_callback(tab_name), font=Font.default().bolded() if index == self.tab.get() else None) # type: ignore[arg-type]
				menu.post(*self.winfo_pointerxy())

		def resize(*_) -> None:
			overflowing = (self.tabs_container.winfo_reqwidth() > self.tabs_container.winfo_width())
			if overflowing and not self.overflowing:
				if not self.overflow_button:
					self.overflow_button = Button(self.tabs_area, image=Assets.get_image('arrow'), width=20, command=show_hidden_tabs)
				self.overflow_button.grid(row=0, column=1, sticky=NSEW)
			elif not overflowing and self.overflowing and self.overflow_button:
				self.overflow_button.grid_forget()
			self.overflowing = overflowing
		self.tabs_area.bind(WidgetEvent.Configure(), resize)
		self.tabs_container.bind(WidgetEvent.Configure(), resize)

	def pack(self, **kw) -> None: # type: ignore[override]
		self.notebook.pack(kw)

	def grid(self, **kw) -> None: # type: ignore[override]
		self.notebook.grid(kw)

	def add_tab(self, frame: Widget, title: str, tab_id: str | None = None) -> Radiobutton:
		tab_id = tab_id or title
		tab = Radiobutton(self.tabs_container, image=Assets.get_image('trans_fix'), text=title, fg='#000', indicatoron=False, compound=RIGHT, variable=self.tab, value=len(self.pages), command=lambda: self.display(tab_id))
		tab.pack(side=LEFT)
		self.tabs.append(tab)
		self.pages[tab_id] = (frame, len(self.pages))
		if not self.active:
			self.display(tab_id)
		return tab

	def display(self, tab_id: str) -> Widget:
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
	def __init__(self, parent: Misc) -> None:
		self.parent = parent
		Frame.__init__(self, parent)

	def activate(self) -> None:
		pass

	def deactivate(self) -> None:
		pass
