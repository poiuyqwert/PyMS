
from ..harness import UITestCase

from ...PyGOT.PyGOT import PyGOT

# These tests drive PyGOT through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; file dialogs and the GOT
# format's file I/O are mocked so no disk access happens.


class PyGOTTestCase(UITestCase):
	def make_pygot(self) -> PyGOT:
		return self.make_window(PyGOT)
