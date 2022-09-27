
from .AutohideScrollbar import AutohideScrollbar
from .UIKit import *
from .ShowScrollbar import ShowScrollbar

class ScrolledCanvas(Frame):
	# `auto_bind` can be `True` to bind to the internal `Listbox`, or can be any `Widget` to bind to
	def __init__(self, parent, frame_config={'bd': 2, 'relief': SUNKEN}, horizontal=ShowScrollbar.when_needed, vertical=ShowScrollbar.when_needed, auto_bind=True, scroll_speed=1, **kwargs):
		Frame.__init__(self, parent, **frame_config)

		if not 'highlightthickness' in kwargs:
			kwargs['highlightthickness'] = 0
		self.canvas = Canvas(self, **kwargs)
		self.canvas.grid(column=0,row=0, sticky=NSEW)

		def scroll_update(low, high, scrollbar):
			scrollbar.set(low, high)
			self.canvas.event_generate(WidgetEvent.Scrolled)

		if horizontal != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
			else:
				scrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
			scrollbar.grid(column=0,row=1, sticky=EW)
			self.canvas.config(xscrollcommand=lambda low,high,_scrollbar=scrollbar: scroll_update(low, high, _scrollbar))
		
		if vertical != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, command=self.canvas.yview)
			else:
				scrollbar = AutohideScrollbar(self, command=self.canvas.yview)
			scrollbar.grid(column=1,row=0, sticky=NS)
			self.canvas.config(yscrollcommand=lambda low,high,_scrollbar=scrollbar: scroll_update(low, high, _scrollbar))

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)

		if auto_bind:
			bind_to = self.canvas
			if isinstance(auto_bind, Widget):
				bind_to = auto_bind
			def scroll(event):
				horizontal = False
				if hasattr(event, 'state') and getattr(event, 'state', 0) & Modifier.Shift.state:
					horizontal = True
				view = self.canvas.yview
				if horizontal:
					view = self.canvas.xview
				cur = view()
				if event.delta > 0 and cur[0] > 0:
					view('scroll', -1 * scroll_speed, 'units')
				elif event.delta <= 0 and cur[1] < 1:
					view('scroll', scroll_speed, 'units')
				return EventPropogation.Break
			# def move(event, offset):
			# 	index = 0
			# 	if offset == END:
			# 		index = self.size()-2
			# 	elif offset not in [0,END] and self.curselection():
			# 		index = max(min(self.size()-1, int(self.curselection()[0]) + offset),0)
			# 	self.select_clear(0,END)
			# 	self.select_set(index)
			# 	self.see(index)
			# 	self.listbox.event_generate(WidgetEvent.Listbox.Select)
			# 	return EventPropogation.Break
			bind = [
				(Mouse.Scroll, scroll),
				# (Key.Home, lambda event: move(event, 0)),
				# (Key.End, lambda event: move(event, END)),
				# (Key.Up, lambda event: move(event, -1)),
				# (Key.Left, lambda event: move(event, -1)),
				# (Key.Down, lambda event: move(event, 1)),
				# (Key.Right, lambda event: move(event, 1)),
				# (Key.Prior, lambda event: move(event, -10)),
				# (Key.Next, lambda event: move(event, 10)),
			]
			for b in bind:
				bind_to.bind(*b, add=True)
