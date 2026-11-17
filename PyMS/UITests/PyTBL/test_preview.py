
from .utils import PyTBLTestCase

from ...PyTBL.PyTBL import PyTBL
from ...PyTBL.PreviewDialog import PreviewDialog
from ...FileFormats import FNT
from ...FileFormats import PCX
from ...FileFormats import GRP

from unittest import mock


class Test_PyTBL_preview(PyTBLTestCase):
	def make_pytbl_with_fonts(self, strings: list[str]) -> PyTBL:
		gui = self.make_pytbl(strings)
		gui.data_context.set_tfontgam_pcx(PCX.PCX())
		gui.data_context.set_font8_fnt(FNT.FNT())
		gui.data_context.set_font10_fnt(FNT.FNT())
		gui.data_context.set_palette('Units', [(0, 0, 0)] * 256)
		gui.data_context.set_icons_grp(GRP.CacheGRP())
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
		# Empty in-memory fonts have no glyphs and the icons have no frames, so nothing is drawn
		gui = self.make_pytbl_with_fonts(['a\x01mineral cost'])
		dialog = self.make_preview(gui)
		self.assertTrue(dialog.winfo_exists())
