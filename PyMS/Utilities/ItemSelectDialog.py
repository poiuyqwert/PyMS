
from PyMS.Utilities.UIKit import Event
from . import UIKit as UI
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
	def __init__(self, *, parent: UI.AnyWindow, title: str, delegate: Delegate, selected: list[int] | None = None, multiselect: bool = False, window_geometry_config: Config.WindowGeometry | None = None, search_history_config: Config.List | None = None):
		self.delegate = delegate
		self.initial_selection: list[int] | None = selected
		self.multiselect = multiselect
		self.window_geometry_config = window_geometry_config
		self.search_history_config = search_history_config

		self.all_items: Sequence[Item] = []
		self.filtered_items: list[tuple[int, Item]] = []

		self.filter_var = UI.StringVar()
		self.filter_var.trace_add('write', lambda *_: self.refresh_filter())
		self.filter_is_regex_var = UI.BooleanVar(value=False)

		PyMSDialog.__init__(self, parent, title)

	def widgetize(self) -> UI.Misc | None:
		self.listbox = UI.ScrolledListbox(self, width=35, height=10, selectmode=UI.EXTENDED if self.multiselect else UI.SINGLE)
		self.listbox.pack(fill=UI.BOTH, padx=1, pady=1, expand=1)
		self.listbox.focus_set()
		self.listbox.bind(UI.WidgetEvent.Listbox.Select(), self.update_states)

		s = UI.Frame(self)
		self.filter_dropdown = UI.TextDropDown(s, self.filter_var, self.search_history_config.data if self.search_history_config else [])
		self.filter_dropdown_bg = self.filter_dropdown.entry['bg']
		self.filter_dropdown.pack(side=UI.LEFT, fill=UI.X, padx=1, pady=2)
		UI.Radiobutton(s, text='Wildcard', variable=self.filter_is_regex_var, value=0, command=self.refresh_filter).pack(side=UI.LEFT, padx=1, pady=2)
		UI.Radiobutton(s, text='Regex', variable=self.filter_is_regex_var, value=1, command=self.refresh_filter).pack(side=UI.LEFT, padx=1, pady=2)
		s.pack(fill=UI.X)

		s = UI.Frame(self)
		self.select_button = UI.Button(s, text='Select', width=10, command=self.ok)
		self.select_button.pack(side=UI.LEFT, padx=(5,5), pady=3)
		UI.Button(s, text='Cancel', width=10, command=self.cancel).pack(side=UI.RIGHT, padx=(1,5), pady=3)
		s.pack(fill=UI.X)

		return self.select_button

	def update_states(self, _event: Event | None = None) -> None:
		self.select_button['state'] = UI.DISABLED if not self.listbox.curselection() else UI.ACTIVE

	def setup_complete(self) -> None:
		if self.window_geometry_config:
			self.window_geometry_config.load_size(self)
		self.refresh_items()

	def refresh_items(self) -> None:
		self.all_items = self.delegate.get_items()
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
		filter_pattern = self.filter_var.get()
		if filter_pattern:
			if self.filter_is_regex_var.get():
				if not filter_pattern.startswith('\\A'):
					filter_pattern = '.*' + filter_pattern
				if not filter_pattern.endswith('\\Z'):
					filter_pattern = filter_pattern + '.*'
			else:
				filter_pattern = f'.*{re.escape(filter_pattern)}.*'
			regex = re.compile(filter_pattern)

		for n,item in enumerate(self.all_items):
			if not regex or regex.match(item.name if isinstance(item, DisplayItem) else item):
				self.filtered_items.append((n, item))

		self.refresh_list(selected_indexes, scroll)

	def refresh_list(self, selected_indexes: list[int], scroll: bool) -> None:
		self.listbox.delete(0, UI.END)
		scroll_to: int | None = None
		for index,item in self.filtered_items:
			self.listbox.insert(UI.END, item.display_name if isinstance(item, DisplayItem) else item)
			if index in selected_indexes:
				self.listbox.select_set(UI.END)
				if scroll:
					scroll_to = self.listbox.index(UI.END)
		if scroll_to is not None:
			self.listbox.see(scroll_to)

	def ok(self, _event: Event | None=None) -> None:
		indexes: list[int] = [self.filtered_items[i][0] for i in self.listbox.curselection()]
		if self.multiselect:
			close = self.delegate.items_selected(indexes)
		else:
			close = self.delegate.item_selected(indexes[0])
		if close:
			PyMSDialog.ok(self)

	def dismiss(self) -> None:
		if self.window_geometry_config:
			self.window_geometry_config.save_size(self)
		PyMSDialog.dismiss(self)
