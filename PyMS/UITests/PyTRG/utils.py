
from ..harness import UITestCase

from ...PyTRG.PyTRG import PyTRG
from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

# These tests drive PyTRG through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; the stat_txt/aiscript handlers
# are supplied as empty in-memory instances so no MPQs are needed.


class PyTRGTestCase(UITestCase):
	def make_pytrg(self) -> PyTRG:
		gui = self.make_window(PyTRG)
		gui.tbl = TBL.TBL()
		gui.aibin = AIBIN.AIBIN()
		return gui

	def settle_syntax_coloring(self, gui: PyTRG) -> None:
		# Recoloring runs on a chained 1ms `after` timer, so a single pump can
		# race it; pump until the pending update range is fully colored.
		for _ in range(10):
			self.pump(gui)
			if not gui.text.tag_ranges('Update'):
				break
