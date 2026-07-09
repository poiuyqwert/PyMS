
from .Item import Item

class File(Item):
	# Files are fallbacks assigned by their containing folder's type, never detected by name
	@classmethod
	def matches(cls, folder_name: str) -> float:
		return 0

	def __repr__(self) -> str:
		return f' - {self.display_name()}'
