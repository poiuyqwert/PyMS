
from . import Source

import os as _os

from typing import Type

class Project:
	def __init__(self, path: str) -> None:
		self.path = path
		self.build_path = _os.path.join(path, '.build')
		self.intermediates_path = _os.path.join(self.build_path, 'intermediates')
		self.artifacts_path = _os.path.join(self.build_path, 'artifacts')
		self.meta_path = _os.path.join(self.build_path, 'meta.json')
		self.source_graph: Source.Item | None = None

	def intermediate_path(self, *path: str) -> str:
		return _os.path.join(self.intermediates_path, *path)

	def intermediates_relative_mpq_path(self, relative_to_source_path: str, *mpq_path: str) -> str | None:
		intermediates_path = self.source_path_to_intermediates_path(relative_to_source_path)
		while intermediates_path.startswith(self.intermediates_path) and not _os.path.basename(intermediates_path).endswith('.mpq'):
			intermediates_path = _os.path.dirname(intermediates_path)
		if not _os.path.basename(intermediates_path).endswith('.mpq'):
			return None
		return _os.path.join(intermediates_path, *mpq_path)

	def source_path_to_intermediates_path(self, source_path: str, base_name: str | None = None) -> str:
		intermediates_path = source_path.replace(self.path, self.intermediates_path)
		if base_name:
			intermediates_path = _os.path.join(_os.path.dirname(intermediates_path), base_name)
		return intermediates_path

	def source_path_to_artifacts_path(self, source_path: str, base_name: str | None = None) -> str:
		artifacts_path = source_path.replace(self.path, self.artifacts_path)
		if base_name:
			artifacts_path = _os.path.join(_os.path.split(artifacts_path)[0], base_name)
		return artifacts_path

	def update_source_graph(self) -> Source.Item | None:
		root: Source.Item | None = None
		parent_folders: dict[str, Source.Folder] = {}
		for folder_path, folder_names, file_names in _os.walk(self.path, topdown=True):
			folder_names[:] = list(folder_name for folder_name in folder_names if not folder_name.startswith('.'))
			folder_name = _os.path.basename(folder_path)
			detected_source_type: Type[Source.Item] = Source.Folder
			detected_source_confidence: float = 0
			for source_type in Source.ITEM_TYPES:
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
			if isinstance(item, Source.Folder):
				parent_folders[folder_path] = item
				for file_name in file_names:
					if file_name.startswith('.'):
						continue
					file_path = _os.path.join(folder_path, file_name)
					item.add_child(Source.File(file_path))
		self.source_graph = root
		return root
