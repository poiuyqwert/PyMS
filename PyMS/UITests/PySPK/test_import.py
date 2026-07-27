
from .utils import PySPKTestCase, make_image

from ...FileFormats import SPK
from ...Utilities.CheckSaved import CheckSaved

from unittest import mock

from typing import Any

SELECT_OPEN = 'PyMS.Utilities.Config.SelectFile.select_open'
LAYER_COUNT_DIALOG = 'PyMS.PySPK.PySPK.LayerCountDialog'
INTERPRET_FILE = 'PyMS.FileFormats.SPK.SPK.interpret_file'


class Test_PySPK_import(PySPKTestCase):
	def test_import_marks_document_edited(self) -> None:
		# A freshly imported parallax is unsaved work: it must be flagged edited
		# so closing without saving prompts instead of silently discarding it.
		gui = self.open_pyspk()
		def fake_interpret(spk: SPK.SPK, _filepath: Any, _layer_count: int) -> None:
			spk.layers = [SPK.SPKLayer()]
			spk.images = [make_image()]
		with mock.patch(SELECT_OPEN, return_value='stars.bmp'), \
				mock.patch(LAYER_COUNT_DIALOG) as layer_count_dialog, \
				mock.patch(INTERPRET_FILE, autospec=True, side_effect=fake_interpret):
			layer_count_dialog.return_value.result.get.return_value = 1
			gui.iimport()
		self.pump(gui)
		self.assertIsNotNone(gui.spk)
		self.assertIsNone(gui.file)
		self.assertTrue(gui.edited)

	def test_import_into_open_file_keeps_it_as_the_save_target(self) -> None:
		gui = self.open_pyspk()
		with mock.patch('PyMS.FileFormats.SPK.SPK.load', return_value=None):
			gui.open(file='opened.spk')
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.spk')
		def fake_interpret(spk: SPK.SPK, _filepath: Any, _layer_count: int) -> None:
			spk.layers = [SPK.SPKLayer()]
			spk.images = [make_image()]
		with mock.patch(SELECT_OPEN, return_value='stars.bmp'), \
				mock.patch(LAYER_COUNT_DIALOG) as layer_count_dialog, \
				mock.patch(INTERPRET_FILE, autospec=True, side_effect=fake_interpret):
			layer_count_dialog.return_value.result.get.return_value = 1
			gui.iimport()
		self.pump(gui)
		self.assertEqual(gui.file, 'opened.spk')
		with mock.patch('PyMS.FileFormats.SPK.SPK.save', return_value=None) as spk_save, \
				mock.patch('PyMS.PySPK.PySPK.check_allow_overwrite_internal_file', return_value=True):
			result = gui.save()
		self.assertEqual(result, CheckSaved.saved)
		spk_save.assert_called_once_with('opened.spk')
