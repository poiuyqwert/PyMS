
from unittest import mock

from .harness import UITestCase

from ..Utilities import UIKit as UI


class TestNotebookDefaultSize(UITestCase):
	# Adding tabs sizes the page container to the largest tab (so switching tabs
	# doesn't resize the notebook), but the per-tab sizing pass is debounced onto
	# idle so building N tabs costs one pass, not N — while still running before
	# `update_idletasks()`-driven callers (e.g. PyMSDialog's min-size) read the size.

	def test_add_tab_debounces_the_sizing_pass(self) -> None:
		window = self.make_window(UI.MainWindow)
		notebook = UI.Notebook(window)
		notebook.pack()
		with mock.patch.object(UI.Notebook, '_update_default_size', autospec=True) as spy:
			for i in range(5):
				notebook.add_tab(UI.Frame(notebook), f'Tab {i}')
			# Deferred: a burst of add_tab calls has not triggered a sizing pass yet.
			self.assertEqual(spy.call_count, 0)
			window.update_idletasks()
			# Coalesced: the whole burst collapses into a single pass on idle.
			self.assertEqual(spy.call_count, 1)

	def test_sizes_to_the_largest_tab_not_the_active_one(self) -> None:
		window = self.make_window(UI.MainWindow)
		notebook = UI.Notebook(window)
		notebook.pack()
		# The narrow tab is added first and so is the active one; the notebook must
		# still reserve room for the wider tab.
		notebook.add_tab(UI.Frame(notebook, width=60, height=40), 'narrow')
		notebook.add_tab(UI.Frame(notebook, width=320, height=40), 'wide')
		window.update_idletasks()
		self.assertGreaterEqual(notebook.winfo_reqwidth(), 320)
