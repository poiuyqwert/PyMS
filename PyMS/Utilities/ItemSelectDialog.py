
from PyMS.Utilities.UIKit import Event
from .UIKit import *
from .PyMSDialog import PyMSDialog
from . import Config

import re
from dataclasses import dataclass

from typing import Protocol, Sequence

@dataclass
class DisplayItem:
	name: str
	display_name: str

Item = str | DisplayItem

class Delegate(Protocol):
	def get_items(self) -> Sequence[Item]:
		...

	def item_selected(self, index: int) -> bool:
		return True

	def items_selected(self, indexes: list[int]) -> bool:
		return True

class ItemSelectDialog(PyMSDialog):
	def __init__(self, parent: AnyWindow, title: str, delegate: Delegate, selected: list[int] = [], multiselect: bool = False, window_geometry_config: Config.WindowGeometry | None = None, search_history_config: Config.List | None = None):
		self.delegate = delegate
		self.initial_selection: list[int] | None = selected
		self.multiselect = multiselect
		self.window_geometry_config = window_geometry_config
		self.search_history_config = search_history_config

		self.all_items: Sequence[Item] = []
		self.filtered_items: list[tuple[int, Item]] = []

		self.filter_var = StringVar()
		self.filter_var.trace_add('write', lambda *_: self.refresh_filter())
		self.filter_is_regex_var = BooleanVar(value=False)

		PyMSDialog.__init__(self, parent, title)

	def widgetize(self) -> Misc | None:
		self.listbox = ScrolledListbox(self, width=35, height=10, selectmode=EXTENDED if self.multiselect else SINGLE)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()
		self.listbox.bind(WidgetEvent.Listbox.Select(), self.update_states)

		s = Frame(self)
		self.filter_dropdown = TextDropDown(s, self.filter_var, self.search_history_config.data if self.search_history_config else [])
		self.filter_dropdown_bg = self.filter_dropdown.entry['bg']
		self.filter_dropdown.pack(side=LEFT, fill=X, padx=1, pady=2)
		Radiobutton(s, text='Wildcard', variable=self.filter_is_regex_var, value=0, command=self.refresh_filter).pack(side=LEFT, padx=1, pady=2)
		Radiobutton(s, text='Regex', variable=self.filter_is_regex_var, value=1, command=self.refresh_filter).pack(side=LEFT, padx=1, pady=2)
		s.pack(fill=X)

		s = Frame(self)
		self.select_button = Button(s, text='Select', width=10, command=self.ok)
		self.select_button.pack(side=LEFT, padx=(5,5), pady=3)
		Button(s, text='Cancel', width=10, command=self.cancel).pack(side=RIGHT, padx=(1,5), pady=3)
		s.pack(fill=X)

		return self.select_button

	def update_states(self, event: Event | None = None) -> None:
		self.select_button['state'] = DISABLED if not self.listbox.curselection() else ACTIVE

	def setup_complete(self) -> None:
		if self.window_geometry_config:
			self.window_geometry_config.load_size(self)
		self.refresh_items()

	def refresh_items(self) -> None:
		self.items = self.delegate.get_items()
		self.refresh_filter()

	def refresh_filter(self) -> None:
		scroll = False
		if self.initial_selection:
			scroll = True
			selected_indexes = self.initial_selection
			self.initial_selection = None
			if not self.multiselect and len(selected_indexes) > 1:
				selected_indexes = selected_indexes[:1]
		else:
			selected_indexes = [self.filtered_items[i][0] for i in self.listbox.curselection()]
		self.filtered_items.clear()

		regex: re.Pattern | None = None
		filter = self.filter_var.get()
		if filter:
			if self.filter_is_regex_var.get():
				if not filter.startswith('\\A'):
					filter = '.*' + filter
				if not filter.endswith('\\Z'):
					filter = filter + '.*'
			else:
				filter = '.*%s.*' % re.escape(filter)
			regex = re.compile(filter)

		for n,item in enumerate(self.items):
			if not regex or regex.match(item.name if isinstance(item, DisplayItem) else item):
				self.filtered_items.append((n, item))

		self.refresh_list(selected_indexes, scroll)

	def refresh_list(self, selected_indexes: list[int], scroll: bool) -> None:
		self.listbox.delete(0, END)
		scroll_to: int | None = None
		for index,item in self.filtered_items:
			self.listbox.insert(END, item.display_name if isinstance(item, DisplayItem) else item)
			if index in selected_indexes:
				self.listbox.select_set(END)
				if scroll:
					scroll_to = self.listbox.index(END)
		if scroll_to is not None:
			self.listbox.see(scroll_to)

	def ok(self, event: Event | None=None) -> None:
		indexes: list[int] = [self.filtered_items[i][0] for i in self.listbox.curselection()]
		if self.multiselect:
			close = self.delegate.items_selected(indexes)
		else:
			close = self.delegate.item_selected(indexes[0])
		if close:
			PyMSDialog.ok(self)

	def dismiss(self): # type: () -> None
		if self.window_geometry_config:
			self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
