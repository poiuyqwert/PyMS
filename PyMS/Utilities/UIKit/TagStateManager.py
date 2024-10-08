
from __future__ import annotations

import tkinter as _Tk

from typing import Any, Sequence, Protocol

class CanSetItem(Protocol):
	def __setitem__(self, key: str, value: Any):
		...

class TagStateManager(object):
	class Item(object):
		def __init__(self, item: CanSetItem, tags: Sequence[str]) -> None:
			self._item = item
			self.tags = tags

		def update(self, enabled: bool) -> None:
			self._item['state'] = _Tk.NORMAL if enabled else _Tk.DISABLED

	def __init__(self) -> None:
		self._tag_states: dict[str, bool] = {}
		self._tagged_items: dict[str, list[TagStateManager.Item]] = {}

	def _update_item(self, item: TagStateManager.Item) -> None:
		enabled = True
		for tag in item.tags:
			enabled = enabled and self._tag_states.get(tag, False)
		item.update(enabled)

	def add_item(self, item: CanSetItem, tags: str | Sequence[str]) -> None:
		if isinstance(tags, str):
			tags = (tags,)
		tag_item = TagStateManager.Item(item, tags)
		for tag in tags:
			items = self._tagged_items.get(tag, [])
			items.append(tag_item)
			if not tag in self._tagged_items:
				self._tagged_items[tag] = items
		self._update_item(tag_item)

	def tag_enabled(self, tag: str, enabled: bool):
		self._tag_states[tag] = enabled
		items = self._tagged_items.get(tag)
		if not items:
			return
		for item in items:
			self._update_item(item)
