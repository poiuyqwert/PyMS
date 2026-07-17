
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CompileIScript import CompileIScript
from ...PyMOD import Source
from ...FileFormats.IScriptBIN import IScriptBIN
from ...Utilities import IO

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

def empty_iscript_bytes() -> bytes:
	iscript_bin = IScriptBIN.IScriptBIN()
	return IO.output_to_bytes(iscript_bin.save)

class Test_source_paths(unittest.TestCase):
	def test_script_inputs_exclude_base_file_and_config(self) -> None:
		source_file = Source.IScript(project_path('iscript.bin'))
		with mock.patch('os.listdir', return_value=['iscript.bin', 'config.json', 'dragoon.txt', 'marine.txt']):
			self.assertEqual(source_file.script_paths(), [
				project_path('iscript.bin', 'dragoon.txt'),
				project_path('iscript.bin', 'marine.txt'),
			])

	def test_base_file_is_the_bin_inside_the_folder(self) -> None:
		source_file = Source.IScript(project_path('iscript.bin'))
		with mock.patch('os.path.isfile', return_value=True):
			self.assertEqual(source_file.base_iscript_path(), project_path('iscript.bin', 'iscript.bin'))

	def test_no_base_file_when_it_is_absent(self) -> None:
		source_file = Source.IScript(project_path('iscript.bin'))
		with mock.patch('os.path.isfile', return_value=False):
			self.assertIsNone(source_file.base_iscript_path())

class Test_compile_step(unittest.TestCase):
	def make_step(self) -> CompileIScript:
		project = Project(ROOT_PATH)
		source_file = Source.IScript(project_path('iscript.bin'))
		return CompileIScript(CompileThread(project), source_file)

	def logs(self, step: CompileIScript) -> list:
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

	def test_no_base_file_starts_from_an_empty_iscript_bin(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			iscript_bin = step.load_base_iscript_bin()
		self.assertEqual(iscript_bin.list_scripts(), [])
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(warnings, [])

	def test_base_iscript_is_loaded_when_present(self) -> None:
		step = self.make_step()
		base_iscript_path = project_path('iscript.bin', 'iscript.bin')
		with mock.patch('os.path.isfile', side_effect=lambda path: path == base_iscript_path):
			with mock.patch('builtins.open', mock.mock_open(read_data=empty_iscript_bytes())):
				iscript_bin = step.load_base_iscript_bin()
		self.assertEqual(iscript_bin.list_scripts(), [])
		logs = [message.text for message in self.logs(step)]
		self.assertTrue(any(base_iscript_path in text for text in logs))

	def test_invalid_base_iscript_is_a_compile_error(self) -> None:
		step = self.make_step()
		base_iscript_path = project_path('iscript.bin', 'iscript.bin')
		with mock.patch('os.path.isfile', side_effect=lambda path: path == base_iscript_path):
			with mock.patch('builtins.open', mock.mock_open(read_data=b'not an iscript.bin')):
				with self.assertRaises(CompileError) as cm:
					step.load_base_iscript_bin()
		self.assertIn("Couldn't load base file", str(cm.exception))
