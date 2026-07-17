
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CompileAIScript import CompileAIScript
from ...PyMOD import Source
from ...FileFormats.AIBIN import AIBIN
from ...Utilities import IO

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

def empty_aiscript_bytes() -> bytes:
	aibin = AIBIN.AIBIN()
	return IO.output_to_bytes(lambda f: aibin.save(f, None))

class Test_source_paths(unittest.TestCase):
	def test_script_and_extdef_inputs_exclude_base_files_and_config(self) -> None:
		source_file = Source.AIScript(project_path('aiscript.bin'))
		with mock.patch('os.listdir', return_value=['aiscript.bin', 'bwscript.bin', 'config.json', 'zerg.txt', 'extdef.txt']):
			self.assertEqual(source_file.script_paths(), [project_path('aiscript.bin', 'zerg.txt')])
			self.assertEqual(source_file.extdef_paths(), [project_path('aiscript.bin', 'extdef.txt')])

	def test_base_files_are_the_bins_inside_the_folder(self) -> None:
		source_file = Source.AIScript(project_path('aiscript.bin'))
		with mock.patch('os.path.isfile', return_value=True):
			self.assertEqual(source_file.base_aiscript_path(), project_path('aiscript.bin', 'aiscript.bin'))
			self.assertEqual(source_file.base_bwscript_path(), project_path('aiscript.bin', 'bwscript.bin'))

	def test_no_base_files_when_they_are_absent(self) -> None:
		source_file = Source.AIScript(project_path('aiscript.bin'))
		with mock.patch('os.path.isfile', return_value=False):
			self.assertIsNone(source_file.base_aiscript_path())
			self.assertIsNone(source_file.base_bwscript_path())

class Test_config(unittest.TestCase):
	def test_defaults_to_not_expanded(self) -> None:
		config = CompileAIScript.Config.from_json({})
		self.assertFalse(config.expanded)

	def test_expanded_is_read(self) -> None:
		config = CompileAIScript.Config.from_json({'expanded': True})
		self.assertTrue(config.expanded)

class Test_compile_step(unittest.TestCase):
	def make_step(self) -> CompileAIScript:
		project = Project(ROOT_PATH)
		source_file = Source.AIScript(project_path('aiscript.bin'))
		return CompileAIScript(CompileThread(project), source_file)

	def logs(self, step: CompileAIScript) -> list:
		messages = []
		while not step.compile_thread.output_queue.empty():
			messages.append(step.compile_thread.output_queue.get())
		return messages

	def test_no_scripts_skips_the_step_with_a_warning(self) -> None:
		step = self.make_step()
		with mock.patch('os.listdir', return_value=[]):
			self.assertIsNone(step.execute())
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(len(warnings), 1)
		self.assertIn('0 scripts found', warnings[0].text)

	def test_no_base_files_starts_from_an_empty_aibin(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			aibin = step.load_base_aibin(CompileAIScript.Config.default())
		self.assertEqual(aibin.list_scripts(), [])
		self.assertFalse(aibin.expanded)
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(warnings, [])

	def test_base_aiscript_is_loaded_when_present(self) -> None:
		step = self.make_step()
		base_aiscript_path = project_path('aiscript.bin', 'aiscript.bin')
		with mock.patch('os.path.isfile', side_effect=lambda path: path == base_aiscript_path):
			with mock.patch('builtins.open', mock.mock_open(read_data=empty_aiscript_bytes())):
				aibin = step.load_base_aibin(CompileAIScript.Config.default())
		self.assertEqual(aibin.list_scripts(), [])
		self.assertFalse(aibin.expanded)
		logs = [message.text for message in self.logs(step)]
		self.assertTrue(any(base_aiscript_path in text for text in logs))

	def test_base_bwscript_without_base_aiscript_is_an_error(self) -> None:
		step = self.make_step()
		base_bwscript_path = project_path('aiscript.bin', 'bwscript.bin')
		with mock.patch('os.path.isfile', side_effect=lambda path: path == base_bwscript_path):
			with self.assertRaises(CompileError) as cm:
				step.load_base_aibin(CompileAIScript.Config.default())
		self.assertIn('no base aiscript.bin beside it', str(cm.exception))

	def test_unexpanded_compiles_without_a_plugin_warning(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			aibin = step.load_base_aibin(CompileAIScript.Config.default())
		self.assertFalse(aibin.expanded)
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(warnings, [])

	def test_config_expands_the_aibin_and_warns_a_plugin_is_required(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			aibin = step.load_base_aibin(CompileAIScript.Config(expanded=True))
		self.assertTrue(aibin.expanded)
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(len(warnings), 1)
		self.assertIn('plugin', warnings[0].text)
