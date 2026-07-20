
from .File import File

import re as _re

class LO(File):
	RE_LO_NAME = _re.compile(r'.+?\.lo[abdfglosux]$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if LO.RE_LO_NAME.match(folder_name):
			return 1
		return 0
