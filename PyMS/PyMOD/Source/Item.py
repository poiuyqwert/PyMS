
from __future__ import annotations

import os as _os

from typing import Type

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

	@staticmethod
	def build_source_graph(project_path: str) -> Item | None:
		from .Folder import Folder
		from .File import File
		from .MPQ import MPQ
		from .GRP import GRP
		from .AIScript import AIScript
		SOURCE_TYPES: list[Type[Item]] = [
			MPQ,
			GRP,
			AIScript,
		]
		root: Item | None = None
		parent_folders: dict[str, Folder] = {}
		for folder_path, folder_names, file_names in _os.walk(project_path, topdown=True):
			folder_names[:] = list(folder_name for folder_name in folder_names if not folder_name.startswith('.'))
			folder_name = _os.path.basename(folder_path)
			detected_source_type: Type[Item]  = Folder
			detected_source_confidence: float = 0
			for source_type in SOURCE_TYPES:
				confidence = source_type.matches(folder_name)
				if confidence > detected_source_confidence:
					detected_source_type = source_type
					detected_source_confidence = confidence
			item = detected_source_type(folder_path)
			parent_path = _os.path.dirname(folder_path)
			if parent_path in parent_folders:
				parent_folders[parent_path].add_child(item)
			if not root:
				root = item
			if isinstance(item, Folder):
				parent_folders[folder_path] = item
				for file_name in file_names:
					if file_name.startswith('.'):
						continue
					file_path = _os.path.join(folder_path, file_name)
					item.add_child(File(file_path))
		return root
