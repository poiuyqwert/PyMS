
from .AutohideScrollbar import AutohideScrollbar
from ..Widgets import *
from ..ShowScrollbar import ShowScrollbar
from ..EventPattern import *

from typing import Literal

class ScrolledTreeview(Frame):
	# `auto_bind` can be `True` to bind to the internal `Listbox`, or can be any `Widget` to bind to
	def __init__(self, parent: Misc, frame_config={'bd': 2, 'relief': SUNKEN}, horizontal: ShowScrollbar = ShowScrollbar.when_needed, vertical: ShowScrollbar = ShowScrollbar.when_needed, auto_bind: Misc | bool = True, scroll_speed: int = 1, **kwargs):
		Frame.__init__(self, parent, **frame_config)

		self.treeview = Treeview(self, show='tree', **kwargs)
		self.treeview.grid(column=0,row=0, sticky=NSEW)

		if horizontal != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
			else:
				scrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
			scrollbar.grid(column=0,row=1, sticky=EW)
			self.treeview.config(xscrollcommand=scrollbar.set)
		
		if vertical != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, command=self.treeview.yview)
			else:
				scrollbar = AutohideScrollbar(self, command=self.treeview.yview)
			scrollbar.grid(column=1,row=0, sticky=NS)
			self.treeview.config(yscrollcommand=scrollbar.set)

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		# if auto_bind:
		# 	bind_to: Misc = self.treeview
		# 	if isinstance(auto_bind, Misc):
		# 		bind_to = auto_bind
		# 	def scroll(event: Event) -> str:
		# 		horizontal = False
		# 		if hasattr(event, 'state') and getattr(event, 'state', 0) & Modifier.Shift.state:
		# 			horizontal = True
		# 		view = self.treeview.yview
		# 		if horizontal:
		# 			view = self.treeview.xview
		# 		cur = view()
		# 		if event.delta > 0 and cur[0] > 0:
		# 			view('scroll', -1 * scroll_speed, 'units')
		# 		elif event.delta <= 0 and cur[1] < 1:
		# 			view('scroll', scroll_speed, 'units')
		# 		return EventPropogation.Break
		# 	def move(event: Event, offset: int | Literal['end']) -> str:
		# 		if self.treeview['selectmode'] == MULTIPLE:
		# 			return EventPropogation.Continue
		# 		if isinstance(event.state, int) and event.state & (Modifier.Shift.state | Modifier.Mac.Ctrl.state | Modifier.Alt.state | Modifier.Ctrl.state):
		# 			return EventPropogation.Continue
		# 		index = 0
		# 		if offset == END:
		# 			index = self.size()-2 # type: ignore[operator]
		# 		elif offset not in [0,END] and self.treeview.selection():
		# 			index = max(min(self.size()-1, int(self.treeview.selection()[0]) + offset),0) # type: ignore[operator]
		# 		self.treeview.selection_clear(0,END)
		# 		self.treeview.selection_set(index)
		# 		self.treeview.see(index)
		# 		self.treeview.event_generate(WidgetEvent.Listbox.Select())
		# 		self.treeview.focus_set()
		# 		return EventPropogation.Break
		# 	bind = [
		# 		(Mouse.Scroll(), scroll),
		# 		(Key.Home(), lambda event: move(event, 0)),
		# 		(Key.End(), lambda event: move(event, END)),
		# 		(Key.Up(), lambda event: move(event, -1)),
		# 		(Key.Left(), lambda event: move(event, -1)),
		# 		(Key.Down(), lambda event: move(event, 1)),
		# 		(Key.Right(), lambda event: move(event, 1)),
		# 		(Key.Prior(), lambda event: move(event, -10)),
		# 		(Key.Next(), lambda event: move(event, 10)),
		# 	]
		# 	for b in bind:
		# 		bind_to.bind(*b, add=True)
