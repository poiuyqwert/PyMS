
from ..harness import UITestCase

from ...PyLO.PyLO import PyLO

# These tests drive PyLO through its public command methods, asserting on both
# widget and model state. The harness neutralizes settings I/O, analytics, the
# update check, and the tracer; file dialogs and file I/O are mocked so no
# files are read or written.


class PyLOTestCase(UITestCase):
	def make_pylo(self) -> PyLO:
		return self.make_window(PyLO)

	def settle_syntax_coloring(self, gui: PyLO) -> None:
		# Recoloring runs on a chained 1ms `after` timer, so a single pump can
		# race it; pump until the pending update range is fully colored.
		for _ in range(10):
			self.pump(gui)
			if not gui.text.tag_ranges('Update'):
				break
