
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.CopyArtifact import CopyArtifact
from ...PyMOD.CompileStep.DetermineSourceFiles import DetermineSourceFiles
from ...PyMOD.CompileStep.PackageMPQ import PackageMPQ
from ...PyMOD import Source

import os
import unittest

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

	def test_top_level_mpqs_are_packaged_to_artifacts(self) -> None:
		project = Project(ROOT_PATH)
		mpq = Source.MPQ(project_path('mod.mpq'))
		step = PackageMPQ(CompileThread(project), mpq)
		self.assertEqual(step.archive_path(), project_path('.build', 'artifacts', 'mod.mpq'))

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

	def test_top_level_source_is_copied_to_artifacts(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.GRP(project_path('test.grp')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.source_path for step in copy_steps], [project_path('.build', 'intermediates', 'test.grp')])
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'artifacts', 'test.grp')])

	def test_sources_inside_an_mpq_are_not_copied_to_artifacts(self) -> None:
		root = Source.Folder(ROOT_PATH)
		mpq = Source.MPQ(project_path('mod.mpq'))
		mpq.add_child(Source.GRP(project_path('mod.mpq', 'test.grp')))
		folder = Source.Folder(project_path('mod.mpq', 'unit'))
		folder.add_child(Source.File(project_path('mod.mpq', 'unit', 'loose.txt')))
		mpq.add_child(folder)
		root.add_child(mpq)

		self.assertEqual(self.make_copy_artifact_steps(root), [])

	def test_source_nested_in_a_plain_folder_mirrors_its_path_in_artifacts(self) -> None:
		root = Source.Folder(ROOT_PATH)
		folder = Source.Folder(project_path('stuff'))
		folder.add_child(Source.GRP(project_path('stuff', 'test.grp')))
		root.add_child(folder)

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'artifacts', 'stuff', 'test.grp')])

	def test_all_output_files_of_a_source_are_copied_to_artifacts(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.AIScript(project_path('aiscript.bin')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.destination_path for step in copy_steps], [
			project_path('.build', 'artifacts', 'aiscript.bin'),
			project_path('.build', 'artifacts', 'bwscript.bin'),
		])

	def test_loose_files_outside_an_mpq_are_copied_to_artifacts(self) -> None:
		root = Source.Folder(ROOT_PATH)
		root.add_child(Source.File(project_path('readme.txt')))

		copy_steps = self.make_copy_artifact_steps(root)
		self.assertEqual([step.source_path for step in copy_steps], [project_path('.build', 'intermediates', 'readme.txt')])
		self.assertEqual([step.destination_path for step in copy_steps], [project_path('.build', 'artifacts', 'readme.txt')])
