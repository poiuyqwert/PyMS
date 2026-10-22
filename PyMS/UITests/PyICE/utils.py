
from ..harness import UITestCase

from ...PyICE.PyICE import PyICE

from typing import Any

# These tests drive PyICE through its public command methods and its menubar,
# asserting on widget state. The harness neutralizes settings I/O, analytics,
# the update check, and the tracer. `initialize()` (which loads the TBL/DAT
# files from the MPQs) is never called, so no game data is read.


class PyICETestCase(UITestCase):
	def make_pyice(self, extra_patches: dict[str, dict[str, Any]] | None = None) -> PyICE:
		return self.make_window(PyICE, extra_patches=extra_patches)
