
from ..Widgets import *
from .DropDown import DropDown
from ..Variables import IntegerVar

from typing import Sequence

class EntryDropDown(Frame):
	# `variable` should be an `IntegerVar`, and it's `callback` will be taken over by the `EntryDropDown`
	#     Use the `callback` of the EntryDropDown to get updates
	# `entries` is an array of the entries to show in the dropdown
	#     They can be a tuple `(str_name, int_value)`, or just `str_name` in which case it will use the index for its `int_value`
	#     One entry can have an `int_value` of `None` to indicate it will be selected for any unknown value
	def __init__(self, parent: Misc, variable: IntegerVar, entries: Sequence[str] | Sequence[tuple[str, int | None]], entry_width: int | None = None, dropdown_width: int | None = None, separator: str = '='):
		Frame.__init__(self, parent)

		self.variable = variable

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
		else:
			self.dropdown_variable.set(index)

	def _dropdown_chosen(self, index: int) -> None:
		if self.index_to_value_map[index] is None:
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
