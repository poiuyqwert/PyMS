
from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...PyTBL.PreviewDialog import PreviewDialog
from ...FileFormats import FNT
from ...FileFormats import PCX
from ...FileFormats import Palette
from ...FileFormats import GRP

from unittest import mock


class Test_PyTBL_preview(PyTBLTestCase):
	def make_pytbl_with_fonts(self, strings: list[str]) -> PyTBL:
		gui = self.make_pytbl(strings)
		gui.tfontgam = PCX.PCX()
		gui.font8 = FNT.FNT()
		gui.font10 = FNT.FNT()
		gui.unitpal = Palette.Palette()
		gui.icons = GRP.GRP()
		return gui

	def make_preview(self, gui: PyTBL) -> PreviewDialog:
		with mock.patch('PyMS.Utilities.UIKit.Widgets.Extensions.WindowExtensions.grab_wait', return_value=None):
			dialog = PreviewDialog(gui, gui)
		self.pump(gui)
		return dialog

	def test_one_character_string_previews_without_error(self) -> None:
		gui = self.make_pytbl_with_fonts(['x'])
		dialog = self.make_preview(gui)
		self.assertTrue(dialog.winfo_exists())

	def test_hotkey_string_with_no_displayable_glyphs_previews_without_error(self) -> None:
		# The resource icon offsets point into the synthetic resource line, which
		# can be shorter than expected when glyphs fall outside the font range
		# (empty in-memory fonts filter out every glyph).
		gui = self.make_pytbl_with_fonts(['a\x01mineral cost'])
		dialog = self.make_preview(gui)
		self.assertTrue(dialog.winfo_exists())
