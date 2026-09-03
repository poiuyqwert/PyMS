
from . import Source

from ..Utilities.PyMSError import PyMSError

import os as _os
import json as _json

from typing import Type

class Project:
	# Hidden so `update_source_graph` skips it (dot-files are never treated as sources)
	MARKER_FILE_NAME = '.pymod_project.json'

	def __init__(self, path: str) -> None:
		self.path = path
		self.marker_path = _os.path.join(path, Project.MARKER_FILE_NAME)
		self.build_path = _os.path.join(path, '.build')
		self.intermediates_path = _os.path.join(self.build_path, 'intermediates')
		self.artifacts_path = _os.path.join(self.build_path, 'artifacts')
		# Artifacts are staged here during a compile and only swapped into `artifacts_path` once the
		# whole build succeeds, so a failed build never destroys the previous artifacts
		self.staging_path = _os.path.join(self.build_path, 'staging')
		self.previous_artifacts_path = _os.path.join(self.build_path, 'artifacts.old')
		self.meta_path = _os.path.join(self.build_path, 'meta.json')
		self.source_graph: Source.Item | None = None

	def load(self) -> None:
		if not _os.path.isfile(self.marker_path):
			raise PyMSError('Load', f'`{self.path}` is not a PyMOD project (missing `{Project.MARKER_FILE_NAME}`)')
		try:
			with open(self.marker_path, 'r', encoding='utf-8') as marker_file:
				_json.load(marker_file)
		except Exception as e:
			raise PyMSError('Load', f"Couldn't load project marker `{self.marker_path}`", cause=e) from e

	def new(self) -> None:
		try:
			if not _os.path.isdir(self.path):
				_os.mkdir(self.path)
			with open(self.marker_path, 'w', encoding='utf-8') as marker_file:
				_json.dump({'version': 1}, marker_file, indent=4)
		except Exception as e:
			raise PyMSError('New', f"Couldn't create project `{self.path}`", cause=e) from e

	def intermediate_path(self, *path: str) -> str:
		return _os.path.join(self.intermediates_path, *path)

	def intermediates_relative_mpq_path(self, relative_to_source_path: str, *mpq_path: str) -> str | None:
		intermediates_path = self.source_path_to_intermediates_path(relative_to_source_path)
		while intermediates_path.startswith(self.intermediates_path) and not _os.path.basename(intermediates_path).endswith('.mpq'):
			intermediates_path = _os.path.dirname(intermediates_path)
		if not _os.path.basename(intermediates_path).endswith('.mpq'):
			return None
		return _os.path.join(intermediates_path, *mpq_path)

	def _map_path(self, source_path: str, destination_root: str, base_name: str | None) -> str:
		relative_path = _os.path.relpath(source_path, self.path)
		if relative_path == _os.pardir or relative_path.startswith(_os.pardir + _os.sep):
			raise ValueError(f'Path `{source_path}` is not inside the project `{self.path}`')
		mapped_path = _os.path.normpath(_os.path.join(destination_root, relative_path))
		if base_name:
			mapped_path = _os.path.join(_os.path.dirname(mapped_path), base_name)
		return mapped_path

	def source_path_to_intermediates_path(self, source_path: str, base_name: str | None = None) -> str:
		return self._map_path(source_path, self.intermediates_path, base_name)

	def source_path_to_staging_path(self, source_path: str, base_name: str | None = None) -> str:
		return self._map_path(source_path, self.staging_path, base_name)

	def mpq_folders(self) -> list[Source.MPQ]:
		source_graph = self.source_graph
		if source_graph is None:
			source_graph = self.update_source_graph()
		mpq_folders: list[Source.MPQ] = []
		def collect(item: Source.Item) -> None:
			if isinstance(item, Source.MPQ):
				mpq_folders.append(item)
			if isinstance(item, Source.Folder):
				for child in item.children:
					collect(child)
		if source_graph:
			collect(source_graph)
		return mpq_folders

	def update_source_graph(self) -> Source.Item | None:
		root: Source.Item | None = None
		parent_folders: dict[str, Source.Folder] = {}
		for folder_path, folder_names, file_names in _os.walk(self.path, topdown=True):
			# Sorted so step order, packaged file order, and the files tree don't depend on the
			# filesystem's enumeration order
			folder_names[:] = sorted(folder_name for folder_name in folder_names if not folder_name.startswith('.'))
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
				for file_name in sorted(file_names):
					if file_name.startswith('.') or file_name == 'config.json' or file_name.endswith('.config.json'):
						continue
					file_path = _os.path.join(folder_path, file_name)
					item.add_child(Source.File(file_path))
			else:
				# File-type sources (`*.grp`, `*.tbl`, `aiscript.bin`) own their whole folder; don't descend into them
				folder_names[:] = []
		self.source_graph = root
		return root
