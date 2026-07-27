
from ..harness import UITestCase

from ...PyFNT.PyFNT import PyFNT
from ...PyFNT.InfoDialog import FontInfo
from ...FileFormats.FNT import FNT
from ...FileFormats.PCX import PCX

from unittest import mock

# These tests drive PyFNT through its public command methods, asserting on both
# widget state and the model. Outside-world boundaries — the file dialogs, the
# FNT specifications dialog, the BMP/FNT converters, and the error dialog — are
# stubbed per test so nothing blocks or touches disk. The special palette is
# seeded in-memory since the harness never runs `initialize()`/`open_files()`.

# Patch-target paths, named where they are looked up. Only the targets more than
# one test module reaches for live here; single-use targets stay in the module
# that needs them.
SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
INFO_DIALOG = 'PyMS.PyFNT.PyFNT.InfoDialog'


def _special_palette() -> PCX:
	# A recognizable special palette: pixel value c maps through `image[0]` to
	# palette index c, whose color is the distinct grayscale (c, c, c).
	pcx = PCX([(i, i, i) for i in range(256)])
	pcx.image = [list(range(256))]
	return pcx


def info_dialog_stub(result: FontInfo | None) -> mock.Mock:
	stub = mock.Mock()
	stub.result = result
	return stub


def make_font(width: int = 4, height: int = 3, start: int = 32, letters: int = 5) -> FNT:
	fnt = FNT()
	fnt.width, fnt.height, fnt.start = width, height, start
	fnt.letters = [[[0] * width for _ in range(height)] for __ in range(letters)]
	return fnt


class PyFNTTestCase(UITestCase):
	def open_pyfnt(self) -> PyFNT:
		gui = self.make_window(PyFNT)
		gui.palette = _special_palette()
		return gui

	def with_new_font(self) -> PyFNT:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=info_dialog_stub(FontInfo(lowi=32, letters=5, width=4, height=3))):
			gui.new()
		self.pump(gui)
		return gui
