
from unittest import mock

from .harness import UITestCase

from ..PyMOD.PyMOD import PyMOD
from ..PyMOD.Project import Project
from ..PyMOD.CompileThread import CompileThread
from ..Utilities import UIKit as UI
from ..Utilities.PyMSError import PyMSError

import os

# These tests drive PyMOD through its public command methods, asserting on both
# widget and model state. The harness neutralizes settings I/O, analytics, the
# update check, and the tracer; project folders are supplied by stubbing the
# project marker check and the directory walk so no files are read.

PROJECT_PATH = os.path.join(os.sep, 'fake', 'project')


class PyMODTestCase(UITestCase):
	def open_project(self, gui: PyMOD, files: list[str] | None = None) -> None:
		def fake_walk(path: str, topdown: bool = True) -> list[tuple[str, list[str], list[str]]]:
			assert topdown, 'The source walk must be top-down so directory pruning works'
			return [(path, [], list(files or ['sound.wav']))]
		with mock.patch.object(Project, 'load', autospec=True, return_value=None), \
				mock.patch('PyMS.PyMOD.Project._os.walk', side_effect=fake_walk):
			gui.open(PROJECT_PATH)
		self.pump(gui)


class Test_PyMOD_startup(PyMODTestCase):
	def test_no_project_open_disables_project_actions(self) -> None:
		gui = self.make_window(PyMOD)
		self.assertIsNone(gui.project)
		self.assertFalse(gui.toolbar.tag_is_enabled('file_open'))
		self.assertTrue(gui.toolbar.tag_is_enabled('not_compiling'))
		self.assertEqual(str(gui.compile_button['state']), UI.DISABLED)
		self.assertEqual(str(gui.extract_button['state']), UI.DISABLED)
		self.assertEqual(str(gui.clean_button['state']), UI.DISABLED)
		self.assertEqual(str(gui.cancel_button['state']), UI.DISABLED)
		self.assertEqual(gui.status.get(), 'Open or create a Mod Project.')


class Test_PyMOD_open_close(PyMODTestCase):
	def test_open_enables_project_actions_and_lists_files(self) -> None:
		gui = self.make_window(PyMOD)
		self.open_project(gui, files=['sound.wav'])
		self.assertIsNotNone(gui.project)
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))
		self.assertEqual(str(gui.compile_button['state']), UI.NORMAL)
		self.assertIn(PROJECT_PATH, gui.title())
		self.assertIn('opened', gui.status.get())

	def test_open_declining_to_initialize_a_non_project_folder_keeps_it_closed(self) -> None:
		gui = self.make_window(PyMOD)
		with mock.patch.object(Project, 'load', autospec=True, side_effect=PyMSError('Load', 'is not a PyMOD project')), \
				mock.patch('tkinter.messagebox.askyesno', return_value=False) as askyesno:
			gui.open(PROJECT_PATH)
		self.pump(gui)
		askyesno.assert_called_once()
		self.assertIsNone(gui.project)

	def test_close_returns_to_the_no_project_state(self) -> None:
		gui = self.make_window(PyMOD)
		self.open_project(gui)
		gui.close()
		self.pump(gui)
		self.assertIsNone(gui.project)
		self.assertFalse(gui.toolbar.tag_is_enabled('file_open'))
		self.assertEqual(str(gui.compile_button['state']), UI.DISABLED)
		self.assertEqual(gui.status.get(), 'Open or create a Mod Project.')


class Test_PyMOD_compile_states(PyMODTestCase):
	def test_a_running_compile_disables_project_and_file_actions(self) -> None:
		gui = self.make_window(PyMOD)
		self.open_project(gui)
		assert gui.project is not None
		gui.compile_thread = CompileThread(gui.project)
		gui.update_states()
		self.pump(gui)
		self.assertFalse(gui.toolbar.tag_is_enabled('not_compiling'))
		self.assertEqual(str(gui.compile_button['state']), UI.DISABLED)
		self.assertEqual(str(gui.cancel_button['state']), UI.NORMAL)
		gui.compile_thread = None
		gui.update_states()
		self.pump(gui)
		self.assertTrue(gui.toolbar.tag_is_enabled('not_compiling'))
		self.assertEqual(str(gui.compile_button['state']), UI.NORMAL)

	def test_watch_compile_logs_messages_left_by_a_finished_compile(self) -> None:
		gui = self.make_window(PyMOD)
		self.open_project(gui)
		assert gui.project is not None
		compile_thread = CompileThread(gui.project)
		compile_thread.output_queue.put(CompileThread.OutputMessage.Log('Compile completed'))
		gui.compile_thread = compile_thread
		gui.watch_compile()
		self.pump(gui)
		self.assertIn('Compile completed', gui.logs_textview.textview.get('1.0', UI.END))
		self.assertIsNone(gui.compile_thread)
		self.assertEqual(gui.status.get(), 'Compile finished.')


class Test_PyMOD_exit(PyMODTestCase):
	def test_exit_saves_config_and_destroys_the_window(self) -> None:
		gui = self.make_window(PyMOD)
		with mock.patch.object(PyMOD, 'destroy', autospec=True) as destroy, \
				mock.patch.object(type(gui.config_), 'save', autospec=True) as save:
			gui.exit()
		destroy.assert_called_once()
		save.assert_called_once()
