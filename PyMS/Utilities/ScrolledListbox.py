
from AutohideScrollbar import AutohideScrollbar

from Tkinter import *


SHOW_SCROLL_NEVER = 0
SHOW_SCROLL_ALWAYS = 1
SHOW_SCROLL_NEEDED = 2

class ScrolledListbox(Frame):
	def __init__(self, parent, frame_config={}, horizontal=SHOW_SCROLL_NEEDED, vertical=SHOW_SCROLL_NEEDED, auto_bind=True, **kwargs):
		Frame.__init__(self, parent, **frame_config)

		self.listbox = Listbox(self, **kwargs)
		self.listbox.grid(column=0,row=0, sticky=NSEW)

		if horizontal != SHOW_SCROLL_NEVER:
			if horizontal == SHOW_SCROLL_ALWAYS:
				scrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.listbox.xview)
			else:
				scrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.listbox.xview)
			scrollbar.grid(column=0,row=1, sticky=EW)
			self.listbox.config(xscrollcommand=scrollbar.set)
		
		if vertical != SHOW_SCROLL_NEVER:
			if horizontal == SHOW_SCROLL_ALWAYS:
				scrollbar = Scrollbar(self, command=self.listbox.yview)
			else:
				scrollbar = AutohideScrollbar(self, command=self.listbox.yview)
			scrollbar.grid(column=1,row=0, sticky=NS)
			self.listbox.config(yscrollcommand=scrollbar.set)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# Forward listbox methods and certain other methods to the listbox
		self.frame_bind = self.bind
		self.bind = self.listbox.bind
		methods = vars(Listbox).keys() + vars(XView).keys() + vars(YView).keys()
		for m in methods:
			if m.startswith('_'):
				continue
			setattr(self, m, getattr(self.listbox, m))

		if auto_bind:
			bind_to = self.listbox
			if isinstance(auto_bind, Widget):
				bind_to = auto_bind
			def scroll(event):
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0):
					horizontal = True
				view = self.yview
				if horizontal:
					view = self.xview
				cur = view()
				if event.delta > 0 and cur[0] > 0:
					view('scroll', -1, 'units')
				elif event.delta <= 0 and cur[1] < 1:
					view('scroll', 1, 'units')
				return "break"
			def move(offset):
				index = 0
				if offset == END:
					index = self.size()-2
				elif offset not in [0,END] and self.curselection():
					index = max(min(self.size()-1, int(self.curselection()[0]) + offset),0)
				self.select_clear(0,END)
				self.select_set(index)
				self.see(index)
				self.listbox.event_generate('<<ListboxSelect>>')
				return "break"
			bind = [
				('<MouseWheel>', scroll),
				('<Home>', lambda e,i=0: move(i)),
				('<End>', lambda e,i=END: move(i)),
				('<Up>', lambda e,i=-1: move(i)),
				('<Left>', lambda e,i=-1: move(i)),
				('<Down>', lambda e,i=1: move(i)),
				('<Right>', lambda e,i=-1: move(i)),
				('<Prior>', lambda e,i=-10: move(i)),
				('<Next>', lambda e,i=10: move(i)),
			]
			for b in bind:
				bind_to.bind(*b, add=True)
