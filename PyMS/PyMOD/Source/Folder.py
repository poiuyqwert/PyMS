
from .Item import Item

class Folder(Item):
	# Folder is the default type when no other source type matches
	@classmethod
	def matches(cls, folder_name: str) -> float:
		return 0

	def __init__(self, path: str) -> None:
		Item.__init__(self, path)
		self.children: list[Item] = []

	def add_child(self, item: Item) -> None:
		self.children.append(item)

	def __repr__(self) -> str:
		result = f' - {self.display_name()}'
		for item in self.children:
			result += '\n  ' + repr(item).replace('\n', '\n  ')
		return result
