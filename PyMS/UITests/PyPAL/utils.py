
from ..harness import UITestCase

from ...PyPAL.PyPAL import PyPAL
from ...Utilities import UIKit as UI

import io
from unittest import mock

from typing import Any, Callable

# These tests drive PyPAL through its public command methods and real widget
# seams (keyboard shortcuts, the canvas, the palette menu), asserting on both
# widget state and the model. Outside-world boundaries that a method reaches —
# file dialogs, message boxes, the color chooser, the on-disk save, and the
# secondary dialog windows — are stubbed per test so nothing blocks or touches
# disk. The harness already neutralizes settings I/O, analytics, the update
# check, and the tracer for construction.

# A recognizable 256-color palette: each entry is distinct so swatch colors and
# round-trips can be asserted precisely. Index 0 is black; index 1 is (1,2,3).
PALETTE = [(i, (i * 2) % 256, (i * 3) % 256) for i in range(256)]

# Patch-target paths, named where they are looked up. Only the targets more than
# one test module reaches for live here; single-use targets stay in the module
# that needs them.
ASKYESNOCANCEL = 'tkinter.messagebox.askyesnocancel'
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
ERROR_DIALOG = 'PyMS.PyPAL.PyPAL.ErrorDialog'


def raw_rgb_bytes() -> bytes:
	# 768-byte raw RGB dump — `Palette.load` detects this as `raw_rgb`.
	return bytes(component for color in PALETTE for component in color)


def make_event(**attrs: Any) -> UI.Event:
	event: UI.Event = UI.Event()
	for name, value in attrs.items():
		setattr(event, name, value)
	return event


class PyPALTestCase(UITestCase):
	def open_pypal(self, factory: Callable[[], PyPAL] = PyPAL, extra_patches: dict[str, dict[str, Any]] | None = None) -> PyPAL:
		return self.make_window(factory, extra_patches=extra_patches)

	def with_new_palette(self) -> PyPAL:
		gui = self.open_pypal()
		gui.new()
		self.pump(gui)
		return gui

	def with_loaded_palette(self) -> PyPAL:
		# Drive the real Open flow with the file dialog stubbed to return an
		# in-memory palette stream, leaving a clean (unedited) loaded document.
		gui = self.open_pypal()
		with mock.patch(SELECT_OPEN, return_value=io.BytesIO(raw_rgb_bytes())):
			gui.open()
		self.pump(gui)
		return gui
