
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.DetermineSourceFiles import DetermineSourceFiles
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CompileLO import CompileLO
from ...PyMOD import Source
from ...FileFormats.LO import LO
from ...Utilities.PyMSError import PyMSError

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class Test_compile_step(unittest.TestCase):
	def make_step(self, file_name: str = 'marine.loa') -> CompileLO:
		project = Project(ROOT_PATH)
		source_file = Source.LO(project_path(file_name))
		return CompileLO(CompileThread(project), source_file)

	def logs(self, step: CompileLO) -> list:
		messages = []
		while not step.compile_thread.output_queue.empty():
			messages.append(step.compile_thread.output_queue.get())
		return messages

	def test_unchanged_source_skips_the_step(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=False):
			self.assertIsNone(step.execute())
		messages = self.logs(step)
		self.assertEqual(len(messages), 1)
		self.assertIn('No changes required', messages[0].text)

	def test_text_source_is_interpreted_and_saved_to_intermediates(self) -> None:
		step = self.make_step()
		expected_source_path = project_path('marine.loa', 'marine.txt')
		expected_destination_path = step.compile_thread.project.source_path_to_intermediates_path(step.source_file.path, step.source_file.name)
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(step.compile_thread.meta, 'update_metas') as update_metas, \
				mock.patch.object(LO, 'interpret') as interpret, \
				mock.patch.object(LO, 'save') as save:
			self.assertIsNone(step.execute())
		interpret.assert_called_once_with(expected_source_path)
		save.assert_called_once_with(expected_destination_path)
		update_metas.assert_called_once_with([expected_source_path], [expected_destination_path])

	def test_parse_failure_is_a_compile_error(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(LO, 'interpret', side_effect=PyMSError('Interpreting', 'Unknown line format')), \
				mock.patch.object(LO, 'save') as save:
			with self.assertRaises(CompileError) as cm:
				step.execute()
		self.assertIn("Couldn't parse", str(cm.exception))
		save.assert_not_called()

	def test_save_failure_is_a_compile_error(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(step.compile_thread.meta, 'update_metas') as update_metas, \
				mock.patch.object(LO, 'interpret'), \
				mock.patch.object(LO, 'save', side_effect=OSError('disk full')):
			with self.assertRaises(CompileError) as cm:
				step.execute()
		self.assertIn("Couldn't save LO*", str(cm.exception))
		update_metas.assert_not_called()

	def test_lo_source_schedules_a_compile_lo_step(self) -> None:
		project = Project(ROOT_PATH)
		project.source_graph = root = Source.Folder(ROOT_PATH)
		source_file = Source.LO(project_path('marine.loa'))
		root.add_child(source_file)
		steps = DetermineSourceFiles(CompileThread(project)).execute() or []
		lo_steps = [step for step in steps if isinstance(step, CompileLO)]
		self.assertEqual(len(lo_steps), 1)
		self.assertIs(lo_steps[0].source_file, source_file)
