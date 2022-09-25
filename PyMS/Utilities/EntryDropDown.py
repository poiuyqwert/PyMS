
from .UIKit import *
from .DropDown import DropDown

class EntryDropDown(Frame):
	# `variable` should be an `IntegerVar`, and it's `callback` will be taken over by the `EntryDropDown`
	#     Use the `callback` of the EntryDropDown to get updates
	# `entries` is an array of the entries to show in the dropdown
	#     They can be a tuple `(str_name, int_value)`, or just `str_name` in which case it will use the index for its `int_value`
	#     One entry can have an `int_value` of `None` to indicate it will be selected for any unknown value
	def __init__(self, parent, variable, entries, callback=None, entry_width=None, dropdown_width=None, separator='='):
		Frame.__init__(self, parent)

		self.variable = variable
		self.callback = callback

		self.value_to_index_map = {}
		self.index_to_value_map = {}
		self.dropdown_variable = IntVar()

		self.variable.callback = self._entry_updated

		self.entry = Entry(self, textvariable=self.variable, width=entry_width)
		self.entry.pack(side=LEFT)
		Label(self, text=separator).pack(side=LEFT)
		self.dropdown = DropDown(self, self.dropdown_variable, [], self._dropdown_chosen, width=dropdown_width)
		self.dropdown.pack(side=LEFT)

		self.set_entries(entries)

	def _entry_updated(self, value):
		index = None
		if value in self.value_to_index_map:
			index = self.value_to_index_map[value]
		elif None in self.value_to_index_map:
			index = self.value_to_index_map[None]
		if index == None:
			self.variable.set(self.index_to_value_map[self.dropdown_variable.get()])
		else:
			self.dropdown_variable.set(index)

	def _dropdown_chosen(self, index):
		if self.index_to_value_map[index] == None:
			return
		self.variable.set(self.index_to_value_map[index])

	# See __init__ for detail of `entries`
	def set_entries(self, entries):
		self.value_to_index_map.clear()
		self.index_to_value_map.clear()
		names = []
		for index,entry in enumerate(entries):
			name = entry
			value = index
			if isinstance(entry, tuple):
				name,value = entry
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
