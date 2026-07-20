
from .File import File

import re as _re

class PCX(File):
	RE_PCX_NAME = _re.compile(r'.+?\.pcx$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if PCX.RE_PCX_NAME.match(folder_name):
			return 1
		return 0
