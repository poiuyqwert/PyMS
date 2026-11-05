
from ..harness import UITestCase

from ...PyGRAFT.PyGRAFT import PyGRAFT
from ...PyGRAFT.Tabs import GraftTab

from typing import cast

SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
ASK_YES_NO_CANCEL = 'tkinter.messagebox.askyesnocancel'

TAB_TITLES = ('Button Sets', 'Button Cards', 'Unit Stat Info', 'Unit Training Reqs.', 'Upgrade Research Reqs.', 'Tech Research Reqs.', 'Tech Usage Reqs.', 'Order Reqs.')

class PyGRAFTTestCase(UITestCase):
	def open_pygraft(self) -> PyGRAFT:
		return self.make_window(PyGRAFT)

	def display_tab(self, gui: PyGRAFT, title: str) -> GraftTab:
		tab = cast(GraftTab, gui.notebook.display(title))
		self.pump(gui)
		return tab

	def list_entries(self, gui: PyGRAFT) -> list[str]:
		return [str(entry) for entry in gui.listbox.get(0, 'end')]

	def list_selection(self, gui: PyGRAFT) -> list[int]:
		return [int(index) for index in gui.listbox.curselection()]

	def select_in_list(self, gui: PyGRAFT, index: int) -> None:
		gui.listbox.select_clear(0, 'end')
		gui.listbox.select_set(index)
		gui.listbox.listbox.event_generate('<<ListboxSelect>>')
		self.pump(gui)
