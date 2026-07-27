
from .utils import PyMODTestCase, PROJECT_PATH

from ...PyMOD.PyMOD import PyMOD
from ...PyMOD.Project import Project
from ...Utilities import UIKit as UI
from ...Utilities.PyMSError import PyMSError

from unittest import mock


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


class Test_PyMOD_exit(PyMODTestCase):
	def test_exit_saves_config_and_destroys_the_window(self) -> None:
		gui = self.make_window(PyMOD)
		with mock.patch.object(PyMOD, 'destroy', autospec=True) as destroy, \
				mock.patch.object(type(gui.config_), 'save', autospec=True) as save:
			gui.exit()
		destroy.assert_called_once()
		save.assert_called_once()
