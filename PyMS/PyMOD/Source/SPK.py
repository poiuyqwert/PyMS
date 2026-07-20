
from .File import File

import re as _re

class SPK(File):
	RE_SPK_NAME = _re.compile(r'.+?\.spk$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if SPK.RE_SPK_NAME.match(folder_name):
			return 1
		return 0
