
from ..Widgets import *
from .DropDownChooser import DropDownChooser
from ..Types import WidgetState

from ... import Assets

from typing import Any

class TextDropDown(Frame):
	def __init__(self, parent: Misc, variable: StringVar, history: list[str] = [], width: int | None = None, state: WidgetState = NORMAL):
		self.variable = variable
		self.set = self.variable.set
		self.history = history
		Frame.__init__(self, parent, borderwidth=2, relief=SUNKEN)
		self.entry = Entry(self, textvariable=self.variable, width=width, highlightthickness=0) # type: ignore[arg-type]
		self.entry.config(bd=0)
		self.entry.pack(side=LEFT, fill=X, expand=1)
		self.entry['state'] = state
		self.button = Button(self, image=Assets.get_image('arrow'), command=self.choose, state=state)
		self.button.pack(side=LEFT, fill=Y)

	def focus_set(self, highlight: bool = False) -> None:
		self.entry.focus_set()
		if highlight:
			self.entry.selection_range(0,END)

	def __setitem__(self, item: str, value: Any) -> None:
		if item == 'state':
			self.entry['state'] = value
			self.button['state'] = value
		else:
			self.entry[item] = value

	def __getitem__(self, item: str) -> Any:
		return self.entry[item]

	def choose(self, e: Event | None = None) -> None:
		if self.entry['state'] == NORMAL and self.history:
			i = -1
			if self.variable.get() in self.history:
				i = self.history.index(self.variable.get())
			c = DropDownChooser(self, self.history, i)
			if c.result > -1:
				self.variable.set(self.history[c.result])
