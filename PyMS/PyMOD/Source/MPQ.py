
from .Folder import Folder

class MPQ(Folder):
	@classmethod
	def matches(cls, folder_name: str) -> float:
		if folder_name.endswith('.mpq'):
			return 1
		return 0
