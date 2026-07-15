
from ...PyMOD.Project import Project
from ...PyMOD.CompileThread import CompileThread
from ...PyMOD.CompileStep.DetermineSourceFiles import DetermineSourceFiles
from ...PyMOD.CompileStep.BaseCompileStep import CompileError
from ...PyMOD.CompileStep.CompileDAT import CompileDAT
from ...PyMOD import Source
from ...FileFormats import DAT
from ...Utilities import Assets

import os
import unittest
from unittest import mock

ROOT_PATH = os.path.join(os.sep, 'project')

def project_path(*path: str) -> str:
	return os.path.join(ROOT_PATH, *path)

class Test_dat_types(unittest.TestCase):
	def test_every_dat_file_name_maps_to_its_format_class(self) -> None:
		expected: dict[str, type] = {
			'units.dat': DAT.UnitsDAT,
			'weapons.dat': DAT.WeaponsDAT,
			'flingy.dat': DAT.FlingyDAT,
			'sprites.dat': DAT.SpritesDAT,
			'images.dat': DAT.ImagesDAT,
			'upgrades.dat': DAT.UpgradesDAT,
			'techdata.dat': DAT.TechDAT,
			'sfxdata.dat': DAT.SoundsDAT,
			'portdata.dat': DAT.PortraitsDAT,
			'mapdata.dat': DAT.CampaignDAT,
			'orders.dat': DAT.OrdersDAT,
		}
		for file_name, dat_type in expected.items():
			source_file = Source.DAT(project_path(file_name))
			self.assertIs(source_file.dat_type(), dat_type)

	def test_every_dat_file_name_has_a_bundled_default(self) -> None:
		for file_name in ('units.dat', 'weapons.dat', 'flingy.dat', 'sprites.dat', 'images.dat', 'upgrades.dat', 'techdata.dat', 'sfxdata.dat', 'portdata.dat', 'mapdata.dat', 'orders.dat'):
			self.assertTrue(os.path.isfile(Assets.mpq_file_path('arr', file_name)), f'No bundled default for `{file_name}`')

class Test_source_paths(unittest.TestCase):
	def test_all_text_files_are_inputs_in_sorted_order(self) -> None:
		source_file = Source.DAT(project_path('units.dat'))
		with mock.patch('os.listdir', return_value=['zerg.txt', 'config.json', 'terran.txt', 'notes.md']):
			self.assertEqual(source_file.text_paths(), [
				project_path('units.dat', 'terran.txt'),
				project_path('units.dat', 'zerg.txt'),
			])

	def test_base_dat_is_the_file_named_the_same_as_the_folder(self) -> None:
		source_file = Source.DAT(project_path('units.dat'))
		with mock.patch('os.path.isfile', return_value=True):
			self.assertEqual(source_file.base_dat_path(), project_path('units.dat', 'units.dat'))

	def test_no_base_dat_when_the_file_is_absent(self) -> None:
		source_file = Source.DAT(project_path('units.dat'))
		with mock.patch('os.path.isfile', return_value=False):
			self.assertIsNone(source_file.base_dat_path())

class Test_config(unittest.TestCase):
	def test_defaults_to_no_expansion(self) -> None:
		config = CompileDAT.Config.from_json({})
		self.assertIsNone(config.entry_count)

	def test_entry_count_is_read(self) -> None:
		config = CompileDAT.Config.from_json({'entry_count': 500})
		self.assertEqual(config.entry_count, 500)

class Test_compile_step(unittest.TestCase):
	def make_step(self, file_name: str = 'units.dat') -> CompileDAT:
		project = Project(ROOT_PATH)
		source_file = Source.DAT(project_path(file_name))
		return CompileDAT(CompileThread(project), source_file)

	def logs(self, step: CompileDAT) -> list:
		messages = []
		while not step.compile_thread.output_queue.empty():
			messages.append(step.compile_thread.output_queue.get())
		return messages

	def test_no_input_files_skips_the_step_with_a_warning(self) -> None:
		step = self.make_step()
		with mock.patch('os.listdir', return_value=[]):
			self.assertIsNone(step.execute())
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(len(warnings), 1)
		self.assertIn('0 input files found', warnings[0].text)

	def test_user_supplied_base_dat_is_used_when_present(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=True):
			self.assertEqual(step.base_dat_path(), project_path('units.dat', 'units.dat'))

	def test_bundled_default_is_used_when_no_base_dat_is_supplied(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			self.assertEqual(step.base_dat_path(), Assets.mpq_file_path('arr', 'units.dat'))

	def test_unexpanded_dat_compiles_without_a_plugin_warning(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			dat = step.load_base_dat(CompileDAT.Config.default())
		self.assertFalse(dat.is_expanded())
		self.assertEqual(dat.entry_count(), DAT.UnitsDAT.FORMAT.entries)
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(warnings, [])

	def test_config_expands_the_dat_and_warns_a_plugin_is_required(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			dat = step.load_base_dat(CompileDAT.Config(entry_count=500))
		self.assertTrue(dat.is_expanded())
		self.assertGreaterEqual(dat.entry_count(), 500)
		warnings = [message for message in self.logs(step) if message.tag == 'warning']
		self.assertEqual(len(warnings), 1)
		self.assertIn('plugin', warnings[0].text)

	def test_config_smaller_than_the_base_does_not_expand(self) -> None:
		step = self.make_step()
		with mock.patch('os.path.isfile', return_value=False):
			dat = step.load_base_dat(CompileDAT.Config(entry_count=DAT.UnitsDAT.FORMAT.entries - 10))
		self.assertFalse(dat.is_expanded())
		self.assertEqual(dat.entry_count(), DAT.UnitsDAT.FORMAT.entries)

	def test_expanding_beyond_the_format_max_is_an_error(self) -> None:
		step = self.make_step('orders.dat')
		with mock.patch('os.path.isfile', return_value=False):
			with self.assertRaises(CompileError) as cm:
				step.load_base_dat(CompileDAT.Config(entry_count=300))
		self.assertIn("can't be expanded to 300 entries", str(cm.exception))

	def test_dat_source_schedules_a_compile_dat_step(self) -> None:
		project = Project(ROOT_PATH)
		project.source_graph = root = Source.Folder(ROOT_PATH)
		source_file = Source.DAT(project_path('units.dat'))
		root.add_child(source_file)
		steps = DetermineSourceFiles(CompileThread(project)).execute() or []
		dat_steps = [step for step in steps if isinstance(step, CompileDAT)]
		self.assertEqual(len(dat_steps), 1)
		self.assertIs(dat_steps[0].source_file, source_file)
