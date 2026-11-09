
from unittest import mock

from ..harness import UITestCase

from ...Utilities import UIKit as UI


class Test_Notebook_default_size(UITestCase):
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


class _VetoTab(UI.NotebookTab):
	def __init__(self, parent: UI.Misc, allow: bool) -> None:
		super().__init__(parent)
		self.allow = allow
		self.asked = 0

	def can_deactivate(self) -> bool:
		self.asked += 1
		return self.allow


class Test_Notebook_can_deactivate(UITestCase):
	# A tab can refuse to be left, so the notebook stays on it (with its own tab still selected)

	def make_notebook(self, allow: bool) -> tuple[UI.Notebook, _VetoTab, UI.Frame]:
		window = self.make_window(UI.MainWindow)
		notebook = UI.Notebook(window)
		notebook.pack()
		first = _VetoTab(notebook, allow)
		second = UI.Frame(notebook)
		notebook.add_tab(first, 'First')
		notebook.add_tab(second, 'Second')
		self.pump(window)
		return notebook, first, second

	def test_refusing_tab_stays_active(self) -> None:
		notebook, first, _ = self.make_notebook(False)
		# Clicking a tab selects its radiobutton before displaying it
		notebook.tab.set(1)
		self.assertIs(notebook.display('Second'), first)
		self.assertIs(notebook.active, first)
		self.assertEqual(notebook.tab.get(), 0)
		self.assertEqual(first.asked, 1)

	def test_allowing_tab_switches(self) -> None:
		notebook, first, second = self.make_notebook(True)
		self.assertIs(notebook.display('Second'), second)
		self.assertIs(notebook.active, second)
		self.assertEqual(notebook.tab.get(), 1)
		self.assertEqual(first.asked, 1)

	def test_redisplaying_active_tab_does_not_ask(self) -> None:
		notebook, first, _ = self.make_notebook(False)
		notebook.display('First')
		self.assertEqual(first.asked, 0)
