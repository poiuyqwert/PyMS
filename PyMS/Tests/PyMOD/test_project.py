
from ...PyMOD.Project import Project
from ...PyMOD import Source
from ...Utilities.PyMSError import PyMSError

import os
import unittest
from unittest import mock

from typing import Iterator

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class Test_load_and_new(unittest.TestCase):
	def test_load_rejects_a_folder_without_a_marker(self) -> None:
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.path.isfile', return_value=False):
			with self.assertRaises(PyMSError) as cm:
				project.load()
		self.assertIn('is not a PyMOD project', str(cm.exception))

	def test_load_rejects_an_unreadable_marker(self) -> None:
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.path.isfile', return_value=True), \
				mock.patch('builtins.open', mock.mock_open(read_data='not json')):
			with self.assertRaises(PyMSError) as cm:
				project.load()
		self.assertIn("Couldn't load project marker", str(cm.exception))

	def test_load_accepts_a_marked_project(self) -> None:
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.path.isfile', return_value=True), \
				mock.patch('builtins.open', mock.mock_open(read_data='{"version": 1}')):
			project.load()

	def test_new_creates_the_folder_and_marker(self) -> None:
		project = Project(ROOT_PATH)
		opened = mock.mock_open()
		with mock.patch('PyMS.PyMOD.Project._os.path.isdir', return_value=False), \
				mock.patch('PyMS.PyMOD.Project._os.mkdir') as mkdir, \
				mock.patch('builtins.open', opened):
			project.new()
		mkdir.assert_called_once_with(ROOT_PATH)
		opened.assert_called_once_with(project.marker_path, 'w', encoding='utf-8')

	def test_new_keeps_an_existing_folder(self) -> None:
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.path.isdir', return_value=True), \
				mock.patch('PyMS.PyMOD.Project._os.mkdir') as mkdir, \
				mock.patch('builtins.open', mock.mock_open()):
			project.new()
		mkdir.assert_not_called()

	def test_new_wraps_failures(self) -> None:
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.path.isdir', return_value=False), \
				mock.patch('PyMS.PyMOD.Project._os.mkdir', side_effect=OSError('denied')):
			with self.assertRaises(PyMSError) as cm:
				project.new()
		self.assertIn("Couldn't create project", str(cm.exception))

class Test_path_mapping(unittest.TestCase):
	def setUp(self) -> None:
		self.project = Project(ROOT_PATH)

	def test_source_path_maps_into_intermediates(self) -> None:
		self.assertEqual(
			self.project.source_path_to_intermediates_path(project_path('sub', 'file.txt')),
			project_path('.build', 'intermediates', 'sub', 'file.txt')
		)

	def test_source_path_maps_into_artifacts(self) -> None:
		self.assertEqual(
			self.project.source_path_to_artifacts_path(project_path('mod.mpq')),
			project_path('.build', 'artifacts', 'mod.mpq')
		)

	def test_base_name_replaces_the_file_name(self) -> None:
		self.assertEqual(
			self.project.source_path_to_intermediates_path(project_path('sub', 'unit.grp'), 'unit.grp'),
			project_path('.build', 'intermediates', 'sub', 'unit.grp')
		)

	def test_project_root_maps_to_the_intermediates_root(self) -> None:
		self.assertEqual(
			self.project.source_path_to_intermediates_path(ROOT_PATH),
			self.project.intermediates_path
		)

	def test_repeated_path_segments_only_map_the_root_prefix(self) -> None:
		nested_repeat = project_path('sub') + ROOT_PATH
		self.assertEqual(
			self.project.source_path_to_intermediates_path(nested_repeat),
			project_path('.build', 'intermediates', 'sub') + ROOT_PATH
		)

	def test_paths_outside_the_project_are_rejected(self) -> None:
		with self.assertRaises(ValueError) as cm:
			self.project.source_path_to_intermediates_path(os.path.join(os.sep, 'elsewhere', 'file.txt'))
		self.assertIn('is not inside the project', str(cm.exception))


# `{'dirs': {name: subtree}, 'files': [names]}` trees walked with `os.walk`'s topdown semantics:
# mutating the yielded directory list prunes recursion
FolderTree = dict

def folder(dirs: dict[str, FolderTree] | None = None, files: list[str] | None = None) -> FolderTree:
	return {'dirs': dirs or {}, 'files': files or []}

class Test_update_source_graph(unittest.TestCase):
	def make_graph(self, tree: FolderTree) -> tuple[Source.Item | None, list[str]]:
		visited: list[str] = []
		def fake_walk(path: str, topdown: bool = True) -> Iterator[tuple[str, list[str], list[str]]]:
			assert topdown, 'The source walk must be top-down so directory pruning works'
			def node_for(node_path: str) -> FolderTree:
				node = tree
				relative_path = os.path.relpath(node_path, ROOT_PATH)
				if relative_path != os.curdir:
					for part in relative_path.split(os.sep):
						node = node['dirs'][part]
				return node
			def walk(walk_path: str) -> Iterator[tuple[str, list[str], list[str]]]:
				visited.append(walk_path)
				node = node_for(walk_path)
				dir_names = list(node['dirs'].keys())
				file_names = list(node['files'])
				yield walk_path, dir_names, file_names
				for dir_name in dir_names:
					yield from walk(os.path.join(walk_path, dir_name))
			return walk(path)
		project = Project(ROOT_PATH)
		with mock.patch('PyMS.PyMOD.Project._os.walk', side_effect=fake_walk):
			root = project.update_source_graph()
		return root, visited

	def child_names(self, item: Source.Item | None) -> list[str]:
		assert isinstance(item, Source.Folder)
		return list(child.name for child in item.children)

	def child(self, item: Source.Item | None, name: str) -> Source.Item:
		assert isinstance(item, Source.Folder)
		for child in item.children:
			if child.name == name:
				return child
		raise AssertionError(f'No child named `{name}` in `{item.name}`')

	def test_sources_are_detected_by_folder_name(self) -> None:
		root, _ = self.make_graph(folder(dirs={
			'mod.mpq': folder(dirs={
				'unit.grp': folder(files=['frame000.bmp']),
				'stat_txt.tbl': folder(files=['stat_txt.txt']),
				'aiscript.bin': folder(files=['scripts.txt']),
				'rez': folder(files=['readme.txt']),
			}),
		}))
		assert root is not None
		mpq = self.child(root, 'mod.mpq')
		self.assertIsInstance(mpq, Source.MPQ)
		self.assertIsInstance(self.child(mpq, 'unit.grp'), Source.GRP)
		self.assertIsInstance(self.child(mpq, 'stat_txt.tbl'), Source.TBL)
		self.assertIsInstance(self.child(mpq, 'aiscript.bin'), Source.AIScript)
		rez = self.child(mpq, 'rez')
		self.assertIsInstance(rez, Source.Folder)
		self.assertNotIsInstance(rez, Source.MPQ)

	def test_config_files_are_excluded_but_similar_names_are_not(self) -> None:
		root, _ = self.make_graph(folder(files=['config.json', 'unit.grp.config.json', 'unitconfig.json', 'myconfig.json', 'sound.wav']))
		self.assertEqual(sorted(self.child_names(root)), ['myconfig.json', 'sound.wav', 'unitconfig.json'])

	def test_dot_files_and_folders_are_excluded(self) -> None:
		root, visited = self.make_graph(folder(dirs={'.build': folder(files=['meta.json'])}, files=['.pymod_project.json', 'sound.wav']))
		self.assertEqual(self.child_names(root), ['sound.wav'])
		self.assertNotIn(project_path('.build'), visited)

	def test_file_type_source_folders_are_not_descended_into(self) -> None:
		root, visited = self.make_graph(folder(dirs={
			'unit.grp': folder(dirs={'nested': folder(files=['file.txt'])}, files=['frame000.bmp']),
		}))
		assert root is not None
		self.assertIsInstance(self.child(root, 'unit.grp'), Source.GRP)
		self.assertNotIn(project_path('unit.grp', 'nested'), visited)
