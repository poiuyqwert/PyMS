
from .utils import PyMODTestCase

from ...PyMOD.PyMOD import PyMOD
from ...PyMOD.CompileThread import CompileThread
from ...Utilities import UIKit as UI


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
