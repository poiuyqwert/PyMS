
from .File import File

import re, os

class AIScript(File):
	RE_NAME = re.compile(r'^aiscript.bin$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if AIScript.RE_NAME.match(folder_name):
			return 1
		return 0

	def display_name(self) -> str:
		return "aiscript.bin/bwscript.bin"

	def output_files(self) -> list[str]:
		return ['aiscript.bin', 'bwscript.bin']

	def script_paths(self) -> list[str]:
		script_paths: list[str] = []
		for filename in os.listdir(self.path):
			if filename.endswith('.txt') and not filename.endswith('def.txt'):
				script_paths.append(os.path.join(self.path, filename))
		return sorted(script_paths)

	# TODO: This should be Souce.AIScript's responsibility?
	def extdef_paths(self) -> list[str]:
		extdef_paths: list[str] = []
		for filename in os.listdir(self.path):
			if filename.endswith('def.txt'):
				extdef_paths.append(os.path.join(self.path, filename))
		return sorted(extdef_paths)
