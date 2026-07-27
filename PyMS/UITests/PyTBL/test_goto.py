
from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...PyTBL.GotoDialog import GotoDialog


class Test_PyTBL_goto(PyTBLTestCase):
	def test_goto_on_empty_tbl_selects_nothing(self) -> None:
		gui = self.make_window(PyTBL)
		gui.new()
		self.pump(gui)
		dialog = GotoDialog(gui, gui)
		dialog.goto.set(5)
		dialog.jump()
		self.pump(gui)
		self.assertIsNone(self.selected_index(gui))

	def test_goto_clamps_to_last_string(self) -> None:
		gui = self.make_pytbl(['a\x00', 'b\x00'])
		dialog = GotoDialog(gui, gui)
		dialog.goto.set(10)
		dialog.jump()
		self.pump(gui)
		self.assertEqual(self.selected_index(gui), 1)

	def test_goto_history_is_capped(self) -> None:
		gui = self.make_pytbl(['a\x00', 'b\x00'])
		dialog = GotoDialog(gui, gui)
		for n in range(15):
			dialog.goto.set(n)
			dialog.jump()
		self.assertEqual(len(dialog.gotohistory.entries), dialog.gotohistory.limit)

	def test_goto_dialog_is_reused_after_close(self) -> None:
		gui = self.make_pytbl(['a\x00'])
		gui.goto()
		self.pump(gui)
		dialog = gui.gotowindow
		assert dialog is not None
		dialog.ok()
		self.pump(gui)
		self.assertTrue(dialog.winfo_exists())
		self.assertEqual(dialog.state(), 'withdrawn')
		gui.goto()
		self.pump(gui)
		self.assertIs(gui.gotowindow, dialog)
		self.assertEqual(dialog.state(), 'normal')
