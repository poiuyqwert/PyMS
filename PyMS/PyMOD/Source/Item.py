
from __future__ import annotations

import os

# The config for a source lives beside it: a file source has a sibling `<name>.config.json`, a
# folder source has a `config.json` inside it. Extraction writes these and the compile steps read
# them back, so the convention lives here rather than in either of them
def config_path_for(path: str) -> str:
	if os.path.isfile(path):
		return f'{path}.config.json'
	return os.path.join(path, 'config.json')

class Item:
	@classmethod
	def matches(cls, folder_name: str) -> float:
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path: str) -> None:
		self.path = path
		self.name = os.path.basename(self.path)

	def display_name(self) -> str:
		return self.name

	def output_files(self) -> list[str]:
		return [self.name]

	def config_path(self) -> str:
		return config_path_for(self.path)
