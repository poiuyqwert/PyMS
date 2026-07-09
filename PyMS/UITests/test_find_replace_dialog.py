
import unittest
from unittest import mock

from .harness import UITestCase

from ..Utilities import UIKit as UI
from ..Utilities import Config
from ..Utilities.FindReplaceDialog import FindReplaceDialog


class _Host(UI.MainWindow):
	def __init__(self) -> None:
		UI.MainWindow.__init__(self)
		self.text = UI.CodeText(self)
		self.text.pack(fill=UI.BOTH, expand=1)


class Test_FindReplaceDialog(UITestCase):
	def make_dialog(self, contents: str) -> tuple[_Host, FindReplaceDialog]:
		window = self.make_window(_Host)
		window.text.load(contents)
		# Search starts from the insert cursor, which `load` leaves at the end
		window.text.mark_set(UI.INSERT, '1.0')
		dialog = FindReplaceDialog(window, window.text, Config.WindowGeometry())
		self.pump(window)
		return window, dialog

	def test_find_next_selects_match_and_records_history(self) -> None:
		window, dialog = self.make_dialog('alpha\nbeta\nalpha\n')
		dialog.find.set('beta')
		with mock.patch.object(UI.MessageBox, 'showinfo') as showinfo:
			dialog.findnext()
		showinfo.assert_not_called()
		self.pump(window)
		sel = tuple(str(index) for index in window.text.tag_ranges('sel'))
		self.assertEqual(sel, ('2.0', '2.4'))
		self.assertEqual(dialog.find_history.entries, ['beta'])
		# The find entry dropdown shares the history, so the recorded entry is
		# available from the dropdown.
		self.assertIs(dialog.findentry.history, dialog.find_history)

	def selection(self, window: _Host) -> tuple[str, ...]:
		return tuple(str(index) for index in window.text.tag_ranges('sel'))

	def test_find_down_continues_from_previous_match(self) -> None:
		window, dialog = self.make_dialog('alpha\nbeta\nalpha\n')
		dialog.find.set('alpha')
		with mock.patch.object(UI.MessageBox, 'showinfo') as showinfo:
			dialog.findnext()
			self.assertEqual(self.selection(window), ('1.0', '1.5'))
			dialog.findnext()
			self.assertEqual(self.selection(window), ('3.0', '3.5'))
			showinfo.assert_not_called()
			dialog.findnext()
		showinfo.assert_called_once()
		self.assertIn("Can't find text", showinfo.call_args.kwargs['message'])

	def test_find_up_selects_last_match_before_cursor(self) -> None:
		window, dialog = self.make_dialog('alpha beta alpha\nbeta\n')
		window.text.mark_set(UI.INSERT, UI.END)
		dialog.updown.set(0)
		dialog.find.set('alpha')
		with mock.patch.object(UI.MessageBox, 'showinfo') as showinfo:
			dialog.findnext()
			self.assertEqual(self.selection(window), ('1.11', '1.16'))
			dialog.findnext()
			self.assertEqual(self.selection(window), ('1.0', '1.5'))
			showinfo.assert_not_called()
			dialog.findnext()
		showinfo.assert_called_once()
		self.assertIn("Can't find text", showinfo.call_args.kwargs['message'])

	def test_find_up_with_no_earlier_match_reports_not_found(self) -> None:
		_window, dialog = self.make_dialog('alpha\nbeta\n')
		dialog.updown.set(0)
		dialog.find.set('alpha')
		with mock.patch.object(UI.MessageBox, 'showinfo') as showinfo:
			dialog.findnext()
		showinfo.assert_called_once()

	def test_replace_all_replaces_matches(self) -> None:
		window, dialog = self.make_dialog('alpha\nbeta\nalpha\n')
		dialog.find.set('alpha')
		dialog.replacewith.set('gamma')
		with mock.patch.object(UI.MessageBox, 'showinfo') as showinfo:
			dialog.replaceall()
		self.pump(window)
		self.assertEqual(window.text.get('1.0', UI.END).rstrip('\n'), 'gamma\nbeta\ngamma')
		self.assertIn('2 matches replaced', showinfo.call_args.kwargs['message'])

	def test_invalid_regex_flashes_find_entry(self) -> None:
		window, dialog = self.make_dialog('alpha\n')
		dialog.regex.set(1)
		dialog.find.set('(')
		with mock.patch.object(UI.MessageBox, 'showinfo'):
			dialog.findnext()
		self.pump(window)
		self.assertEqual(dialog.findentry['bg'], '#FFB4B4')
		dialog.updatecolor()
		self.assertEqual(dialog.findentry['bg'], dialog.findentry_c)

	def test_close_withdraws_for_reuse_and_show_restores(self) -> None:
		window, dialog = self.make_dialog('alpha\n')
		dialog.ok()
		self.pump(window)
		self.assertEqual(dialog.state(), 'withdrawn')
		dialog.show()
		self.pump(window)
		self.assertEqual(dialog.state(), 'normal')

	def test_destroy_really_destroys_the_dialog(self) -> None:
		window, dialog = self.make_dialog('alpha\n')
		dialog.ok()
		self.pump(window)
		dialog.destroy()
		self.pump(window)
		self.assertFalse(dialog.winfo_exists())

	def test_find_only_mode_has_no_replace_buttons(self) -> None:
		window = self.make_window(_Host)
		window.text.load('alpha\n')
		dialog = FindReplaceDialog(window, window.text, Config.WindowGeometry(), can_replace=False)
		self.pump(window)
		self.assertEqual(dialog.title(), 'Find')
		self.assertFalse(hasattr(dialog, 'replaceentry'))


if __name__ == '__main__':
	unittest.main()
