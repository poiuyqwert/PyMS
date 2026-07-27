
from ..harness import UITestCase

from ...PyGRP.PyGRP import PyGRP
from ...FileFormats import GRP

# These tests drive PyGRP's frame list through its public command methods,
# asserting on both the listbox and the model. The harness neutralizes
# settings I/O, analytics, the update check, and the tracer; palettes are
# loaded from the real (read-only) bundled palette files.


def _frame(fill: int, width: int = 4, height: int = 4) -> GRP.Pixels:
	return [[fill] * width for _ in range(height)]


class PyGRPTestCase(UITestCase):
	def with_frames(self, count: int) -> PyGRP:
		# A new GRP populated with `count` distinct in-memory frames.
		gui = self.make_window(PyGRP)
		gui.new()
		assert gui.grp is not None
		gui.grp.load_frames([_frame(n + 1) for n in range(count)])
		gui.frames = [{} for _ in range(count)]
		gui.update_list()
		self.pump(gui)
		return gui

	def selection(self, gui: PyGRP) -> list[int]:
		return [int(i) for i in gui.listbox.curselection()]
