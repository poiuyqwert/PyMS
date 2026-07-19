
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CopyArtifact import CopyArtifact
from ...PyMOD.CompileStep.DetermineSourceFiles import DetermineSourceFiles
from ...PyMOD.CompileStep.PackageMPQ import PackageMPQ
from ...PyMOD.CompileStep.SwapArtifacts import SwapArtifacts
from ...PyMOD import Source

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class Test_package_scheduling(unittest.TestCase):
	def make_steps(self, root: Source.Item) -> list:
		project = Project(ROOT_PATH)
		project.source_graph = root
		compile_thread = CompileThread(project)
		return DetermineSourceFiles(compile_thread).execute() or []

	def test_nested_mpqs_are_packaged_before_the_mpq_embedding_them(self) -> None:
		root = Source.Folder(ROOT_PATH)
		outer = Source.MPQ(project_path('outer.mpq'))
		inner = Source.MPQ(project_path('outer.mpq', 'inner.mpq'))
		innermost = Source.MPQ(project_path('outer.mpq', 'inner.mpq', 'innermost.mpq'))
		innermost.add_child(Source.File(project_path('outer.mpq', 'inner.mpq', 'innermost.mpq', 'file.txt')))
		inner.add_child(innermost)
		outer.add_child(inner)
		root.add_child(outer)

		package_steps = [step for step in self.make_steps(root) if isinstance(step, PackageMPQ)]
		self.assertEqual([step.source_folder for step in package_steps], [innermost, inner, outer])
		self.assertEqual([step.embedded for step in package_steps], [True, True, False])

	def test_top_level_mpqs_are_packaged_to_staging(self) -> None:
		project = Project(ROOT_PATH)
		mpq = Source.MPQ(project_path('mod.mpq'))
		step = PackageMPQ(CompileThread(project), mpq)
		self.assertEqual(step.archive_path(), project_path('.build', 'staging', 'mod.mpq'))

	def test_embedded_mpqs_are_packaged_to_a_hidden_intermediate(self) -> None:
		project = Project(ROOT_PATH)
		inner = Source.MPQ(project_path('outer.mpq', 'inner.mpq'))
		step = PackageMPQ(CompileThread(project), inner, embedded=True)
		self.assertEqual(step.archive_path(), project_path('.build', 'intermediates', 'outer.mpq', '.inner.mpq'))

class Test_artifact_copies(unittest.TestCase):
	def make_copy_artifact_steps(self, root: Source.Item) -> list[CopyArtifact]:
		project = Project(ROOT_PATH)
		project.source_graph = root
		compile_thread = CompileThread(project)
		steps = DetermineSourceFiles(compile_thread).execute() or []
		return [step for step in steps if isinstance(step, CopyArtifact)]

	def test_top_level_source_is_copied_to_staging(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.GRP(project_path('test.grp')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.source_path for step in copy_steps], [project_path('.build', 'intermediates', 'test.grp')])
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'staging', 'test.grp')])

	def test_sources_inside_an_mpq_are_not_copied_to_staging(self) -> None:
		root = Source.Folder(ROOT_PATH)
		mpq = Source.MPQ(project_path('mod.mpq'))
		mpq.add_child(Source.GRP(project_path('mod.mpq', 'test.grp')))
		folder = Source.Folder(project_path('mod.mpq', 'unit'))
		folder.add_child(Source.File(project_path('mod.mpq', 'unit', 'loose.txt')))
		mpq.add_child(folder)
		root.add_child(mpq)

		self.assertEqual(self.make_copy_artifact_steps(root), [])

	def test_source_nested_in_a_plain_folder_mirrors_its_path_in_staging(self) -> None:
		root = Source.Folder(ROOT_PATH)
		folder = Source.Folder(project_path('stuff'))
		folder.add_child(Source.GRP(project_path('stuff', 'test.grp')))
		root.add_child(folder)

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'staging', 'stuff', 'test.grp')])

	def test_all_output_files_of_a_source_are_copied_to_staging(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.AIScript(project_path('aiscript.bin')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.destination_path for step in copy_steps], [
			project_path('.build', 'staging', 'aiscript.bin'),
			project_path('.build', 'staging', 'bwscript.bin'),
		])

	def test_loose_files_outside_an_mpq_are_copied_to_staging(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.File(project_path('readme.txt')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.source_path for step in copy_steps], [project_path('.build', 'intermediates', 'readme.txt')])
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'staging', 'readme.txt')])

class Test_swap_artifacts(unittest.TestCase):
	def setUp(self) -> None:
		self.project = Project(ROOT_PATH)
		self.step = SwapArtifacts(CompileThread(self.project))
		self.existing = {self.project.staging_path}
		self.renames: list[tuple[str, str]] = []
		self.removed: list[str] = []
		def isdir(path: str) -> bool:
			return path in self.existing
		def rename(source_path: str, destination_path: str) -> None:
			self.renames.append((source_path, destination_path))
			self.existing.discard(source_path)
			self.existing.add(destination_path)
		def rmtree(path: str) -> None:
			self.removed.append(path)
			self.existing.discard(path)
		for target, side_effect in (
			('PyMS.PyMOD.CompileStep.SwapArtifacts._os.path.isdir', isdir),
			('PyMS.PyMOD.CompileStep.SwapArtifacts._os.rename', rename),
			('PyMS.PyMOD.CompileStep.SwapArtifacts._shutil.rmtree', rmtree),
		):
			patcher = mock.patch(target, side_effect=side_effect)
			patcher.start()
			self.addCleanup(patcher.stop)

	def test_staged_artifacts_replace_the_previous_artifacts(self) -> None:
		self.existing.add(self.project.artifacts_path)
		self.step.execute()
		self.assertEqual(self.renames, [
			(self.project.artifacts_path, self.project.previous_artifacts_path),
			(self.project.staging_path, self.project.artifacts_path),
		])
		self.assertEqual(self.removed, [self.project.previous_artifacts_path])
		self.assertEqual(self.existing, {self.project.artifacts_path})

	def test_first_build_publishes_without_previous_artifacts(self) -> None:
		self.step.execute()
		self.assertEqual(self.renames, [(self.project.staging_path, self.project.artifacts_path)])
		self.assertEqual(self.removed, [])
		self.assertEqual(self.existing, {self.project.artifacts_path})

	def test_failed_publish_restores_the_previous_artifacts(self) -> None:
		self.existing.add(self.project.artifacts_path)
		def failing_rename(source_path: str, destination_path: str) -> None:
			if source_path == self.project.staging_path:
				raise OSError('denied')
			self.renames.append((source_path, destination_path))
			self.existing.discard(source_path)
			self.existing.add(destination_path)
		with mock.patch('PyMS.PyMOD.CompileStep.SwapArtifacts._os.rename', side_effect=failing_rename):
			with self.assertRaises(CompileError) as cm:
				self.step.execute()
		self.assertIn("Couldn't publish the staged artifacts", str(cm.exception))
		self.assertEqual(self.renames, [
			(self.project.artifacts_path, self.project.previous_artifacts_path),
			(self.project.previous_artifacts_path, self.project.artifacts_path),
		])
		self.assertIn(self.project.artifacts_path, self.existing)

	def test_missing_staging_is_an_error(self) -> None:
		self.existing.discard(self.project.staging_path)
		with self.assertRaises(CompileError) as cm:
			self.step.execute()
		self.assertIn('staged artifacts are missing', str(cm.exception))
		self.assertEqual(self.renames, [])
