
from ..Widgets import Button, Entry, Frame, Misc
from ..Constants import END, LEFT, NORMAL, SUNKEN, X, Y
from ..Variables import StringVar
from ..Event import Event
from .DropDownChooser import DropDownChooser
from ..InputHistory import InputHistory
from ..Types import WidgetState

from ... import Assets

from typing import Any

class TextDropDown(Frame):
	def __init__(self, parent: Misc, variable: StringVar, history: InputHistory | None = None, width: int | None = None, *, state: WidgetState = NORMAL):
		self.variable = variable
		self.set = self.variable.set
		self.history = history if history is not None else InputHistory()
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

	def choose(self, _event: Event | None = None) -> None:
		entries = self.history.entries
		if self.entry['state'] == NORMAL and entries:
			i = -1
			if self.variable.get() in entries:
				i = entries.index(self.variable.get())
			c = DropDownChooser(self, entries, i)
			if c.result > -1:
				self.variable.set(entries[c.result])
