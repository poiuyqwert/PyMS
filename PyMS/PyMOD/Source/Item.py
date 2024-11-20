
from __future__ import annotations

import os as _os

class Item:
	@classmethod
	def matches(cls, folder_name: str) -> float:
		raise NotImplementedError(cls.__name__ + '.matches()')

	def __init__(self, path: str) -> None:
		self.path = path
		self.name = _os.path.basename(self.path)

	def display_name(self) -> str:
		return self.name

	def compiled_name(self) -> str:
		return self.name
