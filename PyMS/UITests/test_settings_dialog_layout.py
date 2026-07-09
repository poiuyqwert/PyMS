
from unittest import mock

from .harness import UITestCase

from ..Utilities import UIKit as UI
from ..Utilities import Config
from ..Utilities.SettingsUI.BaseSettingsDialog import BaseSettingsDialog


class _TestConfig(Config.Config):
	_name = 'uitest_settings'
	_version = 1
	_migrations: dict = {}


class TestSettingsDialogLayout(UITestCase):
	# The settings dialog stacks an expanding Notebook over a fixed Ok/Cancel row.
	# Two invariants keep the buttons reachable at every window size: the dialog
	# enforces a minimum size at least as large as its natural layout, and the
	# button row is anchored to the bottom (packed before the notebook) so it is
	# the notebook — not the buttons — that gives up space when the window shrinks.

	def make_dialog(self) -> BaseSettingsDialog:
		window = self.make_window(UI.MainWindow)
		config = _TestConfig()
		# `grab_wait` blocks on `wait_window` until the dialog closes; neutralize it
		# so construction returns and the test can inspect the live widget tree.
		with mock.patch.object(UI.WindowExtensions, 'grab_wait', lambda self: None):
			dialog = BaseSettingsDialog(window, config)
		self.addCleanup(self._destroy, dialog)
		self.pump(dialog)
		return dialog

	def test_enforces_minimum_size(self) -> None:
		dialog = self.make_dialog()
		min_width, min_height = dialog.minsize()
		self.assertGreater(min_width, 1)
		self.assertGreater(min_height, 1)
		self.assertGreaterEqual(min_width, dialog.winfo_reqwidth())
		self.assertGreaterEqual(min_height, dialog.winfo_reqheight())

	def test_button_row_anchored_below_expanding_notebook(self) -> None:
		dialog = self.make_dialog()
		slaves = dialog.pack_slaves()
		# `Notebook` proxies `pack` to its own container frame, and the buttons live
		# in their own frame, so match each against the dialog's direct slaves by
		# widget path to get the actual packed children.
		button_parent = dialog.ok_button.winfo_parent()
		button_frame = next(slave for slave in slaves if str(slave) == button_parent)
		notebook_parent = dialog.notebook.winfo_parent()
		notebook_container = next(slave for slave in slaves if str(slave) == notebook_parent)

		# The button row is packed before the notebook so the notebook is the
		# last-packed child (the one Tk shrinks first).
		self.assertLess(slaves.index(button_frame), slaves.index(notebook_container))
		self.assertEqual(button_frame.pack_info()['side'], 'bottom')

		notebook_info = notebook_container.pack_info()
		self.assertEqual(int(notebook_info['expand']), 1)
		self.assertEqual(notebook_info['fill'], 'both')
