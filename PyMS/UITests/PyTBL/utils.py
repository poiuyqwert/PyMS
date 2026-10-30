
from ..harness import UITestCase

from ...PyTBL.PyTBL import PyTBL
from ...FileFormats import TBL

from unittest import mock

# These tests drive PyTBL through its public command methods, asserting on
# both widget and model state. The harness neutralizes settings I/O,
# analytics, the update check, and the tracer; TBL contents are supplied by
# stubbing `TBL.load` so no files are read.


class PyTBLTestCase(UITestCase):
	def make_pytbl(self, strings: list[str] | None = None) -> PyTBL:
		gui = self.make_window(PyTBL)
		if strings is not None:
			def fake_load(tbl: TBL.TBL, _file: str) -> None:
				tbl.strings = list(strings)
			with mock.patch('PyMS.FileFormats.TBL.TBL.load', autospec=True, side_effect=fake_load):
				gui.open(file='test.tbl')
			self.pump(gui)
		return gui

	def selected_index(self, gui: PyTBL) -> int | None:
		selection = gui.listbox.curselection()
		if not selection:
			return None
		return int(selection[0])
