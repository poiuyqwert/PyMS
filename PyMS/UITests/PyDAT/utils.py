
from ..harness import UITestCase

from ...PyDAT.PyDAT import PyDAT

# These tests drive PyDAT without `initialize()`, so no data files or default DATs
# are loaded from the MPQs. `with_new_dat` fills one tab with a fresh, empty DAT.


class PyDATTestCase(UITestCase):
	def make_pydat(self) -> PyDAT:
		return self.make_window(PyDAT)

	def with_new_dat(self, tab_name: str = 'Units') -> PyDAT:
		gui = self.make_pydat()
		gui.dattabs.display(tab_name)
		self.pump(gui)
		gui.new()
		self.pump(gui)
		return gui
