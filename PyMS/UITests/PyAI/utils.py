from ..harness import UITestCase

from ...PyAI.PyAI import PyAI


class PyAITestCase(UITestCase):
	def make_pyai(self) -> PyAI:
		return self.make_window(PyAI)
