
try:
	import Tkinter as _Tk
except:
	import tkinter as _Tk

class TagStateManager(object):
	class Item(object):
		def __init__(self, item, tags): # type: (Any, list[str]) -> TagStateManager.Item
			self._item = item
			self.tags = tags

		def update(self, enabled): # type: (bool) -> None
			self._item['state'] = _Tk.NORMAL if enabled else _Tk.DISABLED

	def __init__(self):
		self._tag_states = {} # type: dict[str, bool]
		self._tagged_items = {} # type: dict[str, list[TagStateManager.Item]]

	def _update_item(self, item): # type: (TagStateManager.Item) -> None
		enabled = True
		for tag in item.tags:
			enabled = enabled and self._tag_states.get(tag, False)
		item.update(enabled)

	def add_item(self, item, tags): # type: (Any, Union[str, Iterable[str]]) -> None
		if isinstance(tags, str):
			tags = (tags,)
		item = TagStateManager.Item(item, tags)
		for tag in tags:
			items = self._tagged_items.get(tag, [])
			items.append(item)
			if not tag in self._tagged_items:
				self._tagged_items[tag] = items
		self._update_item(item)

	def tag_enabled(self, tag, enabled):
		self._tag_states[tag] = enabled
		items = self._tagged_items.get(tag)
		if not items:
			return
		for item in items:
			self._update_item(item)
