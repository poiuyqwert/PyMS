
from ..Widgets import Entry, Frame, Label, Misc
from ..Constants import LEFT
from ..Variables import IntVar, IntegerVar
from .DropDown import DropDown

from typing import Callable, Sequence

class EntryDropDown(Frame):
	# `variable` should be an `IntegerVar`, and it's `callback` will be taken over by the `EntryDropDown`
	#     Use the `callback` of the EntryDropDown to get updates
	# `entries` is an array of the entries to show in the dropdown
	#     They can be a tuple `(str_name, int_value)`, or just `str_name` in which case it will use the index for its `int_value`
	#     One entry can have an `int_value` of `None` to indicate it will be selected for any unknown value
	# `callback` is called with the value whenever it changes (typed, chosen in the dropdown, or set)
	def __init__(self, parent: Misc, variable: IntegerVar, entries: Sequence[str] | Sequence[tuple[str, int | None]], *, entry_width: int | None = None, dropdown_width: int | None = None, separator: str = '=', callback: Callable[[int], None] | None = None):
		Frame.__init__(self, parent)

		self.variable = variable
		self.callback = callback

		self.value_to_index_map: dict[int | None, int] = {}
		self.index_to_value_map: dict[int, int] = {}
		self.dropdown_variable = IntVar()

		self.variable.callback = self._entry_updated

		self.entry = Entry(self, textvariable=self.variable, width=entry_width) # type: ignore[arg-type]
		self.entry.pack(side=LEFT)
		Label(self, text=separator).pack(side=LEFT)
		self.dropdown = DropDown(self, self.dropdown_variable, [], self._dropdown_chosen, width=dropdown_width) # type: ignore[arg-type]
		self.dropdown.pack(side=LEFT)

		self.set_entries(entries)

	def _entry_updated(self, value: int) -> None:
		index = None
		if value in self.value_to_index_map:
			index = self.value_to_index_map[value]
		elif None in self.value_to_index_map:
			index = self.value_to_index_map[None]
		if index is None:
			self.variable.set(self.index_to_value_map[self.dropdown_variable.get()])
			return
		self.dropdown_variable.set(index)
		if self.callback:
			self.callback(value)

	def _dropdown_chosen(self, index: int) -> None:
		if self.index_to_value_map[index] is None:
			# The catch-all entry isn't a value, so keep showing the entry that matches the current value
			value = self.variable.get()
			if value in self.value_to_index_map and self.value_to_index_map[value] != index:
				# This runs inside the dropdown variable's trace, which Tcl won't re-fire, so update the dropdown's text directly
				self.dropdown_variable.set(self.value_to_index_map[value])
				self.dropdown.change(self.value_to_index_map[value])
			return
		self.variable.set(self.index_to_value_map[index])

	# See __init__ for detail of `entries`
	def set_entries(self, entries: Sequence[str] | Sequence[tuple[str, int | None]]) -> None:
		self.value_to_index_map.clear()
		self.index_to_value_map.clear()
		names: list[str] = []
		for index,entry in enumerate(entries):
			if isinstance(entry, tuple):
				name,value = entry
			else:
				name = entry
				value = index
			self.value_to_index_map[value] = index
			self.index_to_value_map[index] = value
			names.append(name)
		self.dropdown.setentries(names)
		if self.variable.get() in self.value_to_index_map:
			self.dropdown_variable.set(self.value_to_index_map[self.variable.get()])
		elif None in self.value_to_index_map:
			self.dropdown_variable.set(self.value_to_index_map[None])
		else:
			self.variable.set(self.index_to_value_map[0])
