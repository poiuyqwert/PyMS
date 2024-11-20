
from .File import File

import re as _re

class TBL(File):
	RE_TBL_NAME = _re.compile(r'.+?\.tbl$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if TBL.RE_TBL_NAME.match(folder_name):
			return 1
		return 0
