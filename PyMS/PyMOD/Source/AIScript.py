
from .File import File

import re, os

class AIScript(File):
	RE_NAME = re.compile(r'^aiscript\.bin$')

	@classmethod
	def matches(cls, folder_name: str) -> float:
		if AIScript.RE_NAME.match(folder_name):
			return 1
		return 0

	def display_name(self) -> str:
		return "aiscript.bin/bwscript.bin"

	def output_files(self) -> list[str]:
		return ['aiscript.bin', 'bwscript.bin']

	# A file in the folder named the same as the folder (e.g. `aiscript.bin/aiscript.bin`), and a
	# `bwscript.bin` beside it, are user-supplied base files for the scripts to be compiled on top of
	def base_aiscript_path(self) -> str | None:
		base_aiscript_path = os.path.join(self.path, 'aiscript.bin')
		if os.path.isfile(base_aiscript_path):
			return base_aiscript_path
		return None

	def base_bwscript_path(self) -> str | None:
		base_bwscript_path = os.path.join(self.path, 'bwscript.bin')
		if os.path.isfile(base_bwscript_path):
			return base_bwscript_path
		return None

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
