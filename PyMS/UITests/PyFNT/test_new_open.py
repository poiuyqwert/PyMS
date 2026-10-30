
from .utils import PyFNTTestCase, SELECT_OPEN, INFO_DIALOG, info_dialog_stub, make_font

from ...PyFNT.InfoDialog import FontInfo
from ...FileFormats.FNT import FNT

from unittest import mock

from typing import Any


class Test_PyFNT_new(PyFNTTestCase):
	def test_new_cancelled_dialog_aborts(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=info_dialog_stub(None)):
			gui.new()
		self.assertIsNone(gui.fnt)
		self.assertFalse(gui.is_file_open())

	def test_new_cancelled_dialog_keeps_current_font(self) -> None:
		gui = self.with_new_font()
		original = gui.fnt
		with mock.patch(INFO_DIALOG, return_value=info_dialog_stub(None)):
			gui.new()
		self.assertIs(gui.fnt, original)

	def test_new_accepted_dialog_builds_font(self) -> None:
		gui = self.open_pyfnt()
		with mock.patch(INFO_DIALOG, return_value=info_dialog_stub(FontInfo(lowi=33, letters=6, width=5, height=7))):
			gui.new()
		self.pump(gui)
		assert gui.fnt is not None
		self.assertEqual((gui.fnt.width, gui.fnt.height, gui.fnt.start), (5, 7, 33))
		self.assertEqual(len(gui.fnt.letters), 6)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.is_file_open())
		self.assertTrue(gui.toolbar.tag_is_enabled('file_open'))
		self.assertIn('(Untitled.fnt)', gui.title())


class Test_PyFNT_open(PyFNTTestCase):
	def test_open_in_memory_font_clears_stale_file(self) -> None:
		# Opening a font object (the Import path) must not leave the previous
		# document's path behind, or a later Save would silently overwrite it.
		gui = self.with_new_font()
		gui.file = 'previous.fnt'
		gui.open(file=make_font())
		self.assertIsNone(gui.file)
		self.assertIn('(Untitled.fnt)', gui.title())

	def test_open_from_path_records_file(self) -> None:
		gui = self.open_pyfnt()
		loaded = make_font()
		def fake_load(fnt: FNT, _file: Any) -> None:
			fnt.width, fnt.height, fnt.start = loaded.width, loaded.height, loaded.start
			fnt.letters = loaded.letters
		with mock.patch(SELECT_OPEN, return_value='opened.fnt'), \
				mock.patch('PyMS.FileFormats.FNT.FNT.load', new=fake_load):
			gui.open()
		self.assertEqual(gui.file, 'opened.fnt')
		self.assertIn('(opened.fnt)', gui.title())
