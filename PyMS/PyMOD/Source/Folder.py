
from .Item import Item

import os as _os

class Folder(Item):
	def __init__(self, path: str) -> None:
		self.path = path
		self.name = _os.path.basename(self.path)
		self.children: list[Item] = []

	def add_child(self, item: Item) -> None:
		self.children.append(item)

	def __repr__(self) -> str:
		result = ' - %s' % self.display_name()
		for item in self.children:
			result += '\n  ' + repr(item).replace('\n', '\n  ')
		return result
