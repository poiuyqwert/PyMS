
from .AutohideScrollbar import AutohideScrollbar
from ..Widgets import Canvas, Frame, Misc, Scrollbar
from ..Constants import EW, HORIZONTAL, NS, NSEW, SUNKEN
from ..ShowScrollbar import ShowScrollbar
from ..EventPattern import WidgetEvent

from typing import Callable, Any

class ScrolledCanvas(Frame):
	def __init__(self, parent: Misc, *, frame_config: dict[str, Any] | None = None, horizontal: ShowScrollbar = ShowScrollbar.when_needed, vertical: ShowScrollbar = ShowScrollbar.when_needed, **kwargs: Any) -> None:
		frame_config = frame_config if frame_config is not None else {'bd': 2, 'relief': SUNKEN}
		Frame.__init__(self, parent, **frame_config)

		if not 'highlightthickness' in kwargs:
			kwargs['highlightthickness'] = 0
		self.canvas = Canvas(self, **kwargs)
		if not 'bd' in kwargs:
			self.canvas.config(bd=0)
		self.canvas.grid(column=0,row=0, sticky=NSEW)

		def scroll_callback(scrollbar: Scrollbar) -> Callable[[float, float], None]:
			def scroll_update(low: float, high: float) -> None:
				scrollbar.set(low, high)
				self.canvas.event_generate(WidgetEvent.Scrolled())
			return scroll_update

		if horizontal != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
			else:
				scrollbar = AutohideScrollbar(self, orient=HORIZONTAL, command=self.canvas.xview)
			scrollbar.grid(column=0,row=1, sticky=EW)
			self.canvas.config(xscrollcommand=scroll_callback(scrollbar))

		if vertical != ShowScrollbar.never:
			if horizontal == ShowScrollbar.always:
				scrollbar = Scrollbar(self, command=self.canvas.yview)
			else:
				scrollbar = AutohideScrollbar(self, command=self.canvas.yview)
			scrollbar.grid(column=1,row=0, sticky=NS)
			self.canvas.config(yscrollcommand=scroll_callback(scrollbar))

		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
