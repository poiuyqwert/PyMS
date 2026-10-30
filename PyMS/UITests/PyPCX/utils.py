
from ..harness import UITestCase

from ...PyPCX.PyPCX import PyPCX
from ...FileFormats.PCX import PCX

from unittest import mock

from typing import Any

# These tests drive PyPCX through its public command methods, asserting on both
# widget state and the model. Outside-world boundaries — the file dialogs, the
# PCX/BMP/Palette loaders and savers, and the unsaved-changes prompt — are
# stubbed per test so nothing blocks or touches disk.

# Patch-target paths, named where they are looked up. Only the targets more than
# one test module reaches for live here; single-use targets stay in the module
# that needs them.
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
ASK_SAVE = 'tkinter.messagebox.askyesnocancel'
PCX_LOAD = 'PyMS.FileFormats.PCX.PCX.load'
BMP_LOAD = 'PyMS.FileFormats.BMP.BMP.load'

PALETTE = [(i, i, i) for i in range(256)]

def _fake_bmp_load(bmp: Any, _file: Any) -> None:
	bmp.set_pixels([[0, 1], [2, 3]], PALETTE)

def _fake_pcx_load(pcx: PCX, _file: Any) -> None:
	pcx.load_pixels([[0, 1], [2, 3]], PALETTE)


class PyPCXTestCase(UITestCase):
	def open_pypcx(self) -> PyPCX:
		return self.make_window(PyPCX)

	def open_pcx_file(self, gui: PyPCX, file: str = 'opened.pcx') -> None:
		with mock.patch(SELECT_OPEN, return_value=file), \
				mock.patch(PCX_LOAD, new=_fake_pcx_load):
			gui.open()
		self.pump(gui)

	def import_bmp(self, gui: PyPCX) -> None:
		# Discard unsaved changes if prompted, so a repeat import can't block on
		# a real message box now that importing marks the content edited.
		with mock.patch(SELECT_OPEN, return_value='image.bmp'), \
				mock.patch(BMP_LOAD, new=_fake_bmp_load), \
				mock.patch(ASK_SAVE, return_value=False):
			gui.iimport()
		self.pump(gui)
