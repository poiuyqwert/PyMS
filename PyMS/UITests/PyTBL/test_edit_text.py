from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...Utilities import UIKit as UI


class Test_PyTBL_edit_text(PyTBLTestCase):
	def run_tk(self, gui: PyTBL, script: str) -> None:
		# Tk's text bindings `catch` expected failures, but tkinter stashes any
		# Python exception raised by a widget proxy and re-raises it from
		# `mainloop()`. Run the script inside a short mainloop so such errors
		# surface the way they do in the running app.
		# A watchdog ends the mainloop if the script never gets to run (or opens
		# something that waits), so the test fails instead of hanging.
		timed_out = False
		def timeout() -> None:
			nonlocal timed_out
			timed_out = True
			UI.Misc.quit(gui)
		watchdog = gui.after(5000, timeout)
		def run() -> None:
			try:
				gui.tk.eval(script)
			finally:
				gui.after_cancel(watchdog)
				UI.Misc.quit(gui)
		gui.after(0, run)
		UI.Misc.mainloop(gui)
		self.assertFalse(timed_out, f'Timed out running {script!r}')

	def select_string(self, gui: PyTBL, index: int) -> None:
		gui.listbox.select_set(index)
		gui.update_string()
		self.pump(gui)

	def test_paste_without_selection_inserts_clipboard(self) -> None:
		gui = self.make_pytbl(['abc\x00', 'def\x00'])
		self.select_string(gui, 0)
		gui.text.tag_remove(UI.SEL, '1.0', UI.END)
		gui.text.mark_set(UI.INSERT, '1.0')
		gui.clipboard_clear()
		gui.clipboard_append('XYZ')
		self.run_tk(gui, f'tk_textPaste {getattr(gui.text, "_w")}')
		assert gui.tbl is not None
		self.assertEqual(gui.tbl.strings[0], 'XYZabc\x00')
		self.assertEqual(gui.listbox.get(0), 'XYZabc<0>')
		self.assertTrue(gui.edited)

	def test_paste_with_selection_replaces_selection(self) -> None:
		gui = self.make_pytbl(['abc\x00'])
		self.select_string(gui, 0)
		gui.text.tag_add(UI.SEL, '1.0', '1.2')
		gui.text.mark_set(UI.INSERT, '1.2')
		gui.clipboard_clear()
		gui.clipboard_append('XYZ')
		self.run_tk(gui, f'tk_textPaste {getattr(gui.text, "_w")}')
		assert gui.tbl is not None
		self.assertEqual(gui.tbl.strings[0], 'XYZc\x00')

	def test_clear_without_selection_leaves_string_unedited(self) -> None:
		gui = self.make_pytbl(['abc\x00'])
		self.select_string(gui, 0)
		gui.text.tag_remove(UI.SEL, '1.0', UI.END)
		self.run_tk(gui, f'event generate {getattr(gui.text, "_w")} <<Clear>>')
		assert gui.tbl is not None
		self.assertEqual(gui.tbl.strings[0], 'abc\x00')
		self.assertFalse(gui.edited)
