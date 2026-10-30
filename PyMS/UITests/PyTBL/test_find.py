
from .utils import PyTBLTestCase

from ...PyTBL.FindDialog import FindDialog
from ...Utilities import UIKit as UI

from unittest import mock


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
