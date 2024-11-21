
from __future__ import annotations

import os

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
		if os.path.isfile(self.path):
			return f'{self.path}.config.json'
		return os.path.join(self.path, 'config.json')
