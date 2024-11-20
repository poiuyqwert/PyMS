
from .File import File

import re as _re

class AIScript(File):
	RE_NAME = _re.compile(r'^aiscript.bin$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if AIScript.RE_NAME.match(folder_name):
			return 1
		return 0

	def display_name(self) -> str:
		return "aiscript.bin/bwscript.bin"
