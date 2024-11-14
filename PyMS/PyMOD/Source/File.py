
from .Item import Item

class File(Item):
	def __repr__(self) -> str:
		return ' - %s' % self.display_name()
