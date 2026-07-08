
from unittest import mock

from .harness import UITestCase

from ..PyTBL.PyTBL import PyTBL
from ..PyTBL.FindDialog import FindDialog
from ..PyTBL.GotoDialog import GotoDialog
from ..PyTBL.PreviewDialog import PreviewDialog
from ..FileFormats import TBL
from ..FileFormats import FNT
from ..FileFormats import PCX
from ..FileFormats import Palette
from ..FileFormats import GRP
from ..Utilities import UIKit as UI

# These tests drive PyTBL through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; TBL contents are supplied by
# stubbing `TBL.load` so no files are read.


class PyTBLTestCase(UITestCase):
	def make_pytbl(self, strings: list[str] | None = None) -> PyTBL:
		gui = self.make_window(PyTBL)
		if strings is not None:
			def fake_load(tbl: TBL.TBL, _file: str) -> None:
				tbl.strings = list(strings)
			with mock.patch('PyMS.FileFormats.TBL.TBL.load', autospec=True, side_effect=fake_load):
				gui.open(file='test.tbl')
			self.pump(gui)
		return gui

	def selected_index(self, gui: PyTBL) -> int | None:
		selection = gui.listbox.curselection()
		if not selection:
			return None
		return int(selection[0])


class Test_PyTBL_open(PyTBLTestCase):
	def test_open_populates_list_and_selects_first_string(self) -> None:
		gui = self.make_pytbl(['first\x00', 'second\x00'])
		self.assertEqual(gui.listbox.size(), 2)
		self.assertEqual(self.selected_index(gui), 0)
		self.assertEqual(gui.file, 'test.tbl')
		self.assertEqual(gui.status.get(), 'Load Successful!')
		self.assertFalse(gui.edited)

	def test_import_populates_list_and_selects_first_string(self) -> None:
		gui = self.make_window(PyTBL)
		def fake_interpret(tbl: TBL.TBL, _file: str) -> None:
			tbl.strings = ['first\x00']
		with mock.patch('PyMS.FileFormats.TBL.TBL.interpret', autospec=True, side_effect=fake_interpret), \
				mock.patch('PyMS.Utilities.Config.SelectFile.select_open', return_value='test.txt'):
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.listbox.size(), 1)
		self.assertEqual(self.selected_index(gui), 0)
		self.assertEqual(gui.file, 'test.txt')
		self.assertEqual(gui.status.get(), 'Import Successful!')


class Test_PyTBL_find(PyTBLTestCase):
	def test_find_with_no_selection_searches_from_start(self) -> None:
		gui = self.make_pytbl(['alpha', 'beta', 'gamma'])
		gui.listbox.select_clear(0, UI.END)
		dialog = FindDialog(gui, gui)
		dialog.find.set('gamma')
		dialog.findnext()
		self.pump(gui)
		self.assertEqual(self.selected_index(gui), 2)

	def test_regex_alternation_matches_anywhere_in_string(self) -> None:
		gui = self.make_pytbl(['nothing here', 'xx bar yy'])
		dialog = FindDialog(gui, gui)
		dialog.regex.set(True)
		dialog.find.set('foo|bar')
		with mock.patch('tkinter.messagebox.showinfo') as showinfo:
			dialog.findnext()
		self.pump(gui)
		showinfo.assert_not_called()
		self.assertEqual(self.selected_index(gui), 1)

	def test_find_history_is_capped(self) -> None:
		gui = self.make_pytbl(['alpha'])
		dialog = FindDialog(gui, gui)
		with mock.patch('tkinter.messagebox.showinfo'):
			for n in range(15):
				dialog.find.set(f'entry{n}')
				dialog.findnext()
		self.assertEqual(len(dialog.findhistory.entries), dialog.findhistory.limit)

	def test_find_dialog_is_reused_after_close(self) -> None:
		gui = self.make_pytbl(['alpha'])
		gui.find()
		self.pump(gui)
		dialog = gui.findwindow
		assert dialog is not None
		dialog.ok()
		self.pump(gui)
		self.assertTrue(dialog.winfo_exists())
		self.assertEqual(dialog.state(), 'withdrawn')
		gui.find()
		self.pump(gui)
		self.assertIs(gui.findwindow, dialog)
		self.assertEqual(dialog.state(), 'normal')


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


class Test_PyTBL_preview(PyTBLTestCase):
	def make_pytbl_with_fonts(self, strings: list[str]) -> PyTBL:
		gui = self.make_pytbl(strings)
		gui.tfontgam = PCX.PCX()
		gui.font8 = FNT.FNT()
		gui.font10 = FNT.FNT()
		gui.unitpal = Palette.Palette()
		gui.icons = GRP.GRP()
		return gui

	def make_preview(self, gui: PyTBL) -> PreviewDialog:
		with mock.patch('PyMS.Utilities.UIKit.Widgets.Extensions.WindowExtensions.grab_wait', return_value=None):
			dialog = PreviewDialog(gui, gui)
		self.pump(gui)
		return dialog

	def test_one_character_string_previews_without_error(self) -> None:
		gui = self.make_pytbl_with_fonts(['x'])
		dialog = self.make_preview(gui)
		self.assertTrue(dialog.winfo_exists())

	def test_hotkey_string_with_no_displayable_glyphs_previews_without_error(self) -> None:
		# The resource icon offsets point into the synthetic resource line, which
		# can be shorter than expected when glyphs fall outside the font range
		# (empty in-memory fonts filter out every glyph).
		gui = self.make_pytbl_with_fonts(['a\x01mineral cost'])
		dialog = self.make_preview(gui)
		self.assertTrue(dialog.winfo_exists())
