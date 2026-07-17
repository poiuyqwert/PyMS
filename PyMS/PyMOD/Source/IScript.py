
from .File import File

import re, os

class IScript(File):
	RE_NAME = re.compile(r'^iscript\.bin$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if IScript.RE_NAME.match(folder_name):
			return 1
		return 0

	# A file in the folder named the same as the folder (e.g. `iscript.bin/iscript.bin`) is a
	# user-supplied base file for the scripts to be compiled on top of
	def base_iscript_path(self) -> str | None:
		base_iscript_path = os.path.join(self.path, 'iscript.bin')
		if os.path.isfile(base_iscript_path):
			return base_iscript_path
		return None

	def script_paths(self) -> list[str]:
		script_paths: list[str] = []
		for filename in os.listdir(self.path):
			if filename.endswith('.txt'):
				script_paths.append(os.path.join(self.path, filename))
		return sorted(script_paths)
