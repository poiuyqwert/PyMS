
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.DetermineSourceFiles import DetermineSourceFiles
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CompileSPK import CompileSPK
from ...PyMOD import Source
from ...FileFormats.SPK import SPK
from ...Utilities.PyMSError import PyMSError

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class Test_config(unittest.TestCase):
	def test_defaults_to_max_layers(self) -> None:
		config = CompileSPK.Config.from_json({})
		self.assertEqual(config.layer_count, SPK.MAX_LAYERS)

	def test_layer_count_is_read(self) -> None:
		config = CompileSPK.Config.from_json({'layer_count': 3})
		self.assertEqual(config.layer_count, 3)

class Test_compile_step(unittest.TestCase):
	def make_step(self, file_name: str = 'star.spk') -> CompileSPK:
		project = Project(ROOT_PATH)
		source_file = Source.SPK(project_path(file_name))
		return CompileSPK(CompileThread(project), source_file)

	def logs(self, step: CompileSPK) -> list:
		messages = []
		while not step.compile_thread.output_queue.empty():
			messages.append(step.compile_thread.output_queue.get())
		return messages

	def test_unchanged_source_skips_the_step(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=False):
			self.assertIsNone(step.execute())
		messages = self.logs(step)
		self.assertIn('No changes required', messages[-1].text)

	def test_bmp_source_is_interpreted_and_saved_to_intermediates(self) -> None:
		step = self.make_step()
		expected_source_path = project_path('star.spk', 'star.bmp')
		expected_destination_path = step.compile_thread.project.source_path_to_intermediates_path(step.source_file.path, step.source_file.name)
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(step.compile_thread.meta, 'update_metas') as update_metas, \
				mock.patch.object(SPK, 'interpret_file') as interpret_file, \
				mock.patch.object(SPK, 'save') as save:
			self.assertIsNone(step.execute())
		interpret_file.assert_called_once_with(expected_source_path, SPK.MAX_LAYERS)
		save.assert_called_once_with(expected_destination_path)
		update_metas.assert_called_once_with([expected_source_path], [expected_destination_path])

	def test_config_layer_count_is_passed_to_interpret(self) -> None:
		step = self.make_step()
		expected_source_path = project_path('star.spk', 'star.bmp')
		with mock.patch.object(step, 'load_config', return_value=CompileSPK.Config(layer_count=3)), \
				mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(step.compile_thread.meta, 'update_metas'), \
				mock.patch.object(SPK, 'interpret_file') as interpret_file, \
				mock.patch.object(SPK, 'save'):
			self.assertIsNone(step.execute())
		interpret_file.assert_called_once_with(expected_source_path, 3)

	def test_invalid_layer_count_is_a_compile_error(self) -> None:
		for layer_count in (0, SPK.MAX_LAYERS + 1):
			step = self.make_step()
			with mock.patch.object(step, 'load_config', return_value=CompileSPK.Config(layer_count=layer_count)), \
					mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
					mock.patch.object(SPK, 'save') as save:
				with self.assertRaises(CompileError) as cm:
					step.execute()
			self.assertIn('`layer_count` must be between', str(cm.exception))
			save.assert_not_called()

	def test_interpret_failure_is_a_compile_error(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(SPK, 'interpret_file', side_effect=PyMSError('Interpreting', 'Image is not the correct height to fit 5 layers')), \
				mock.patch.object(SPK, 'save') as save:
			with self.assertRaises(CompileError) as cm:
				step.execute()
		self.assertIn("Couldn't compile SPK", str(cm.exception))
		save.assert_not_called()

	def test_save_failure_is_a_compile_error(self) -> None:
		step = self.make_step()
		with mock.patch.object(step.compile_thread.meta, 'check_requires_update', return_value=True), \
				mock.patch.object(step.compile_thread.meta, 'update_metas') as update_metas, \
				mock.patch.object(SPK, 'interpret_file'), \
				mock.patch.object(SPK, 'save', side_effect=OSError('disk full')):
			with self.assertRaises(CompileError) as cm:
				step.execute()
		self.assertIn("Couldn't save SPK", str(cm.exception))
		update_metas.assert_not_called()

	def test_spk_source_schedules_a_compile_spk_step(self) -> None:
		project = Project(ROOT_PATH)
		project.source_graph = root = Source.Folder(ROOT_PATH)
		source_file = Source.SPK(project_path('star.spk'))
		root.add_child(source_file)
		steps = DetermineSourceFiles(CompileThread(project)).execute() or []
		spk_steps = [step for step in steps if isinstance(step, CompileSPK)]
		self.assertEqual(len(spk_steps), 1)
		self.assertIs(spk_steps[0].source_file, source_file)
