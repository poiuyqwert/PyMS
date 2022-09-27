
from .AutohideScrollbar import AutohideScrollbar
from .UIKit import *
from .ShowScrollbar import ShowScrollbar

class ScrolledListbox(Frame):
	# `auto_bind` can be `True` to bind to the internal `Listbox`, or can be any `Widget` to bind to
	def __init__(self, parent, frame_config={'bd': 2, 'relief': SUNKEN}, horizontal=ShowScrollbar.when_needed, vertical=ShowScrollbar.when_needed, auto_bind=True, scroll_speed=1, **kwargs):
		Frame.__init__(self, parent, **frame_config)

		if not 'exportselection' in kwargs:
			kwargs['exportselection'] = 0
		if not 'highlightthickness' in kwargs:
			kwargs['highlightthickness'] = 0
		if not 'bd' in kwargs:
			kwargs['bd'] = 0
		if not 'activestyle' in kwargs:
			kwargs['activestyle'] = DOTBOX

		self.listbox = Listbox(self, **kwargs)
		self.listbox.grid(column=0,row=0, sticky=NSEW)

		if horizontal != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.listbox.xview)
			else:
				scrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.listbox.xview)
			scrollbar.grid(column=0,row=1, sticky=EW)
			self.listbox.config(xscrollcommand=scrollbar.set)
		
		if vertical != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, command=self.listbox.yview)
			else:
				scrollbar = AutohideScrollbar(self, command=self.listbox.yview)
			scrollbar.grid(column=1,row=0, sticky=NS)
			self.listbox.config(yscrollcommand=scrollbar.set)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# Proxy listbox binding on self, but preserve binding to self in separate function
		self.frame_bind = self.bind
		self.bind = self.listbox.bind
		# Proxy listbox functions on self
		self.scan_mark = self.listbox.scan_mark
		self.selection_includes = self.listbox.selection_includes
		self.activate = self.listbox.activate
		self.itemconfigure = self.listbox.itemconfigure
		self.nearest = self.listbox.nearest
		self.scan_dragto = self.listbox.scan_dragto
		self.select_anchor = self.listbox.select_anchor
		self.see = self.listbox.see
		self.selection_clear = self.listbox.selection_clear
		self.size = self.listbox.size
		self.index = self.listbox.index
		self.selection_set = self.listbox.selection_set
		self.itemcget = self.listbox.itemcget
		self.select_set = self.listbox.select_set
		self.itemconfig = self.listbox.itemconfig
		self.get = self.listbox.get
		self.selection_anchor = self.listbox.selection_anchor
		self.bbox = self.listbox.bbox
		self.insert = self.listbox.insert
		self.select_clear = self.listbox.select_clear
		self.select_includes = self.listbox.select_includes
		self.curselection = self.listbox.curselection
		self.delete = self.listbox.delete
		self.xview_moveto = self.listbox.xview_moveto
		self.xview = self.listbox.xview
		self.xview_scroll = self.listbox.xview_scroll
		self.yview_moveto = self.listbox.yview_moveto
		self.yview_scroll = self.listbox.yview_scroll
		self.yview = self.listbox.yview

		if auto_bind:
			bind_to = self.listbox
			if isinstance(auto_bind, Widget):
				bind_to = auto_bind
			def scroll(event):
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0) & Modifier.Shift.state:
					horizontal = True
				view = self.yview
				if horizontal:
					view = self.xview
				cur = view()
				if event.delta > 0 and cur[0] > 0:
					view('scroll', -1 * scroll_speed, 'units')
				elif event.delta <= 0 and cur[1] < 1:
					view('scroll', scroll_speed, 'units')
				return EventPropogation.Break
			def move(event, offset):
				if self.listbox['selectmode'] == MULTIPLE:
					return EventPropogation.Continue
				if event.state & (Modifier.Shift.state | Modifier.Mac.Ctrl.state | Modifier.Alt.state | Modifier.Ctrl.state):
					return EventPropogation.Continue
				index = 0
				if offset == END:
					index = self.size()-2
				elif offset not in [0,END] and self.curselection():
					index = max(min(self.size()-1, int(self.curselection()[0]) + offset),0)
				self.select_clear(0,END)
				self.select_set(index)
				self.see(index)
				self.listbox.event_generate(WidgetEvent.Listbox.Select)
				self.listbox.focus_set()
				return EventPropogation.Break
			bind = [
				(Mouse.Scroll, scroll),
				(Key.Home, lambda event: move(event, 0)),
				(Key.End, lambda event: move(event, END)),
				(Key.Up, lambda event: move(event, -1)),
				(Key.Left, lambda event: move(event, -1)),
				(Key.Down, lambda event: move(event, 1)),
				(Key.Right, lambda event: move(event, 1)),
				(Key.Prior, lambda event: move(event, -10)),
				(Key.Next, lambda event: move(event, 10)),
			]
			for b in bind:
				bind_to.bind(*b, add=True)
