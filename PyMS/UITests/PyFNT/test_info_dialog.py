
from .utils import PyFNTTestCase

from ...PyFNT.PyFNT import PyFNT
from ...PyFNT.InfoDialog import InfoDialog, FontInfo
from ...Utilities import UIKit as UI

from unittest import mock


class Test_InfoDialog_result(PyFNTTestCase):
	def _open_dialog(self, gui: PyFNT, need_size: bool = False) -> InfoDialog:
		# `grab_wait` blocks on `wait_window` until the dialog closes; neutralize
		# it so the constructor returns with the dialog still open.
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			return InfoDialog(gui, need_size)

	def test_dialog_starts_with_no_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui)
		self.assertIsNone(dialog.result)
		dialog.cancel()

	def test_ok_captures_entered_values_as_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui, need_size=True)
		dialog.lowi.set(33)
		dialog.letters.set(6)
		dialog.width.set(5)
		dialog.height.set(7)
		dialog.ok()
		self.assertEqual(dialog.result, FontInfo(lowi=33, letters=6, width=5, height=7))

	def test_cancel_leaves_no_result(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui)
		dialog.cancel()
		self.assertIsNone(dialog.result)

	def test_size_prompts_ask_for_width_and_height(self) -> None:
		gui = self.open_pyfnt()
		dialog = self._open_dialog(gui, need_size=True)
		labels = [str(child.cget('text')) for child in dialog.winfo_children() if isinstance(child, UI.Label)]
		self.assertTrue(any('max width' in label for label in labels))
		self.assertTrue(any('max height' in label for label in labels))
		dialog.cancel()
