
from .AutohideScrollbar import AutohideScrollbar
from ..Widgets import Frame, Misc, Scrollbar, Treeview
from ..Constants import EW, HORIZONTAL, NS, NSEW, SUNKEN
from ..ShowScrollbar import ShowScrollbar

from typing import Any

class ScrolledTreeview(Frame):
	def __init__(self, parent: Misc, frame_config: dict[str, Any] | None = None, horizontal: ShowScrollbar = ShowScrollbar.when_needed, vertical: ShowScrollbar = ShowScrollbar.when_needed, **kwargs: Any) -> None:
		frame_config = frame_config if frame_config is not None else {'bd': 2, 'relief': SUNKEN}
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
